"""Quick test: verify action coupling works end-to-end."""
import numpy as np
from ultron.tissue import Tissue

config = {
    'observation_dim': 12,
    'env_dim': 8,
    'signal_dim': 4,
    'action_dim': 4,  # 4 action channels: up, down, left, right
    'action_division_coupling': 1.0,  # enable directed division
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

np.random.seed(42)
t = Tissue(10, 10, config)
t.seed_center(1)

# Run 500 ticks
for i in range(500):
    t.step()

s = t.snapshot()
print(f"Cells: {s['cell_count']}, Energy: {s['total_energy']:.0f}")

# Check that cells have action outputs
action_count = 0
action_sum = np.zeros(4)
for r in range(t.rows):
    for c in range(t.cols):
        cell = t.grid[r][c]
        if cell is not None and cell.is_alive and cell.action is not None:
            action_count += 1
            action_sum += cell.action

if action_count > 0:
    print(f"Cells with actions: {action_count}")
    print(f"Mean action: {action_sum / action_count}")
else:
    print("ERROR: No cells have action outputs!")

# Check model weight shape
cell = None
for r in range(t.rows):
    for c in range(t.cols):
        if t.grid[r][c] is not None and t.grid[r][c].is_alive:
            cell = t.grid[r][c]
            break
    if cell:
        break

print(f"Weight shape: {cell.state.model.weights.shape} (expected 16x12)")

# Verify action weights are inherited: seed a new organism, let it divide
# and check parent vs child action weights
np.random.seed(99)
t2 = Tissue(5, 5, config)
t2.place_cell(2, 2)
founder = t2.grid[2][2]
founder_action_weights = founder.state.model.weights[12:, :].copy()
print(f"\nFounder action weights norm: {np.linalg.norm(founder_action_weights):.4f}")

# Run until first division
for i in range(2000):
    t2.step()
    if t2.total_births > 0:
        break

if t2.total_births > 0:
    print(f"Division happened at tick {i+1}")
    # Find the child
    for r in range(t2.rows):
        for c in range(t2.cols):
            child = t2.grid[r][c]
            if child is not None and child.is_alive and child.cell_id > 0:
                child_action_weights = child.state.model.weights[12:, :].copy()
                diff = np.linalg.norm(child_action_weights - founder_action_weights)
                print(f"Child action weights diff from founder: {diff:.4f} (should be small, ~mutation)")
                break
else:
    print("No division in 2000 ticks (try longer)")

print("\nAction coupling test PASSED" if action_count > 0 else "\nAction coupling test FAILED")
