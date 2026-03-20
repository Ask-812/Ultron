#!/usr/bin/env python3
"""
SCALE SURVIVAL CORRELATION

Test if birth scale predicts survival at boundary.
Use controlled scale ranges.
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
    'extraction_factor': 0.30,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
}

TICKS = 100000
signal_ratio = 0.52

# Test specific scale ranges
scale_ranges = [
    ('small', 0.098, 0.099),
    ('medium', 0.099, 0.101),
    ('large', 0.101, 0.102),
]

print('SCALE-SURVIVAL CORRELATION AT BOUNDARY')
print('=' * 70)

results = {}

for name, scale_min, scale_max in scale_ranges:
    survivors = 0
    deaths = 0
    death_times = []
    
    for i in range(50):
        np.random.seed(i * 13 + hash(name) % 1000)
        weight_scale = np.random.uniform(scale_min, scale_max)
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        state.model.weights *= weight_scale / 0.1
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            survivors += 1
        else:
            deaths += 1
            death_times.append(t)
    
    results[name] = {
        'survivors': survivors,
        'deaths': deaths,
        'rate': survivors / 50,
        'mean_death': np.mean(death_times) if death_times else 0,
    }
    
    print(f'{name:8s} ({scale_min:.3f}-{scale_max:.3f}): {survivors}/50 survive ({100*survivors/50:.0f}%)')
    if death_times:
        print(f'         Mean death time: {np.mean(death_times):.0f}')
    print()

print('CONCLUSION')
print('-' * 40)
rates = [results[n]['rate'] for n in ['small', 'medium', 'large']]
if rates[2] > rates[0]:
    print('Larger scale → better survival')
elif rates[0] > rates[2]:
    print('Smaller scale → better survival')
else:
    print('No clear scale-survival relationship')
