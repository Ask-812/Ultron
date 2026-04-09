"""Long-duration action evolution experiment.

Does natural selection shape action weights over many generations?
Test: 10k ticks on a 15x15 grid with resource depletion + action coupling.
With ~80+ divisions, action weights should drift from random initialization
if they provide any fitness advantage.

Measure: action weight statistics at intervals, compared to random baseline.
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
    'resource_depletion_rate': 0.001,
    'resource_regen_rate': 0.0002,
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.5,
    'action_dim': 4,
    'action_division_coupling': 2.0,
}

SIZE = 12
TICKS = 5000

np.random.seed(42)
t = Tissue(SIZE, SIZE, BASE)
# Start with 3x3 seed
cr, cc = SIZE // 2, SIZE // 2
for dr in range(-1, 2):
    for dc in range(-1, 2):
        t.place_cell(cr + dr, cc + dc)

t0 = time.time()
checkpoints = [0, 500, 1000, 2000, 3000, 4999]

print(f"Long-duration action evolution: {SIZE}x{SIZE}, {TICKS} ticks")
print(f"Resource depletion + action coupling")
print("=" * 70)

for tick in range(TICKS):
    t.step()
    if tick in checkpoints:
        # Collect action weight statistics from all living cells
        action_weights = []
        action_outputs = []
        for r in range(t.rows):
            for c in range(t.cols):
                cell = t.grid[r][c]
                if cell and cell.is_alive:
                    obs_dim = BASE['observation_dim']
                    aw = cell.state.model.weights[obs_dim:, :]  # action weight rows
                    action_weights.append(aw.flatten())
                    if cell.action is not None:
                        action_outputs.append(cell.action)

        s = t.snapshot()
        print(f"\nt={tick:5d}: cells={s['cell_count']:3d}  births={t.total_births:4d}  "
              f"deaths={t.total_deaths:4d}  resource={s.get('resource_mean',1):.3f}")

        if action_weights:
            aw = np.array(action_weights)
            print(f"  Action weight stats: mean={aw.mean():.5f}  std={aw.std():.5f}  "
                  f"norm_mean={np.mean(np.linalg.norm(aw, axis=1)):.4f}")
            # Compare weight distribution to random N(0, 0.01) baseline
            # After many generations, weights should differ from initial distribution
            print(f"  Weight range: [{aw.min():.4f}, {aw.max():.4f}]")

        if action_outputs:
            ao = np.array(action_outputs)
            mean_ao = ao.mean(0)
            std_ao = ao.std(0)
            print(f"  Action outputs: mean=[{','.join(f'{a:+.4f}' for a in mean_ao)}]  "
                  f"std=[{','.join(f'{a:.4f}' for a in std_ao)}]")

            # Check if any direction is systematically preferred
            dominant_dir = np.argmax(np.abs(mean_ao))
            dirs = ['up', 'down', 'left', 'right']
            if np.abs(mean_ao[dominant_dir]) > 2 * std_ao[dominant_dir] / np.sqrt(len(ao)):
                print(f"  ** Significant directional bias: {dirs[dominant_dir]} "
                      f"(mean={mean_ao[dominant_dir]:+.4f}, SE={std_ao[dominant_dir]/np.sqrt(len(ao)):.4f})")

dt = time.time() - t0
print(f"\nTotal time: {dt:.1f}s, births={t.total_births}, deaths={t.total_deaths}")

# Final grid
print(f"\nFinal grid (t={TICKS}):")
for r in range(SIZE):
    row = "  "
    for c in range(SIZE):
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            if cell.action is not None:
                dirs = "UDLR"
                best = np.argmax(cell.action)
                row += dirs[best]
            else:
                row += "#"
        else:
            row += "."
    print(row)

# Compare: what are the average action weights of high-energy vs low-energy cells?
print("\nAction weight differences by cell energy:")
high_e, low_e = [], []
median_energy = np.median([t.grid[r][c].energy for r in range(SIZE) for c in range(SIZE)
                           if t.grid[r][c] and t.grid[r][c].is_alive])
for r in range(SIZE):
    for c in range(SIZE):
        cell = t.grid[r][c]
        if cell and cell.is_alive:
            obs_dim = BASE['observation_dim']
            aw_norm = np.linalg.norm(cell.state.model.weights[obs_dim:, :])
            if cell.energy > median_energy:
                high_e.append(aw_norm)
            else:
                low_e.append(aw_norm)
if high_e and low_e:
    print(f"  High-energy cells ({len(high_e)}): mean weight norm = {np.mean(high_e):.4f}")
    print(f"  Low-energy cells ({len(low_e)}): mean weight norm = {np.mean(low_e):.4f}")
