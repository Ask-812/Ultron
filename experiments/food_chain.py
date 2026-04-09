"""
Food Chain Experiment: Can three-level trophic dynamics emerge?

3 organisms on a gradient landscape:
- Organism A: bottom-left, poor resources (will be prey)
- Organism B: center, moderate resources (will be mesopredator?)
- Organism C: top-right, rich resources (will be apex predator?)

Predation enabled with moderate threshold. The question:
Do we get genuine A->B->C trophic cascades?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 35
CONFIG = dict(
    rows=GRID, cols=GRID,
    observation_dim=12, signal_dim=4, action_dim=4, env_dim=8,
    start_energy=100.0, energy_capacity=250.0, consumption_rate=0.08,
    extraction_factor=0.55, metabolic_cost=0.25,
    signal_noise=0.01, base_signal_ratio=0.55, spatial_gradient=0.15,
    signal_emission_strength=0.3, signal_hop_decay=0.9,
    division_energy_threshold=85.0, division_cost=35.0,
    signal_division_coupling=0.1,
    cell_mutation_rate=0.005, birth_trait_variation=0.02,
    energy_leak_rate=0.05, signal_energy_coupling=1.0,
    apoptosis_threshold=1.0, apoptosis_streak=300,
    phenotype_emission_coupling=2.0, phenotype_affinity_coupling=2.0,
    resource_depletion_rate=0.003, resource_regen_rate=0.001,
    migration_enabled=True,
    migration_energy_cost=2.0, migration_resource_threshold=0.4,
    action_division_coupling=2.0,
    action_weight_scale=0.15, action_mutation_rate=0.03,
    displacement_energy_ratio=3.0,
    # Gradient landscape: left=poor, right=rich
    landscape_type='gradient', landscape_base=0.15,
    # Fragmentation
    fragmentation_enabled=True, fragmentation_interval=200,
    fragmentation_min_size=5,
    # Stigmergy
    death_imprint_strength=1.0, stigmergy_decay=0.995,
    stigmergy_sensing=0.3, stigmergy_avoidance=0.3,
    # PREDATION
    predation_enabled=True,
    predation_energy_ratio=1.3,     # lower threshold = more predation
    predation_efficiency=0.6,       # high efficiency = predation is rewarding
    predation_cooldown=3,           # Short cooldown
    predation_action_threshold=0.0,
)

TICKS = 10000
REPORT = 500

def place(tissue, cr, cc, lid, n=8, energy=100.0):
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

    # A: bottom-left (poor resources), B: center, C: top-right (rich)
    na = place(t, 28, 7, lid=1, n=8, energy=80.0)
    nb = place(t, 17, 17, lid=2, n=8, energy=100.0)
    nc = place(t, 7, 28, lid=3, n=8, energy=120.0)

    print("=" * 70)
    print("  FOOD CHAIN EXPERIMENT: Three-Level Trophic Dynamics")
    print(f"  Grid: {GRID}x{GRID} gradient | Ticks: {TICKS}")
    print(f"  A={na} cells (poor zone, 80E)")
    print(f"  B={nb} cells (mid zone, 100E)")
    print(f"  C={nc} cells (rich zone, 120E)")
    print(f"  Predation: ratio={CONFIG['predation_energy_ratio']}, "
          f"eff={CONFIG['predation_efficiency']}")
    print("=" * 70)

    extinctions = {}
    history = []

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT == 0:
            snap = t.ecosystem_snapshot()
            counts = {lid: d['cell_count'] for lid, d in snap['lineages'].items()}

            # Track extinctions
            for lid in [1, 2, 3]:
                if lid not in counts and lid not in extinctions:
                    extinctions[lid] = tick

            history.append({
                'tick': tick, 'counts': dict(counts),
                'n_lineages': snap['n_lineages'],
                'total': snap['total_cells'],
                'predation': t.predation_kills,
            })

            count_str = " ".join(f"L{lid}={counts.get(lid, 0)}" for lid in sorted(counts))
            print(f"  t={tick:5d}: {count_str}  "
                  f"(total={snap['total_cells']}, lin={snap['n_lineages']}, "
                  f"pred={t.predation_kills}, d={t.total_deaths})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  FOOD CHAIN RESULTS")
    print("=" * 70)
    snap = t.ecosystem_snapshot()
    print(f"\n  Final state: {snap['total_cells']} cells, "
          f"{snap['n_lineages']} lineages")
    print(f"  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Predation kills: {t.predation_kills}")
    print(f"  Starvation deaths: {t.total_deaths - t.predation_kills}")

    if extinctions:
        print(f"\n  EXTINCTIONS:")
        for lid, tick in sorted(extinctions.items()):
            print(f"    L{lid}: extinct at t={tick}")
    else:
        print(f"\n  No extinctions — all original lineages survived!")

    for lid, d in sorted(snap['lineages'].items()):
        print(f"  L{lid}: {d['cell_count']} cells, E={d['mean_energy']:.1f}, "
              f"err={d['mean_error']:.4f}, age={d['mean_age']:.0f}")

    # Population dynamics analysis
    if len(history) >= 4:
        pops = [h['total'] for h in history]
        print(f"\n  Pop dynamics: mean={np.mean(pops):.1f}, "
              f"std={np.std(pops):.1f}, "
              f"CV={np.std(pops)/np.mean(pops):.3f}")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
