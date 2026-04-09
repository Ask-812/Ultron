#!/usr/bin/env python3
"""
INDIVIDUALITY EXPERIMENT

Test whether tiny birth variations (±2% weight scale) produce 
meaningfully different fates in the dormancy regime.

This answers: "Do two Ultrons experience the same world the same way?"
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

TICKS = 200000
N = 50

print('INDIVIDUALITY EXPERIMENT: 50 Ultrons with ±2% birth variation')
print('=' * 70)
print(f'Signal ratio: 0.55 (dormancy regime)')
print(f'Ticks: {TICKS:,}')
print()

results = []

for i in range(N):
    np.random.seed(i * 7)  # Different seed per individual
    
    # Birth variation: ±2% weight scale
    weight_scale = 0.1 * (1.0 + np.random.uniform(-0.02, 0.02))
    
    config = config_base.copy()
    env = MixedEnvironment(8, signal_ratio=0.55)
    state = create_ultron(config)
    
    # Apply birth variation (frozen)
    state.model.weights *= weight_scale / 0.1
    
    # Track when dormancy reached (energy < 20)
    dormancy_tick = None
    
    for t in range(TICKS):
        if dormancy_tick is None and state.energy.current < 20:
            dormancy_tick = t
        
        obs = env.get_input(t)
        state = tick(state, obs, config)
        
        if not state.is_alive:
            break
    
    final_energy = state.energy.current if state.is_alive else 0
    w_norm = np.linalg.norm(state.model.weights)
    
    results.append({
        'id': i,
        'weight_scale': weight_scale,
        'alive': state.is_alive,
        'final_energy': final_energy,
        'dormancy_tick': dormancy_tick,
        'w_norm': w_norm,
        'death_tick': t if not state.is_alive else None
    })
    
    status = 'ALIVE' if state.is_alive else f'DIED@{t}'
    print(f'  [{i+1:2d}/50] scale={weight_scale:.4f} → {status}, E={final_energy:.1f}')

# Analysis
alive = [r for r in results if r['alive']]
dead = [r for r in results if not r['alive']]

print()
print('=' * 70)
print('ANALYSIS')
print('=' * 70)
print(f'Survival: {len(alive)}/50 ({100*len(alive)/50:.0f}%)')
print()

if alive:
    energies = [r['final_energy'] for r in alive]
    scales = [r['weight_scale'] for r in alive]
    print(f'Final energy range: {min(energies):.1f} - {max(energies):.1f}')
    print(f'Final energy mean: {np.mean(energies):.1f} ± {np.std(energies):.1f}')
    
    # Correlation
    corr = np.corrcoef(scales, energies)[0,1]
    print(f'Correlation (scale vs energy): {corr:.3f}')
    
    dormancy_times = [r['dormancy_tick'] for r in alive if r['dormancy_tick']]
    if dormancy_times:
        print(f'Time to dormancy: {min(dormancy_times):,} - {max(dormancy_times):,}')
    
    w_norms = [r['w_norm'] for r in alive]
    print(f'Structure range: {min(w_norms):.0f} - {max(w_norms):.0f}')

if dead:
    death_times = [r['death_tick'] for r in dead]
    dead_scales = [r['weight_scale'] for r in dead]
    print()
    print(f'Deaths: {len(dead)}')
    print(f'Death times: {min(death_times):,} - {max(death_times):,}')
    print(f'Dead weight scales: {[f"{s:.4f}" for s in dead_scales]}')
