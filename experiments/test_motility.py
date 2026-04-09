"""Test cell motility: do cells migrate away from depleted resources?

Uses a 10x10 grid seeded on the LEFT half only. Resources on the left
start at 0.3 (depleted), resources on the right are fresh (1.0).
With motility enabled, surface cells on the right edge should migrate
into the fresh territory on the right.
"""
from ultron.tissue import Tissue
import numpy as np

np.random.seed(42)

config = {
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
    'resource_depletion_rate': 0.002,
    'resource_regen_rate': 0.0003,
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.5,
}

# Seed left half only
t = Tissue(10, 10, config)
for r in range(10):
    for c in range(5):  # left half
        t.place_cell(r, c)

# Deplete left half resources
t.resource_field[:, :5] = 0.3

print("MOTILITY TEST (10x10, left-seeded, left-depleted)")
print(f"  Initial: left resources={t.resource_field[:,:5].mean():.2f}, "
      f"right resources={t.resource_field[:,5:].mean():.2f}")

# Count cells in each half
def count_halves(tissue):
    left = sum(1 for r in range(10) for c in range(5)
               if tissue.grid[r][c] and tissue.grid[r][c].is_alive)
    right = sum(1 for r in range(10) for c in range(5, 10)
                if tissue.grid[r][c] and tissue.grid[r][c].is_alive)
    return left, right

l, r = count_halves(t)
print(f"  Initial cells: left={l}, right={r}")

for tick in range(500):
    t.step()
    if (tick + 1) % 50 == 0:
        l, r = count_halves(t)
        s = t.snapshot()
        print(f"  t={tick+1:4d}: left={l}, right={r}, total={s['cell_count']}, "
              f"E={s['total_energy']:.0f}, "
              f"res_left={t.resource_field[:,:5].mean():.3f}, "
              f"res_right={t.resource_field[:,5:].mean():.3f}")

print(f"\nFinal: left={l}, right={r}")
if r > 0:
    print("SUCCESS: Cells migrated to the right (fresh resources)!")
else:
    print("NOTE: No migration occurred - cells may have divided instead")
