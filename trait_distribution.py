#!/usr/bin/env python3
"""
TRAIT DISTRIBUTION ANALYSIS

Track how trait distribution changes during evolution.
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

TICKS = 3000000  # 3M ticks for longer evolution
MAX_POP = 100
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 40
signal_ratio = 0.55

print('EXTENDED EVOLUTION: TRAIT DISTRIBUTION')
print('=' * 70)

np.random.seed(42)  # Original seed that worked well
env = MixedEnvironment(8, signal_ratio=signal_ratio)
population = [create_ultron(config) for _ in range(30)]

births = 0
deaths = 0
gens = [0] * len(population)

# Track snapshots
snapshots = []

for t in range(TICKS):
    if not population:
        print(f't={t}: EXTINCTION')
        break
    
    competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))
    obs = env.get_input(t)
    
    # Update
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
    
    # Snapshot every 500K
    if t % 500000 == 0 and population:
        ext = [p.traits.extraction_efficiency for p in population]
        met = [p.traits.metabolic_rate for p in population]
        fit = [e / m for e, m in zip(ext, met)]
        
        snapshot = {
            'time': t,
            'fitness': np.mean(fit),
            'fitness_std': np.std(fit),
            'extraction': np.mean(ext),
            'extraction_std': np.std(ext),
            'metabolic': np.mean(met),
            'metabolic_std': np.std(met),
            'pop': len(population),
            'births': births,
            'deaths': deaths,
            'gen': max(gens)
        }
        snapshots.append(snapshot)
        
        print(f"\nt={t//1000}K: pop={len(population)}, gen={max(gens)}")
        print(f"  Fitness: {np.mean(fit):.4f} ± {np.std(fit):.4f} [{min(fit):.4f} - {max(fit):.4f}]")
        print(f"  Extract: {np.mean(ext):.4f} ± {np.std(ext):.4f}")
        print(f"  Metab:   {np.mean(met):.4f} ± {np.std(met):.4f}")
        print(f"  Births: {births}, Deaths: {deaths}")

print()
print('=' * 70)
print('SUMMARY')
print('=' * 70)

if snapshots:
    print(f"\n{'Time':<10} {'Fitness':<12} {'Extraction':<12} {'Metabolic':<12} {'Gen'}")
    print('-' * 60)
    for s in snapshots:
        t_str = f"{s['time']//1000}K"
        print(f"{t_str:<10} {s['fitness']:.4f}±{s['fitness_std']:.3f}  {s['extraction']:.4f}±{s['extraction_std']:.3f}  {s['metabolic']:.4f}±{s['metabolic_std']:.3f}  {s['gen']}")
    
    print()
    initial = snapshots[0]
    final = snapshots[-1]
    print(f"Total change: fitness {initial['fitness']:.4f} → {final['fitness']:.4f} (+{(final['fitness']/initial['fitness']-1)*100:.1f}%)")
    print(f"Total births: {final['births']}")
    print(f"Total deaths: {final['deaths']}")
    print(f"Max generation: {final['gen']}")
