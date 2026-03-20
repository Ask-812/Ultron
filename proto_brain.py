#!/usr/bin/env python3
"""
PROTO-BRAIN EXPERIMENT: Information bottlenecks + signal propagation.

Cells now broadcast prediction error as multi-channel signals.
Signals decay per hop (×0.9), creating information locality.
Cells that relay signals extend information range — evolution favors this.

Question: do we see signal corridors, integration hubs, sensor layers?
Does centralized prediction emerge from distributed cells?

Config:
  env_dim  = 8   (environment observation)
  signal_dim = 4  (signal channels — information bottleneck)
  observation_dim = 12  (env + signals → model input)
  signal_hop_decay = 0.9 (multiplicative decay per hop)

Grid: 20×20, spatial gradient ON (center = structured, edges = noisy).
Start: seed full grid (focus on signal emergence, not growth).
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue

CONFIG = {
    # Dimensions: env (8) + signal (4) = observation (12)
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

    # Spatial gradient: center structured, edges noisy
    # This makes information VALUABLE — predicting edges requires relay from center
    'base_signal_ratio': 0.55,
    'spatial_gradient': 0.20,

    # Signal propagation
    'signal_hop_decay': 0.9,
    'signal_emission_strength': 0.3,

    # Energy sharing
    'energy_leak_rate': 0.03,

    # Cell lifecycle
    'division_energy_threshold': 140.0,
    'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

TICKS = 5000
GRID = 20
np.random.seed(42)

tissue = Tissue(GRID, GRID, CONFIG)
tissue.seed_full()

print(f'PROTO-BRAIN: Signal propagation with decay ({GRID}x{GRID})', flush=True)
print(f'env_dim={CONFIG["env_dim"]}, signal_dim={CONFIG["signal_dim"]}, '
      f'obs_dim={CONFIG["observation_dim"]}', flush=True)
print(f'signal_hop_decay={CONFIG["signal_hop_decay"]}, '
      f'emission_strength={CONFIG["signal_emission_strength"]}', flush=True)
print(f'Ticks: {TICKS}', flush=True)
print(flush=True)

history = []

for t in range(TICKS):
    tissue.step()

    if (t + 1) % 500 == 0:
        s = tissue.snapshot()

        # Count surface vs interior
        n_surface = n_interior = 0
        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell is not None and cell.is_alive:
                    if cell.is_surface:
                        n_surface += 1
                    else:
                        n_interior += 1

        # Signal statistics per cell type
        sig_mag = tissue.get_signal_magnitude_map()
        occ = tissue.get_occupancy_map()
        err = tissue.get_error_map()

        # Surface vs interior signal & error
        surf_sig = []
        int_sig = []
        surf_err = []
        int_err = []
        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell is not None and cell.is_alive:
                    if cell.is_surface:
                        surf_sig.append(sig_mag[r, c])
                        surf_err.append(err[r, c])
                    else:
                        int_sig.append(sig_mag[r, c])
                        int_err.append(err[r, c])

        history.append({
            'tick': t + 1,
            'cells': s['cell_count'],
            'surface': n_surface,
            'interior': n_interior,
            'mean_energy': s.get('mean_energy', 0),
            'mean_error': s.get('mean_error', 0),
            'signal_max': s.get('signal_max', 0),
            'signal_mean': s.get('signal_mean', 0),
            'surf_sig': np.mean(surf_sig) if surf_sig else 0,
            'int_sig': np.mean(int_sig) if int_sig else 0,
            'surf_err': np.mean(surf_err) if surf_err else 0,
            'int_err': np.mean(int_err) if int_err else 0,
            'births': s['births'],
            'deaths': s['deaths'],
        })

        print(f't={t+1:5d}: cells={s["cell_count"]:3d} '
              f'(S={n_surface:3d} I={n_interior:3d}), '
              f'E={s.get("mean_energy",0):5.1f}, '
              f'err={s.get("mean_error",0):.3f}, '
              f'sig_max={s.get("signal_max",0):.3f}, '
              f'sig_S={np.mean(surf_sig) if surf_sig else 0:.3f} '
              f'sig_I={np.mean(int_sig) if int_sig else 0:.3f}',
              flush=True)

    if tissue.cell_count == 0:
        print('EXTINCT', flush=True)
        break

# === Final spatial maps ===
energy_map = tissue.get_energy_map()
error_map = tissue.get_error_map()
occupancy = tissue.get_occupancy_map()
signal_map = tissue.get_signal_magnitude_map()

surface_map = np.zeros((GRID, GRID))
age_map = np.zeros((GRID, GRID))

for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            surface_map[r, c] = 1.0 if cell.is_surface else 0.5
            age_map[r, c] = cell.age

# === Print maps ===
print(flush=True)
print('=== OCCUPANCY (S=surface, I=interior, .=empty) ===', flush=True)
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
print('=== SIGNAL MAGNITUDE (higher = more information flowing) ===', flush=True)
for r in range(GRID):
    vals = []
    for c in range(GRID):
        if occupancy[r, c] > 0:
            vals.append(f'{signal_map[r,c]:4.2f}')
        else:
            vals.append('  . ')
    print(' '.join(vals), flush=True)

print(flush=True)
print('=== ERROR MAP ===', flush=True)
for r in range(GRID):
    vals = []
    for c in range(GRID):
        if occupancy[r, c] > 0:
            vals.append(f'{error_map[r,c]:4.2f}')
        else:
            vals.append('  . ')
    print(' '.join(vals), flush=True)

# === Signal flow analysis ===
print(flush=True)
print('=== SIGNAL FLOW ANALYSIS ===', flush=True)

# Find cells with highest signal reception (potential integration hubs)
alive_cells = []
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            alive_cells.append((r, c, signal_map[r, c], error_map[r, c],
                                cell.is_surface, cell.energy))

alive_cells.sort(key=lambda x: x[2], reverse=True)
print(f'Top 10 signal receivers (potential hubs):', flush=True)
print(f'  {"pos":>8s}  {"sig_mag":>7s}  {"error":>7s}  {"type":>7s}  {"energy":>7s}', flush=True)
for r, c, sig, err_val, is_surf, eng in alive_cells[:10]:
    cell_type = 'SURF' if is_surf else 'INT'
    print(f'  ({r:2d},{c:2d})  {sig:7.3f}  {err_val:7.3f}  {cell_type:>7s}  {eng:7.1f}', flush=True)

# Radial signal profile
print(flush=True)
print('=== RADIAL PROFILES (distance from center) ===', flush=True)
cr, cc = GRID / 2.0, GRID / 2.0
radial_bins = {}
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            dist = int(np.sqrt((r - cr)**2 + (c - cc)**2))
            if dist not in radial_bins:
                radial_bins[dist] = {'sig': [], 'err': [], 'energy': []}
            radial_bins[dist]['sig'].append(signal_map[r, c])
            radial_bins[dist]['err'].append(error_map[r, c])
            radial_bins[dist]['energy'].append(energy_map[r, c])

print(f'  {"dist":>4s}  {"n":>3s}  {"signal":>7s}  {"error":>7s}  {"energy":>7s}', flush=True)
for d in sorted(radial_bins.keys()):
    b = radial_bins[d]
    print(f'  {d:4d}  {len(b["sig"]):3d}  '
          f'{np.mean(b["sig"]):7.3f}  {np.mean(b["err"]):7.3f}  '
          f'{np.mean(b["energy"]):7.1f}', flush=True)

# === Plots ===
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Proto-Brain: Signal Propagation with Decay', fontsize=14)

im0 = axes[0, 0].imshow(surface_map, cmap='RdYlGn', vmin=0, vmax=1, aspect='equal')
axes[0, 0].set_title('Cell Type (green=surface, yellow=interior)')
plt.colorbar(im0, ax=axes[0, 0])

im1 = axes[0, 1].imshow(energy_map, cmap='YlOrRd', aspect='equal')
axes[0, 1].set_title('Cell Energy')
plt.colorbar(im1, ax=axes[0, 1])

im2 = axes[0, 2].imshow(error_map, cmap='viridis', aspect='equal')
axes[0, 2].set_title('Prediction Error')
plt.colorbar(im2, ax=axes[0, 2])

im3 = axes[1, 0].imshow(signal_map, cmap='hot', aspect='equal')
axes[1, 0].set_title('Signal Magnitude (information flow)')
plt.colorbar(im3, ax=axes[1, 0])

im4 = axes[1, 1].imshow(age_map, cmap='plasma', aspect='equal')
axes[1, 1].set_title('Cell Age')
plt.colorbar(im4, ax=axes[1, 1])

# Timeline: signal and error
if history:
    ticks_h = [h['tick'] for h in history]
    ax5 = axes[1, 2]
    ax5.plot(ticks_h, [h['surf_err'] for h in history], 'b-', label='Surface error')
    ax5.plot(ticks_h, [h['int_err'] for h in history], 'r-', label='Interior error')
    ax5.set_xlabel('Tick')
    ax5.set_ylabel('Mean Error', color='b')
    ax5.legend(loc='upper left')
    ax5b = ax5.twinx()
    ax5b.plot(ticks_h, [h['surf_sig'] for h in history], 'b--', alpha=0.5, label='Surface signal')
    ax5b.plot(ticks_h, [h['int_sig'] for h in history], 'r--', alpha=0.5, label='Interior signal')
    ax5b.set_ylabel('Mean Signal', color='r')
    ax5b.legend(loc='upper right')
    ax5.set_title('Error & Signal by Cell Type')

plt.tight_layout()
plt.savefig('proto_brain.png', dpi=150)
print(f'\nPlot saved: proto_brain.png', flush=True)
