#!/usr/bin/env python3
"""
COMPETITIVE EVOLUTION

Add resource competition: total available energy is limited,
so organisms compete for extraction.
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
    'extraction_factor': 0.35,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.03,
    'reproduction_cost': 60.0,
    'mutation_rate': 0.015,
}

TICKS = 1000000
MAX_POP = 100
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 40  # Soft limit via competition
signal_ratio = 0.55

print('COMPETITIVE EVOLUTION')
print('=' * 70)
print(f'Carrying capacity: {CARRYING_CAPACITY}')
print()

np.random.seed(42)
env = MixedEnvironment(8, signal_ratio=signal_ratio)
population = [create_ultron(config) for _ in range(30)]

births = 0
deaths = 0
gens = [0] * len(population)

initial_fitness = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])

for t in range(TICKS):
    if not population:
        print(f't={t}: EXTINCTION')
        break
    
    if t % 15000 == 0:
        alive = [p for p in population if p.is_alive]
        fitness = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in alive]
        energy = np.mean([p.energy.current for p in alive])
        print(f't={t:6d}: pop={len(alive):2d}, fit={np.mean(fitness):.4f}, E={energy:5.1f}, b={births:4d}, d={deaths:4d}, gen={max(gens)}')
    
    obs = env.get_input(t)
    
    # Competition factor: reduce extraction when over carrying capacity
    competition_factor = min(1.0, CARRYING_CAPACITY / max(1, len(population)))
    
    for i in range(len(population)):
        if population[i].is_alive:
            # Modify config temporarily to simulate competition
            comp_config = config.copy()
            comp_config['extraction_factor'] = config['extraction_factor'] * competition_factor
            population[i] = tick(population[i], obs, comp_config)
    
    for i in range(len(population) - 1, -1, -1):
        if not population[i].is_alive:
            deaths += 1
            population.pop(i)
            gens.pop(i)
    
    if len(population) < MAX_POP:
        n = len(population)
        for i in range(n):
            if population[i].energy.current >= REPRODUCTION_THRESHOLD:
                parent, child = reproduce(population[i], config)
                if child:
                    population.append(child)
                    gens.append(gens[i] + 1)
                    births += 1

print()
print('=' * 70)
print('RESULTS')
print('=' * 70)
if population:
    final_fitness = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])
    extraction = np.mean([p.traits.extraction_efficiency for p in population])
    metabolic = np.mean([p.traits.metabolic_rate for p in population])
    
    print(f'Initial fitness: {initial_fitness:.4f}')
    print(f'Final fitness:   {final_fitness:.4f}')
    print(f'Change: {(final_fitness - initial_fitness) / initial_fitness * 100:+.1f}%')
    print(f'Mean extraction: {extraction:.4f}')
    print(f'Mean metabolic:  {metabolic:.4f}')
    print(f'Max generation:  {max(gens)}')
    print(f'Total births: {births}')
    print(f'Total deaths: {deaths}')
