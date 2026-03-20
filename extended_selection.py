#!/usr/bin/env python3
"""
EXTENDED SELECTION

More generations, harder environment, larger population.
"""

from ultron import create_ultron, tick, BirthTraits
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
    'birth_trait_variation': 0.0,
}

TICKS = 40000
POPULATION = 30
GENERATIONS = 25
MUTATION_RATE = 0.01
signal_ratio = 0.52  # Harder environment (boundary)

print('EXTENDED SELECTION (harder environment)')
print('=' * 70)
print(f'Signal ratio: {signal_ratio} (boundary)')
print(f'Population: {POPULATION}, Generations: {GENERATIONS}')
print()

np.random.seed(42)
population_traits = []
for _ in range(POPULATION):
    traits = BirthTraits(
        extraction_efficiency=1.0 + np.random.uniform(-0.03, 0.03),
        metabolic_rate=1.0 + np.random.uniform(-0.03, 0.03),
        learning_capacity=1.0 + np.random.uniform(-0.03, 0.03),
    )
    population_traits.append(traits)

fitness_history = []

for gen in range(GENERATIONS):
    survivors = []
    survivor_energies = []
    
    for traits in population_traits:
        np.random.seed(gen * 1000 + hash(id(traits)) % 1000)
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config_base)
        
        state.traits.extraction_efficiency = traits.extraction_efficiency
        state.traits.metabolic_rate = traits.metabolic_rate
        state.traits.learning_capacity = traits.learning_capacity
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config_base)
            if not state.is_alive:
                break
        
        if state.is_alive:
            survivors.append(traits)
            survivor_energies.append(state.energy.current)
    
    mean_fitness = np.mean([t.extraction_efficiency / t.metabolic_rate for t in population_traits])
    fitness_history.append(mean_fitness)
    
    survival_rate = 100 * len(survivors) / POPULATION
    print(f'Gen {gen+1:2d}: {len(survivors):2d}/{POPULATION} ({survival_rate:3.0f}%), fitness={mean_fitness:.4f}')
    
    if len(survivors) < 2:
        print('  EXTINCTION!')
        break
    
    # Next generation
    next_gen = []
    for _ in range(POPULATION):
        parent = np.random.choice(survivors)
        child = BirthTraits(
            extraction_efficiency=parent.extraction_efficiency * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
            metabolic_rate=parent.metabolic_rate * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
            learning_capacity=parent.learning_capacity * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
        )
        next_gen.append(child)
    
    population_traits = next_gen

print()
print('RESULTS:')
print('-' * 40)
print(f'Initial fitness: {fitness_history[0]:.4f}')
print(f'Final fitness:   {fitness_history[-1]:.4f}')
print(f'Fitness change:  {(fitness_history[-1] - fitness_history[0]) / fitness_history[0] * 100:.1f}%')
