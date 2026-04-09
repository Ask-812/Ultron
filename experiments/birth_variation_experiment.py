#!/usr/bin/env python3
"""
BIRTH VARIATION EXPERIMENT

Tests whether tiny frozen variations at birth lead to different equilibria.
This is the precondition for evolution: individuality must matter.

Variation: initial weight scale ±2% (frozen at birth)
Environment: signal_ratio=0.55 (dormancy regime)
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
N_ULTRONS = 20
SIGNAL_RATIO = 0.55  # Dormancy regime

print('=' * 70)
print('BIRTH VARIATION EXPERIMENT')
print('=' * 70)
print(f'Environment: signal_ratio={SIGNAL_RATIO} (dormancy regime)')
print(f'Ticks: {TICKS:,}')
print(f'N: {N_ULTRONS}')
print()
print('Variation: initial weight scale ±2% (frozen at birth)')
print()

results = []

for i in range(N_ULTRONS):
    np.random.seed(i * 1000)  # Different seed per individual
    
    # Create Ultron
    state = create_ultron(config_base)
    
    # === BIRTH VARIATION ===
    # Tiny perturbation to initial weight scale: 0.98 to 1.02
    birth_scale = 1.0 + np.random.uniform(-0.02, 0.02)
    state.model.weights *= birth_scale
    # Freeze: this is the only change, forever
    
    # Create environment (same for all, different noise realization)
    np.random.seed(i)  # Reset for environment
    env = MixedEnvironment(8, signal_ratio=SIGNAL_RATIO)
    
    # Track trajectory
    energy_at = {}
    sample_ticks = [0, 10000, 50000, 100000, 150000, 200000]
    next_sample = 0
    
    time_to_dormancy = None  # First time energy < 20
    min_energy = 100.0
    
    for t in range(TICKS + 1):
        # Check dormancy threshold
        if time_to_dormancy is None and state.energy.current < 20:
            time_to_dormancy = t
        
        min_energy = min(min_energy, state.energy.current)
        
        if next_sample < len(sample_ticks) and t == sample_ticks[next_sample]:
            energy_at[t] = state.energy.current
            next_sample += 1
        
        if not state.is_alive:
            break
            
        obs = env.get_input(t)
        state = tick(state, obs, config_base)
    
    final_energy = state.energy.current if state.is_alive else 0
    final_w_norm = np.linalg.norm(state.model.weights)
    alive = state.is_alive
    
    results.append({
        'id': i,
        'birth_scale': birth_scale,
        'alive': alive,
        'final_energy': final_energy,
        'final_w_norm': final_w_norm,
        'time_to_dormancy': time_to_dormancy,
        'min_energy': min_energy,
        'energy_100k': energy_at.get(100000, 0),
        'energy_200k': energy_at.get(200000, 0),
    })

# Print results
print('ID | Scale  | Alive | Final E | Dorman | Min E  | E@100k | E@200k | W Norm')
print('-' * 78)
for r in results:
    status = 'YES' if r['alive'] else 'NO '
    dorman = f"{r['time_to_dormancy']:6,}" if r['time_to_dormancy'] else '   N/A'
    print(f"{r['id']:2d} | {r['birth_scale']:.4f} | {status}   | {r['final_energy']:6.1f} | {dorman} | {r['min_energy']:5.1f} | {r['energy_100k']:5.1f} | {r['energy_200k']:5.1f} | {r['final_w_norm']:.0f}")

# Summary statistics
alive_count = sum(1 for r in results if r['alive'])
alive_results = [r for r in results if r['alive']]
dead_results = [r for r in results if not r['alive']]

print()
print('=' * 70)
print('SUMMARY')
print('=' * 70)
print(f'Survival: {alive_count}/{N_ULTRONS}')

if alive_results:
    energies = [r['final_energy'] for r in alive_results]
    w_norms = [r['final_w_norm'] for r in alive_results]
    dormancy_times = [r['time_to_dormancy'] for r in alive_results if r['time_to_dormancy']]
    
    print()
    print('SURVIVORS:')
    print(f'  Final energy range: {min(energies):.1f} - {max(energies):.1f}')
    print(f'  Final energy mean:  {np.mean(energies):.1f} ± {np.std(energies):.1f}')
    print(f'  Structure range:    {min(w_norms):.0f} - {max(w_norms):.0f}')
    if dormancy_times:
        print(f'  Dormancy time range: {min(dormancy_times):,} - {max(dormancy_times):,}')

if dead_results:
    birth_scales_dead = [r['birth_scale'] for r in dead_results]
    birth_scales_alive = [r['birth_scale'] for r in alive_results]
    print()
    print('DEATHS:')
    print(f'  Count: {len(dead_results)}')
    print(f'  Birth scales (dead):  {[f"{s:.4f}" for s in birth_scales_dead]}')
    if alive_results:
        print(f'  Birth scales (alive): mean={np.mean(birth_scales_alive):.4f}')

# Correlation analysis
if alive_results:
    print()
    print('=' * 70)
    print('CORRELATION ANALYSIS')
    print('=' * 70)
    
    scales = np.array([r['birth_scale'] for r in alive_results])
    energies = np.array([r['final_energy'] for r in alive_results])
    w_norms = np.array([r['final_w_norm'] for r in alive_results])
    
    if len(scales) > 2:
        corr_scale_energy = np.corrcoef(scales, energies)[0, 1]
        corr_scale_structure = np.corrcoef(scales, w_norms)[0, 1]
        
        print(f'Correlation (birth_scale vs final_energy):  {corr_scale_energy:+.3f}')
        print(f'Correlation (birth_scale vs structure):     {corr_scale_structure:+.3f}')

print()
print('=' * 70)
print('INTERPRETATION')
print('=' * 70)
print()

# Check for meaningful variation
if alive_results:
    energies = [r['final_energy'] for r in alive_results]
    energy_range = max(energies) - min(energies)
    energy_cv = np.std(energies) / np.mean(energies) if np.mean(energies) > 0 else 0
    
    if energy_cv > 0.2:
        print('HIGH VARIATION in final energy (CV > 20%)')
        print('-> Birth differences lead to different equilibria')
        print('-> Individuality is meaningful')
    elif energy_cv > 0.1:
        print('MODERATE VARIATION in final energy (CV 10-20%)')
        print('-> Some individual differences persist')
    else:
        print('LOW VARIATION in final energy (CV < 10%)')
        print('-> All individuals converge to similar equilibrium')
        print('-> Dormancy is a single attractor')
