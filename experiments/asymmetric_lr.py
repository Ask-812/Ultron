#!/usr/bin/env python3
"""
ASYMMETRIC LEARNING RATE VARIATION

Birth variation: each dimension learns at slightly different rate.
This is structural asymmetry that can't normalize away.
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

TICKS = 150000
signal_ratio = 0.55

# Variation: ±10% per-dimension learning rate multiplier
VARIATION = 0.10
SAMPLES = 30

print('ASYMMETRIC LEARNING RATE VARIATION')
print('=' * 70)
print(f'Variation: ±{100*VARIATION:.0f}% per dimension')
print(f'Signal ratio: {signal_ratio}')
print()

results = []

for i in range(SAMPLES):
    np.random.seed(i * 23)
    
    # Birth variation: per-dimension learning multiplier
    dim = config_base['observation_dim']
    lr_multipliers = 1.0 + np.random.uniform(-VARIATION, VARIATION, dim)
    
    # Create state
    config = config_base.copy()
    env = MixedEnvironment(8, signal_ratio=signal_ratio)
    state = create_ultron(config)
    
    # Store multipliers in state for use during updates
    # (We'll need to modify tick to use these, so for now just track theoretically)
    
    # Track trajectory
    energy_samples = []
    
    for t in range(TICKS):
        if t % 10000 == 0:
            energy_samples.append(state.energy.current)
        
        obs = env.get_input(t)
        state = tick(state, obs, config)
        if not state.is_alive:
            break
    
    # Compute variance of multipliers as "asymmetry score"
    asymmetry = np.std(lr_multipliers)
    
    results.append({
        'id': i,
        'asymmetry': asymmetry,
        'alive': state.is_alive,
        'final_energy': state.energy.current if state.is_alive else 0,
        'multipliers': lr_multipliers,
    })
    
    status = 'ALIVE' if state.is_alive else 'DIED'
    print(f'  [{i+1:2d}/{SAMPLES}] asymmetry={asymmetry:.3f} → {status}, E={results[-1]["final_energy"]:.1f}')

# Analysis
alive = [r for r in results if r['alive']]
energies = [r['final_energy'] for r in alive]
asymmetries = [r['asymmetry'] for r in alive]

print()
print('=' * 70)
print('ANALYSIS')
print()
if len(alive) > 2:
    corr = np.corrcoef(asymmetries, energies)[0, 1]
    print(f'Correlation (asymmetry vs energy): {corr:.3f}')
print(f'Energy range: {min(energies):.1f} - {max(energies):.1f}')
print(f'Asymmetry range: {min(asymmetries):.3f} - {max(asymmetries):.3f}')
