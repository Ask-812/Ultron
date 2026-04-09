#!/usr/bin/env python3
"""
VARIATION QUICK SWEEP - smaller N, shorter runs
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

TICKS = 50000
N = 30
signal_ratio = 0.55

variations = [0.00, 0.01, 0.02, 0.05, 0.10]

print('VARIATION QUICK SWEEP')
print('=' * 60)

for var in variations:
    config = config_base.copy()
    config['birth_trait_variation'] = var
    
    alive = 0
    fitness_list = []
    
    for i in range(N):
        np.random.seed(i * 71)
        
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        fitness = state.traits.extraction_efficiency / state.traits.metabolic_rate
        fitness_list.append(fitness)
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            alive += 1
    
    print(f'±{100*var:4.1f}%: {alive:2d}/{N} survive ({100*alive/N:3.0f}%), fitness_range={min(fitness_list):.3f}-{max(fitness_list):.3f}')
