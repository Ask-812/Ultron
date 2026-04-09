"""Migration experiment: organism response to resource depletion.

Compare:
  1. No motility, no depletion (control)
  2. Depletion only (organism starves in place)
  3. Depletion + motility (organism can flee)

Key question: does motility help organisms survive resource depletion?
"""
from ultron.tissue import Tissue
import numpy as np

np.random.seed(42)

BASE = {
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
}

CONDITIONS = {
    'Control': {
        'resource_depletion_rate': 0.0, 'resource_regen_rate': 0.0,
        'migration_resource_threshold': 0.0,  # no migration
    },
    'Depletion only': {
        'resource_depletion_rate': 0.002, 'resource_regen_rate': 0.0003,
        'migration_resource_threshold': 0.0,  # no migration
    },
    'Depletion + motility': {
        'resource_depletion_rate': 0.002, 'resource_regen_rate': 0.0003,
        'migration_energy_cost': 2.0,
        'migration_resource_threshold': 0.5,
    },
}

# Use 25x25 grid for more space to migrate
GRID = 25
TICKS = 3000

def compute_centroid(tissue):
    """Center of mass of the organism."""
    total_e, cx, cy = 0.0, 0.0, 0.0
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell and cell.is_alive:
                total_e += cell.energy
                cx += r * cell.energy
                cy += c * cell.energy
    if total_e > 0:
        return cx / total_e, cy / total_e
    return tissue.rows / 2, tissue.cols / 2

for name, overrides in CONDITIONS.items():
    np.random.seed(42)
    cfg = {**BASE, **overrides}
    t = Tissue(GRID, GRID, cfg)
    # Seed a 10x10 block in the center
    cr, cc = GRID // 2, GRID // 2
    for dr in range(-5, 5):
        for dc in range(-5, 5):
            t.place_cell(cr + dr, cc + dc)
    
    print(f"\n=== {name} ===")
    for tick in range(TICKS):
        t.step()
        if (tick + 1) % 500 == 0:
            s = t.snapshot()
            centroid = compute_centroid(t)
            # Compute spatial extent (max distance from centroid)
            max_dist = 0.0
            for r in range(t.rows):
                for c in range(t.cols):
                    cell = t.grid[r][c]
                    if cell and cell.is_alive:
                        d = np.sqrt((r - centroid[0])**2 + (c - centroid[1])**2)
                        if d > max_dist:
                            max_dist = d
            print(f"  t={tick+1}: cells={s['cell_count']:3d}  E={s['total_energy']:7.0f}  "
                  f"res={s.get('resource_mean',1):.3f}  "
                  f"extent={max_dist:.1f}  center=({centroid[0]:.1f},{centroid[1]:.1f})")
