#!/usr/bin/env python3
"""
METABOLIC THRESHOLD MAPPING

Find the precise threshold where survival becomes possible.
"""

from ultron import create_ultron, tick
from ultron.environments import MixedEnvironment
import numpy as np

config_base = {
    'observation_dim': 8,
    'model_dim': 16,
    'initial_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
}

TICKS = 100000
signal_ratio = 0.55
SAMPLES_PER = 20

extraction_values = [0.290, 0.293, 0.296, 0.298, 0.300, 0.302, 0.305, 0.310]

print('METABOLIC THRESHOLD MAPPING')
print('=' * 70)
print(f'Signal ratio: {signal_ratio}')
print()

for extraction in extraction_values:
    survivors = 0
    energies = []
    
    for i in range(SAMPLES_PER):
        np.random.seed(i * 41)
        
        config = config_base.copy()
        config['extraction_factor'] = extraction
        
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            survivors += 1
            energies.append(state.energy.current)
    
    rate = survivors / SAMPLES_PER
    mean_e = np.mean(energies) if energies else 0
    bar = '█' * int(rate * 20)
    print(f'extraction={extraction:.3f}: {survivors:2d}/{SAMPLES_PER} ({100*rate:3.0f}%) E={mean_e:5.1f} {bar}')
