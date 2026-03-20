"""Test v0.6.0 action coupling with known-working config."""
import numpy as np
from ultron.tissue import Tissue

BASE = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.60,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 140.0, 'division_cost': 30.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 500,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
}

# Test 1: without actions (should match previous behavior)
print("=== action_dim=0 (control) ===")
np.random.seed(42)
cfg0 = {**BASE, 'action_dim': 0}
t0 = Tissue(15, 15, cfg0)
t0.seed_full()
for i in range(1000):
    t0.step()
s = t0.snapshot()
print(f"t=1000: cells={s['cell_count']}, energy={s['total_energy']:.0f}")

# Test 2: with actions, coupling OFF
print("\n=== action_dim=4, coupling=0.0 ===")
np.random.seed(42)
cfg1 = {**BASE, 'action_dim': 4, 'action_division_coupling': 0.0}
t1 = Tissue(15, 15, cfg1)
t1.seed_full()
for i in range(1000):
    t1.step()
s1 = t1.snapshot()
print(f"t=1000: cells={s1['cell_count']}, energy={s1['total_energy']:.0f}")

# Check action outputs
action_count = 0
for r in range(t1.rows):
    for c in range(t1.cols):
        cell = t1.grid[r][c]
        if cell and cell.is_alive and cell.action is not None:
            action_count += 1
print(f"Cells with actions: {action_count}")

# Show one cell's action and weight shape
for r in range(t1.rows):
    for c in range(t1.cols):
        cell = t1.grid[r][c]
        if cell and cell.is_alive:
            print(f"Weight shape: {cell.state.model.weights.shape} (expect 16x12)")
            if cell.action is not None:
                print(f"Action: {cell.action}")
            break
    else:
        continue
    break

# Test 3: with actions, coupling ON
print("\n=== action_dim=4, coupling=1.0 ===")
np.random.seed(42)
cfg2 = {**BASE, 'action_dim': 4, 'action_division_coupling': 1.0}
t2 = Tissue(15, 15, cfg2)
t2.seed_full()
for i in range(1000):
    t2.step()
s2 = t2.snapshot()
print(f"t=1000: cells={s2['cell_count']}, energy={s2['total_energy']:.0f}")

# Check action weight inheritance
print("\n=== Action inheritance test ===")
np.random.seed(42)
cfg3 = {**BASE, 'action_dim': 4, 'action_division_coupling': 0.5}
t3 = Tissue(10, 10, cfg3)
t3.seed_full()
# Get founder action weights
founder = t3.grid[5][5]
founder_aw = founder.state.model.weights[12:, :].copy()
founder_id = founder.cell_id
# Run a while
for i in range(500):
    t3.step()
# Find a descendant (cell_id > max initial id)
max_init_id = 100
for r in range(t3.rows):
    for c in range(t3.cols):
        cell = t3.grid[r][c]
        if cell and cell.is_alive and cell.cell_id > max_init_id:
            diff = np.linalg.norm(cell.state.model.weights[12:, :] - founder_aw)
            print(f"Descendant {cell.cell_id} action weight diff from founder: {diff:.4f}")
            break
    else:
        continue
    break

print("\nAll tests complete.")
