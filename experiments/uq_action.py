"""Ultra-quick action test: 8x8 grid, 500 ticks, 1 seed."""
import numpy as np, time
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
for name, ov in [('NoAct', {'action_dim': 0}),
                  ('ActOFF', {'action_dim': 4, 'action_division_coupling': 0.0}),
                  ('ActON', {'action_dim': 4, 'action_division_coupling': 1.0})]:
    np.random.seed(42)
    cfg = {**BASE, **ov}
    t = Tissue(8, 8, cfg)
    t.seed_full()
    t0 = time.time()
    for tick in range(500):
        t.step()
    dt = time.time() - t0
    s = t.snapshot()
    print(f"{name:8s}: cells={s['cell_count']:3d}  births={t.total_births:3d}  ({dt:.1f}s)")
