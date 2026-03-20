"""Quick test of resource depletion."""
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
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.002,
    'resource_regen_rate': 0.0005,
}
t = Tissue(10, 10, config)
t.seed_full()
for tick in range(1000):
    t.step()
    if (tick + 1) % 200 == 0:
        s = t.snapshot()
        print(f"t={tick+1}: cells={s['cell_count']}, E={s['total_energy']:.0f}, "
              f"res_mean={s['resource_mean']:.3f}, res_min={s['resource_min']:.3f}")
