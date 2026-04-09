"""Minimal action coupling test."""
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
    'action_dim': 4,
    'action_division_coupling': 1.0,
}

# Tiny test: 5x5, seed 4 cells
np.random.seed(42)
t = Tissue(5, 5, BASE)
for dr in range(-1, 1):
    for dc in range(-1, 1):
        t.place_cell(2 + dr, 2 + dc)

print(f"Initial cells: {t.cell_count}")
cell = t.grid[2][2]
print(f"Weight shape: {cell.state.model.weights.shape}")

for i in range(100):
    t.step()
    if i % 20 == 0:
        s = t.snapshot()
        # Check actions
        act_cells = 0
        for r in range(t.rows):
            for c in range(t.cols):
                cl = t.grid[r][c]
                if cl and cl.is_alive and cl.action is not None:
                    act_cells += 1
        print(f"t={i}: cells={s['cell_count']}, energy={s['total_energy']:.0f}, action_cells={act_cells}")

# Show final actions
print("\nFinal cell actions:")
for r in range(t.rows):
    for c in range(t.cols):
        cl = t.grid[r][c]
        if cl and cl.is_alive:
            act_str = f"[{','.join(f'{a:.2f}' for a in cl.action)}]" if cl.action is not None else "None"
            print(f"  ({r},{c}): action={act_str}")
