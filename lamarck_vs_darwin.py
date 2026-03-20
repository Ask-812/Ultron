"""
Lamarckian Evolution: Does inherited knowledge accelerate adaptation?

Compare two organisms on the SAME landscape:
- Organism A: weight_inheritance_ratio = 0.0 (fresh brains, Darwinian)
- Organism B: weight_inheritance_ratio = 0.7 (inherited brains, Lamarckian)

Measure prediction error over time. If Lamarckian inheritance works,
L2 should have lower prediction error because children start with
parent's learned predictive structure instead of random weights.

We run this as two separate tissues to avoid cross-contamination,
then compare their prediction error trajectories.
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 25
BASE_CONFIG = {
    'observation_dim': 12, 'signal_dim': 4, 'action_dim': 4, 'env_dim': 8,
    'starting_energy': 150.0, 'energy_capacity': 200.0, 'consumption_rate': 0.08,
    'extraction_factor': 0.65, 'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 90.0, 'division_cost': 12.0,
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
    'landscape_type': 'patches', 'landscape_base': 0.25,
    'landscape_n_patches': 4, 'landscape_patch_radius': 0.22,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(7,7), (7,18), (18,7), (18,18)],
    'fragmentation_enabled': False,
    'death_imprint_strength': 0.0, 'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.0, 'stigmergy_avoidance': 0.0,
    'predation_enabled': False, 'toxin_enabled': False,
}

TICKS = 8000
REPORT = 500

def run_tissue(config, seed, label):
    np.random.seed(seed)
    t = Tissue(GRID, GRID, config)
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = GRID // 2 + dr, GRID // 2 + dc
            if 0 <= r < GRID and 0 <= c < GRID and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 1

    history = []
    for tick in range(1, TICKS + 1):
        t.step()
        if tick % REPORT == 0:
            snap = t.snapshot()
            history.append({
                'tick': tick,
                'cells': snap['cell_count'],
                'mean_error': snap['mean_error'],
                'mean_energy': snap.get('mean_energy', 0),
                'births': snap['births'],
            })
            print(f"  [{label}] t={tick:5d}: cells={snap['cell_count']}, "
                  f"error={snap['mean_error']:.4f}, energy={snap.get('mean_energy', 0):.1f}, "
                  f"births={snap['births']}")
    return history

def run():
    start = time.time()

    print("=" * 70)
    print("  LAMARCKIAN vs DARWINIAN: Does Inherited Knowledge Help?")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS} | Same seed, same landscape")
    print("=" * 70)

    # Darwinian: fresh weights each generation
    print("\n--- DARWINIAN (weight_inheritance_ratio=0.0) ---")
    darwinian_cfg = dict(BASE_CONFIG)
    darwinian_cfg['weight_inheritance_ratio'] = 0.0
    h_darwin = run_tissue(darwinian_cfg, seed=42, label="DARWIN")

    # Lamarckian: inherited weights
    print("\n--- LAMARCKIAN (weight_inheritance_ratio=0.7) ---")
    lamarck_cfg = dict(BASE_CONFIG)
    lamarck_cfg['weight_inheritance_ratio'] = 0.7
    lamarck_cfg['weight_inheritance_noise'] = 0.005
    h_lamarck = run_tissue(lamarck_cfg, seed=42, label="LAMARCK")

    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print("  COMPARISON")
    print("=" * 70)

    print(f"\n  {'Tick':>6}  {'Darwin Error':>13}  {'Lamarck Error':>14}  {'Advantage':>10}")
    print(f"  {'-'*6}  {'-'*13}  {'-'*14}  {'-'*10}")
    for d, l in zip(h_darwin, h_lamarck):
        adv = (d['mean_error'] - l['mean_error']) / d['mean_error'] * 100 if d['mean_error'] > 0 else 0
        print(f"  {d['tick']:6d}  {d['mean_error']:13.4f}  {l['mean_error']:14.4f}  {adv:+9.1f}%")

    if h_darwin and h_lamarck:
        d_early = np.mean([h['mean_error'] for h in h_darwin[:3]])
        l_early = np.mean([h['mean_error'] for h in h_lamarck[:3]])
        d_late = np.mean([h['mean_error'] for h in h_darwin[-3:]])
        l_late = np.mean([h['mean_error'] for h in h_lamarck[-3:]])

        print(f"\n  Early error: Darwin={d_early:.4f}, Lamarck={l_early:.4f}")
        print(f"  Late error:  Darwin={d_late:.4f}, Lamarck={l_late:.4f}")

        d_improve = (d_early - d_late) / d_early * 100
        l_improve = (l_early - l_late) / l_early * 100
        print(f"  Darwin improvement: {d_improve:+.1f}%")
        print(f"  Lamarck improvement: {l_improve:+.1f}%")

        late_advantage = (d_late - l_late) / d_late * 100
        if late_advantage > 5:
            print(f"\n  -> LAMARCKIAN ADVANTAGE: {late_advantage:.1f}% lower prediction error!")
            print(f"     Inherited knowledge genuinely helps adaptation.")
        elif late_advantage < -5:
            print(f"\n  -> DARWINIAN ADVANTAGE: {-late_advantage:.1f}% lower prediction error!")
            print(f"     Fresh weights may maintain beneficial diversity.")
        else:
            print(f"\n  -> No significant difference ({late_advantage:.1f}%)")

        # Compare population sizes
        d_pop = h_darwin[-1]['cells']
        l_pop = h_lamarck[-1]['cells']
        print(f"\n  Final population: Darwin={d_pop}, Lamarck={l_pop}")
        if l_pop > d_pop * 1.1:
            print(f"  -> Lamarckian organisms are MORE fit ({l_pop/d_pop:.1f}x population)!")
        elif d_pop > l_pop * 1.1:
            print(f"  -> Darwinian organisms are MORE fit ({d_pop/l_pop:.1f}x population)!")
        else:
            print(f"  -> Similar fitness (comparable populations)")

    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
