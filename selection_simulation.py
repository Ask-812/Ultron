#!/usr/bin/env python3
"""
SELECTION SIMULATION

What would happen if survivors could reproduce?
Simulate multiple "generations" by:
1. Run N organisms
2. Those that survive become "parents"
3. Next generation inherits parent traits (with small mutation)
4. Repeat

No actual reproduction—just trait inheritance simulation.
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
    'birth_trait_variation': 0.0,  # We'll set traits manually
}

TICKS = 50000
POPULATION = 20
GENERATIONS = 10
MUTATION_RATE = 0.01  # ±1% mutation per generation
signal_ratio = 0.55

print('SELECTION SIMULATION')
print('=' * 70)
print(f'Population: {POPULATION}')
print(f'Generations: {GENERATIONS}')
print(f'Mutation: ±{100*MUTATION_RATE:.0f}%')
print(f'Signal ratio: {signal_ratio}')
print()

# Initialize population with random traits (±2% variation)
np.random.seed(42)
population_traits = []
for _ in range(POPULATION):
    traits = BirthTraits(
        extraction_efficiency=1.0 + np.random.uniform(-0.02, 0.02),
        metabolic_rate=1.0 + np.random.uniform(-0.02, 0.02),
        learning_capacity=1.0 + np.random.uniform(-0.02, 0.02),
    )
    population_traits.append(traits)

for gen in range(GENERATIONS):
    survivors = []
    
    for i, traits in enumerate(population_traits):
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config_base)
        
        # Override traits
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
    
    # Compute population stats
    fitness_values = [t.extraction_efficiency / t.metabolic_rate for t in population_traits]
    survivor_fitness = [t.extraction_efficiency / t.metabolic_rate for t in survivors]
    
    mean_fitness = np.mean(fitness_values)
    survivor_mean = np.mean(survivor_fitness) if survivors else 0
    
    print(f'Gen {gen+1:2d}: {len(survivors):2d}/{POPULATION} survive, mean_fitness={mean_fitness:.4f} → survivor_mean={survivor_mean:.4f}')
    
    if len(survivors) < 2:
        print('  Population collapsed!')
        break
    
    # Create next generation: inherit from survivors with mutation
    next_gen = []
    for _ in range(POPULATION):
        parent = np.random.choice(survivors)
        
        # Inherit with mutation
        child = BirthTraits(
            extraction_efficiency=parent.extraction_efficiency * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
            metabolic_rate=parent.metabolic_rate * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
            learning_capacity=parent.learning_capacity * (1 + np.random.uniform(-MUTATION_RATE, MUTATION_RATE)),
        )
        next_gen.append(child)
    
    population_traits = next_gen

print()
print('FINAL POPULATION TRAITS:')
print('-' * 40)
final_fitness = [t.extraction_efficiency / t.metabolic_rate for t in population_traits]
print(f'Mean fitness: {np.mean(final_fitness):.4f} ± {np.std(final_fitness):.4f}')
print(f'Mean extraction: {np.mean([t.extraction_efficiency for t in population_traits]):.4f}')
print(f'Mean metabolic: {np.mean([t.metabolic_rate for t in population_traits]):.4f}')
