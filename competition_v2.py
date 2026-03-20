"""Multi-organism competition v2: organisms share a border from the start.

Left half = lineage 1, right half = lineage 2.
With resource depletion + motility, which side wins?
"""
from ultron.tissue import Tissue
from ultron.cell import create_cell
import numpy as np

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

GRID = 20
TICKS = 3000

# Run 3 seeds to check for consistency
for seed in [42, 123, 777]:
    np.random.seed(seed)
    t = Tissue(GRID, GRID, CONFIG)
    
    # Left half = lineage 1
    for r in range(GRID):
        for c in range(GRID // 2):
            cell = create_cell(CONFIG, cell_id=t.next_cell_id)
            cell.lineage_id = 1
            t.next_cell_id += 1
            t.grid[r][c] = cell
    
    # Right half = lineage 2
    for r in range(GRID):
        for c in range(GRID // 2, GRID):
            cell = create_cell(CONFIG, cell_id=t.next_cell_id)
            cell.lineage_id = 2
            t.next_cell_id += 1
            t.grid[r][c] = cell
    
    print(f"\n=== Seed {seed} ===")
    for tick in range(TICKS):
        t.step()
        if (tick + 1) % 500 == 0:
            c1 = sum(1 for r in range(GRID) for c in range(GRID)
                     if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 1)
            c2 = sum(1 for r in range(GRID) for c in range(GRID)
                     if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 2)
            # Count boundary cells (neighbors from different lineage)
            boundary = 0
            for r in range(GRID):
                for c in range(GRID):
                    cell = t.grid[r][c]
                    if cell and cell.is_alive:
                        for nr, nc in t._get_neighbors(r, c):
                            nbr = t.grid[nr][nc]
                            if nbr and nbr.is_alive and nbr.lineage_id != cell.lineage_id:
                                boundary += 1
                                break
            # Count which lineage occupies which column
            col_owners = []
            for c in range(GRID):
                n1 = sum(1 for r in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 1)
                n2 = sum(1 for r in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 2)
                if n1 > n2:
                    col_owners.append('A')
                elif n2 > n1:
                    col_owners.append('B')
                elif n1 == 0 and n2 == 0:
                    col_owners.append('.')
                else:
                    col_owners.append('?')
            border_line = ''.join(col_owners)
            print(f"  t={tick+1}: A={c1:3d} B={c2:3d}  boundary={boundary:3d}  [{border_line}]")
    
    # Final stats
    c1 = sum(1 for r in range(GRID) for c in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 1)
    c2 = sum(1 for r in range(GRID) for c in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 2)
    print(f"  FINAL: A={c1}, B={c2}")
    if c1 > c2 * 1.2:
        print(f"  >> Organism A dominates ({c1/c2:.2f}x)")
    elif c2 > c1 * 1.2:
        print(f"  >> Organism B dominates ({c2/c1:.2f}x)")
    else:
        print(f"  >> Roughly equal coexistence")
