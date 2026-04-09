#!/usr/bin/env python3
"""
SURVIVOR ANALYSIS

What makes rare boundary survivors survive?
Track detailed trajectories for survivors vs deaths.
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
}

TICKS = 100000
signal_ratio = 0.52  # boundary

# Find survivors and non-survivors
print('SEARCHING FOR SURVIVORS AT BOUNDARY (signal_ratio=0.52)')
print('=' * 70)

survivors = []
deaths = []

for i in range(100):
    np.random.seed(i * 7)
    weight_scale = 0.1 * (1.0 + np.random.uniform(-0.02, 0.02))
    
    config = config_base.copy()
    env = MixedEnvironment(8, signal_ratio=signal_ratio)
    state = create_ultron(config)
    state.model.weights *= weight_scale / 0.1
    
    # Track trajectory
    energy_trajectory = []
    error_trajectory = []
    
    for t in range(TICKS):
        if t % 5000 == 0:
            energy_trajectory.append(state.energy.current)
            err = np.linalg.norm(state.current.error) if state.current.error is not None else 0
            error_trajectory.append(err)
        
        obs = env.get_input(t)
        state = tick(state, obs, config)
        
        if not state.is_alive:
            break
    
    result = {
        'id': i,
        'weight_scale': weight_scale,
        'alive': state.is_alive,
        'death_tick': t if not state.is_alive else None,
        'energy_trajectory': energy_trajectory,
        'error_trajectory': error_trajectory,
        'final_energy': state.energy.current if state.is_alive else 0,
    }
    
    if state.is_alive:
        survivors.append(result)
        print(f'  SURVIVOR #{len(survivors)}: id={i}, scale={weight_scale:.4f}, E={state.energy.current:.1f}')
    else:
        deaths.append(result)

print()
print(f'Found {len(survivors)} survivors out of 100')
print()

if survivors:
    print('ANALYZING SURVIVOR TRAJECTORIES')
    print('=' * 70)
    
    for s in survivors[:5]:  # Show up to 5 survivors
        print(f'\nSurvivor {s["id"]} (scale={s["weight_scale"]:.4f}):')
        print(f'  Energy trajectory: {[f"{e:.1f}" for e in s["energy_trajectory"][:10]]}')
        print(f'  Error trajectory:  {[f"{e:.2f}" for e in s["error_trajectory"][:10]]}')
        print(f'  Final energy: {s["final_energy"]:.1f}')
    
    # Compare early energy between survivors and sample of deaths
    print()
    print('EARLY ENERGY COMPARISON (tick 5000)')
    print('-' * 40)
    
    survivor_early = [s['energy_trajectory'][1] if len(s['energy_trajectory']) > 1 else s['energy_trajectory'][0] for s in survivors]
    death_early = [d['energy_trajectory'][1] if len(d['energy_trajectory']) > 1 else d['energy_trajectory'][0] for d in deaths[:50]]
    
    print(f'Survivors at t=5000: {np.mean(survivor_early):.1f} ± {np.std(survivor_early):.1f}')
    print(f'Deaths at t=5000:    {np.mean(death_early):.1f} ± {np.std(death_early):.1f}')
    
    # Compare early error
    print()
    print('EARLY ERROR COMPARISON (tick 5000)')
    print('-' * 40)
    
    survivor_err = [s['error_trajectory'][1] if len(s['error_trajectory']) > 1 else 0 for s in survivors]
    death_err = [d['error_trajectory'][1] if len(d['error_trajectory']) > 1 else 0 for d in deaths[:50]]
    
    print(f'Survivors error at t=5000: {np.mean(survivor_err):.2f} ± {np.std(survivor_err):.2f}')
    print(f'Deaths error at t=5000:    {np.mean(death_err):.2f} ± {np.std(death_err):.2f}')
    
    # Weight scale comparison
    print()
    print('WEIGHT SCALE COMPARISON')
    print('-' * 40)
    
    survivor_scales = [s['weight_scale'] for s in survivors]
    death_scales = [d['weight_scale'] for d in deaths]
    
    print(f'Survivor scales: {np.mean(survivor_scales):.4f} ± {np.std(survivor_scales):.4f}')
    print(f'Death scales:    {np.mean(death_scales):.4f} ± {np.std(death_scales):.4f}')
