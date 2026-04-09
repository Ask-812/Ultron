"""Quick 500-tick ecosystem test."""
import numpy as np
import time
from ultron.tissue import Tissue

CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.60,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 100.0, 'division_cost': 15.0,
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
    'landscape_n_patches': 4, 'landscape_patch_radius': 0.18,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(10, 10), (10, 30), (30, 10), (30, 30)],
    'fragmentation_enabled': True, 'fragmentation_interval': 100,
    'fragmentation_min_size': 5,
    'displacement_energy_ratio': 2.5,
}

np.random.seed(7)
t = Tissue(40, 40, CONFIG)
for (row, col, lid) in [(10, 10, 1), (10, 30, 2), (30, 10, 3), (30, 30, 4)]:
    for dr in range(-1, 2):
        for dc in range(-1, 2):
            r, c = row + dr, col + dc
            if 0 <= r < 40 and 0 <= c < 40:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = lid

print("t=0: %d cells" % t.cell_count)
t0 = time.time()
for tick in range(500):
    t.step()
    if tick % 100 == 99:
        eco = t.ecosystem_snapshot()
        dt = time.time() - t0
        print("t=%d: cells=%d lineages=%d births=%d deaths=%d (%.1fs)" %
              (tick + 1, eco['total_cells'], eco['n_lineages'],
               t.total_births, t.total_deaths, dt))
        for lid in sorted(eco['lineages'].keys()):
            d = eco['lineages'][lid]
            print("  L%d: n=%d E=%.0f" % (lid, d['cell_count'], d['mean_energy']))
print("DONE")
