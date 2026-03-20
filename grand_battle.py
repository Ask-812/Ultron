"""
GRAND BATTLE: The Ultimate v0.9.0 Experiment

4 organisms on a 4-patch landscape with EVERYTHING enabled:
- Heterogeneous resources (patches)
- Toxin chemical warfare
- Predation (energy dominance)
- Lamarckian weight inheritance
- Organism fragmentation
- Stigmergy (death trace memory)
- Evolved action behavior

The question: What emerges when all forces act simultaneously?
Do we get stable coexistence, competitive exclusion, or chaos?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 35
CONFIG = {
    'observation_dim': 12, 'signal_dim': 4, 'action_dim': 4, 'env_dim': 8,
    'starting_energy': 150.0, 'energy_capacity': 200.0, 'consumption_rate': 0.08,
    'extraction_factor': 0.60, 'base_signal_ratio': 0.55, 'spatial_gradient': 0.15,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 90.0, 'division_cost': 12.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 100,
    'cell_mutation_rate': 0.015,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.002, 'resource_regen_rate': 0.0005,
    'migration_enabled': True,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_division_coupling': 2.0,
    'action_weight_scale': 0.15, 'action_mutation_rate': 0.03,
    'displacement_energy_ratio': 3.0,
    # 4-patch landscape
    'landscape_type': 'patches', 'landscape_base': 0.15,
    'landscape_n_patches': 4, 'landscape_patch_radius': 0.22,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(9,9), (9,26), (26,9), (26,26)],
    # Fragmentation
    'fragmentation_enabled': True, 'fragmentation_interval': 200,
    'fragmentation_min_size': 5,
    # Stigmergy
    'death_imprint_strength': 1.0, 'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.3, 'stigmergy_avoidance': 0.3,
    # PREDATION + evolved attack/defense
    'predation_enabled': True,
    'predation_energy_ratio': 1.5,
    'predation_efficiency': 0.5,
    'predation_cooldown': 5,
    'predation_action_threshold': 0.0,
    'predation_action_power': 0.5,     # action magnitude amplifies attack
    'predation_evasion_scaling': 0.2,  # competent cells can dodge
    'predation_alarm_strength': 0.5,   # alarm signals on predation
    # TOXIN WARFARE
    'toxin_enabled': True,
    'toxin_emission_rate': 0.15,
    'toxin_damage_rate': 0.6,
    'toxin_range': 3,
    'toxin_cost_rate': 0.05,
    # LAMARCKIAN INHERITANCE
    'weight_inheritance_ratio': 0.5,
    'weight_inheritance_noise': 0.01,
}

TICKS = 15000
REPORT = 1000


def place(tissue, cr, cc, lid, n=8, energy=150.0):
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


def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    # 4 organisms on 4 patches
    patches = [(9, 9), (9, 26), (26, 9), (26, 26)]
    for i, (cr, cc) in enumerate(patches):
        place(t, cr, cc, lid=i + 1, n=8)

    print("=" * 70)
    print("  GRAND BATTLE: 4 Organisms, All Physics, Full Evolution")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS}")
    print(f"  Features: predation + toxins + Lamarckian + fragmentation + stigmergy")
    print("=" * 70)

    extinctions = {}

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT == 0:
            snap = t.ecosystem_snapshot()
            counts = {lid: d['cell_count'] for lid, d in snap['lineages'].items()}

            # Track extinctions
            for lid in [1, 2, 3, 4]:
                if lid not in counts and lid not in extinctions:
                    extinctions[lid] = tick

            # Action magnitude per lineage
            action_strs = []
            for lid, d in sorted(snap['lineages'].items()):
                cells = []
                for r in range(t.rows):
                    for c in range(t.cols):
                        cell = t.grid[r][c]
                        if cell and cell.is_alive and cell.lineage_id == lid and cell.action is not None:
                            cells.append(float(np.linalg.norm(cell.action)))
                amag = np.mean(cells) if cells else 0
                action_strs.append(f"L{lid}={d['cell_count']}({amag:.2f})")

            print(f"  t={tick:5d}: {' '.join(action_strs)}  "
                  f"(total={snap['total_cells']}, lin={snap['n_lineages']}, "
                  f"pred={t.predation_kills}, toxin_dmg={t.toxin_damage_dealt:.0f}, "
                  f"deaths={t.total_deaths}, births={t.total_births})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  GRAND BATTLE RESULTS")
    print("=" * 70)
    snap = t.ecosystem_snapshot()
    print(f"\n  Final: {snap['total_cells']} cells, {snap['n_lineages']} lineages")
    print(f"  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Predation kills: {t.predation_kills}")
    print(f"  Toxin events: {t.toxin_events}")
    print(f"  Toxin damage: {t.toxin_damage_dealt:.1f}")
    print(f"  Non-violent deaths: {t.total_deaths - t.predation_kills}")

    if extinctions:
        print(f"\n  EXTINCTIONS:")
        for lid, tick in sorted(extinctions.items()):
            print(f"    L{lid}: extinct at t={tick}")
    else:
        print(f"\n  No extinctions — all original lineages survived!")

    surviving = [lid for lid in range(1, 5) if lid not in extinctions]
    print(f"\n  SURVIVORS: {', '.join(f'L{lid}' for lid in surviving)}")

    for lid, d in sorted(snap['lineages'].items()):
        print(f"  L{lid}: {d['cell_count']} cells, E={d['mean_energy']:.1f}, "
              f"err={d['mean_error']:.4f}, age={d['mean_age']:.0f}")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
