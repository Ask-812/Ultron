"""Natural selection test: does a genetically superior organism outcompete a weaker one?

Organism A: default traits (extraction_efficiency=1.0, metabolic_rate=1.0)
Organism B: 20% better extraction efficiency (1.2x)

If natural selection works, B should gradually displace A.
"""
from ultron.tissue import Tissue
from ultron.cell import Cell, create_cell
from ultron.core import create_ultron, BirthTraits
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
    'displacement_energy_ratio': 2.0,  # divider needs 2x enemy energy to displace
}

GRID = 20
TICKS = 5000

np.random.seed(42)
t = Tissue(GRID, GRID, CONFIG)

# Organism A: left half, default traits
for r in range(GRID):
    for c in range(GRID // 2):
        state = create_ultron(CONFIG)
        cell = Cell(state, cell_id=t.next_cell_id, signal_dim=4)
        cell.lineage_id = 1
        t.next_cell_id += 1
        t.grid[r][c] = cell

# Organism B: right half, 20% better extraction
for r in range(GRID):
    for c in range(GRID // 2, GRID):
        state = create_ultron(CONFIG)
        # Override with superior extraction traits
        state.traits = BirthTraits(
            extraction_efficiency=1.5,
            metabolic_rate=1.0,
            learning_capacity=1.0,
        )
        cell = Cell(state, cell_id=t.next_cell_id, signal_dim=4)
        cell.lineage_id = 2
        t.next_cell_id += 1
        t.grid[r][c] = cell

print(f"NATURAL SELECTION TEST ({GRID}x{GRID}, {TICKS} ticks)")
print(f"  Organism A: default traits (extraction=1.0)")
print(f"  Organism B: superior (extraction=1.5)")

for tick in range(TICKS):
    t.step()
    if (tick + 1) % 250 == 0:
        c1, c2 = 0, 0
        e1, e2 = 0.0, 0.0
        for r in range(GRID):
            for c in range(GRID):
                cell = t.grid[r][c]
                if cell and cell.is_alive:
                    if cell.lineage_id == 1:
                        c1 += 1; e1 += cell.energy
                    elif cell.lineage_id == 2:
                        c2 += 1; e2 += cell.energy
        # Column ownership
        cols = []
        for c in range(GRID):
            n1 = sum(1 for r in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 1)
            n2 = sum(1 for r in range(GRID) if t.grid[r][c] and t.grid[r][c].is_alive and t.grid[r][c].lineage_id == 2)
            cols.append('A' if n1 > n2 else ('B' if n2 > n1 else ('?' if n1 > 0 else '.')))
        line = ''.join(cols)
        avg_e_a = e1/c1 if c1 > 0 else 0
        avg_e_b = e2/c2 if c2 > 0 else 0
        print(f"  t={tick+1:4d}: A={c1:3d}({avg_e_a:5.1f}E/c)  B={c2:3d}({avg_e_b:5.1f}E/c)  [{line}]")

# Final
c1, c2 = 0, 0
for r in range(GRID):
    for c in range(GRID):
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            if cell.lineage_id == 1: c1 += 1
            elif cell.lineage_id == 2: c2 += 1
print(f"\nFINAL: A={c1}, B={c2}")
if c2 > c1 * 1.3:
    print(">> NATURAL SELECTION CONFIRMED: Superior organism B displaced weaker A")
elif c1 > c2 * 1.3:
    print(">> UNEXPECTED: Default organism A outcompeted superior B")
else:
    print(">> Coexistence: neither organism displaced the other")
