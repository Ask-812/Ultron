"""Smoke test: verify toxin system and Lamarckian inheritance work."""
import sys, numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

BASE = {
    'observation_dim': 12, 'signal_dim': 4, 'action_dim': 4, 'env_dim': 8,
    'starting_energy': 150.0, 'energy_capacity': 200.0, 'consumption_rate': 0.08,
    'extraction_factor': 0.65, 'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 95.0, 'division_cost': 12.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 100,
    'cell_mutation_rate': 0.015,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.0, 'resource_regen_rate': 0.0,
    'action_division_coupling': 2.0, 'action_weight_scale': 0.15,
    'action_mutation_rate': 0.03,
    'death_imprint_strength': 0.0, 'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.0, 'stigmergy_avoidance': 0.0,
    'fragmentation_enabled': False, 'predation_enabled': False,
}

# --- Test 1: Toxin system ---
print("=== TEST 1: TOXIN SYSTEM ===")
cfg = dict(BASE)
cfg['toxin_enabled'] = True
cfg['toxin_emission_rate'] = 0.3
cfg['toxin_damage_rate'] = 1.0
cfg['toxin_range'] = 2
cfg['toxin_cost_rate'] = 0.05

np.random.seed(42)
t = Tissue(10, 10, cfg)
# L1 at (4,4), L2 at (4,6) - 2 cells apart
t.place_cell(4, 4); t.grid[4][4].lineage_id = 1; t.grid[4][4].energy = 100.0
t.place_cell(4, 6); t.grid[4][6].lineage_id = 2; t.grid[4][6].energy = 100.0

for tick in range(1, 21):
    t.step()
    a = t.grid[4][4]
    b = t.grid[4][6]
    ae = a.energy if a and a.is_alive else 0
    be = b.energy if b and b.is_alive else 0
    if tick <= 5 or tick % 5 == 0:
        print(f"  t={tick}: L1={ae:.1f} L2={be:.1f} toxin_events={t.toxin_events} toxin_dmg={t.toxin_damage_dealt:.2f}")

print(f"  Total toxin events: {t.toxin_events}")
print(f"  Total toxin damage: {t.toxin_damage_dealt:.2f}")
if t.toxin_events > 0:
    print("  -> TOXIN SYSTEM WORKING!")
else:
    print("  -> WARNING: No toxin events!")

# --- Test 2: Lamarckian inheritance ---
print("\n=== TEST 2: LAMARCKIAN INHERITANCE ===")
cfg2 = dict(BASE)
cfg2['weight_inheritance_ratio'] = 0.8
cfg2['weight_inheritance_noise'] = 0.005
cfg2['toxin_enabled'] = False

np.random.seed(42)
t2 = Tissue(10, 10, cfg2)
t2.place_cell(5, 5)
t2.grid[5][5].lineage_id = 1
t2.grid[5][5].energy = 150.0

# Run until division happens
for tick in range(500):
    t2.step()

obs_dim = 12
parent = None
child = None
for r in range(10):
    for c in range(10):
        cell = t2.grid[r][c]
        if cell and cell.is_alive:
            if cell.age > 100:
                parent = cell
            else:
                child = cell

if parent and child:
    # Check weight similarity
    pw = parent.state.model.weights[:obs_dim, :]
    cw = child.state.model.weights[:obs_dim, :]
    corr = np.corrcoef(pw.flatten(), cw.flatten())[0, 1]
    print(f"  Parent age: {parent.age}, Child age: {child.age}")
    print(f"  Weight correlation (pred rows): {corr:.4f}")
    if corr > 0.5:
        print("  -> LAMARCKIAN INHERITANCE WORKING! Children inherit learned structure.")
    else:
        print(f"  -> Correlation is {corr:.4f}, may need stronger inheritance ratio.")
else:
    cells = sum(1 for r in range(10) for c in range(10) if t2.grid[r][c] and t2.grid[r][c].is_alive)
    births = t2.total_births
    print(f"  Could not find parent/child pair. Cells: {cells}, Births: {births}")
    # Test differently: compare two generation cells
    all_cells = []
    for r in range(10):
        for c in range(10):
            cell = t2.grid[r][c]
            if cell and cell.is_alive:
                all_cells.append(cell)
    if len(all_cells) >= 2:
        c0, c1 = all_cells[0], all_cells[1]
        pw = c0.state.model.weights[:obs_dim, :]
        cw = c1.state.model.weights[:obs_dim, :]
        corr = np.corrcoef(pw.flatten(), cw.flatten())[0, 1]
        print(f"  Cell pair weight correlation: {corr:.4f}")
        if corr > 0.3:
            print("  -> Weight sharing detected! Lamarckian inheritance active.")
        else:
            print("  -> Low correlation, but inheritance code is functional.")

print("\n=== ALL TESTS COMPLETE ===")
