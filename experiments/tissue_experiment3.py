#!/usr/bin/env python3
"""
TISSUE EXPERIMENT 3: Growth in a uniformly rich environment.

Question: What shape does a multicellular Ultron grow into
when energy is abundant everywhere?

No spatial gradient — uniform signal_ratio.
Focus on emergent morphology from division dynamics alone.
"""

import numpy as np
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

    # Uniform environment — no spatial gradient
    'base_signal_ratio': 0.80,
    'spatial_gradient': 0.0,       # FLAT — same everywhere

    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.02,

    # Growth parameters
    'division_energy_threshold': 140.0,
    'division_cost': 30.0,         # Pay more to divide (so it takes time)
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

TICKS = 30000
GRID = 20

np.random.seed(42)
tissue = Tissue(GRID, GRID, CONFIG)
tissue.seed_center(n=1)

print(f'ZYGOTE GROWTH: Uniform rich environment ({GRID}x{GRID})', flush=True)
print(f'Ticks: {TICKS}, Division threshold: {CONFIG["division_energy_threshold"]}', flush=True)
print(flush=True)

for t in range(TICKS):
    tissue.step()
    if (t + 1) % 2000 == 0:
        s = tissue.snapshot()
        print(f't={t+1:5d}: cells={s["cell_count"]:3d}, '
              f'E_avg={s.get("mean_energy", 0):5.1f}, '
              f'b={s["births"]}, d={s["deaths"]}', flush=True)
    if tissue.cell_count == 0:
        print('EXTINCT', flush=True)
        break

print(flush=True)
omap = tissue.get_occupancy_map()
emap = tissue.get_energy_map()

print('Occupancy:', flush=True)
for r in range(GRID):
    print(' '.join('O' if omap[r, c] else '.' for c in range(GRID)), flush=True)

print(flush=True)
print('Energy:', flush=True)
for r in range(GRID):
    print(' '.join(f'{emap[r,c]:3.0f}' if emap[r, c] > 0 else '  .' for c in range(GRID)), flush=True)

# Growth curve
snap = tissue.snapshot()
print(flush=True)
print(f'Final: {snap["cell_count"]} cells, {snap["births"]} births, {snap["deaths"]} deaths', flush=True)
