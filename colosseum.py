"""
Colosseum: 4 organisms confined with predation. Only the strong survive.

Small grid, high predation, limited resources. The ultimate survival test.
Can we produce genuine competitive exclusion or does coexistence persist?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 20
CONFIG = dict(
    rows=GRID, cols=GRID,
    observation_dim=12, signal_dim=4, action_dim=4, env_dim=8,
    start_energy=100.0, energy_capacity=200.0, consumption_rate=0.08,
    extraction_factor=0.55, metabolic_cost=0.3,
    signal_noise=0.01, base_signal_ratio=0.55, spatial_gradient=0.15,
    signal_emission_strength=0.3, signal_hop_decay=0.9,
    division_energy_threshold=90.0, division_cost=35.0,
    signal_division_coupling=0.1,
    cell_mutation_rate=0.005, birth_trait_variation=0.02,
    energy_leak_rate=0.05, signal_energy_coupling=1.0,
    apoptosis_threshold=1.0, apoptosis_streak=200,
    phenotype_emission_coupling=2.0, phenotype_affinity_coupling=2.0,
    resource_depletion_rate=0.005, resource_regen_rate=0.002,
    migration_enabled=True,
    migration_energy_cost=2.0, migration_resource_threshold=0.4,
    action_division_coupling=2.0,
    action_weight_scale=0.20, action_mutation_rate=0.04,
    displacement_energy_ratio=2.5,
    # Single central patch - everyone fights over it
    landscape_type='patches', landscape_base=0.1,
    landscape_n_patches=1, landscape_patch_radius=0.35,
    landscape_patch_richness=1.0,
    landscape_patch_centers=[(10, 10)],
    # No fragmentation (keep it simple)
    fragmentation_enabled=False,
    # Stigmergy
    death_imprint_strength=1.0, stigmergy_decay=0.99,
    stigmergy_sensing=0.5, stigmergy_avoidance=0.5,
    # AGGRESSIVE PREDATION
    predation_enabled=True,
    predation_energy_ratio=1.2,     # very easy to predate
    predation_efficiency=0.7,       # very rewarding
    predation_cooldown=2,           # fast repeat
    predation_action_threshold=0.0,
)

TICKS = 6000
REPORT = 200

def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    # 4 organisms in the 4 quadrants, all close to the center patch
    corners = [(5, 5), (5, 15), (15, 5), (15, 15)]
    for i, (cr, cc) in enumerate(corners):
        lid = i + 1
        placed = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r, c = cr + dr, cc + dc
                if 0 <= r < GRID and 0 <= c < GRID and t.grid[r][c] is None:
                    t.place_cell(r, c)
                    t.grid[r][c].lineage_id = lid
                    t.grid[r][c].energy = 100.0
                    placed += 1

    print("=" * 70)
    print("  COLOSSEUM: 4 Organisms, 1 Resource, Aggressive Predation")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS}")
    print(f"  Predation: ratio={CONFIG['predation_energy_ratio']}, "
          f"eff={CONFIG['predation_efficiency']}, cd={CONFIG['predation_cooldown']}")
    print("=" * 70)

    extinctions = {}

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT == 0:
            snap = t.ecosystem_snapshot()
            counts = {lid: d['cell_count'] for lid, d in snap['lineages'].items()}
            for lid in [1, 2, 3, 4]:
                if lid not in counts and lid not in extinctions:
                    extinctions[lid] = tick

            count_str = " ".join(f"L{lid}={counts.get(lid, 0)}" for lid in range(1, 5))
            extra = [f"L{lid}={d['cell_count']}" for lid, d in snap['lineages'].items() if lid > 4]
            extra_str = " " + " ".join(extra) if extra else ""
            print(f"  t={tick:5d}: {count_str}{extra_str}  "
                  f"(total={snap['total_cells']}, pred={t.predation_kills}, "
                  f"d={t.total_deaths}, b={t.total_births})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  COLOSSEUM RESULTS")
    print("=" * 70)
    snap = t.ecosystem_snapshot()
    print(f"\n  Survivors: {snap['total_cells']} cells, {snap['n_lineages']} lineages")
    print(f"  Predation kills: {t.predation_kills}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Total births: {t.total_births}")

    if extinctions:
        print(f"\n  EXTINCTIONS:")
        for lid, tick in sorted(extinctions.items()):
            print(f"    Organism {lid}: extinct at t={tick}")
        surviving = [lid for lid in range(1, 5) if lid not in extinctions]
        if surviving:
            print(f"  WINNER(S): {', '.join(f'L{lid}' for lid in surviving)}")
    else:
        print(f"\n  No extinctions — all 4 organisms survived!")

    for lid, d in sorted(snap['lineages'].items()):
        print(f"  L{lid}: {d['cell_count']} cells, E={d['mean_energy']:.1f}")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
