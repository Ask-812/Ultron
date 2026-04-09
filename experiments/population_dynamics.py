#!/usr/bin/env python3
"""
POPULATION DYNAMICS

Real reproduction experiment:
- Population of Ultrons share environment ticks
- Those with surplus energy can reproduce
- Deaths and births change population
- Track population size and mean fitness over time
"""

from ultron import create_ultron, tick, reproduce
from ultron.environments import MixedEnvironment
import numpy as np

config = {
    'observation_dim': 8,
    'model_dim': 16,
    'initial_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.30,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,
    'reproduction_cost': 80.0,
    'mutation_rate': 0.01,
}

TICKS = 100000
INITIAL_POP = 10
MAX_POP = 50
REPRODUCTION_THRESHOLD = 150.0  # Need this much energy to reproduce
signal_ratio = 0.55

print('POPULATION DYNAMICS')
print('=' * 70)
print(f'Initial population: {INITIAL_POP}')
print(f'Max population: {MAX_POP}')
print(f'Reproduction threshold: {REPRODUCTION_THRESHOLD}')
print(f'Signal ratio: {signal_ratio}')
print()

np.random.seed(42)
env = MixedEnvironment(8, signal_ratio=signal_ratio)

# Initialize population
population = [create_ultron(config) for _ in range(INITIAL_POP)]

# Track history
pop_history = []
fitness_history = []
births_total = 0
deaths_total = 0

sample_ticks = [0, 1000, 5000, 10000, 25000, 50000, 75000, 100000]
next_sample = 0

for t in range(TICKS):
    if not population:
        print(f'  EXTINCTION at tick {t}')
        break
    
    # Sample and report
    if next_sample < len(sample_ticks) and t == sample_ticks[next_sample]:
        alive = [p for p in population if p.is_alive]
        if alive:
            fitness_values = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in alive]
            mean_fitness = np.mean(fitness_values)
            mean_energy = np.mean([p.energy.current for p in alive])
            print(f't={t:6d}: pop={len(alive):2d}, fitness={mean_fitness:.4f}, energy={mean_energy:.1f}, births={births_total}, deaths={deaths_total}')
            pop_history.append(len(alive))
            fitness_history.append(mean_fitness)
        next_sample += 1
    
    # Get environment input
    obs = env.get_input(t)
    
    # Tick all organisms
    for i in range(len(population)):
        if population[i].is_alive:
            population[i] = tick(population[i], obs, config)
    
    # Remove dead
    dead_count = sum(1 for p in population if not p.is_alive)
    if dead_count > 0:
        deaths_total += dead_count
        population = [p for p in population if p.is_alive]
    
    # Reproduction
    if len(population) < MAX_POP:
        new_children = []
        for p in population:
            if p.energy.current >= REPRODUCTION_THRESHOLD:
                parent, child = reproduce(p, config)
                if child:
                    new_children.append(child)
                    births_total += 1
        population.extend(new_children)

print()
print('=' * 70)
print('FINAL RESULTS')
print('=' * 70)
print(f'Final population: {len(population)}')
print(f'Total births: {births_total}')
print(f'Total deaths: {deaths_total}')

if population:
    fitness_values = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population]
    print(f'Final mean fitness: {np.mean(fitness_values):.4f}')
    print(f'Fitness range: {min(fitness_values):.4f} - {max(fitness_values):.4f}')

if len(fitness_history) >= 2:
    print(f'Fitness change: {fitness_history[0]:.4f} → {fitness_history[-1]:.4f}')
