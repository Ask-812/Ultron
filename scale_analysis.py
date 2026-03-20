#!/usr/bin/env python3
"""
EXTENDED SCALE ANALYSIS

Test wider range of scales with more samples.
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

TICKS = 80000
signal_ratio = 0.52

# Test specific scales (not ranges)
scales = [0.08, 0.09, 0.10, 0.11, 0.12]
SAMPLES_PER_SCALE = 30

print('SCALE-SURVIVAL ANALYSIS (fixed scales, varied seeds)')
print('=' * 70)

for scale in scales:
    survivors = 0
    death_times = []
    
    for i in range(SAMPLES_PER_SCALE):
        np.random.seed(i * 17)
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        state.model.weights *= scale / 0.1
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            survivors += 1
        else:
            death_times.append(t)
    
    rate = survivors / SAMPLES_PER_SCALE
    mean_death = np.mean(death_times) if death_times else TICKS
    
    bar = '█' * int(rate * 20)
    print(f'scale={scale:.2f}: {survivors:2d}/{SAMPLES_PER_SCALE} ({100*rate:4.0f}%) {bar}')
    print(f'           mean death: {mean_death:.0f}')
