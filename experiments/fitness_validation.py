#!/usr/bin/env python3
"""
FITNESS VALIDATION

Confirm that fitness = extraction/metabolic predicts survival.
Large sample size, multiple environments.
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
    'birth_trait_variation': 0.02,
}

TICKS = 100000
N = 100

print('FITNESS VALIDATION')
print('=' * 70)

for env_name, signal_ratio in [('margin', 0.55)]:
    print(f'\n{env_name.upper()} (N={N}, ticks={TICKS})')
    print('-' * 50)
    
    alive_fitness = []
    dead_fitness = []
    
    for i in range(N):
        np.random.seed(i * 59)
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        
        fitness = state.traits.extraction_efficiency / state.traits.metabolic_rate
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            alive_fitness.append(fitness)
        else:
            dead_fitness.append(fitness)
        
        if (i + 1) % 20 == 0:
            print(f'  Progress: {i+1}/{N}')
    
    print()
    print(f'Survival: {len(alive_fitness)}/{N} ({100*len(alive_fitness)/N:.0f}%)')
    print()
    print(f'Alive fitness: {np.mean(alive_fitness):.4f} ± {np.std(alive_fitness):.4f}')
    print(f'Dead fitness:  {np.mean(dead_fitness):.4f} ± {np.std(dead_fitness):.4f}')
    print()
    
    # Find threshold
    all_fitness = [(f, 1) for f in alive_fitness] + [(f, 0) for f in dead_fitness]
    all_fitness.sort(key=lambda x: x[0])
    
    # Binary search for threshold
    best_accuracy = 0
    best_threshold = 1.0
    
    for threshold in np.linspace(0.96, 1.04, 100):
        predicted_alive = sum(1 for f, actual in all_fitness if f >= threshold and actual == 1)
        predicted_dead = sum(1 for f, actual in all_fitness if f < threshold and actual == 0)
        accuracy = (predicted_alive + predicted_dead) / N
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold
    
    print(f'Best fitness threshold: {best_threshold:.4f}')
    print(f'Classification accuracy: {100*best_accuracy:.1f}%')
