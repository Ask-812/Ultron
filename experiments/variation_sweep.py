#!/usr/bin/env python3
"""
TRAIT VARIATION SWEEP

How does the magnitude of birth variation affect the system?
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
N = 50
signal_ratio = 0.55

variations = [0.00, 0.01, 0.02, 0.05, 0.10]

print('TRAIT VARIATION SWEEP')
print('=' * 70)
print(f'Signal ratio: {signal_ratio}')
print(f'N per variation: {N}')
print()

for var in variations:
    config = config_base.copy()
    config['birth_trait_variation'] = var
    
    alive_count = 0
    fitness_values = []
    energies = []
    
    for i in range(N):
        np.random.seed(i * 67)
        
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        
        fitness = state.traits.extraction_efficiency / state.traits.metabolic_rate
        fitness_values.append(fitness)
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            alive_count += 1
            energies.append(state.energy.current)
    
    rate = alive_count / N
    fitness_std = np.std(fitness_values)
    energy_std = np.std(energies) if energies else 0
    
    print(f'variation=±{100*var:4.1f}%: survival={100*rate:3.0f}%, fitness_std={fitness_std:.4f}, energy_std={energy_std:5.1f}')

print()
print('INTERPRETATION')
print('-' * 40)
print('No variation → deterministic fate (all same)')
print('High variation → high fitness variance → high fate variance')
