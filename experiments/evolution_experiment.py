#!/usr/bin/env python3
"""
EVOLUTION EXPERIMENT

Long-running population with real births, deaths, and selection.
Track lineage and fitness over many generations.
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
    'extraction_factor': 0.32,  # Slightly more viable
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.03,  # More initial variation
    'reproduction_cost': 50.0,
    'mutation_rate': 0.01,
}

TICKS = 200000
MAX_POP = 100
REPRODUCTION_THRESHOLD = 100.0
signal_ratio = 0.60  # Moderate challenge

print('EVOLUTION EXPERIMENT')
print('=' * 70)

np.random.seed(42)
env = MixedEnvironment(8, signal_ratio=signal_ratio)
population = [create_ultron(config) for _ in range(30)]

births = 0
deaths = 0
generations = [0] * len(population)  # Track generation number

for t in range(TICKS):
    if not population:
        print(f't={t}: EXTINCTION')
        break
    
    if t % 20000 == 0:
        alive = [p for p in population if p.is_alive]
        fitness = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in alive]
        energy = [p.energy.current for p in alive]
        
        print(f't={t:6d}: pop={len(alive):3d}, fitness={np.mean(fitness):.4f}±{np.std(fitness):.4f}, E={np.mean(energy):5.1f}, births={births:4d}, deaths={deaths:4d}')
    
    obs = env.get_input(t)
    
    # Tick all
    for i in range(len(population)):
        if population[i].is_alive:
            population[i] = tick(population[i], obs, config)
    
    # Count and remove dead
    for i in range(len(population) - 1, -1, -1):
        if not population[i].is_alive:
            deaths += 1
            population.pop(i)
            generations.pop(i)
    
    # Reproduction
    if len(population) < MAX_POP:
        n = len(population)
        for i in range(n):
            if population[i].energy.current >= REPRODUCTION_THRESHOLD:
                parent, child = reproduce(population[i], config)
                if child:
                    population.append(child)
                    generations.append(generations[i] + 1)
                    births += 1

print()
print('=' * 70)
print('FINAL RESULTS')
print('=' * 70)
print(f'Population: {len(population)}')
print(f'Total births: {births}')
print(f'Total deaths: {deaths}')

if population:
    fitness = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population]
    extraction = [p.traits.extraction_efficiency for p in population]
    metabolic = [p.traits.metabolic_rate for p in population]
    
    print(f'Final fitness: {np.mean(fitness):.4f} ± {np.std(fitness):.4f}')
    print(f'Fitness range: {min(fitness):.4f} - {max(fitness):.4f}')
    print(f'Mean extraction: {np.mean(extraction):.4f}')
    print(f'Mean metabolic: {np.mean(metabolic):.4f}')
    print(f'Max generation: {max(generations)}')
