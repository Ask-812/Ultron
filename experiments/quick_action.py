"""Action Coupling: Quick comparison."""
import numpy as np
import time
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

CONDITIONS = [
    ('No actions', {'action_dim': 0}),
    ('Actions OFF', {'action_dim': 4, 'action_division_coupling': 0.0}),
    ('Actions ON', {'action_dim': 4, 'action_division_coupling': 1.0}),
    ('Actions STRONG', {'action_dim': 4, 'action_division_coupling': 3.0}),
]

SIZE = 10
TICKS = 1000

print(f"Grid: {SIZE}x{SIZE}, Ticks: {TICKS}")
print("=" * 70)

for name, overrides in CONDITIONS:
    np.random.seed(42)
    cfg = {**BASE, **overrides}
    t = Tissue(SIZE, SIZE, cfg)
    t.seed_full()
    t0 = time.time()
    for tick in range(TICKS):
        t.step()
    dt = time.time() - t0
    s = t.snapshot()
    print(f"{name:16s}: cells={s['cell_count']:3d}  energy={s['total_energy']:7.0f}  "
          f"births={t.total_births:3d}  deaths={t.total_deaths:3d}  ({dt:.1f}s)")

# Action evolution analysis
print("\nAction evolution over time (coupling=1.0):")
np.random.seed(42)
cfg = {**BASE, 'action_dim': 4, 'action_division_coupling': 1.0}
t = Tissue(SIZE, SIZE, cfg)
t.seed_full()
for tick in range(1500):
    t.step()
    if tick in [0, 250, 500, 1000, 1499]:
        actions = []
        for r in range(t.rows):
            for c in range(t.cols):
                cell = t.grid[r][c]
                if cell and cell.is_alive and cell.action is not None:
                    actions.append(cell.action.copy())
        if actions:
            actions = np.array(actions)
            mean_act = np.mean(actions, axis=0)
            std_act = np.std(actions, axis=0)
            print(f"  t={tick:4d}: cells={len(actions):3d}, "
                  f"mean=[{','.join(f'{a:+.3f}' for a in mean_act)}], "
                  f"std=[{','.join(f'{a:.3f}' for a in std_act)}]")

# Spatial map at end
print(f"\nSpatial layout at t=1500 ({SIZE}x{SIZE}):")
for r in range(t.rows):
    row_str = ""
    for c in range(t.cols):
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            if cell.action is not None:
                # Show preferred direction: U/D/L/R
                dirs = "UDLR"
                best = np.argmax(cell.action)
                row_str += dirs[best]
            else:
                row_str += "?"
        else:
            row_str += "."
    print(f"  {row_str}")
