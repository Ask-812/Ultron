"""
Chemical Arms Race: Do organisms evolve increasing toxin output over time?

Two organisms on adjacent patches with toxin warfare enabled.
Track action magnitude (= toxin output) over generations.
The question: do we see Red Queen dynamics — escalating arms race?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 30
CONFIG = {
    'observation_dim': 12, 'signal_dim': 4, 'action_dim': 4, 'env_dim': 8,
    'starting_energy': 150.0, 'energy_capacity': 200.0, 'consumption_rate': 0.08,
    'extraction_factor': 0.65, 'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 95.0, 'division_cost': 12.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 100,
    'cell_mutation_rate': 0.015,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.001, 'resource_regen_rate': 0.0003,
    'migration_enabled': True,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_division_coupling': 2.0,
    'action_weight_scale': 0.15, 'action_mutation_rate': 0.03,
    'displacement_energy_ratio': 3.0,
    # Landscape: two adjacent patches
    'landscape_type': 'patches', 'landscape_base': 0.2,
    'landscape_n_patches': 2, 'landscape_patch_radius': 0.25,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(10, 15), (20, 15)],
    'fragmentation_enabled': False,
    'death_imprint_strength': 1.0, 'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.3, 'stigmergy_avoidance': 0.2,
    # Predation disabled — ONLY toxin warfare
    'predation_enabled': False,
    # TOXIN WARFARE
    'toxin_enabled': True,
    'toxin_emission_rate': 0.2,
    'toxin_damage_rate': 0.8,
    'toxin_range': 3,
    'toxin_cost_rate': 0.05,
}

TICKS = 12000
REPORT = 500


def place(tissue, cr, cc, lid, n=10, energy=150.0):
    placed = 0
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if placed >= n:
                return placed
            r, c = cr + dr, cc + dc
            if (0 <= r < GRID and 0 <= c < GRID
                    and tissue.grid[r][c] is None and abs(dr) + abs(dc) <= 3):
                tissue.place_cell(r, c)
                tissue.grid[r][c].lineage_id = lid
                tissue.grid[r][c].energy = energy
                placed += 1
    return placed


def get_lineage_stats(tissue, lid):
    actions = []
    energies = []
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell and cell.is_alive and cell.lineage_id == lid:
                if cell.action is not None:
                    actions.append(float(np.linalg.norm(cell.action)))
                energies.append(cell.energy)
    if not actions:
        return None
    return {
        'count': len(actions),
        'action_mean': float(np.mean(actions)),
        'action_max': float(np.max(actions)),
        'energy_mean': float(np.mean(energies)),
    }


def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    na = place(t, 10, 15, lid=1, n=10)
    nb = place(t, 20, 15, lid=2, n=10)

    print("=" * 70)
    print("  CHEMICAL ARMS RACE: Toxin Evolution Between Two Organisms")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS}")
    print(f"  Toxin: rate={CONFIG['toxin_emission_rate']}, dmg={CONFIG['toxin_damage_rate']}, "
          f"range={CONFIG['toxin_range']}, cost={CONFIG['toxin_cost_rate']}")
    print(f"  Predation: DISABLED (pure chemical warfare)")
    print("=" * 70)

    action_history = {1: [], 2: []}

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT == 0:
            s1 = get_lineage_stats(t, 1)
            s2 = get_lineage_stats(t, 2)

            if s1:
                action_history[1].append(s1['action_mean'])
            if s2:
                action_history[2].append(s2['action_mean'])

            l1_str = f"L1={s1['count']}c E={s1['energy_mean']:.1f} A={s1['action_mean']:.3f}" if s1 else "L1=EXTINCT"
            l2_str = f"L2={s2['count']}c E={s2['energy_mean']:.1f} A={s2['action_mean']:.3f}" if s2 else "L2=EXTINCT"

            print(f"  t={tick:5d}: {l1_str} | {l2_str}  "
                  f"(toxin_evts={t.toxin_events}, toxin_dmg={t.toxin_damage_dealt:.0f}, "
                  f"deaths={t.total_deaths})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  ARMS RACE RESULTS")
    print("=" * 70)
    snap = t.ecosystem_snapshot()
    print(f"\n  Final: {snap['total_cells']} cells, {snap['n_lineages']} lineages")
    print(f"  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Toxin events: {t.toxin_events}")
    print(f"  Toxin damage dealt: {t.toxin_damage_dealt:.1f}")

    for lid in [1, 2]:
        hist = action_history[lid]
        if len(hist) >= 4:
            early = np.mean(hist[:3])
            late = np.mean(hist[-3:])
            change = (late - early) / early * 100 if early > 0 else 0
            print(f"\n  L{lid} Action Magnitude Escalation:")
            print(f"    Early (first 1500 ticks): {early:.4f}")
            print(f"    Late (last 1500 ticks): {late:.4f}")
            print(f"    Change: {change:+.1f}%")
            if change > 10:
                print(f"    -> ESCALATION DETECTED: toxin output increasing!")
            elif change < -10:
                print(f"    -> DE-ESCALATION: organisms reducing chemical warfare!")
            else:
                print(f"    -> Stable: toxin output roughly constant")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
