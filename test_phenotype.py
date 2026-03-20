"""Quick test of v0.4.0 phenotype mechanism."""
import numpy as np
from ultron.tissue import Tissue
import ultron

print(f"Version: {ultron.__version__}")
config = {
    'observation_dim': 12, 'env_dim': 8, 'signal_dim': 4,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.60,
    'update_cost_factor': 0.015, 'learning_rate': 0.05,
    'birth_trait_variation': 0.02,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 140.0, 'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 500,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001, 'phenotype_emission_coupling': 2.0,
}
np.random.seed(42)
t = Tissue(20, 20, config)
t.seed_full()  # Start with full organism — rich signal environment from tick 0

for i in range(1, 3001):
    t.step()
    if i in (100, 500, 1000, 2000, 3000):
        s = t.snapshot()
        print(f"t={i}: cells={s['cell_count']}, E={s['total_energy']:.0f}, "
              f"pheno_div={s['phenotype_diversity']:.4f}, pheno_mag={s['phenotype_mean_mag']:.4f}")

s = t.snapshot()
print(f"\nFinal: cells={s['cell_count']}, E={s['total_energy']:.0f}")
print(f"Phenotype diversity: {s['phenotype_diversity']:.4f}")
print(f"Phenotype mean mag:  {s['phenotype_mean_mag']:.4f}")

# Collect phenotypes by type
surface_phenos = []
interior_phenos = []
for r in range(20):
    for c in range(20):
        cell = t.grid[r][c]
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            if cell.is_surface:
                surface_phenos.append(cell.phenotype.copy())
            else:
                interior_phenos.append(cell.phenotype.copy())

if surface_phenos:
    sp = np.array(surface_phenos)
    print(f"\nSurface cells ({len(sp)}):")
    print(f"  Mean phenotype: [{sp[:,0].mean():+.3f}, {sp[:,1].mean():+.3f}, {sp[:,2].mean():+.3f}, {sp[:,3].mean():+.3f}]")
    print(f"  Std per channel: [{sp[:,0].std():.3f}, {sp[:,1].std():.3f}, {sp[:,2].std():.3f}, {sp[:,3].std():.3f}]")

if interior_phenos:
    ip = np.array(interior_phenos)
    print(f"\nInterior cells ({len(ip)}):")
    print(f"  Mean phenotype: [{ip[:,0].mean():+.3f}, {ip[:,1].mean():+.3f}, {ip[:,2].mean():+.3f}, {ip[:,3].mean():+.3f}]")
    print(f"  Std per channel: [{ip[:,0].std():.3f}, {ip[:,1].std():.3f}, {ip[:,2].std():.3f}, {ip[:,3].std():.3f}]")

# Distance between surface and interior mean phenotypes
if surface_phenos and interior_phenos:
    d = np.linalg.norm(np.mean(sp, axis=0) - np.mean(ip, axis=0))
    print(f"\nPhenotype distance (surface vs interior): {d:.4f}")

# Simple k-means to find natural clusters
all_phenos = []
all_types = []
for r in range(20):
    for c in range(20):
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            all_phenos.append(cell.phenotype.copy())
            all_types.append('S' if cell.is_surface else 'I')

if len(all_phenos) > 5:
    X = np.array(all_phenos)
    # Try k=3 clusters via simple k-means
    from itertools import combinations
    best_score = float('inf')
    for _ in range(10):
        centers = X[np.random.choice(len(X), 3, replace=False)]
        for _ in range(20):
            dists = np.array([np.linalg.norm(X - c, axis=1) for c in centers])
            labels = dists.argmin(axis=0)
            new_centers = np.array([X[labels == k].mean(axis=0) if (labels == k).any() else centers[k] for k in range(3)])
            if np.allclose(new_centers, centers):
                break
            centers = new_centers
        score = sum(np.linalg.norm(X[labels == k] - centers[k], axis=1).sum() for k in range(3))
        if score < best_score:
            best_score = score
            best_labels = labels.copy()
            best_centers = centers.copy()

    print(f"\nK-means (k=3) cluster analysis:")
    for k in range(3):
        mask = best_labels == k
        n = mask.sum()
        s_count = sum(1 for i, m in enumerate(mask) if m and all_types[i] == 'S')
        i_count = n - s_count
        c = best_centers[k]
        print(f"  Cluster {k}: n={n} (S={s_count}, I={i_count}) center=[{c[0]:+.3f},{c[1]:+.3f},{c[2]:+.3f},{c[3]:+.3f}]")
