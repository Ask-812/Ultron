#!/usr/bin/env python3
"""
TISSUE EXPERIMENT: Patterned environment — sine-wave signal gradient.

signal_ratio(row, col) = 0.6 + 0.3 * sin(col / 4)

Creates vertical stripes of predictability across the grid.
Some columns are highly ordered (ratio ~0.9), others chaotic (~0.3).

Question: does the organism develop internal structure —
different cell types in different regions?
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue
from ultron.environments import MixedEnvironment


class StripedTissue(Tissue):
    """Tissue with sine-wave patterned environment."""

    def get_env_observation(self, row, col, tick):
        ratio = 0.6 + 0.3 * np.sin(col / 4.0)
        ratio = np.clip(ratio, 0.0, 1.0)
        obs_dim = self.config.get('observation_dim', 8)
        key = round(ratio, 4)
        if key not in self._env_cache:
            self._env_cache[key] = MixedEnvironment(obs_dim, signal_ratio=ratio)
        return self._env_cache[key].get_input(tick)


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

    # These are overridden by StripedTissue but needed for config
    'base_signal_ratio': 0.60,
    'spatial_gradient': 0.0,

    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.02,

    'division_energy_threshold': 140.0,
    'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

TICKS = 12000
GRID = 20

np.random.seed(42)
tissue = StripedTissue(GRID, GRID, CONFIG)
tissue.seed_center(n=1)

print(f'PATTERNED ENVIRONMENT: sin(col/4) stripes on {GRID}x{GRID}', flush=True)
print(f'signal_ratio = 0.6 + 0.3*sin(col/4)', flush=True)
print(f'Ticks: {TICKS}', flush=True)

# Show the signal ratio pattern
print('\nSignal ratio by column:', flush=True)
for c in range(GRID):
    r = 0.6 + 0.3 * np.sin(c / 4.0)
    bar = '#' * int(r * 30)
    print(f'  col {c:2d}: {r:.2f} {bar}', flush=True)

print(flush=True)

for t in range(TICKS):
    tissue.step()
    if (t + 1) % 2000 == 0:
        s = tissue.snapshot()
        print(f't={t+1:5d}: cells={s["cell_count"]:3d}, '
              f'E_avg={s.get("mean_energy", 0):5.1f}, '
              f'err={s.get("mean_error", 0):.3f}, '
              f'b={s["births"]}, d={s["deaths"]}', flush=True)
    if tissue.cell_count == 0:
        print('EXTINCT', flush=True)
        break

# === Collect spatial maps ===
energy_map = tissue.get_energy_map()
error_map = tissue.get_error_map()

# Age map
age_map = np.zeros((GRID, GRID))
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            age_map[r, c] = cell.age

# Signal ratio map (the environment pattern)
ratio_map = np.zeros((GRID, GRID))
for r in range(GRID):
    for c in range(GRID):
        ratio_map[r, c] = 0.6 + 0.3 * np.sin(c / 4.0)

# Extraction efficiency trait map
trait_map = np.zeros((GRID, GRID))
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            trait_map[r, c] = cell.state.traits.extraction_efficiency

# === Print column averages ===
print('\n--- Column averages (vertical stripes expected) ---', flush=True)
print(f'{"col":>4s} {"ratio":>6s} {"energy":>7s} {"error":>7s} {"age":>7s}', flush=True)
for c in range(GRID):
    col_cells = [(r, c) for r in range(GRID)
                 if tissue.grid[r][c] is not None and tissue.grid[r][c].is_alive]
    if col_cells:
        e_avg = np.mean([tissue.grid[r][c].energy for r, c in col_cells])
        err_avg = np.mean([tissue.grid[r][c].state.current.error_magnitude for r, c in col_cells])
        age_avg = np.mean([tissue.grid[r][c].age for r, c in col_cells])
    else:
        e_avg = err_avg = age_avg = 0
    ratio = 0.6 + 0.3 * np.sin(c / 4.0)
    print(f'{c:4d} {ratio:6.2f} {e_avg:7.1f} {err_avg:7.3f} {age_avg:7.0f}', flush=True)

# === Plot ===
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Patterned Environment: sin(col/4) — Spatial Differentiation', fontsize=14)

# 1. Environment pattern
im0 = axes[0, 0].imshow(ratio_map, cmap='RdYlBu', vmin=0.3, vmax=0.9, aspect='equal')
axes[0, 0].set_title('Environment: signal_ratio')
plt.colorbar(im0, ax=axes[0, 0])

# 2. Energy map
im1 = axes[0, 1].imshow(energy_map, cmap='YlOrRd', aspect='equal')
axes[0, 1].set_title('Cell Energy')
plt.colorbar(im1, ax=axes[0, 1])

# 3. Prediction error map
im2 = axes[0, 2].imshow(error_map, cmap='viridis', aspect='equal')
axes[0, 2].set_title('Prediction Error')
plt.colorbar(im2, ax=axes[0, 2])

# 4. Cell age map
im3 = axes[1, 0].imshow(age_map, cmap='plasma', aspect='equal')
axes[1, 0].set_title('Cell Age')
plt.colorbar(im3, ax=axes[1, 0])

# 5. Extraction efficiency trait map
im4 = axes[1, 1].imshow(trait_map, cmap='coolwarm', aspect='equal')
axes[1, 1].set_title('Extraction Efficiency Trait')
plt.colorbar(im4, ax=axes[1, 1])

# 6. Column-averaged profiles
cols = np.arange(GRID)
ratios = [0.6 + 0.3 * np.sin(c / 4.0) for c in cols]
e_profile = [np.mean(energy_map[:, c][energy_map[:, c] > 0]) if np.any(energy_map[:, c] > 0) else 0 for c in cols]
err_profile = [np.mean(error_map[:, c][error_map[:, c] > 0]) if np.any(error_map[:, c] > 0) else 0 for c in cols]

ax5 = axes[1, 2]
ax5.plot(cols, ratios, 'b-', label='signal_ratio', linewidth=2)
ax5r = ax5.twinx()
ax5r.plot(cols, e_profile, 'r-', label='energy', linewidth=1.5)
ax5r.plot(cols, [e / max(max(err_profile), 1e-9) * max(max(e_profile), 1) for e in err_profile],
          'g--', label='error (scaled)', linewidth=1.5)
ax5.set_xlabel('Column')
ax5.set_ylabel('Signal Ratio', color='b')
ax5r.set_ylabel('Energy', color='r')
ax5.set_title('Column Profiles')
ax5.legend(loc='upper left')
ax5r.legend(loc='upper right')

plt.tight_layout()
plt.savefig('patterned_result.png', dpi=150)
print('\nPlot saved: patterned_result.png', flush=True)
print(f'\nFinal: {tissue.cell_count} cells, {tissue.total_births} births, {tissue.total_deaths} deaths', flush=True)
