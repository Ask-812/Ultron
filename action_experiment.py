"""Action Coupling Experiment: Does directed division change organism morphology?

Compare three conditions:
1. No actions (action_dim=0): random division direction (v0.5 behavior)
2. Actions, coupling OFF (action_dim=4, coupling=0): actions computed but unused
3. Actions, coupling ON (action_dim=4, coupling=1.0): division direction guided by actions

Key question: Does action-guided division change growth pattern, survival, or morphology?
"""
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
    ('No actions     ', {'action_dim': 0}),
    ('Actions OFF    ', {'action_dim': 4, 'action_division_coupling': 0.0}),
    ('Actions ON     ', {'action_dim': 4, 'action_division_coupling': 1.0}),
    ('Actions STRONG ', {'action_dim': 4, 'action_division_coupling': 3.0}),
]

SIZE = 15
TICKS = 2000
SEEDS = [42, 99, 137]

print(f"Grid: {SIZE}x{SIZE}, Ticks: {TICKS}, Seeds: {SEEDS}")
print("=" * 80)

for name, overrides in CONDITIONS:
    cells_list, energy_list, births_list, deaths_list = [], [], [], []
    for seed in SEEDS:
        np.random.seed(seed)
        cfg = {**BASE, **overrides}
        t = Tissue(SIZE, SIZE, cfg)
        t.seed_full()
        t0 = time.time()
        for tick in range(TICKS):
            t.step()
        dt = time.time() - t0
        s = t.snapshot()
        cells_list.append(s['cell_count'])
        energy_list.append(s['total_energy'])
        births_list.append(t.total_births)
        deaths_list.append(t.total_deaths)
    
    avg_cells = np.mean(cells_list)
    avg_energy = np.mean(energy_list)
    avg_births = np.mean(births_list)
    avg_deaths = np.mean(deaths_list)
    print(f"{name}: cells={avg_cells:.0f} (+/-{np.std(cells_list):.0f})  "
          f"energy={avg_energy:.0f}  births={avg_births:.0f}  deaths={avg_deaths:.0f}  "
          f"[{','.join(str(c) for c in cells_list)}]")

# Detailed analysis of action evolution with coupling ON
print("\n" + "=" * 80)
print("Action evolution analysis (coupling=1.0):")
np.random.seed(42)
cfg = {**BASE, 'action_dim': 4, 'action_division_coupling': 1.0}
t = Tissue(SIZE, SIZE, cfg)
t.seed_full()
for tick in range(3000):
    t.step()
    if tick in [0, 500, 1000, 2000, 2999]:
        # Collect action statistics
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
            print(f"  t={tick}: cells={len(actions)}, "
                  f"mean_action=[{','.join(f'{a:.3f}' for a in mean_act)}], "
                  f"std=[{','.join(f'{a:.3f}' for a in std_act)}]")

# Spatial pattern: which direction do edge vs interior cells prefer?
print("\nEdge vs Interior action preferences (t=3000):")
edge_actions, interior_actions = [], []
for r in range(t.rows):
    for c in range(t.cols):
        cell = t.grid[r][c]
        if cell and cell.is_alive and cell.action is not None:
            if cell.is_surface:
                edge_actions.append(cell.action.copy())
            else:
                interior_actions.append(cell.action.copy())
if edge_actions:
    ea = np.array(edge_actions)
    print(f"  Surface cells ({len(edge_actions)}): mean=[{','.join(f'{a:.3f}' for a in np.mean(ea, axis=0))}]")
if interior_actions:
    ia = np.array(interior_actions)
    print(f"  Interior cells ({len(interior_actions)}): mean=[{','.join(f'{a:.3f}' for a in np.mean(ia, axis=0))}]")
