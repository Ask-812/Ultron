"""Quick resource depletion comparison: 2000 ticks, 15x15."""
from ultron.tissue import Tissue
import numpy as np

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

CONDITIONS = [
    ('No depletion', 0.0, 0.0),
    ('Mild',         0.001, 0.0005),
    ('Harsh',        0.003, 0.0003),
]

for name, depl, regen in CONDITIONS:
    np.random.seed(42)
    cfg = {**BASE, 'resource_depletion_rate': depl, 'resource_regen_rate': regen}
    t = Tissue(15, 15, cfg)
    t.seed_full()
    for tick in range(2000):
        t.step()
    s = t.snapshot()
    print(f"{name:15s}: cells={s['cell_count']:3d}  E={s['total_energy']:7.0f}  "
          f"res={s.get('resource_mean',1):.3f}/{s.get('resource_min',1):.3f}  "
          f"div={s.get('phenotype_diversity',0):.4f}  mag={s.get('phenotype_mean_mag',0):.3f}")
