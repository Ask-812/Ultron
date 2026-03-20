#!/usr/bin/env python3
"""
PROTO-BRAIN v2: Action Coupling.

Mechanism 1 (Session 7): Signal propagation with decay — information flow.
Mechanism 2 (THIS):       Signal-coupled energy sharing + division — action coupling.

Signals now change physical behavior:
  - Energy diffusion rate amplified by local signal magnitude
  - Division threshold lowered by incoming signal strength

Cells receiving strong signals become energy ROUTERS and reproduction HUBS.
This turns passive integrators into active controllers.

Expected: signal corridors, integration hubs, sensor/relay/controller differentiation.
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

    # Spatial gradient: center structured, edges noisy
    'base_signal_ratio': 0.55,
    'spatial_gradient': 0.20,

    # Signal propagation
    'signal_hop_decay': 0.9,
    'signal_emission_strength': 0.3,

    # ACTION COUPLING — the new physics
    'signal_energy_coupling': 1.0,     # energy_rate *= (1 + coupling × signal)
    'signal_division_coupling': 0.1,   # division_threshold /= (1 + coupling × signal)

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

print(f'PROTO-BRAIN v2: Action Coupling ({GRID}x{GRID})', flush=True)
print(f'signal_energy_coupling={CONFIG["signal_energy_coupling"]}, '
      f'signal_division_coupling={CONFIG["signal_division_coupling"]}', flush=True)
print(f'Ticks: {TICKS}', flush=True)
print(flush=True)

history = []

for t in range(TICKS):
    tissue.step()

    if (t + 1) % 500 == 0:
        s = tissue.snapshot()

        n_surface = n_interior = 0
        sig_mag = tissue.get_signal_magnitude_map()
        err_map = tissue.get_error_map()
        energy_map = tissue.get_energy_map()
        occ = tissue.get_occupancy_map()

        surf_sig, int_sig = [], []
        surf_err, int_err = [], []
        surf_eng, int_eng = [], []

        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell is not None and cell.is_alive:
                    if cell.is_surface:
                        n_surface += 1
                        surf_sig.append(sig_mag[r, c])
                        surf_err.append(err_map[r, c])
                        surf_eng.append(energy_map[r, c])
                    else:
                        n_interior += 1
                        int_sig.append(sig_mag[r, c])
                        int_err.append(err_map[r, c])
                        int_eng.append(energy_map[r, c])

        # Effective diffusion rate map (base × (1 + coupling × signal))
        rate_map = CONFIG['energy_leak_rate'] * (1.0 + CONFIG['signal_energy_coupling'] * sig_mag)
        rate_alive = rate_map[occ > 0]

        history.append({
            'tick': t + 1,
            'cells': s['cell_count'],
            'surface': n_surface,
            'interior': n_interior,
            'mean_energy': s.get('mean_energy', 0),
            'mean_error': s.get('mean_error', 0),
            'signal_max': s.get('signal_max', 0),
            'surf_sig': np.mean(surf_sig) if surf_sig else 0,
            'int_sig': np.mean(int_sig) if int_sig else 0,
            'surf_err': np.mean(surf_err) if surf_err else 0,
            'int_err': np.mean(int_err) if int_err else 0,
            'surf_eng': np.mean(surf_eng) if surf_eng else 0,
            'int_eng': np.mean(int_eng) if int_eng else 0,
            'rate_max': float(rate_alive.max()) if len(rate_alive) > 0 else 0,
            'rate_mean': float(rate_alive.mean()) if len(rate_alive) > 0 else 0,
            'births': s['births'],
            'deaths': s['deaths'],
        })

        print(f't={t+1:5d}: cells={s["cell_count"]:3d} '
              f'(S={n_surface:3d} I={n_interior:3d}), '
              f'E_S={np.mean(surf_eng) if surf_eng else 0:5.1f} '
              f'E_I={np.mean(int_eng) if int_eng else 0:5.1f}, '
              f'sig_S={np.mean(surf_sig) if surf_sig else 0:.3f} '
              f'sig_I={np.mean(int_sig) if int_sig else 0:.3f}, '
              f'rate={float(rate_alive.mean()) if len(rate_alive) > 0 else 0:.4f}',
              flush=True)

    if tissue.cell_count == 0:
        print('EXTINCT', flush=True)
        break

# === Final maps ===
energy_map = tissue.get_energy_map()
error_map = tissue.get_error_map()
occupancy = tissue.get_occupancy_map()
signal_map = tissue.get_signal_magnitude_map()

surface_map = np.zeros((GRID, GRID))
age_map = np.zeros((GRID, GRID))
rate_map_final = CONFIG['energy_leak_rate'] * (1.0 + CONFIG['signal_energy_coupling'] * signal_map)

for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            surface_map[r, c] = 1.0 if cell.is_surface else 0.5
            age_map[r, c] = cell.age

# === Print maps ===
print(flush=True)
print('=== OCCUPANCY ===', flush=True)
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
print('=== EFFECTIVE DIFFUSION RATE (signal-coupled) ===', flush=True)
for r in range(GRID):
    vals = []
    for c in range(GRID):
        if occupancy[r, c] > 0:
            vals.append(f'{rate_map_final[r,c]:.3f}')
        else:
            vals.append('  .  ')
    print(' '.join(vals), flush=True)

# === Signal flow analysis ===
print(flush=True)
print('=== SIGNAL FLOW ANALYSIS ===', flush=True)

alive_cells = []
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            alive_cells.append((r, c, signal_map[r, c], error_map[r, c],
                                cell.is_surface, cell.energy,
                                rate_map_final[r, c]))

alive_cells.sort(key=lambda x: x[2], reverse=True)
print(f'Top 10 signal receivers (potential controllers):', flush=True)
print(f'  {"pos":>8s}  {"sig":>6s}  {"error":>6s}  {"type":>5s}  {"energy":>6s}  {"rate":>6s}', flush=True)
for r, c, sig, err_val, is_surf, eng, rate in alive_cells[:10]:
    cell_type = 'SURF' if is_surf else 'INT'
    print(f'  ({r:2d},{c:2d})  {sig:6.3f}  {err_val:6.3f}  {cell_type:>5s}  {eng:6.1f}  {rate:6.4f}', flush=True)

# === Radial profiles ===
print(flush=True)
print('=== RADIAL PROFILES ===', flush=True)
cr, cc = GRID / 2.0, GRID / 2.0
radial_bins = {}
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell is not None and cell.is_alive:
            dist = int(np.sqrt((r - cr)**2 + (c - cc)**2))
            if dist not in radial_bins:
                radial_bins[dist] = {'sig': [], 'err': [], 'energy': [], 'rate': []}
            radial_bins[dist]['sig'].append(signal_map[r, c])
            radial_bins[dist]['err'].append(error_map[r, c])
            radial_bins[dist]['energy'].append(energy_map[r, c])
            radial_bins[dist]['rate'].append(rate_map_final[r, c])

print(f'  {"dist":>4s}  {"n":>3s}  {"signal":>7s}  {"error":>7s}  {"energy":>7s}  {"rate":>7s}', flush=True)
for d in sorted(radial_bins.keys()):
    b = radial_bins[d]
    print(f'  {d:4d}  {len(b["sig"]):3d}  '
          f'{np.mean(b["sig"]):7.3f}  {np.mean(b["err"]):7.3f}  '
          f'{np.mean(b["energy"]):7.1f}  {np.mean(b["rate"]):7.4f}', flush=True)

# === Differentiation index ===
print(flush=True)
print('=== DIFFERENTIATION INDEX ===', flush=True)
if alive_cells:
    rates = [x[6] for x in alive_cells]
    print(f'Rate range: {min(rates):.4f} — {max(rates):.4f} (ratio: {max(rates)/min(rates):.1f}x)', flush=True)
    signals = [x[2] for x in alive_cells]
    print(f'Signal range: {min(signals):.3f} — {max(signals):.3f} (ratio: {max(signals)/max(min(signals),0.001):.1f}x)', flush=True)
    # Count cells with rate > 2× base
    high_rate = sum(1 for r in rates if r > 2 * CONFIG['energy_leak_rate'])
    print(f'High-activity cells (rate > 2× base): {high_rate}/{len(rates)} ({100*high_rate/len(rates):.0f}%)', flush=True)

# === Plots ===
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Proto-Brain v2: Action Coupling', fontsize=14)

im0 = axes[0, 0].imshow(surface_map, cmap='RdYlGn', vmin=0, vmax=1, aspect='equal')
axes[0, 0].set_title('Cell Type (green=surface, yellow=interior)')
plt.colorbar(im0, ax=axes[0, 0])

im1 = axes[0, 1].imshow(energy_map, cmap='YlOrRd', aspect='equal')
axes[0, 1].set_title('Cell Energy')
plt.colorbar(im1, ax=axes[0, 1])

im2 = axes[0, 2].imshow(signal_map, cmap='hot', aspect='equal')
axes[0, 2].set_title('Signal Magnitude')
plt.colorbar(im2, ax=axes[0, 2])

# Effective diffusion rate map — shows where energy routes form
rate_display = rate_map_final * occupancy  # zero out empty cells
im3 = axes[1, 0].imshow(rate_display, cmap='plasma', aspect='equal')
axes[1, 0].set_title('Effective Diffusion Rate (signal-coupled)')
plt.colorbar(im3, ax=axes[1, 0])

im4 = axes[1, 1].imshow(error_map, cmap='viridis', aspect='equal')
axes[1, 1].set_title('Prediction Error')
plt.colorbar(im4, ax=axes[1, 1])

# Timeline: energy by cell type + diffusion rate
if history:
    ticks_h = [h['tick'] for h in history]
    ax5 = axes[1, 2]
    ax5.plot(ticks_h, [h['surf_eng'] for h in history], 'g-', label='Surface E')
    ax5.plot(ticks_h, [h['int_eng'] for h in history], 'r-', label='Interior E')
    ax5.set_xlabel('Tick')
    ax5.set_ylabel('Mean Energy')
    ax5.legend(loc='upper left')
    ax5b = ax5.twinx()
    ax5b.plot(ticks_h, [h['rate_mean'] for h in history], 'b--', alpha=0.6, label='Mean rate')
    ax5b.set_ylabel('Diffusion Rate', color='b')
    ax5b.legend(loc='upper right')
    ax5.set_title('Energy & Diffusion Rate by Cell Type')

plt.tight_layout()
plt.savefig('proto_brain2.png', dpi=150)
print(f'\nPlot saved: proto_brain2.png', flush=True)
