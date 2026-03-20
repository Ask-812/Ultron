#!/usr/bin/env python3
"""
CELL DIFFERENTIATION v0.4.0 — Phenotype Emergence Experiment.

Each cell develops a 4-channel phenotype through experience:
  [0] surface_history: how often this cell has been on the surface
  [1] signal_exposure: how much inter-cell signal it receives
  [2] competence: how accurately it predicts its environment
  [3] energy_status: its metabolic state (energy / capacity)

Phenotype plasticity decays with age (critical period for commitment).
Emission modulation: phenotype amplifies signal channels, creating
channel specialization across cell types.

Expected: 3+ distinct cell types, spatial phenotype patterns,
stable identity after lock-in.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue

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
    'update_cost_factor': 0.015,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,

    # Spatial gradient
    'base_signal_ratio': 0.55,
    'spatial_gradient': 0.20,

    # Signal propagation + action coupling
    'signal_hop_decay': 0.9,
    'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0,
    'signal_division_coupling': 0.1,

    # Energy sharing
    'energy_leak_rate': 0.03,

    # Cell lifecycle
    'division_energy_threshold': 140.0,
    'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,

    # Phenotype (v0.4.0)
    'phenotype_max_plasticity': 0.05,
    'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0,
}

TICKS = 5000
GRID = 20
np.random.seed(42)

tissue = Tissue(GRID, GRID, CONFIG)
tissue.seed_full()

print(f"CELL DIFFERENTIATION v0.4.0 ({GRID}x{GRID}, {TICKS} ticks)", flush=True)

# Track metrics
history = {
    'tick': [], 'cells': [], 'energy': [],
    'pheno_div': [], 'pheno_mag': [],
    'surface_mean_pheno': [], 'interior_mean_pheno': [],
    'pheno_distance': [],
}

for t in range(1, TICKS + 1):
    tissue.step()

    if t % 250 == 0 or t == 1:
        s = tissue.snapshot()
        cells_data = []
        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell and cell.is_alive:
                    cells_data.append({
                        'r': r, 'c': c,
                        'surface': cell.is_surface,
                        'phenotype': cell.phenotype.copy(),
                        'energy': cell.energy,
                        'age': cell.age,
                    })

        surface_p = np.array([cd['phenotype'] for cd in cells_data if cd['surface']])
        interior_p = np.array([cd['phenotype'] for cd in cells_data if not cd['surface']])

        if len(surface_p) > 0 and len(interior_p) > 0:
            dist = float(np.linalg.norm(surface_p.mean(0) - interior_p.mean(0)))
        else:
            dist = 0.0

        history['tick'].append(t)
        history['cells'].append(s['cell_count'])
        history['energy'].append(s['total_energy'])
        history['pheno_div'].append(s['phenotype_diversity'])
        history['pheno_mag'].append(s['phenotype_mean_mag'])
        history['pheno_distance'].append(dist)

        if t % 1000 == 0:
            n_s = len(surface_p)
            n_i = len(interior_p)
            sp_mean = surface_p.mean(0) if n_s > 0 else np.zeros(4)
            ip_mean = interior_p.mean(0) if n_i > 0 else np.zeros(4)
            print(f"  t={t:5d}: cells={s['cell_count']:3d}  E={s['total_energy']:7.0f}  "
                  f"S/I={n_s}/{n_i}  "
                  f"pheno_dist={dist:.3f}  "
                  f"div={s['phenotype_diversity']:.4f}  "
                  f"S_mean=[{sp_mean[0]:.2f},{sp_mean[1]:.2f},{sp_mean[2]:.2f},{sp_mean[3]:.2f}]  "
                  f"I_mean=[{ip_mean[0]:.2f},{ip_mean[1]:.2f},{ip_mean[2]:.2f},{ip_mean[3]:.2f}]",
                  flush=True)

# === Final analysis ===
print("\n=== FINAL ANALYSIS ===", flush=True)
s = tissue.snapshot()
print(f"Cells: {s['cell_count']}, Total Energy: {s['total_energy']:.0f}", flush=True)
print(f"Phenotype diversity: {s['phenotype_diversity']:.4f}", flush=True)
print(f"Phenotype mean magnitude: {s['phenotype_mean_mag']:.4f}", flush=True)

# Collect all phenotypes for clustering
all_phenos = []
all_pos = []
all_surface = []
all_ages = []
all_energies = []
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell and cell.is_alive:
            all_phenos.append(cell.phenotype.copy())
            all_pos.append((r, c))
            all_surface.append(cell.is_surface)
            all_ages.append(cell.age)
            all_energies.append(cell.energy)

X = np.array(all_phenos)
n_clusters = 4

# K-means clustering
best_score = float('inf')
for trial in range(20):
    centers = X[np.random.choice(len(X), n_clusters, replace=False)]
    for _ in range(50):
        dists = np.array([np.linalg.norm(X - c, axis=1) for c in centers])
        labels = dists.argmin(axis=0)
        new_centers = np.array([
            X[labels == k].mean(axis=0) if (labels == k).any() else centers[k]
            for k in range(n_clusters)
        ])
        if np.allclose(new_centers, centers, atol=1e-6):
            break
        centers = new_centers
    score = sum(np.linalg.norm(X[labels == k] - centers[k], axis=1).sum()
                for k in range(n_clusters) if (labels == k).any())
    if score < best_score:
        best_score = score
        best_labels = labels.copy()
        best_centers = centers.copy()

# Sort clusters by surface_history (phenotype[0])
order = np.argsort(best_centers[:, 0])
relabel = {old: new for new, old in enumerate(order)}
best_labels = np.array([relabel[l] for l in best_labels])
best_centers = best_centers[order]

# Name clusters based on phenotype profile
type_names = []
for k in range(n_clusters):
    c = best_centers[k]
    if c[0] > 0.7 and c[3] > 0.6:
        name = "Absorptive"
    elif c[0] > 0.7 and c[3] < 0.5:
        name = "Sensory"
    elif c[0] < 0.3:
        name = "Interior/Relay"
    elif 0.3 <= c[0] <= 0.7:
        name = "Boundary"
    else:
        name = "Mixed"
    type_names.append(name)

print(f"\nK-means ({n_clusters} clusters):", flush=True)
for k in range(n_clusters):
    mask = best_labels == k
    n = mask.sum()
    s_count = sum(1 for i in range(len(mask)) if mask[i] and all_surface[i])
    mean_age = np.mean([all_ages[i] for i in range(len(mask)) if mask[i]])
    mean_e = np.mean([all_energies[i] for i in range(len(mask)) if mask[i]])
    c = best_centers[k]
    print(f"  Type {k} '{type_names[k]}': n={n:3d} (S={s_count}, I={n - s_count})  "
          f"age={mean_age:.0f}  E={mean_e:.0f}  "
          f"pheno=[{c[0]:.3f}, {c[1]:.3f}, {c[2]:.3f}, {c[3]:.3f}]", flush=True)

# === VISUALIZATION ===
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle(f'Cell Differentiation v0.4.0 @ t={TICKS}  ({s["cell_count"]} cells)', fontsize=14)

# Row 1: Spatial maps
# 1a: Cell type map
type_map = np.full((GRID, GRID), -1.0)
for i, (r, c) in enumerate(all_pos):
    type_map[r, c] = best_labels[i]
masked_type = np.ma.masked_where(type_map < 0, type_map)
import matplotlib.colors as mcolors
cmap_types = mcolors.ListedColormap(['#2196F3', '#4CAF50', '#FF9800', '#F44336'])
axes[0, 0].imshow(masked_type, cmap=cmap_types, vmin=0, vmax=n_clusters - 1, interpolation='nearest')
axes[0, 0].set_title('Cell Type Map')
for k in range(n_clusters):
    axes[0, 0].plot([], [], 's', color=cmap_types(k / (n_clusters - 1)), label=f'{type_names[k]}')
axes[0, 0].legend(loc='upper left', fontsize=7)

# 1b: Energy map
energy_map = tissue.get_energy_map()
im1 = axes[0, 1].imshow(energy_map, cmap='YlOrRd', interpolation='nearest')
axes[0, 1].set_title('Energy Map')
plt.colorbar(im1, ax=axes[0, 1], shrink=0.7)

# 1c: Signal magnitude
sig_map = tissue.get_signal_magnitude_map()
im2 = axes[0, 2].imshow(sig_map, cmap='viridis', interpolation='nearest')
axes[0, 2].set_title('Signal Magnitude')
plt.colorbar(im2, ax=axes[0, 2], shrink=0.7)

# 1d: Phenotype magnitude
phenotype_map = tissue.get_phenotype_map()
pheno_mag_map = np.linalg.norm(phenotype_map, axis=2)
pheno_mag_map[tissue.get_occupancy_map() == 0] = np.nan
im3 = axes[0, 3].imshow(pheno_mag_map, cmap='plasma', interpolation='nearest')
axes[0, 3].set_title('Phenotype Magnitude')
plt.colorbar(im3, ax=axes[0, 3], shrink=0.7)

# Row 2: Phenotype channels + time series
# 2a: Surface history (phenotype[0])
p0_map = np.full((GRID, GRID), np.nan)
for i, (r, c) in enumerate(all_pos):
    p0_map[r, c] = all_phenos[i][0]
im4 = axes[1, 0].imshow(p0_map, cmap='RdYlBu_r', interpolation='nearest', vmin=0, vmax=1)
axes[1, 0].set_title('Phenotype[0]: Surface History')
plt.colorbar(im4, ax=axes[1, 0], shrink=0.7)

# 2b: Signal exposure (phenotype[1])
p1_map = np.full((GRID, GRID), np.nan)
for i, (r, c) in enumerate(all_pos):
    p1_map[r, c] = all_phenos[i][1]
im5 = axes[1, 1].imshow(p1_map, cmap='inferno', interpolation='nearest')
axes[1, 1].set_title('Phenotype[1]: Signal Exposure')
plt.colorbar(im5, ax=axes[1, 1], shrink=0.7)

# 2c: Energy status (phenotype[3])
p3_map = np.full((GRID, GRID), np.nan)
for i, (r, c) in enumerate(all_pos):
    p3_map[r, c] = all_phenos[i][3]
im6 = axes[1, 2].imshow(p3_map, cmap='Greens', interpolation='nearest', vmin=0, vmax=1)
axes[1, 2].set_title('Phenotype[3]: Energy Status')
plt.colorbar(im6, ax=axes[1, 2], shrink=0.7)

# 2d: Time series
ax_ts = axes[1, 3]
ax_ts.plot(history['tick'], history['pheno_distance'], 'b-', label='S-I Distance', linewidth=2)
ax_ts.plot(history['tick'], history['pheno_div'], 'r-', label='Diversity', linewidth=1)
ax_ts.set_xlabel('Tick')
ax_ts.set_ylabel('Phenotype Metric')
ax_ts.set_title('Differentiation Over Time')
ax_ts.legend(fontsize=8)
ax_ts2 = ax_ts.twinx()
ax_ts2.plot(history['tick'], history['cells'], 'g--', alpha=0.5, label='Cells')
ax_ts2.set_ylabel('Cell Count', color='green')
ax_ts2.legend(loc='upper right', fontsize=8)

plt.tight_layout()
plt.savefig('differentiation_v040.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: differentiation_v040.png", flush=True)

# === Phenotype scatter plot ===
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
fig2.suptitle('Phenotype Space Projections', fontsize=13)

colors = [cmap_types(k / (n_clusters - 1)) for k in best_labels]

axes2[0].scatter(X[:, 0], X[:, 3], c=colors, s=15, alpha=0.7)
axes2[0].set_xlabel('Surface History')
axes2[0].set_ylabel('Energy Status')
axes2[0].set_title('Surface vs Energy')

axes2[1].scatter(X[:, 0], X[:, 1], c=colors, s=15, alpha=0.7)
axes2[1].set_xlabel('Surface History')
axes2[1].set_ylabel('Signal Exposure')
axes2[1].set_title('Surface vs Signal')

axes2[2].scatter(X[:, 1], X[:, 3], c=colors, s=15, alpha=0.7)
axes2[2].set_xlabel('Signal Exposure')
axes2[2].set_ylabel('Energy Status')
axes2[2].set_title('Signal vs Energy')

for ax in axes2:
    for k in range(n_clusters):
        ax.plot([], [], 's', color=cmap_types(k / (n_clusters - 1)), label=type_names[k])
    ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig('phenotype_scatter.png', dpi=150, bbox_inches='tight')
print(f"Saved: phenotype_scatter.png", flush=True)
