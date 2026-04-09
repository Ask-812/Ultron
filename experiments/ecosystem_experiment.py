"""
GRAND ECOSYSTEM EXPERIMENT
==========================
The question: Can multiple organisms on a heterogeneous landscape evolve
genuinely different strategies through competition and niche partitioning?

Setup:
  - 40x40 grid with 4 resource patches (oases in desert)
  - 4 founding organisms, each seeded near a different patch
  - Full physics: signals, phenotype, actions, motility, resource depletion
  - Fragmentation enabled: organisms can reproduce by splitting
  - Competitive displacement: organisms can invade each other's territory
  - 10,000 ticks (~100+ cell generations)

Measurements:
  - Population dynamics per lineage over time
  - Trait divergence (extraction efficiency, metabolic rate)
  - Phenotype specialization per organism
  - Spatial territory maps at key timepoints
  - Action weight divergence
  - Resource landscape evolution
"""
import numpy as np
import sys
import time
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ultron.tissue import Tissue

# ==== CONFIGURATION ====
GRID_SIZE = 40
TICKS = 10000
CHECKPOINT_INTERVAL = 500

CONFIG = {
    # Dimensions
    'env_dim': 8,
    'signal_dim': 4,
    'observation_dim': 12,

    # Energy
    'starting_energy': 150.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.60,

    # Signal propagation
    'base_signal_ratio': 0.55,
    'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9,
    'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0,
    'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,

    # Cell biology
    'division_energy_threshold': 100.0,
    'division_cost': 15.0,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 400,
    'cell_mutation_rate': 0.01,  # Slightly higher for faster evolution

    # Phenotype
    'phenotype_max_plasticity': 0.05,
    'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0,
    'phenotype_affinity_coupling': 2.0,

    # Resource dynamics — fast enough to see effects but not instant death
    'resource_depletion_rate': 0.0008,
    'resource_regen_rate': 0.0001,

    # Motility — enables crawling toward resources
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.4,

    # Action coupling — evolved directional preferences
    'action_dim': 4,
    'action_division_coupling': 2.0,
    'action_weight_scale': 0.1,
    'action_mutation_rate': 0.02,

    # Heterogeneous landscape with explicit patch centers
    'landscape_type': 'patches',
    'landscape_base': 0.25,      # Desert baseline
    'landscape_n_patches': 4,
    'landscape_patch_radius': 0.18,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(10, 10), (10, 30), (30, 10), (30, 30)],

    # Fragmentation: organism reproduction via splitting
    'fragmentation_enabled': True,
    'fragmentation_interval': 100,
    'fragmentation_min_size': 5,

    # Multi-organism competition
    'displacement_energy_ratio': 2.5,
}


def place_founder(tissue, row, col, lineage_id, n_cells=5):
    """Place a small founder colony with a unique lineage ID."""
    placed = 0
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            r, c = row + dr, col + dc
            if (0 <= r < tissue.rows and 0 <= c < tissue.cols
                    and tissue.grid[r][c] is None and placed < n_cells):
                tissue.place_cell(r, c)
                tissue.grid[r][c].lineage_id = lineage_id
                placed += 1
    return placed


def ascii_territory_map(tissue, width=40):
    """Generate a compact ASCII territory map."""
    lmap = tissue.get_lineage_map()
    symbols = '.ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#'
    lines = []
    for r in range(tissue.rows):
        row = ''
        for c in range(tissue.cols):
            lid = lmap[r, c]
            if lid < 0:
                # Show resource level for empty cells
                res = tissue.resource_field[r, c]
                row += ' ' if res < 0.3 else '.' if res < 0.6 else ':'
            else:
                idx = lid % (len(symbols) - 1) + 1
                row += symbols[idx]
        lines.append(row)
    return '\n'.join(lines)


def ascii_resource_map(tissue):
    """Generate ASCII resource level map."""
    lines = []
    chars = ' .:-=+*#@'
    for r in range(tissue.rows):
        row = ''
        for c in range(tissue.cols):
            res = tissue.resource_field[r, c]
            idx = min(int(res * (len(chars) - 1)), len(chars) - 1)
            row += chars[idx]
        lines.append(row)
    return '\n'.join(lines)


def trait_summary(eco):
    """Extract trait divergence metrics from ecosystem snapshot."""
    lineages = eco['lineages']
    if len(lineages) < 2:
        return None

    extractions = []
    metabolics = []
    phenotypes = []
    for lid, data in lineages.items():
        extractions.append(data['mean_extraction'])
        metabolics.append(data['mean_metabolic'])
        phenotypes.append(data['phenotype_mean'])

    # Trait divergence: std across organism means
    ext_div = float(np.std(extractions))
    met_div = float(np.std(metabolics))

    # Phenotype divergence: mean pairwise distance
    phenos = np.array(phenotypes)
    n = len(phenos)
    if n >= 2:
        dists = []
        for i in range(n):
            for j in range(i + 1, n):
                dists.append(float(np.linalg.norm(phenos[i] - phenos[j])))
        pheno_div = float(np.mean(dists))
    else:
        pheno_div = 0.0

    return {
        'extraction_divergence': ext_div,
        'metabolic_divergence': met_div,
        'phenotype_divergence': pheno_div,
    }


def collect_action_stats(tissue):
    """Collect per-lineage action weight statistics."""
    lineage_actions = {}
    obs_dim = tissue.config.get('observation_dim', 12)
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell is not None and cell.is_alive and cell.action is not None:
                lid = cell.lineage_id
                if lid not in lineage_actions:
                    lineage_actions[lid] = {'actions': [], 'weight_norms': []}
                lineage_actions[lid]['actions'].append(cell.action.copy())
                aw = cell.state.model.weights[obs_dim:, :]
                lineage_actions[lid]['weight_norms'].append(float(np.linalg.norm(aw)))
    result = {}
    for lid, data in lineage_actions.items():
        actions = np.array(data['actions'])
        result[lid] = {
            'mean_action': actions.mean(0).tolist(),
            'std_action': actions.std(0).tolist(),
            'mean_weight_norm': float(np.mean(data['weight_norms'])),
        }
    return result


def run_experiment():
    print("=" * 70)
    print("  ULTRON ECOSYSTEM EXPERIMENT")
    print("  Grid: %dx%d | Ticks: %d | Landscape: patches" % (GRID_SIZE, GRID_SIZE, TICKS))
    print("=" * 70)

    np.random.seed(7)
    tissue = Tissue(GRID_SIZE, GRID_SIZE, CONFIG)

    # Show initial landscape
    print("\n--- INITIAL RESOURCE LANDSCAPE ---")
    print(ascii_resource_map(tissue))

    # Place 4 founder organisms right at the resource patch centers
    founders = [
        (10, 10, 1),   # top-left patch
        (10, 30, 2),   # top-right patch
        (30, 10, 3),   # bottom-left patch
        (30, 30, 4),   # bottom-right patch
    ]

    for row, col, lid in founders:
        n = place_founder(tissue, row, col, lid)
        print(f"Founder {lid}: placed {n} cells at ({row}, {col})")

    print("\n--- SIMULATION BEGINS ---\n")

    history = []
    t0 = time.time()

    for tick in range(TICKS):
        tissue.step()

        if tick % CHECKPOINT_INTERVAL == 0 or tick == TICKS - 1:
            eco = tissue.ecosystem_snapshot()
            snap = tissue.snapshot()
            action_stats = collect_action_stats(tissue)
            diverg = trait_summary(eco)

            dt = time.time() - t0
            rate = (tick + 1) / max(dt, 0.001)
            eta = (TICKS - tick - 1) / max(rate, 0.001)

            print(f"t={tick:5d} | cells={eco['total_cells']:4d} | "
                  f"lineages={eco['n_lineages']:2d} | "
                  f"births={snap['births']:5d} deaths={snap['deaths']:5d} | "
                  f"resource={snap['resource_mean']:.3f} | "
                  f"{dt:.0f}s elapsed, ~{eta:.0f}s left")

            # Per-lineage summary
            for lid in sorted(eco['lineages'].keys()):
                d = eco['lineages'][lid]
                act_info = ""
                if lid in action_stats:
                    ma = action_stats[lid]['mean_action']
                    act_info = f" act=[{ma[0]:+.3f},{ma[1]:+.3f},{ma[2]:+.3f},{ma[3]:+.3f}]"
                print(f"  L{lid}: n={d['cell_count']:3d} E={d['mean_energy']:.0f} "
                      f"err={d['mean_error']:.3f} ext={d['mean_extraction']:.3f} "
                      f"met={d['mean_metabolic']:.3f} "
                      f"at=({d['centroid'][0]:.1f},{d['centroid'][1]:.1f}){act_info}")

            if diverg:
                print(f"  Divergence: ext={diverg['extraction_divergence']:.5f} "
                      f"met={diverg['metabolic_divergence']:.5f} "
                      f"pheno={diverg['phenotype_divergence']:.4f}")

            checkpoint = {
                'tick': tick,
                'ecosystem': eco,
                'snapshot': snap,
                'divergence': diverg,
                'action_stats': {str(k): v for k, v in action_stats.items()},
            }
            history.append(checkpoint)

            # Territory maps at key moments
            if tick in [0, 1000, 2500, 5000, 7500, TICKS - 1]:
                print(f"\n--- TERRITORY MAP t={tick} ---")
                print(ascii_territory_map(tissue))
                print(f"--- RESOURCE MAP t={tick} ---")
                print(ascii_resource_map(tissue))
                print()

    dt = time.time() - t0
    print("\n" + "=" * 70)
    print("  EXPERIMENT COMPLETE")
    print(f"  Duration: {dt:.1f}s ({dt/60:.1f}m)")
    print(f"  Final: {tissue.cell_count} cells, "
          f"{tissue.total_births} births, {tissue.total_deaths} deaths")
    print("=" * 70)

    # ===== FINAL ANALYSIS =====
    print("\n" + "=" * 70)
    print("  ANALYSIS: EMERGENT PHENOMENA")
    print("=" * 70)

    eco = tissue.ecosystem_snapshot()
    action_stats = collect_action_stats(tissue)

    # 1. Population dynamics
    print("\n--- 1. POPULATION DYNAMICS ---")
    for cp in history:
        e = cp['ecosystem']
        line = f"  t={cp['tick']:5d}: "
        parts = []
        for lid in sorted(e['lineages'].keys()):
            d = e['lineages'][lid]
            parts.append(f"L{lid}={d['cell_count']}")
        line += ' '.join(parts) + f" (total={e['total_cells']})"
        print(line)

    # 2. Trait divergence over time
    if any(cp['divergence'] for cp in history):
        print("\n--- 2. TRAIT DIVERGENCE OVER TIME ---")
        for cp in history:
            if cp['divergence']:
                d = cp['divergence']
                print(f"  t={cp['tick']:5d}: ext_div={d['extraction_divergence']:.5f} "
                      f"met_div={d['metabolic_divergence']:.5f} "
                      f"pheno_div={d['phenotype_divergence']:.4f}")

    # 3. Niche partitioning: where are organisms?
    print("\n--- 3. SPATIAL NICHE PARTITIONING ---")
    for lid in sorted(eco['lineages'].keys()):
        d = eco['lineages'][lid]
        print(f"  L{lid}: centroid=({d['centroid'][0]:.1f}, {d['centroid'][1]:.1f}), "
              f"extent={d['extent']:.1f}, cells={d['cell_count']}")

    # 4. Action specialization per organism
    if action_stats:
        print("\n--- 4. ACTION SPECIALIZATION PER ORGANISM ---")
        dirs = ['up', 'down', 'left', 'right']
        for lid in sorted(action_stats.keys()):
            a = action_stats[lid]
            mean = a['mean_action']
            dominant = np.argmax(np.abs(mean))
            print(f"  L{lid}: mean_action=[{mean[0]:+.4f},{mean[1]:+.4f},"
                  f"{mean[2]:+.4f},{mean[3]:+.4f}] "
                  f"dominant={dirs[dominant]} "
                  f"weight_norm={a['mean_weight_norm']:.3f}")

    # 5. Phenotype profiles per organism
    print("\n--- 5. PHENOTYPE PROFILES ---")
    print("  [surface_history, signal_exposure, competence, energy_status]")
    for lid in sorted(eco['lineages'].keys()):
        d = eco['lineages'][lid]
        p = d['phenotype_mean']
        print(f"  L{lid}: [{p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}, {p[3]:.3f}] "
              f"(internal_std={d['phenotype_std']:.4f})")

    # 6. Did speciation occur?
    print("\n--- 6. SPECIATION ASSESSMENT ---")
    n_surviving = len(eco['lineages'])
    n_fragments = eco['n_lineages']
    diverg = trait_summary(eco)
    if diverg and n_surviving >= 2:
        ext_d = diverg['extraction_divergence']
        pheno_d = diverg['phenotype_divergence']
        if pheno_d > 0.1:
            print(f"  YES: {n_surviving} lineages with phenotype divergence = {pheno_d:.4f}")
            print(f"  Organisms have developed meaningfully different identities.")
        elif pheno_d > 0.01:
            print(f"  PARTIAL: {n_surviving} lineages with phenotype divergence = {pheno_d:.4f}")
            print(f"  Some differentiation but organisms are still similar.")
        else:
            print(f"  NO: {n_surviving} lineages but phenotype divergence = {pheno_d:.4f} (too similar)")
    elif n_surviving == 1:
        print(f"  EXTINCTION: Only 1 lineage survived. Competition winner-take-all.")
    else:
        print(f"  NO SURVIVORS")

    # 7. Final territory map
    print("\n--- FINAL TERRITORY MAP ---")
    print(ascii_territory_map(tissue))

    # Save results
    output = {
        'config': {k: v for k, v in CONFIG.items() if not isinstance(v, np.ndarray)},
        'history': [],
        'final_ecosystem': eco,
    }
    for cp in history:
        entry = {
            'tick': cp['tick'],
            'total_cells': cp['ecosystem']['total_cells'],
            'n_lineages': cp['ecosystem']['n_lineages'],
            'births': cp['snapshot']['births'],
            'deaths': cp['snapshot']['deaths'],
            'resource_mean': cp['snapshot']['resource_mean'],
            'divergence': cp['divergence'],
        }
        # Per-lineage cell counts
        for lid, d in cp['ecosystem']['lineages'].items():
            entry[f'L{lid}_cells'] = d['cell_count']
            entry[f'L{lid}_energy'] = d['mean_energy']
        output['history'].append(entry)

    os.makedirs('history', exist_ok=True)
    with open('history/ecosystem_experiment.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print("\nResults saved to history/ecosystem_experiment.json")


if __name__ == '__main__':
    run_experiment()
