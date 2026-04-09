"""Quick test: verify predation mechanics work."""
import sys, numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

CONFIG = dict(
    rows=10, cols=10, observation_dim=8, signal_dim=4, action_dim=4, env_dim=4,
    start_energy=100.0, energy_capacity=200.0, consumption_rate=1.0,
    extraction_factor=0.60, metabolic_cost=0.3,
    signal_noise=0.01, base_signal_ratio=0.55, spatial_gradient=0.15,
    signal_emission_strength=0.3, signal_hop_decay=0.9,
    division_energy_threshold=95.0, division_cost=40.0,
    signal_division_coupling=0.1, cell_mutation_rate=0.005,
    birth_trait_variation=0.02, energy_leak_rate=0.05,
    signal_energy_coupling=1.0, apoptosis_threshold=1.0, apoptosis_streak=500,
    phenotype_emission_coupling=2.0, phenotype_affinity_coupling=2.0,
    resource_depletion_rate=0.0, resource_regen_rate=0.0,
    migration_enabled=False,
    action_division_coupling=0.0, action_weight_scale=0.15,
    action_mutation_rate=0.03,
    death_imprint_strength=0.0, stigmergy_decay=0.995,
    stigmergy_sensing=0.0, stigmergy_avoidance=0.0,
    fragmentation_enabled=False,
    predation_enabled=True,
    predation_energy_ratio=1.5,
    predation_efficiency=0.5,
    predation_cooldown=3,
    predation_action_threshold=0.0,
)

np.random.seed(42)
t = Tissue(10, 10, CONFIG)

# Strong cell at (5,5) with high energy (lineage 1)
t.place_cell(5, 5)
t.grid[5][5].lineage_id = 1
t.grid[5][5].energy = 150.0

# Weak cell at (5,6) with low energy (lineage 2)
t.place_cell(5, 6)
t.grid[5][6].lineage_id = 2
t.grid[5][6].energy = 50.0

print(f"Before: A={t.grid[5][5].energy:.1f} B={t.grid[5][6].energy:.1f}")
print(f"  A/B ratio = {t.grid[5][5].energy / t.grid[5][6].energy:.2f}")

for i in range(20):
    t.step()
    a = t.grid[5][5]
    b = t.grid[5][6]
    a_e = a.energy if a and a.is_alive else 0
    b_alive = b is not None and b.is_alive
    print(f"  t={i+1}: A={a_e:.1f}, B={'alive' if b_alive else 'DEAD'}, "
          f"predation_kills={t.predation_kills}")
    if not b_alive:
        print(f"  -> PREDATION CONFIRMED at tick {i+1}!")
        break
else:
    print("  No predation occurred in 20 ticks")

print(f"\nTotal predation kills: {t.predation_kills}")
print(f"Total deaths: {t.total_deaths}")
