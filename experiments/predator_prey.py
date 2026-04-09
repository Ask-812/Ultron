"""
Predator-Prey Ecosystem: Can trophic dynamics emerge from energy dominance?

Setup: Two organisms on a patchy landscape.
- Organism A: starts on a rich patch (high energy)
- Organism B: starts on a poor patch (low energy)

Predation is enabled: cells can consume adjacent foreign cells when
they have significantly more energy. This creates a potential predator-prey
dynamic where the rich-patch organism becomes the predator.

The question: Does the system produce Lotka-Volterra-like oscillations,
stable coexistence, or extinction?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 30
CONFIG = dict(
    rows=GRID, cols=GRID,
    observation_dim=12, signal_dim=4, action_dim=4, env_dim=8,
    start_energy=100.0, energy_capacity=200.0, consumption_rate=0.08,
    extraction_factor=0.65, metabolic_cost=0.3,
    signal_noise=0.01, base_signal_ratio=0.55, spatial_gradient=0.15,
    signal_emission_strength=0.3, signal_hop_decay=0.9,
    division_energy_threshold=95.0, division_cost=40.0,
    signal_division_coupling=0.1,
    cell_mutation_rate=0.005, birth_trait_variation=0.02,
    energy_leak_rate=0.05, signal_energy_coupling=1.0,
    apoptosis_threshold=1.0, apoptosis_streak=500,
    phenotype_emission_coupling=2.0, phenotype_affinity_coupling=2.0,
    resource_depletion_rate=0.002, resource_regen_rate=0.001,
    migration_enabled=True,
    migration_energy_cost=2.0, migration_resource_threshold=0.4,
    action_division_coupling=2.0,
    action_weight_scale=0.15, action_mutation_rate=0.03,
    displacement_energy_ratio=3.0,
    # Landscape: 2 patches, one rich and one poor
    landscape_type='patches', landscape_base=0.2,
    landscape_n_patches=2, landscape_patch_radius=0.25,
    landscape_patch_richness=1.0,
    landscape_patch_centers=[(10, 15), (20, 15)],
    # Fragmentation
    fragmentation_enabled=True, fragmentation_interval=100,
    fragmentation_min_size=5,
    # Stigmergy
    death_imprint_strength=1.0, stigmergy_decay=0.995,
    stigmergy_sensing=0.3, stigmergy_avoidance=0.2,
    # PREDATION: the new v0.8.0 mechanic
    predation_enabled=True,
    predation_energy_ratio=1.5,     # need 1.5x prey energy to consume
    predation_efficiency=0.5,       # gain 50% of prey's energy
    predation_cooldown=5,           # 5 ticks between kills
    predation_action_threshold=0.0, # all cells can attempt predation
)

def place_organism(tissue, center_r, center_c, lineage_id, n=10, energy=100.0):
    """Place a cluster of cells around a center position."""
    placed = 0
    for dr in range(-3, 4):
        for dc in range(-3, 4):
            if placed >= n:
                return placed
            r, c = center_r + dr, center_c + dc
            if (0 <= r < tissue.rows and 0 <= c < tissue.cols
                    and tissue.grid[r][c] is None
                    and abs(dr) + abs(dc) <= 3):
                tissue.place_cell(r, c)
                tissue.grid[r][c].lineage_id = lineage_id
                tissue.grid[r][c].energy = energy
                placed += 1
    return placed

TICKS = 8000
REPORT_INTERVAL = 500

def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    # Organism A: on the rich top patch (starts with high energy)
    n_a = place_organism(t, 10, 15, lineage_id=1, n=10, energy=120.0)
    # Organism B: on the rich bottom patch
    n_b = place_organism(t, 20, 15, lineage_id=2, n=10, energy=100.0)

    print("=" * 70)
    print("  PREDATOR-PREY ECOSYSTEM EXPERIMENT")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS}")
    print(f"  A: {n_a} cells (rich patch, 120 energy)")
    print(f"  B: {n_b} cells (bottom patch, 100 energy)")
    print(f"  Predation: ratio={CONFIG['predation_energy_ratio']}, "
          f"eff={CONFIG['predation_efficiency']}, cd={CONFIG['predation_cooldown']}")
    print("=" * 70)

    history = []

    for tick in range(1, TICKS + 1):
        t.step()

        if tick % REPORT_INTERVAL == 0:
            snap = t.ecosystem_snapshot()
            predation_total = t.predation_kills

            # Count cells by lineage
            lineage_counts = {}
            lineage_energies = {}
            for lid, data in snap['lineages'].items():
                lineage_counts[lid] = data['cell_count']
                lineage_energies[lid] = data['mean_energy']

            history.append({
                'tick': tick,
                'counts': dict(lineage_counts),
                'energies': dict(lineage_energies),
                'n_lineages': snap['n_lineages'],
                'total_cells': snap['total_cells'],
                'predation_kills': predation_total,
                'total_deaths': t.total_deaths,
                'total_births': t.total_births,
            })

            # Print summary
            count_str = " ".join(f"L{lid}={cnt}" for lid, cnt in sorted(lineage_counts.items()))
            print(f"  t={tick:5d}: {count_str}  "
                  f"(total={snap['total_cells']}, "
                  f"lineages={snap['n_lineages']}, "
                  f"predation={predation_total}, "
                  f"births={t.total_births}, deaths={t.total_deaths})")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  FINAL RESULTS")
    print("=" * 70)

    snap = t.ecosystem_snapshot()
    print(f"\n  Total cells: {snap['total_cells']}")
    print(f"  Lineages: {snap['n_lineages']}")
    print(f"  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    print(f"  Predation kills: {t.predation_kills}")
    print(f"  Starvation deaths: {t.total_deaths - t.predation_kills}")

    print(f"\n  Per-lineage breakdown:")
    for lid, data in sorted(snap['lineages'].items()):
        print(f"    L{lid}: {data['cell_count']} cells, "
              f"energy={data['mean_energy']:.1f}, "
              f"error={data['mean_error']:.4f}, "
              f"age={data['mean_age']:.0f}, "
              f"centroid=({data['centroid'][0]:.1f},{data['centroid'][1]:.1f})")

    # Check for oscillations in history
    if len(history) >= 4:
        total_pop = [h['total_cells'] for h in history]
        mean_pop = np.mean(total_pop)
        std_pop = np.std(total_pop)
        cv = std_pop / mean_pop if mean_pop > 0 else 0
        print(f"\n  Population dynamics:")
        print(f"    Mean: {mean_pop:.1f}, Std: {std_pop:.1f}, CV: {cv:.3f}")
        if cv > 0.15:
            print(f"    -> HIGH VARIANCE: possible oscillatory dynamics!")
        elif cv > 0.05:
            print(f"    -> Moderate variance: fluctuating equilibrium")
        else:
            print(f"    -> Low variance: stable equilibrium")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
