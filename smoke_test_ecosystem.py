"""Quick smoke test of ecosystem experiment — 200 ticks only."""
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ultron.tissue import Tissue

CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.50,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 130.0, 'division_cost': 25.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 400,
    'cell_mutation_rate': 0.01,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.0008, 'resource_regen_rate': 0.0001,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_dim': 4, 'action_division_coupling': 2.0,
    'action_weight_scale': 0.1, 'action_mutation_rate': 0.02,
    'landscape_type': 'patches', 'landscape_base': 0.25,
    'landscape_n_patches': 4, 'landscape_patch_radius': 0.2,
    'landscape_patch_richness': 1.0, 'landscape_seed': 42,
    'fragmentation_enabled': True, 'fragmentation_interval': 100,
    'displacement_energy_ratio': 2.5,
}

np.random.seed(7)
t = Tissue(20, 20, CONFIG)
print("Resource field range:", t.resource_field.min(), "-", t.resource_field.max())
print("Resource field mean:", t.resource_field.mean())

# Place 2 founders
from ultron.cell import create_cell
for dr in range(-1, 2):
    for dc in range(-1, 2):
        r, c = 5 + dr, 5 + dc
        if 0 <= r < 20 and 0 <= c < 20:
            t.place_cell(r, c)
            t.grid[r][c].lineage_id = 1

for dr in range(-1, 2):
    for dc in range(-1, 2):
        r, c = 14 + dr, 14 + dc
        if 0 <= r < 20 and 0 <= c < 20:
            t.place_cell(r, c)
            t.grid[r][c].lineage_id = 2

print(f"t=0: cells={t.cell_count}")
for tick in range(200):
    t.step()
    if tick % 50 == 49:
        eco = t.ecosystem_snapshot()
        print(f"t={tick+1}: cells={eco['total_cells']}, lineages={eco['n_lineages']}, "
              f"births={t.total_births}, deaths={t.total_deaths}")
        for lid in sorted(eco['lineages'].keys()):
            d = eco['lineages'][lid]
            print(f"  L{lid}: n={d['cell_count']} E={d['mean_energy']:.1f}")

print("\nLineage map:")
lm = t.get_lineage_map()
for r in range(20):
    line = ''
    for c in range(20):
        if lm[r, c] < 0:
            line += '.'
        else:
            line += str(lm[r, c])
    print(' ', line)
print("SMOKE TEST PASSED")
