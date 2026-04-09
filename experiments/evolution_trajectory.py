#!/usr/bin/env python3
"""
EVOLUTION TRAJECTORY

Track and visualize fitness over time with real selection.
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
CARRYING_CAPACITY = 40
signal_ratio = 0.55

print('EVOLUTION TRAJECTORY')
print('=' * 70)

np.random.seed(42)
env = MixedEnvironment(8, signal_ratio=signal_ratio)
population = [create_ultron(config) for _ in range(30)]

births = 0
deaths = 0
gens = [0] * len(population)

# Track trajectory
fitness_history = []
extraction_history = []
metabolic_history = []
pop_history = []
times = []

for t in range(TICKS):
    if not population:
        print(f't={t}: EXTINCTION')
        break
    
    # Competition factor
    competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))
    
    obs = env.get_input(t)
    
    # Update all
    for i in range(len(population)):
        if population[i].is_alive:
            comp_config = config.copy()
            comp_config['extraction_factor'] = config['extraction_factor'] * competition
            population[i] = tick(population[i], obs, comp_config)
    
    # Remove dead
    alive = []
    new_gens = []
    for i, ultron in enumerate(population):
        if ultron.is_alive:
            alive.append(ultron)
            new_gens.append(gens[i])
        else:
            deaths += 1
    
    # Reproduction
    n = len(alive)
    for i in range(n):
        if alive[i].energy.current >= REPRODUCTION_THRESHOLD and len(alive) < MAX_POP:
            parent, child = reproduce(alive[i], config)
            if child:
                alive.append(child)
                new_gens.append(new_gens[i] + 1)
                births += 1
    
    population = alive
    gens = new_gens
    
    # Record every 5000 ticks
    if t % 5000 == 0 and population:
        fit = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])
        ext = np.mean([p.traits.extraction_efficiency for p in population])
        met = np.mean([p.traits.metabolic_rate for p in population])
        
        fitness_history.append(fit)
        extraction_history.append(ext)
        metabolic_history.append(met)
        pop_history.append(len(population))
        times.append(t)
    
    # Progress
    if t % 100000 == 0:
        fit = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])
        print(f't={t:7d}: fit={fit:.4f}, b={births:4d}, d={deaths:4d}, gen={max(gens)}')

# Save data
print()
print('=' * 70)
print('Saving trajectory data...')

data = np.array([times, fitness_history, extraction_history, metabolic_history, pop_history]).T
np.savetxt('evolution_trajectory.csv', data, delimiter=',', 
           header='time,fitness,extraction,metabolic,population', comments='')

print(f'Saved {len(times)} data points to evolution_trajectory.csv')

# Summary stats
print()
print('SUMMARY')
print('=' * 70)
print(f'Initial fitness: {fitness_history[0]:.4f}')
print(f'Final fitness:   {fitness_history[-1]:.4f}')
print(f'Change: +{(fitness_history[-1]/fitness_history[0]-1)*100:.1f}%')
print()
print(f'Initial extraction: {extraction_history[0]:.4f}')
print(f'Final extraction:   {extraction_history[-1]:.4f}')
print()
print(f'Initial metabolic: {metabolic_history[0]:.4f}')
print(f'Final metabolic:   {metabolic_history[-1]:.4f}')
print()
print(f'Total births: {births}')
print(f'Total deaths: {deaths}')
print(f'Max generation: {max(gens) if gens else 0}')
