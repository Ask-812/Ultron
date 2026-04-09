#!/usr/bin/env python3
"""Zygote growth in richer environment on 12x12 grid."""

import numpy as np
from ultron.tissue import Tissue

CONFIG = {
    'observation_dim': 10,
    'model_dim': 20,
    'initial_energy': 100.0,
    'starting_energy': 170.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.50,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,
    'base_signal_ratio': 0.70,
    'spatial_gradient': 0.20,
    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.01,
    'division_energy_threshold': 160.0,
    'division_cost': 10.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

np.random.seed(42)
tissue = Tissue(12, 12, CONFIG)
tissue.seed_center(n=1)

for t in range(10000):
    tissue.step()
    if (t + 1) % 1000 == 0:
        snap = tissue.snapshot()
        cc = snap['cell_count']
        ea = snap.get('mean_energy', 0)
        b = snap['births']
        d = snap['deaths']
        print(f't={snap["tick"]:5d}: cells={cc:2d}, E_avg={ea:5.1f}, b={b}, d={d}', flush=True)
    if tissue.cell_count == 0:
        print('EXTINCTION', flush=True)
        break

print(flush=True)
print('Occupancy:', flush=True)
omap = tissue.get_occupancy_map()
for r in range(12):
    print(' '.join('O' if omap[r, c] else '.' for c in range(12)), flush=True)

print(flush=True)
print('Energy map:', flush=True)
emap = tissue.get_energy_map()
for r in range(12):
    print(' '.join(f'{emap[r,c]:3.0f}' if emap[r, c] > 0 else '  .' for c in range(12)), flush=True)
