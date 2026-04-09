"""Action + Resource Depletion: Do actions evolve to guide growth toward resources?

With resource depletion, cells deplete local resources. The organism must
grow toward fresh resources to survive. With action coupling, cells can
influence division direction through their model outputs. If useful action weights
are inherited, the organism should evolve to preferentially grow outward.

Compare:
1. Depletion + Random division (no actions)
2. Depletion + Action-directed division
"""
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
    'resource_depletion_rate': 0.002,
    'resource_regen_rate': 0.0003,
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.5,
}

SIZE = 12
TICKS = 3000

print(f"Grid: {SIZE}x{SIZE}, Ticks: {TICKS}, resource depletion ON")
print("=" * 70)

for name, ov in [('Random division', {'action_dim': 0}),
                  ('Action division', {'action_dim': 4, 'action_division_coupling': 2.0})]:
    np.random.seed(42)
    cfg = {**BASE, **ov}
    t = Tissue(SIZE, SIZE, cfg)
    cr, cc = SIZE // 2, SIZE // 2
    for dr in [0, 1]:
        for dc in [0, 1]:
            t.place_cell(cr + dr, cc + dc)
    
    t0 = time.time()
    snapshots = []
    for tick in range(TICKS):
        t.step()
        if tick % 500 == 0 or tick == TICKS - 1:
            s = t.snapshot()
            snapshots.append((tick, s['cell_count'], s['total_energy'],
                             s.get('resource_mean', 1.0)))
    dt = time.time() - t0
    
    s = t.snapshot()
    # Bounding box
    min_r, max_r, min_c, max_c = SIZE, 0, SIZE, 0
    for r in range(SIZE):
        for c in range(SIZE):
            if t.grid[r][c] and t.grid[r][c].is_alive:
                min_r = min(min_r, r)
                max_r = max(max_r, r)
                min_c = min(min_c, c)
                max_c = max(max_c, c)
    extent = (max_r - min_r + 1) * (max_c - min_c + 1) if s['cell_count'] > 0 else 0
    
    print(f"\n{name}:")
    print(f"  Final: cells={s['cell_count']}, births={t.total_births}, "
          f"extent={extent}, resource_mean={s.get('resource_mean', 1):.3f}")
    for tick, cells, energy, res in snapshots:
        print(f"  t={tick:4d}: cells={cells:3d}  energy={energy:6.0f}  resource={res:.3f}")
    
    # Show grid
    print(f"  Grid at t={TICKS}:")
    for r in range(SIZE):
        row = "  "
        for c in range(SIZE):
            cell = t.grid[r][c]
            if cell and cell.is_alive:
                row += "#"
            else:
                row += "."
        print(row)
    print(f"  ({dt:.1f}s)")
