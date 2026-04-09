"""
CAMBRIAN EXPLOSION: Mass speciation under predation pressure.

8 founder organisms on a large grid with aggressive predation,
fast fragmentation, and high mutation. Does the system produce:
1. Rapid diversification (many new lineages)?
2. Mass extinction events (sudden lineage collapses)?
3. "Cambrian-like" pattern: explosion of diversity followed by consolidation?

This is the ultimate long-run ecosystem experiment.
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 50
CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'action_dim': 4,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.55,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.15,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 85.0, 'division_cost': 10.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 150,
    'cell_mutation_rate': 0.025,           # HIGH mutation
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.003, 'resource_regen_rate': 0.001,
    'migration_enabled': True,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_division_coupling': 2.0,
    'action_weight_scale': 0.20,           # Larger initial actions
    'action_mutation_rate': 0.05,          # HIGH action mutation
    'displacement_energy_ratio': 3.0,
    # Many resource patches for diverse niches
    'landscape_type': 'patches', 'landscape_base': 0.15,
    'landscape_n_patches': 8, 'landscape_patch_radius': 0.15,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [
        (10, 10), (10, 25), (10, 40),
        (25, 10), (25, 40),
        (40, 10), (40, 25), (40, 40),
    ],
    # AGGRESSIVE fragmentation
    'fragmentation_enabled': True,
    'fragmentation_interval': 50,          # Check every 50 ticks
    'fragmentation_min_size': 3,           # Small fragments viable
    # Stigmergy
    'death_imprint_strength': 1.0,
    'stigmergy_decay': 0.99,              # Faster decay
    'stigmergy_sensing': 0.3,
    'stigmergy_avoidance': 0.4,
    # v0.9.0 PREDATION with arms race
    'predation_enabled': True,
    'predation_energy_ratio': 1.3,         # Easy to predate
    'predation_efficiency': 0.6,
    'predation_cooldown': 3,               # Fast killing
    'predation_action_threshold': 0.0,
    'predation_action_power': 1.5,         # Action-coupled
    'predation_evasion_scaling': 0.2,      # Some evasion
    'predation_alarm_strength': 0.5,       # Alarm signals
}

TICKS = 12000
REPORT = 500

def place(tissue, cr, cc, lid, n=6, energy=120.0):
    placed = 0
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if placed >= n:
                return placed
            r, c = cr + dr, cc + dc
            if (0 <= r < GRID and 0 <= c < GRID
                    and tissue.grid[r][c] is None and abs(dr) + abs(dc) <= 2):
                tissue.place_cell(r, c)
                tissue.grid[r][c].lineage_id = lid
                tissue.grid[r][c].energy = energy
                placed += 1
    return placed

def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    # 8 founders on 8 patches
    patches = CONFIG['landscape_patch_centers']
    for i, (cr, cc) in enumerate(patches):
        place(t, cr, cc, lid=i+1, n=6)

    print("=" * 70)
    print("  CAMBRIAN EXPLOSION: Mass Speciation Under Predation")
    print(f"  Grid: {GRID}x{GRID} | 8 founders | {TICKS} ticks")
    print(f"  Mutation: cell={CONFIG['cell_mutation_rate']}, "
          f"action={CONFIG['action_mutation_rate']}")
    print(f"  Predation: ratio={CONFIG['predation_energy_ratio']}, "
          f"action_power={CONFIG['predation_action_power']}")
    print("=" * 70)

    history = []
    peak_lineages = 0
    peak_tick = 0
    extinctions = {}
    original_lineages = set(range(1, 9))

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT == 0:
            snap = t.ecosystem_snapshot()
            n_lin = snap['n_lineages']
            
            if n_lin > peak_lineages:
                peak_lineages = n_lin
                peak_tick = tick

            # Track original lineage extinctions
            for lid in list(original_lineages):
                if lid not in snap['lineages']:
                    extinctions[lid] = tick
                    original_lineages.discard(lid)

            # Top 5 lineages by size
            sorted_lin = sorted(snap['lineages'].items(), key=lambda x: x[1]['cell_count'], reverse=True)
            top5 = sorted_lin[:5]
            top5_str = " ".join(f"L{lid}={d['cell_count']}" for lid, d in top5)
            others = sum(d['cell_count'] for _, d in sorted_lin[5:])
            others_str = f" +{len(sorted_lin)-5}lin/{others}c" if len(sorted_lin) > 5 else ""

            history.append({
                'tick': tick,
                'total': snap['total_cells'],
                'n_lineages': n_lin,
                'predation': t.predation_kills,
                'births': t.total_births,
                'deaths': t.total_deaths,
            })

            print(f"  t={tick:5d}: {top5_str}{others_str}  "
                  f"(tot={snap['total_cells']}, lin={n_lin}, "
                  f"pred={t.predation_kills}, d={t.total_deaths})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  CAMBRIAN EXPLOSION RESULTS")
    print("=" * 70)

    snap = t.ecosystem_snapshot()
    print(f"\n  Final: {snap['total_cells']} cells, {snap['n_lineages']} lineages")
    print(f"  Peak lineages: {peak_lineages} at t={peak_tick}")
    print(f"  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Predation kills: {t.predation_kills}")
    print(f"  Starvation deaths: {t.total_deaths - t.predation_kills}")

    if extinctions:
        print(f"\n  ORIGINAL LINEAGE EXTINCTIONS ({len(extinctions)}/8):")
        for lid, tick in sorted(extinctions.items(), key=lambda x: x[1]):
            print(f"    L{lid}: extinct at t={tick}")
        survivors = [i for i in range(1, 9) if i not in extinctions]
        print(f"  SURVIVORS: {', '.join(f'L{s}' for s in survivors)}" if survivors else "  ALL ORIGINAL LINEAGES EXTINCT!")

    # Diversity trajectory
    if len(history) >= 4:
        lineage_counts = [h['n_lineages'] for h in history]
        print(f"\n  DIVERSITY TRAJECTORY:")
        print(f"    Early (t=1000): {history[1]['n_lineages']} lineages")
        mid = len(history) // 2
        print(f"    Mid (t={history[mid]['tick']}): {history[mid]['n_lineages']} lineages")
        print(f"    Late (t={history[-1]['tick']}): {history[-1]['n_lineages']} lineages")
        print(f"    Peak: {peak_lineages} lineages at t={peak_tick}")

        # Cambrian pattern detection
        early_div = np.mean(lineage_counts[:4])
        late_div = np.mean(lineage_counts[-4:])
        if peak_lineages > max(early_div, late_div) * 1.5:
            print(f"\n    -> CAMBRIAN PATTERN DETECTED!")
            print(f"       Rapid diversification peaking at {peak_lineages} lineages,")
            print(f"       followed by consolidation to {lineage_counts[-1]} lineages.")
        elif late_div > early_div * 1.5:
            print(f"\n    -> ONGOING RADIATION: diversity still increasing")
        else:
            print(f"\n    -> Stable ecosystem: diversity plateau")

    # Final lineage analysis
    print(f"\n  TOP 5 LINEAGES:")
    sorted_lin = sorted(snap['lineages'].items(), key=lambda x: x[1]['cell_count'], reverse=True)
    for lid, d in sorted_lin[:5]:
        is_original = "ORIGINAL" if lid <= 8 else f"fragment"
        print(f"    L{lid} ({is_original}): {d['cell_count']} cells, "
              f"E={d['mean_energy']:.1f}, err={d['mean_error']:.3f}, "
              f"centroid=({d['centroid'][0]:.0f},{d['centroid'][1]:.0f})")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
