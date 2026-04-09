#!/usr/bin/env python3
"""
EVOLUTION VISUALIZATION

Plot fitness trajectory from evolution_trajectory.csv
"""

import numpy as np
import matplotlib.pyplot as plt

# Load data
data = np.loadtxt('evolution_trajectory.csv', delimiter=',', skiprows=1)
times = data[:, 0] / 1000  # Convert to thousands
fitness = data[:, 1]
extraction = data[:, 2]
metabolic = data[:, 3]
population = data[:, 4]

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Fitness over time
ax1 = axes[0, 0]
ax1.plot(times, fitness, 'b-', linewidth=2)
ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
ax1.set_xlabel('Time (thousands of ticks)')
ax1.set_ylabel('Fitness (extraction/metabolic)')
ax1.set_title(f'FITNESS EVOLUTION: {fitness[0]:.3f} → {fitness[-1]:.3f} (+{(fitness[-1]/fitness[0]-1)*100:.1f}%)')
ax1.grid(True, alpha=0.3)

# Extraction trait
ax2 = axes[0, 1]
ax2.plot(times, extraction, 'g-', linewidth=2)
ax2.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
ax2.set_xlabel('Time (thousands of ticks)')
ax2.set_ylabel('Extraction efficiency')
ax2.set_title(f'EXTRACTION: {extraction[0]:.3f} → {extraction[-1]:.3f} (+{(extraction[-1]-1)*100:.1f}%)')
ax2.grid(True, alpha=0.3)

# Metabolic trait
ax3 = axes[1, 0]
ax3.plot(times, metabolic, 'r-', linewidth=2)
ax3.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('Time (thousands of ticks)')
ax3.set_ylabel('Metabolic rate')
ax3.set_title(f'METABOLIC: {metabolic[0]:.3f} → {metabolic[-1]:.3f} ({(metabolic[-1]-1)*100:.1f}%)')
ax3.grid(True, alpha=0.3)

# Population
ax4 = axes[1, 1]
ax4.plot(times, population, 'purple', linewidth=2)
ax4.set_xlabel('Time (thousands of ticks)')
ax4.set_ylabel('Population size')
ax4.set_title('POPULATION DYNAMICS')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('evolution_trajectory.png', dpi=150)
print('Saved evolution_trajectory.png')

# Combined traits plot
fig2, ax = plt.subplots(figsize=(10, 6))
ax.plot(times, fitness, 'b-', linewidth=2, label=f'Fitness (+{(fitness[-1]/fitness[0]-1)*100:.1f}%)')
ax.plot(times, extraction, 'g--', linewidth=2, label=f'Extraction (+{(extraction[-1]-1)*100:.1f}%)')
ax.plot(times, metabolic, 'r--', linewidth=2, label=f'Metabolic ({(metabolic[-1]-1)*100:.1f}%)')
ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
ax.set_xlabel('Time (thousands of ticks)', fontsize=12)
ax.set_ylabel('Trait value', fontsize=12)
ax.set_title('DARWINIAN EVOLUTION IN ULTRON\n21 generations, 126 births, 101 deaths', fontsize=14)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('evolution_combined.png', dpi=150)
print('Saved evolution_combined.png')
