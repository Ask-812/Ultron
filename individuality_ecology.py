#!/usr/bin/env python3
"""
INDIVIDUALITY ACROSS ECOLOGIES

Test whether birth variation matters differently in order vs margin vs boundary.
"""

from ultron import create_ultron, tick
from ultron.environments import MixedEnvironment
import numpy as np
import json
from datetime import datetime

config_base = {
    'observation_dim': 8,
    'model_dim': 16,
    'initial_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.30,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
}

TICKS = 100000
N = 30

environments = [
    ('order', 0.80),
    ('margin', 0.55),
    ('boundary', 0.52),
    ('chaos', 0.40),
]

all_results = {}

for env_name, signal_ratio in environments:
    print(f'\n{"="*70}')
    print(f'TESTING: {env_name} (signal_ratio={signal_ratio})')
    print(f'{"="*70}')
    
    results = []
    
    for i in range(N):
        np.random.seed(i * 7)
        weight_scale = 0.1 * (1.0 + np.random.uniform(-0.02, 0.02))
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        state.model.weights *= weight_scale / 0.1
        
        dormancy_tick = None
        min_energy = 100.0
        
        for t in range(TICKS):
            if dormancy_tick is None and state.energy.current < 20:
                dormancy_tick = t
            min_energy = min(min_energy, state.energy.current)
            
            obs = env.get_input(t)
            state = tick(state, obs, config)
            
            if not state.is_alive:
                break
        
        results.append({
            'id': i,
            'weight_scale': weight_scale,
            'alive': state.is_alive,
            'final_energy': state.energy.current if state.is_alive else 0,
            'min_energy': min_energy,
            'dormancy_tick': dormancy_tick,
            'death_tick': t if not state.is_alive else None,
            'w_norm': np.linalg.norm(state.model.weights),
        })
        
        status = 'ALIVE' if state.is_alive else f'DIED@{t}'
        print(f'  [{i+1:2d}/{N}] {status}, E={results[-1]["final_energy"]:.1f}')
    
    alive = [r for r in results if r['alive']]
    dead = [r for r in results if not r['alive']]
    
    print(f'\n  Survival: {len(alive)}/{N}')
    if alive:
        energies = [r['final_energy'] for r in alive]
        print(f'  Energy: {np.mean(energies):.1f} ± {np.std(energies):.1f}')
        scales = [r['weight_scale'] for r in alive]
        if len(alive) > 2:
            corr = np.corrcoef(scales, energies)[0,1]
            print(f'  Correlation: {corr:.3f}')
    
    all_results[env_name] = {
        'signal_ratio': signal_ratio,
        'survival_rate': len(alive) / N,
        'results': results,
    }

# Save results
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
with open(f'history/individuality_ecology_{timestamp}.json', 'w') as f:
    json.dump(all_results, f, indent=2)

print(f'\n{"="*70}')
print('SUMMARY')
print(f'{"="*70}')
for env_name, data in all_results.items():
    alive = [r for r in data['results'] if r['alive']]
    if alive:
        energies = [r['final_energy'] for r in alive]
        cv = np.std(energies) / np.mean(energies) if np.mean(energies) > 0 else 0
        print(f'{env_name:10s}: {100*data["survival_rate"]:3.0f}% survive, CV={cv:.2f}')
    else:
        print(f'{env_name:10s}: 0% survive')
