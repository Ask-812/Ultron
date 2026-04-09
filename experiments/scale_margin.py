#!/usr/bin/env python3
"""
SCALE EFFECT AT MARGIN

Where survival is common (0.55), does scale affect equilibrium?
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
signal_ratio = 0.55  # margin - most survive

scales = [0.06, 0.08, 0.10, 0.12, 0.14]
SAMPLES = 20

print('SCALE EFFECT AT MARGIN (signal_ratio=0.55)')
print('=' * 70)

for scale in scales:
    energies = []
    deaths = 0
    
    for i in range(SAMPLES):
        np.random.seed(i * 17)
        
        config = config_base.copy()
        env = MixedEnvironment(8, signal_ratio=signal_ratio)
        state = create_ultron(config)
        state.model.weights *= scale / 0.1
        
        for t in range(TICKS):
            obs = env.get_input(t)
            state = tick(state, obs, config)
            if not state.is_alive:
                break
        
        if state.is_alive:
            energies.append(state.energy.current)
        else:
            deaths += 1
    
    if energies:
        mean_e = np.mean(energies)
        std_e = np.std(energies)
        bar = '█' * int(mean_e / 2)
        print(f'scale={scale:.2f}: E={mean_e:5.1f} ± {std_e:4.1f} (died: {deaths}/{SAMPLES}) {bar}')
    else:
        print(f'scale={scale:.2f}: ALL DIED')
