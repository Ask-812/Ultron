#!/usr/bin/env python3
"""
SEASONAL SURVIVAL EXPERIMENT — Can a differentiated organism survive winter?

The environment oscillates between summer (high signal_ratio, easy extraction)
and winter (low signal_ratio, chaos). The organism must:
  - Accumulate energy during summer
  - Buffer through winter using stored energy
  - Maintain tissue integrity across seasons

Compares 3 conditions:
  1. No seasons (control) — constant environment
  2. Mild seasons (amplitude=0.15) — moderate oscillation
  3. Harsh seasons (amplitude=0.30) — extreme oscillation

Hypothesis: Differentiated organisms (v0.4.0) survive seasonal stress
better because absorptive cells buffer energy during summer.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ultron.tissue import Tissue

BASE_CONFIG = {
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
TICKS = 8000
SEASON_PERIOD = 1000  # 1000 ticks per full cycle

conditions = [
    ('No seasons',    0.0),
    ('Mild seasons',  0.15),
    ('Harsh seasons', 0.30),
]

print(f"SEASONAL SURVIVAL EXPERIMENT ({GRID}x{GRID}, {TICKS} ticks)", flush=True)
print(f"Season period: {SEASON_PERIOD} ticks", flush=True)

results = {}

for name, amplitude in conditions:
    config = dict(BASE_CONFIG)
    config['season_amplitude'] = amplitude
    config['season_period'] = float(SEASON_PERIOD)

    np.random.seed(42)
    tissue = Tissue(GRID, GRID, config)
    tissue.seed_full()

    history = {'tick': [], 'cells': [], 'energy': [], 'signal_ratio_center': [],
               'pheno_div': [], 'surface_count': [], 'interior_count': [],
               'mean_energy_surface': [], 'mean_energy_interior': []}

    print(f"\n--- {name} (amplitude={amplitude}) ---", flush=True)

    for t in range(1, TICKS + 1):
        tissue.step()

        if t % 100 == 0:
            s = tissue.snapshot()
            # Compute season phase
            if amplitude > 0:
                current_ratio = 0.55 + amplitude * np.sin(2 * np.pi * t / SEASON_PERIOD)
            else:
                current_ratio = 0.55

            # Surface vs interior energy
            s_energies = []
            i_energies = []
            for r in range(GRID):
                for c in range(GRID):
                    cell = tissue.grid[r][c]
                    if cell and cell.is_alive:
                        if cell.is_surface:
                            s_energies.append(cell.energy)
                        else:
                            i_energies.append(cell.energy)

            history['tick'].append(t)
            history['cells'].append(s['cell_count'])
            history['energy'].append(s['total_energy'])
            history['signal_ratio_center'].append(current_ratio)
            history['pheno_div'].append(s['phenotype_diversity'])
            history['surface_count'].append(len(s_energies))
            history['interior_count'].append(len(i_energies))
            history['mean_energy_surface'].append(np.mean(s_energies) if s_energies else 0)
            history['mean_energy_interior'].append(np.mean(i_energies) if i_energies else 0)

        if t % 2000 == 0:
            phase = "SUMMER" if amplitude > 0 and np.sin(2 * np.pi * t / SEASON_PERIOD) > 0 else "WINTER" if amplitude > 0 else "STATIC"
            s = tissue.snapshot()
            print(f"  t={t:5d} [{phase:6s}]: cells={s['cell_count']:3d}  E={s['total_energy']:7.0f}  "
                  f"pheno_div={s['phenotype_diversity']:.3f}", flush=True)

    results[name] = history
    final = tissue.snapshot()
    print(f"  FINAL: cells={final['cell_count']}, E={final['total_energy']:.0f}, "
          f"births={final['births']}, deaths={final['deaths']}", flush=True)

# === VISUALIZATION ===
fig, axes = plt.subplots(2, 3, figsize=(20, 10))
fig.suptitle(f'Seasonal Survival (period={SEASON_PERIOD} ticks)', fontsize=14)

# Row 1: Cell count, Energy, Phenotype diversity
for i, (name, amplitude) in enumerate(conditions):
    h = results[name]
    color = ['green', 'orange', 'red'][i]

    axes[0, 0].plot(h['tick'], h['cells'], color=color, label=name, linewidth=1.5)
    axes[0, 1].plot(h['tick'], h['energy'], color=color, label=name, linewidth=1.5)
    axes[0, 2].plot(h['tick'], h['pheno_div'], color=color, label=name, linewidth=1.5)

axes[0, 0].set_ylabel('Cell Count')
axes[0, 0].set_title('Population')
axes[0, 0].legend(fontsize=8)

axes[0, 1].set_ylabel('Total Energy')
axes[0, 1].set_title('Total Energy')
axes[0, 1].legend(fontsize=8)

axes[0, 2].set_ylabel('Phenotype Diversity')
axes[0, 2].set_title('Differentiation')
axes[0, 2].legend(fontsize=8)

# Add season shading for harsh condition
for ax in axes[0]:
    for cycle in range(TICKS // SEASON_PERIOD + 1):
        # Winter is when sin < 0: period/2 to period
        w_start = cycle * SEASON_PERIOD + SEASON_PERIOD // 4
        w_end = cycle * SEASON_PERIOD + 3 * SEASON_PERIOD // 4
        ax.axvspan(w_start, w_end, alpha=0.05, color='blue')

# Row 2: Surface vs interior energy, signal ratio over time, survival comparison
for i, (name, amplitude) in enumerate(conditions):
    h = results[name]
    color = ['green', 'orange', 'red'][i]
    axes[1, 0].plot(h['tick'], h['mean_energy_surface'], color=color, linewidth=1.5,
                    label=f'{name} (S)')
    axes[1, 0].plot(h['tick'], h['mean_energy_interior'], color=color, linewidth=1.5,
                    linestyle='--', alpha=0.6)

axes[1, 0].set_ylabel('Mean Energy')
axes[1, 0].set_xlabel('Tick')
axes[1, 0].set_title('Surface (solid) vs Interior (dashed)')
axes[1, 0].legend(fontsize=7)

# Signal ratio over time for harsh
h_harsh = results['Harsh seasons']
axes[1, 1].plot(h_harsh['tick'], h_harsh['signal_ratio_center'], 'b-', linewidth=1.5)
axes[1, 1].axhline(y=0.55, color='gray', linestyle=':', alpha=0.5)
axes[1, 1].set_ylabel('Signal Ratio at Center')
axes[1, 1].set_xlabel('Tick')
axes[1, 1].set_title('Season Cycle (Harsh)')
axes[1, 1].set_ylim(0, 1)

# Final cell count comparison
final_cells = [results[name]['cells'][-1] if results[name]['cells'] else 0
               for name, _ in conditions]
final_energy = [results[name]['energy'][-1] if results[name]['energy'] else 0
                for name, _ in conditions]
labels = [name for name, _ in conditions]
x = np.arange(len(labels))
bars = axes[1, 2].bar(x, final_cells, color=['green', 'orange', 'red'], alpha=0.7)
axes[1, 2].set_xticks(x)
axes[1, 2].set_xticklabels(labels, fontsize=8)
axes[1, 2].set_ylabel('Final Cell Count')
axes[1, 2].set_title('Survival Comparison')
for bar, count, energy in zip(bars, final_cells, final_energy):
    axes[1, 2].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                    f'{count}\nE={energy:.0f}', ha='center', fontsize=8)

for ax in axes.flat:
    ax.set_xlabel('Tick')

plt.tight_layout()
plt.savefig('seasonal_survival.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: seasonal_survival.png", flush=True)

# Summary
print("\n=== SUMMARY ===", flush=True)
for name, amplitude in conditions:
    h = results[name]
    final_c = h['cells'][-1]
    final_e = h['energy'][-1]
    min_c = min(h['cells'])
    min_e = min(h['energy'])
    print(f"  {name:15s}: final cells={final_c:3d}  E={final_e:7.0f}  "
          f"min_cells={min_c:3d}  min_E={min_e:.0f}", flush=True)
