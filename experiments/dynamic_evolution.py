#!/usr/bin/env python3
"""
DYNAMIC ENVIRONMENT EVOLUTION

Add environmental fluctuation to break evolutionary plateaus.
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

TICKS = 3000000
MAX_POP = 100
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 40
# Fluctuating signal ratio
BASE_SIGNAL = 0.55
SIGNAL_AMPLITUDE = 0.1  # ±0.1 fluctuation
SEASON_LENGTH = 100000  # Fluctuation period

print('DYNAMIC ENVIRONMENT EVOLUTION')
print('=' * 70)
print(f'Signal: {BASE_SIGNAL} ± {SIGNAL_AMPLITUDE}')
print(f'Season length: {SEASON_LENGTH}')
print()

np.random.seed(42)
population = [create_ultron(config) for _ in range(30)]

births = 0
deaths = 0
gens = [0] * len(population)

for t in range(TICKS):
    if not population:
        print(f't={t}: EXTINCTION')
        break
    
    # Fluctuating signal ratio
    phase = (t % SEASON_LENGTH) / SEASON_LENGTH * 2 * np.pi
    signal_ratio = BASE_SIGNAL + SIGNAL_AMPLITUDE * np.sin(phase)
    env = MixedEnvironment(8, signal_ratio=signal_ratio)
    
    competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))
    obs = env.get_input(t)
    
    for i in range(len(population)):
        if population[i].is_alive:
            comp_config = config.copy()
            comp_config['extraction_factor'] = config['extraction_factor'] * competition
            population[i] = tick(population[i], obs, comp_config)
    
    # Remove dead
    alive = []
    new_gens = []
    for i, p in enumerate(population):
        if p.is_alive:
            alive.append(p)
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
    
    if t % 500000 == 0:
        fit = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])
        print(f"t={t//1000}K: pop={len(population)}, fit={fit:.4f}, b={births}, d={deaths}, gen={max(gens)}")

print()
print('=' * 70)
print('RESULTS')
print('=' * 70)

if population:
    fit = np.mean([p.traits.extraction_efficiency / p.traits.metabolic_rate for p in population])
    ext = np.mean([p.traits.extraction_efficiency for p in population])
    met = np.mean([p.traits.metabolic_rate for p in population])
    
    print(f'Final fitness: {fit:.4f}')
    print(f'Extraction: {ext:.4f}')
    print(f'Metabolic: {met:.4f}')
    print(f'Total births: {births}')
    print(f'Total deaths: {deaths}')
    print(f'Max generation: {max(gens)}')
