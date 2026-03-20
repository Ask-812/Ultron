"""Debug: verify tissue still works after v0.6.0 changes."""
import numpy as np
from ultron.tissue import Tissue

config = {
    'observation_dim': 12,
    'env_dim': 8,
    'signal_dim': 4,
    'action_dim': 0,
    'starting_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 1.0,
    'extraction_factor': 0.5,
    'environmental_richness': 1.0,
    'signal_ratio': 0.6,
    'signal_decay': 0.5,
    'signal_emission_strength': 0.3,
    'signal_propagation_hops': 3,
    'division_energy_threshold': 130.0,
    'signal_division_coupling': 0.1,
    'apoptosis_threshold': 5.0,
    'apoptosis_streak': 500,
    'observation_noise': 0.01,
    'learning_rate': 0.01,
    'update_cost_factor': 0.1,
    'energy_share_fraction': 0.05,
    'division_cost': 0.0,
    'cell_mutation_rate': 0.005,
    'birth_trait_variation': 0.02,
}

# Test 1: single seed on 10x10
np.random.seed(42)
t = Tissue(10, 10, config)
t.seed_center(1)
for i in range(100):
    t.step()
    if i % 20 == 0:
        s = t.snapshot()
        print(f"t={i}: cells={s['cell_count']}, energy={s['total_energy']:.0f}")
        if s['cell_count'] == 0:
            print("  All dead!")
            break

# Test 2: 3x3 seed on 10x10
print("\n--- 3x3 seed ---")
np.random.seed(42)
t2 = Tissue(10, 10, config)
for dr in range(-1, 2):
    for dc in range(-1, 2):
        t2.place_cell(5 + dr, 5 + dc)
for i in range(500):
    t2.step()
    if i % 100 == 0:
        s = t2.snapshot()
        print(f"t={i}: cells={s['cell_count']}, energy={s['total_energy']:.0f}")

# Test 3: check model weight shape
print(f"\nModel weight shape: {t2.grid[5][5].state.model.weights.shape if t2.grid[5][5] else 'dead'}")

# Test 4: same with action_dim=4
print("\n--- action_dim=4, 3x3 seed ---")
config4 = dict(config)
config4['action_dim'] = 4
np.random.seed(42)
t3 = Tissue(10, 10, config4)
for dr in range(-1, 2):
    for dc in range(-1, 2):
        t3.place_cell(5 + dr, 5 + dc)
for i in range(500):
    t3.step()
    if i % 100 == 0:
        s = t3.snapshot()
        print(f"t={i}: cells={s['cell_count']}, energy={s['total_energy']:.0f}")

# Check action outputs
for r in range(t3.rows):
    for c in range(t3.cols):
        cell = t3.grid[r][c]
        if cell and cell.is_alive and cell.action is not None:
            print(f"\nCell at ({r},{c}) action: {cell.action}")
            print(f"Weight shape: {cell.state.model.weights.shape}")
            break
    else:
        continue
    break
