"""Action Coupling Experiment: Growth from single seed on 15x15."""
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

SIZE = 12
TICKS = 2000

print(f"Grid: {SIZE}x{SIZE}, Ticks: {TICKS}, seed from center")
print("=" * 70)

for name, ov in [('No actions', {'action_dim': 0}),
                  ('Actions ON (1.0)', {'action_dim': 4, 'action_division_coupling': 1.0}),
                  ('Actions ON (3.0)', {'action_dim': 4, 'action_division_coupling': 3.0})]:
    np.random.seed(42)
    cfg = {**BASE, **ov}
    t = Tissue(SIZE, SIZE, cfg)
    # Start from a 2x2 seed at center
    cr, cc = SIZE // 2, SIZE // 2
    for dr in [0, 1]:
        for dc in [0, 1]:
            t.place_cell(cr + dr, cc + dc)
    
    t0 = time.time()
    for tick in range(TICKS):
        t.step()
    dt = time.time() - t0
    s = t.snapshot()
    
    # Compute spatial extent (bounding box of living cells)
    min_r, max_r, min_c, max_c = SIZE, 0, SIZE, 0
    for r in range(SIZE):
        for c in range(SIZE):
            if t.grid[r][c] and t.grid[r][c].is_alive:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)
    extent = (max_r - min_r + 1) * (max_c - min_c + 1) if s['cell_count'] > 0 else 0
    
    print(f"{name:20s}: cells={s['cell_count']:3d}  energy={s['total_energy']:6.0f}  "
          f"births={t.total_births:3d}  extent={extent:3d}  ({dt:.1f}s)")
    
    # Show grid
    grid_str = ""
    for r in range(SIZE):
        row = ""
        for c in range(SIZE):
            cell = t.grid[r][c]
            if cell and cell.is_alive:
                row += "#"
            else:
                row += "."
        grid_str += f"  {row}\n"
    print(grid_str)

# Action evolution over time
print("Action evolution (coupling=1.0, single run):")
np.random.seed(42)
cfg = {**BASE, 'action_dim': 4, 'action_division_coupling': 1.0}
t = Tissue(SIZE, SIZE, cfg)
cr, cc = SIZE // 2, SIZE // 2
for dr in [0, 1]:
    for dc in [0, 1]:
        t.place_cell(cr + dr, cc + dc)

for tick in range(TICKS):
    t.step()
    if tick in [100, 500, 1000, 1999]:
        actions = []
        for r in range(t.rows):
            for c in range(t.cols):
                cell = t.grid[r][c]
                if cell and cell.is_alive and cell.action is not None:
                    actions.append(cell.action)
        if actions:
            acts = np.array(actions)
            print(f"  t={tick:4d}: n={len(actions):3d}  "
                  f"mean=[{','.join(f'{a:+.3f}' for a in acts.mean(0))}]  "
                  f"std=[{','.join(f'{a:.3f}' for a in acts.std(0))}]")
