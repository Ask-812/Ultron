#!/usr/bin/env python3
"""
STIMULUS-RESPONSE EXPERIMENT — Does the organism respond coherently?

Protocol:
  1. Grow organism to steady state (3000 ticks)
  2. Record baseline metrics
  3. Inject localized stimulus (energy pulse or signal injection)
  4. Track response propagation: energy redistribution, signal wave, cell type changes
  5. Compare response speed and coherence across cell types

This tests whether the signal-phenotype-energy machinery produces
organism-level coordination or remains purely local.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue

CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.60,
    'update_cost_factor': 0.015, 'learning_rate': 0.05,
    'birth_trait_variation': 0.02,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 140.0, 'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 500,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001, 'phenotype_emission_coupling': 2.0,
    'phenotype_affinity_coupling': 2.0,
}

GRID = 20
WARMUP = 3000
PRE_RECORD = 50   # baseline ticks before stimulus
POST_RECORD = 200 # tracking ticks after stimulus

np.random.seed(42)
tissue = Tissue(GRID, GRID, CONFIG)
tissue.seed_full()

print(f"STIMULUS-RESPONSE EXPERIMENT ({GRID}x{GRID})", flush=True)
print(f"Warmup: {WARMUP} ticks...", flush=True)

for t in range(WARMUP):
    tissue.step()
    if (t + 1) % 1000 == 0:
        s = tissue.snapshot()
        print(f"  t={t+1}: cells={s['cell_count']}, E={s['total_energy']:.0f}", flush=True)

# Record baseline
print(f"\nRecording baseline ({PRE_RECORD} ticks)...", flush=True)
baseline_energy = []
baseline_signal = []
for t in range(PRE_RECORD):
    tissue.step()
    baseline_energy.append(tissue.get_energy_map().copy())
    baseline_signal.append(tissue.get_signal_magnitude_map().copy())

mean_baseline_energy = np.mean(baseline_energy, axis=0)
mean_baseline_signal = np.mean(baseline_signal, axis=0)
std_baseline_energy = np.std(baseline_energy, axis=0)
std_baseline_signal = np.std(baseline_signal, axis=0)

# Choose stimulus location: center of the organism
stim_r, stim_c = GRID // 2, GRID // 2
cell = tissue.grid[stim_r][stim_c]
if cell and cell.is_alive:
    print(f"\nStimulus target: ({stim_r},{stim_c}), surface={cell.is_surface}, "
          f"E={cell.energy:.1f}, phenotype=[{cell.phenotype[0]:.2f},{cell.phenotype[1]:.2f},{cell.phenotype[2]:.2f},{cell.phenotype[3]:.2f}]", flush=True)

# === STIMULUS 1: Energy injection ===
print(f"\n=== STIMULUS 1: Energy injection at ({stim_r},{stim_c}) ===", flush=True)
# Inject 200 energy units into center cell
if cell and cell.is_alive:
    cell.energy = min(cell.energy + 200, cell.state.energy.capacity * 2)  # temporarily exceed cap

# Track response over time
response_energy = []
response_signal = []
response_snapshots = []

# Also track per-ring metrics (distance from stimulus)
max_dist = int(np.sqrt(2) * GRID / 2) + 1
ring_energy_response = {d: [] for d in range(max_dist)}

for t in range(POST_RECORD):
    tissue.step()
    e_map = tissue.get_energy_map().copy()
    s_map = tissue.get_signal_magnitude_map().copy()
    response_energy.append(e_map)
    response_signal.append(s_map)

    # Compute per-ring energy deviation from baseline
    for r in range(GRID):
        for c in range(GRID):
            d = int(np.sqrt((r - stim_r)**2 + (c - stim_c)**2))
            if d < max_dist and mean_baseline_energy[r, c] > 0:
                deviation = (e_map[r, c] - mean_baseline_energy[r, c]) / (mean_baseline_energy[r, c] + 1e-6)
                ring_energy_response[d].append((t, deviation))

    if t in (1, 5, 10, 20, 50, 100, 199):
        delta_e = e_map - mean_baseline_energy
        delta_s = s_map - mean_baseline_signal
        # Measure how far the energy perturbation has spread
        # Compute "response radius" = distance at which deviation > 2 * baseline_std
        responded_cells = 0
        max_response_dist = 0
        for r in range(GRID):
            for c in range(GRID):
                d = np.sqrt((r - stim_r)**2 + (c - stim_c)**2)
                threshold = max(2 * std_baseline_energy[r, c], 1.0)
                if abs(delta_e[r, c]) > threshold:
                    responded_cells += 1
                    max_response_dist = max(max_response_dist, d)
        print(f"  t+{t+1:3d}: responded={responded_cells}, max_dist={max_response_dist:.1f}, "
              f"stim_cell_E={e_map[stim_r, stim_c]:.1f}", flush=True)

# === STIMULUS 2: Signal injection ===
print(f"\n=== STIMULUS 2: Signal pulse at ({stim_r},{stim_c}) ===", flush=True)

# Record new baseline (50 ticks after energy stimulus settled)
for t in range(100):
    tissue.step()

baseline2_signal = []
for t in range(PRE_RECORD):
    tissue.step()
    baseline2_signal.append(tissue.get_signal_magnitude_map().copy())
mean_baseline2 = np.mean(baseline2_signal, axis=0)

# Inject a massive signal pulse
tissue.signal_field[stim_r, stim_c] = np.array([5.0, 5.0, 5.0, 5.0])

signal_response = []
for t in range(POST_RECORD):
    tissue.step()
    s_map = tissue.get_signal_magnitude_map().copy()
    signal_response.append(s_map)

    if t in (0, 1, 2, 5, 10, 20, 50, 100, 199):
        delta = s_map - mean_baseline2
        # Signal wavefront: count cells with delta > 2 * std
        responded = 0
        max_d = 0
        for r in range(GRID):
            for c in range(GRID):
                d = np.sqrt((r - stim_r)**2 + (c - stim_c)**2)
                if delta[r, c] > 0.1:  # significant signal above baseline
                    responded += 1
                    max_d = max(max_d, d)
        print(f"  t+{t+1:3d}: signal_responded={responded}, wavefront_dist={max_d:.1f}, "
              f"stim_signal={s_map[stim_r, stim_c]:.3f}", flush=True)

# === VISUALIZATION ===
fig, axes = plt.subplots(3, 4, figsize=(22, 15))
fig.suptitle('Stimulus-Response Experiment', fontsize=14)

# Row 1: Energy stimulus snapshots
for i, t_idx in enumerate([0, 4, 19, 99]):
    if t_idx < len(response_energy):
        delta = response_energy[t_idx] - mean_baseline_energy
        vmax = max(abs(delta.min()), abs(delta.max()), 1)
        im = axes[0, i].imshow(delta, cmap='RdBu_r', vmin=-vmax, vmax=vmax, interpolation='nearest')
        axes[0, i].plot(stim_c, stim_r, 'k*', markersize=12)
        axes[0, i].set_title(f'Energy delta t+{t_idx+1}')
        plt.colorbar(im, ax=axes[0, i], shrink=0.7)

# Row 2: Signal stimulus snapshots
for i, t_idx in enumerate([0, 1, 4, 19]):
    if t_idx < len(signal_response):
        delta = signal_response[t_idx] - mean_baseline2
        vmax = max(abs(delta.min()), abs(delta.max()), 0.1)
        im = axes[1, i].imshow(delta, cmap='hot', vmin=0, vmax=vmax, interpolation='nearest')
        axes[1, i].plot(stim_c, stim_r, 'c*', markersize=12)
        axes[1, i].set_title(f'Signal delta t+{t_idx+1}')
        plt.colorbar(im, ax=axes[1, i], shrink=0.7)

# Row 3: Analysis
# 3a: Ring response over time (energy)
ax = axes[2, 0]
for d in [0, 1, 2, 3, 5, 8]:
    if ring_energy_response[d]:
        times, devs = zip(*ring_energy_response[d])
        # Bin by time
        bins = np.arange(0, POST_RECORD, 5)
        binned = []
        for b_start in bins:
            vals = [dv for tm, dv in zip(times, devs) if b_start <= tm < b_start + 5]
            binned.append(np.mean(vals) if vals else 0)
        ax.plot(bins, binned, label=f'd={d}')
ax.set_xlabel('Ticks after stimulus')
ax.set_ylabel('Energy deviation (%)')
ax.set_title('Energy response by distance')
ax.legend(fontsize=7)

# 3b: Signal wavefront propagation
ax = axes[2, 1]
wavefront_times = []
wavefront_dists = []
for t_idx in range(min(50, len(signal_response))):
    delta = signal_response[t_idx] - mean_baseline2
    max_d = 0
    for r in range(GRID):
        for c in range(GRID):
            d = np.sqrt((r - stim_r)**2 + (c - stim_c)**2)
            if delta[r, c] > 0.05:
                max_d = max(max_d, d)
    wavefront_times.append(t_idx)
    wavefront_dists.append(max_d)
ax.plot(wavefront_times, wavefront_dists, 'r-o', markersize=3)
ax.set_xlabel('Ticks after signal pulse')
ax.set_ylabel('Wavefront distance (cells)')
ax.set_title('Signal propagation speed')

# 3c: Cell type map at end
phenotype_map = tissue.get_phenotype_map()
surface_map = np.full((GRID, GRID), np.nan)
for r in range(GRID):
    for c in range(GRID):
        cell = tissue.grid[r][c]
        if cell and cell.is_alive:
            surface_map[r, c] = cell.phenotype[0]
im = axes[2, 2].imshow(surface_map, cmap='RdYlBu_r', vmin=0, vmax=1, interpolation='nearest')
axes[2, 2].set_title('Phenotype[0] (surface history)')
plt.colorbar(im, ax=axes[2, 2], shrink=0.7)

# 3d: Energy map at end
im = axes[2, 3].imshow(tissue.get_energy_map(), cmap='YlOrRd', interpolation='nearest')
axes[2, 3].set_title('Final energy map')
plt.colorbar(im, ax=axes[2, 3], shrink=0.7)

plt.tight_layout()
plt.savefig('stimulus_response.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: stimulus_response.png", flush=True)

# === Summary ===
print("\n=== SUMMARY ===", flush=True)

# Compute signal propagation speed
speeds = []
for i in range(1, len(wavefront_dists)):
    if wavefront_dists[i] > wavefront_dists[i-1]:
        speeds.append(wavefront_dists[i] - wavefront_dists[i-1])

if speeds:
    print(f"Signal propagation speed: {np.mean(speeds):.2f} cells/tick (peak: {max(speeds):.1f})", flush=True)
print(f"Signal wavefront max reach: {max(wavefront_dists):.1f} cells", flush=True)

# Energy response delay by distance
for d in [1, 3, 5, 8]:
    if ring_energy_response[d]:
        times, devs = zip(*ring_energy_response[d])
        # Find first tick where deviation > 1%
        sorted_pairs = sorted(zip(times, devs))
        first_response = None
        for tm, dv in sorted_pairs:
            if abs(dv) > 0.01:
                first_response = tm
                break
        if first_response is not None:
            print(f"Energy response at d={d}: first detected at t+{first_response}", flush=True)
