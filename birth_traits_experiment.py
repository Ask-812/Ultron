#!/usr/bin/env python3
"""
BIRTH TRAITS EXPERIMENT

Test how the new birth traits (extraction_efficiency, metabolic_rate, learning_capacity)
affect survival and equilibrium in different environments.
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
    'birth_trait_variation': 0.02,  # ±2% variation in each trait
}

TICKS = 150000
N = 40

print('BIRTH TRAITS EXPERIMENT')
print('=' * 70)
print(f'Variation: ±{100*config_base["birth_trait_variation"]:.0f}% per trait')
print(f'Traits: extraction_efficiency, metabolic_rate, learning_capacity')
print()

for env_name, signal_ratio in [('margin', 0.55), ('boundary', 0.52)]:
    print(f'\n--- {env_name.upper()} (signal_ratio={signal_ratio}) ---\n')
    
    results = []
    
    for i in range(N):
        np.random.seed(i * 47)
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        
        # Store birth traits
        traits = {
            'extraction': state.traits.extraction_efficiency,
            'metabolic': state.traits.metabolic_rate,
            'learning': state.traits.learning_capacity,
        }
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        results.append({
            'id': i,
            'traits': traits,
            'alive': state.is_alive,
            'final_energy': state.energy.current if state.is_alive else 0,
            'death_tick': t if not state.is_alive else None,
        })
        
        status = 'ALIVE' if state.is_alive else f'DIED@{t}'
        print(f'  [{i+1:2d}/{N}] ext={traits["extraction"]:.3f} met={traits["metabolic"]:.3f} → {status}, E={results[-1]["final_energy"]:.1f}')
    
    # Analysis
    alive = [r for r in results if r['alive']]
    dead = [r for r in results if not r['alive']]
    
    print(f'\n  Survival: {len(alive)}/{N} ({100*len(alive)/N:.0f}%)')
    
    if len(alive) >= 5:
        extractions = [r['traits']['extraction'] for r in alive]
        metabolics = [r['traits']['metabolic'] for r in alive]
        energies = [r['final_energy'] for r in alive]
        
        # Compute "fitness score" = extraction / metabolic
        fitness = [e / m for e, m in zip(extractions, metabolics)]
        
        corr_ext = np.corrcoef(extractions, energies)[0, 1]
        corr_met = np.corrcoef(metabolics, energies)[0, 1]
        corr_fit = np.corrcoef(fitness, energies)[0, 1]
        
        print(f'  Correlation (extraction vs energy): {corr_ext:.3f}')
        print(f'  Correlation (metabolic vs energy):  {corr_met:.3f}')
        print(f'  Correlation (fitness vs energy):    {corr_fit:.3f}')
        print(f'  Energy range: {min(energies):.1f} - {max(energies):.1f}')
    
    if dead:
        dead_ext = [r['traits']['extraction'] for r in dead]
        dead_met = [r['traits']['metabolic'] for r in dead]
        print(f'  Dead extraction mean: {np.mean(dead_ext):.4f}')
        print(f'  Dead metabolic mean:  {np.mean(dead_met):.4f}')
        if alive:
            alive_ext = [r['traits']['extraction'] for r in alive]
            alive_met = [r['traits']['metabolic'] for r in alive]
            print(f'  Alive extraction mean: {np.mean(alive_ext):.4f}')
            print(f'  Alive metabolic mean:  {np.mean(alive_met):.4f}')
