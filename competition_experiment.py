"""Multi-organism competition: two organisms on one grid.

Two organisms seeded at opposite corners of a 30x30 grid.
They grow, consume resources, and eventually encounter each other.

Key questions:
  1. Do they merge or maintain boundaries?
  2. Does one outcompete the other?
  3. Does resource depletion + motility change competitive dynamics?
"""
from ultron.tissue import Tissue
from ultron.cell import create_cell
import numpy as np

np.random.seed(42)

CONFIG = {
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
    'resource_depletion_rate': 0.001,
    'resource_regen_rate': 0.0003,
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.5,
}

GRID = 30
TICKS = 4000

t = Tissue(GRID, GRID, CONFIG)

# Seed organism A: 5x5 block in top-left corner
for r in range(2, 7):
    for c in range(2, 7):
        cell = create_cell(CONFIG, cell_id=t.next_cell_id)
        cell.lineage_id = 1
        t.next_cell_id += 1
        t.grid[r][c] = cell

# Seed organism B: 5x5 block in bottom-right corner
for r in range(23, 28):
    for c in range(23, 28):
        cell = create_cell(CONFIG, cell_id=t.next_cell_id)
        cell.lineage_id = 2
        t.next_cell_id += 1
        t.grid[r][c] = cell

def count_by_lineage(tissue):
    counts = {1: 0, 2: 0, 0: 0}
    energies = {1: 0.0, 2: 0.0, 0: 0.0}
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell and cell.is_alive:
                lid = cell.lineage_id
                counts[lid] = counts.get(lid, 0) + 1
                energies[lid] = energies.get(lid, 0) + cell.energy
    return counts, energies

def find_boundary_cells(tissue):
    """Count cells that have a neighbor from a different lineage."""
    boundary = 0
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell and cell.is_alive:
                for nr, nc in tissue._get_neighbors(r, c):
                    nbr = tissue.grid[nr][nc]
                    if nbr and nbr.is_alive and nbr.lineage_id != cell.lineage_id:
                        boundary += 1
                        break
    return boundary

print(f"MULTI-ORGANISM COMPETITION ({GRID}x{GRID}, {TICKS} ticks)")
print(f"  Organism A (lineage=1): top-left 5x5")
print(f"  Organism B (lineage=2): bottom-right 5x5")

counts, energies = count_by_lineage(t)
print(f"  Initial: A={counts[1]} cells, B={counts[2]} cells")

for tick in range(TICKS):
    t.step()
    if (tick + 1) % 200 == 0:
        counts, energies = count_by_lineage(t)
        boundary = find_boundary_cells(t)
        s = t.snapshot()
        print(f"  t={tick+1:4d}: A={counts[1]:3d}({energies[1]:6.0f}E)  "
              f"B={counts[2]:3d}({energies[2]:6.0f}E)  "
              f"boundary={boundary:2d}  "
              f"res={s.get('resource_mean',1):.3f}  total={s['cell_count']}")

# Final analysis
print("\n=== FINAL ANALYSIS ===")
counts, energies = count_by_lineage(t)
boundary = find_boundary_cells(t)
print(f"Organism A: {counts[1]} cells, {energies[1]:.0f} energy")
print(f"Organism B: {counts[2]} cells, {energies[2]:.0f} energy")
print(f"Boundary cells: {boundary}")

if counts[1] > 0 and counts[2] > 0:
    # Phenotype comparison between organisms
    pheno_a, pheno_b = [], []
    for r in range(t.rows):
        for c in range(t.cols):
            cell = t.grid[r][c]
            if cell and cell.is_alive:
                if cell.lineage_id == 1:
                    pheno_a.append(cell.phenotype.copy())
                elif cell.lineage_id == 2:
                    pheno_b.append(cell.phenotype.copy())
    if pheno_a and pheno_b:
        mean_a = np.mean(pheno_a, axis=0)
        mean_b = np.mean(pheno_b, axis=0)
        inter_dist = np.linalg.norm(mean_a - mean_b)
        print(f"\nPhenotype A mean: [{', '.join(f'{x:.3f}' for x in mean_a)}]")
        print(f"Phenotype B mean: [{', '.join(f'{x:.3f}' for x in mean_b)}]")
        print(f"Inter-organism phenotype distance: {inter_dist:.4f}")
        
        if inter_dist < 0.1:
            print(">> Organisms are phenotypically IDENTICAL — they merged")
        elif inter_dist < 0.3:
            print(">> Organisms are phenotypically similar — weak boundary")
        else:
            print(">> Organisms are phenotypically DISTINCT — strong boundary")
elif counts[1] == 0 and counts[2] > 0:
    print(">> Organism B won — A went extinct!")
elif counts[2] == 0 and counts[1] > 0:
    print(">> Organism A won — B went extinct!")
else:
    print(">> Both organisms went extinct!")
