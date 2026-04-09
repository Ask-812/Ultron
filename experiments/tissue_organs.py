#!/usr/bin/env python3
"""
ORGAN EMERGENCE EXPERIMENT: Surface-only metabolism.

Only cells touching empty space can extract energy.
Interior cells must survive on energy diffused from boundary cells.

Question: does functional differentiation emerge?
Do we see hollow structures, transport corridors, specialized zones?

Grid: 20x20, uniform environment (no spatial gradient)
so any structure is self-organized, not environmentally imposed.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue

CONFIG = {
    'observation_dim': 10,
    'model_dim': 20,
    'initial_energy': 100.0,
    'starting_energy': 180.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.60,
    'update_cost_factor': 0.015,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,

    # Uniform environment — structure must be self-organized
    'base_signal_ratio': 0.80,
    'spatial_gradient': 0.0,

    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.03,  # slightly higher to feed interior

    'division_energy_threshold': 140.0,
    'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

TICKS = 15000
GRID = 20

np.random.seed(42)
tissue = Tissue(GRID, GRID, CONFIG)
tissue.seed_center(n=1)

print(f'ORGAN EMERGENCE: Surface-only metabolism ({GRID}x{GRID})', flush=True)
print(f'Only boundary cells extract energy. Interior must rely on diffusion.', flush=True)
print(f'Ticks: {TICKS}', flush=True)
print(flush=True)

# Track history
history = []

for t in range(TICKS):
    tissue.step()
    if (t + 1) % 1000 == 0:
        s = tissue.snapshot()

        # Count surface vs interior cells
        n_surface = 0
        n_interior = 0
        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell is not None and cell.is_alive:
                    if cell.is_surface:
                        n_surface += 1
                    else:
                        n_interior += 1

        history.append({
            'tick': t + 1,
            'cells': s['cell_count'],
            'energy': s.get('mean_energy', 0),
            'error': s.get('mean_error', 0),
            'births': s['births'],
            'deaths': s['deaths'],
            'surface': n_surface,
            'interior': n_interior,
        })

        print(f't={t+1:5d}: cells={s["cell_count"]:3d} '
              f'(S={n_surface:3d} I={n_interior:3d}), '
              f'E_avg={s.get("mean_energy", 0):5.1f}, '
              f'err={s.get("mean_error", 0):.3f}, '
              f'b={s["births"]}, d={s["deaths"]}', flush=True)
    if tissue.cell_count == 0:
        print('EXTINCT', flush=True)
        break

# === Collect spatial maps ===
energy_map = tissue.get_energy_map()
error_map = tissue.get_error_map()
occupancy = tissue.get_occupancy_map()

# Surface map (1=surface, 0.5=interior, 0=empty)
surface_map = np.zeros((GRID, GRID))
age_map = np.zeros((GRID, GRID))
trait_ext_map = np.zeros((GRID, GRID))
trait_met_map = np.zeros((GRID, GRID))

for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            surface_map[r, c] = 1.0 if cell.is_surface else 0.5
            age_map[r, c] = cell.age
            trait_ext_map[r, c] = cell.state.traits.extraction_efficiency
            trait_met_map[r, c] = cell.state.traits.metabolic_rate

# === Print summary ===
print(flush=True)
print('Occupancy:', flush=True)
for r in range(GRID):
    row_str = ''
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is None or not cell.is_alive:
            row_str += '. '
        elif cell.is_surface:
            row_str += 'S '
        else:
            row_str += 'I '
    print(row_str, flush=True)

print(flush=True)
print('Energy:', flush=True)
for r in range(GRID):
    print(' '.join(f'{energy_map[r,c]:3.0f}' if energy_map[r,c] > 0 else '  .' for c in range(GRID)), flush=True)

# === Plot ===
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Organ Emergence: Surface-Only Metabolism', fontsize=14)

# 1. Surface/Interior map
im0 = axes[0, 0].imshow(surface_map, cmap='RdYlGn', vmin=0, vmax=1, aspect='equal')
axes[0, 0].set_title('Cell Type (green=surface, yellow=interior, red=empty)')
plt.colorbar(im0, ax=axes[0, 0])

# 2. Energy map
im1 = axes[0, 1].imshow(energy_map, cmap='YlOrRd', aspect='equal')
axes[0, 1].set_title('Cell Energy')
plt.colorbar(im1, ax=axes[0, 1])

# 3. Prediction error
im2 = axes[0, 2].imshow(error_map, cmap='viridis', aspect='equal')
axes[0, 2].set_title('Prediction Error')
plt.colorbar(im2, ax=axes[0, 2])

# 4. Cell age
im3 = axes[1, 0].imshow(age_map, cmap='plasma', aspect='equal')
axes[1, 0].set_title('Cell Age')
plt.colorbar(im3, ax=axes[1, 0])

# 5. Extraction efficiency trait
im4 = axes[1, 1].imshow(trait_ext_map, cmap='coolwarm', aspect='equal')
axes[1, 1].set_title('Extraction Efficiency Trait')
plt.colorbar(im4, ax=axes[1, 1])

# 6. Timeline
if history:
    ticks = [h['tick'] for h in history]
    ax5 = axes[1, 2]
    ax5.plot(ticks, [h['cells'] for h in history], 'b-', label='total cells')
    ax5.plot(ticks, [h['surface'] for h in history], 'g-', label='surface')
    ax5.plot(ticks, [h['interior'] for h in history], 'r-', label='interior')
    ax5.set_xlabel('Tick')
    ax5.set_ylabel('Count')
    ax5.set_title('Cell Populations Over Time')
    ax5.legend()

    ax5r = ax5.twinx()
    ax5r.plot(ticks, [h['energy'] for h in history], 'k--', alpha=0.5, label='avg energy')
    ax5r.set_ylabel('Energy', color='k')
    ax5r.legend(loc='center right')

plt.tight_layout()
plt.savefig('organ_emergence.png', dpi=150)
print(f'\nPlot saved: organ_emergence.png', flush=True)
print(f'Final: {tissue.cell_count} cells, {tissue.total_births} births, {tissue.total_deaths} deaths', flush=True)
