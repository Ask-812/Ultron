#!/usr/bin/env python3
"""
METABOLIC EFFICIENCY VARIATION

Birth variation: extraction_factor varies ±5%
This cannot normalize away—it's a permanent metabolic trait.
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
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
}

TICKS = 150000
signal_ratio = 0.55

# Variation: ±5% extraction efficiency
BASE_EXTRACTION = 0.30
VARIATION = 0.05
SAMPLES = 30

print('METABOLIC EFFICIENCY VARIATION')
print('=' * 70)
print(f'Base extraction: {BASE_EXTRACTION}')
print(f'Variation: ±{100*VARIATION:.0f}%')
print()

results = []

for i in range(SAMPLES):
    np.random.seed(i * 31)
    
    # Birth variation: extraction efficiency
    extraction_factor = BASE_EXTRACTION * (1.0 + np.random.uniform(-VARIATION, VARIATION))
    
    config = config_base.copy()
    config['extraction_factor'] = extraction_factor
    
    env = MixedEnvironment(8, signal_ratio=signal_ratio)
    state = create_ultron(config)
    
    for t in range(TICKS):
        obs = env.get_input(t)
        state = tick(state, obs, config)
        if not state.is_alive:
            break
    
    results.append({
        'id': i,
        'extraction': extraction_factor,
        'alive': state.is_alive,
        'final_energy': state.energy.current if state.is_alive else 0,
        'death_tick': t if not state.is_alive else None,
    })
    
    status = 'ALIVE' if state.is_alive else f'DIED@{t}'
    print(f'  [{i+1:2d}/{SAMPLES}] extraction={extraction_factor:.4f} → {status}, E={results[-1]["final_energy"]:.1f}')

# Analysis
alive = [r for r in results if r['alive']]
dead = [r for r in results if not r['alive']]

print()
print('=' * 70)
print('ANALYSIS')
print()

print(f'Survival: {len(alive)}/{SAMPLES}')

if len(alive) > 2:
    extractions = [r['extraction'] for r in alive]
    energies = [r['final_energy'] for r in alive]
    corr = np.corrcoef(extractions, energies)[0, 1]
    print(f'Correlation (extraction vs energy): {corr:.3f}')
    print(f'Survivor extraction range: {min(extractions):.4f} - {max(extractions):.4f}')
    print(f'Energy range: {min(energies):.1f} - {max(energies):.1f}')

if dead:
    dead_extractions = [r['extraction'] for r in dead]
    print(f'Dead extraction range: {min(dead_extractions):.4f} - {max(dead_extractions):.4f}')
