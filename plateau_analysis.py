#!/usr/bin/env python3
"""
PLATEAU ANALYSIS

Why does evolution plateau? Analyze energy dynamics at equilibrium.
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

MAX_POP = 100
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 40
signal_ratio = 0.55

print('PLATEAU ANALYSIS')
print('=' * 70)

# First evolve to plateau
np.random.seed(42)
env = MixedEnvironment(8, signal_ratio=signal_ratio)
population = [create_ultron(config) for _ in range(30)]

# Evolve for 2M ticks
for t in range(2000000):
    if not population:
        break
    
    competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))
    obs = env.get_input(t)
    
    for i in range(len(population)):
        if population[i].is_alive:
            comp_config = config.copy()
            comp_config['extraction_factor'] = config['extraction_factor'] * competition
            population[i] = tick(population[i], obs, comp_config)
    
    # Remove dead
    population = [p for p in population if p.is_alive]
    
    # Reproduction
    n = len(population)
    for i in range(n):
        if population[i].energy.current >= REPRODUCTION_THRESHOLD and len(population) < MAX_POP:
            parent, child = reproduce(population[i], config)
            if child:
                population.append(child)

print(f'Population at plateau: {len(population)}')

# Now analyze the system
print()
print('ENERGY ANALYSIS')
print('=' * 70)

energies = [p.energy.current for p in population]
fitness = [p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population]

print(f'Energy: {np.mean(energies):.1f} ± {np.std(energies):.1f} [{min(energies):.1f} - {max(energies):.1f}]')
print(f'Fitness: {np.mean(fitness):.4f} ± {np.std(fitness):.4f}')
print()
print(f'Reproduction threshold: {REPRODUCTION_THRESHOLD}')
print(f'Max energy: {max(energies):.1f}')
print(f'Gap to reproduction: {REPRODUCTION_THRESHOLD - max(energies):.1f}')
print()
print(f'Population: {len(population)}')
print(f'Carrying capacity: {CARRYING_CAPACITY}')
print(f'Competition factor: {min(1.0, CARRYING_CAPACITY / len(population)):.3f}')
print()

# Test: what if we lower carrying capacity to force more competition?
print('=' * 70)
print('SIMULATION: What if carrying capacity were lower?')
print()

for cc in [40, 35, 30, 25, 20]:
    comp = min(1.0, cc / len(population))
    effective_extraction = config['extraction_factor'] * comp
    print(f'CC={cc}: competition={comp:.3f}, effective_extraction={effective_extraction:.4f}')
