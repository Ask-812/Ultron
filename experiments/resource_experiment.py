"""Resource depletion experiment: does scarcity drive differentiation and adaptation?

Compare organisms under:
  1. No depletion (control)
  2. Mild depletion (rate=0.001, regen=0.0005)
  3. Harsh depletion (rate=0.003, regen=0.0003)

Key questions:
  - Does the organism survive long-term under depletion?
  - Does scarcity produce different cell types than abundance?
  - Does phenotype diversity increase under pressure?
"""
from ultron.tissue import Tissue
import numpy as np

np.random.seed(42)

BASE_CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.60,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 140.0, 'division_cost': 30.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 500,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.0,
    'resource_regen_rate': 0.0,
}

CONDITIONS = {
    'No depletion': {'resource_depletion_rate': 0.0, 'resource_regen_rate': 0.0},
    'Mild depletion': {'resource_depletion_rate': 0.001, 'resource_regen_rate': 0.0005},
    'Harsh depletion': {'resource_depletion_rate': 0.003, 'resource_regen_rate': 0.0003},
}

TICKS = 5000
GRID = 20

results = {}
for name, overrides in CONDITIONS.items():
    np.random.seed(42)
    cfg = {**BASE_CONFIG, **overrides}
    t = Tissue(GRID, GRID, cfg)
    t.seed_full()
    
    history = {'cells': [], 'energy': [], 'diversity': [],
               'res_mean': [], 'res_min': [], 'pheno_mag': []}
    
    for tick in range(TICKS):
        t.step()
        if (tick + 1) % 100 == 0:
            s = t.snapshot()
            history['cells'].append(s['cell_count'])
            history['energy'].append(s['total_energy'])
            history['diversity'].append(s.get('phenotype_diversity', 0))
            history['res_mean'].append(s.get('resource_mean', 1.0))
            history['res_min'].append(s.get('resource_min', 1.0))
            history['pheno_mag'].append(s.get('phenotype_mean_mag', 0))
    
    final = t.snapshot()
    results[name] = {
        'history': history,
        'final': final,
    }
    
    print(f"\n=== {name} ===")
    print(f"  Final cells: {final['cell_count']}")
    print(f"  Total energy: {final['total_energy']:.0f}")
    print(f"  Mean energy/cell: {final['mean_energy']:.1f}")
    print(f"  Surface/Interior: {final.get('surface_count', '?')}/{final.get('interior_count', '?')}")
    print(f"  Phenotype diversity: {final.get('phenotype_diversity', 0):.4f}")
    print(f"  Phenotype mean mag: {final.get('phenotype_mean_mag', 0):.3f}")
    print(f"  Resource mean: {final.get('resource_mean', 1.0):.3f}")
    print(f"  Resource min: {final.get('resource_min', 1.0):.3f}")
    
    # Analyze cell types via k-means
    pheno_map = t.get_phenotype_map()
    phenotypes = []
    energies = []
    for r in range(t.rows):
        for c in range(t.cols):
            cell = t.grid[r][c]
            if cell and cell.is_alive:
                phenotypes.append(pheno_map[r, c])
                energies.append(cell.energy)
    
    if len(phenotypes) > 4:
        phenotypes = np.array(phenotypes)
        energies = np.array(energies)
        
        # Simple k-means (k=4)
        from scipy.cluster.vq import kmeans2
        centroids, labels = kmeans2(phenotypes, 4, minit='points')
        
        print("  Cell types:")
        for k in range(4):
            mask = labels == k
            if mask.sum() > 0:
                print(f"    Type {k}: n={mask.sum()}, "
                      f"pheno={centroids[k].round(2)}, "
                      f"E={energies[mask].mean():.0f}")


# === Visualization ===
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    ticks_axis = list(range(100, TICKS + 1, 100))
    colors = {'No depletion': 'green', 'Mild depletion': 'orange', 'Harsh depletion': 'red'}
    
    for name, data in results.items():
        h = data['history']
        c = colors[name]
        axes[0, 0].plot(ticks_axis, h['cells'], color=c, label=name)
        axes[0, 1].plot(ticks_axis, h['energy'], color=c, label=name)
        axes[0, 2].plot(ticks_axis, h['diversity'], color=c, label=name)
        axes[1, 0].plot(ticks_axis, h['res_mean'], color=c, label=name)
        axes[1, 1].plot(ticks_axis, h['res_min'], color=c, label=name)
        axes[1, 2].plot(ticks_axis, h['pheno_mag'], color=c, label=name)
    
    axes[0, 0].set_title('Cell Count'); axes[0, 0].set_ylabel('Cells')
    axes[0, 1].set_title('Total Energy'); axes[0, 1].set_ylabel('Energy')
    axes[0, 2].set_title('Phenotype Diversity'); axes[0, 2].set_ylabel('Diversity')
    axes[1, 0].set_title('Resource Mean'); axes[1, 0].set_ylabel('Level')
    axes[1, 1].set_title('Resource Min'); axes[1, 1].set_ylabel('Level')
    axes[1, 2].set_title('Phenotype Mean Magnitude'); axes[1, 2].set_ylabel('Magnitude')
    
    for ax in axes.flat:
        ax.set_xlabel('Tick')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    
    fig.suptitle('Resource Depletion Experiment', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('resource_depletion.png', dpi=150)
    print("\nSaved resource_depletion.png")
except ImportError:
    print("\nMatplotlib not available, skipping plot")
