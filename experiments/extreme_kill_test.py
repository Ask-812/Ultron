"""Extreme kill test: Can the organism survive 90-99% cell death?"""
import sys, numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

# Use the exact same config as breaking_point.py (known to work)
CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.65,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 95.0, 'division_cost': 12.0,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 100,
    'cell_mutation_rate': 0.015,
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.001, 'resource_regen_rate': 0.0003,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_dim': 4, 'action_division_coupling': 2.0,
    'action_weight_scale': 0.15, 'action_mutation_rate': 0.03,
    'landscape_type': 'patches', 'landscape_base': 0.25,
    'landscape_n_patches': 4, 'landscape_patch_radius': 0.22,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(8, 8), (8, 22), (22, 8), (22, 22)],
    'fragmentation_enabled': False,
    'death_imprint_strength': 1.0,
    'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.3,
    'stigmergy_avoidance': 0.2,
}

def get_cell_positions(t):
    """Get all occupied positions."""
    positions = []
    for r in range(t.rows):
        for c in range(t.cols):
            if t.grid[r][c] is not None and t.grid[r][c].is_alive:
                positions.append((r, c))
    return positions

def run_extreme(kill_pct, seed):
    rng = np.random.RandomState(seed)
    np.random.seed(seed)
    t = Tissue(30, 30, CONFIG)
    # Place organism in center
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = 15 + dr, 15 + dc
            if 0 <= r < 30 and 0 <= c < 30 and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 1
    
    # Grow for 2000 ticks
    for _ in range(2000):
        t.step()
    
    pre = t.cell_count
    
    # Destroy ALL patches
    t.resource_field[:] = 0.05
    t._landscape_capacity[:] = 0.05
    
    # Kill cells
    n_kill = int(pre * kill_pct / 100)
    positions = get_cell_positions(t)
    if n_kill > 0 and n_kill < len(positions):
        victims = rng.choice(len(positions), size=n_kill, replace=False)
        for idx in victims:
            r, c = positions[idx]
            t.grid[r][c].state.is_alive = False
            t.grid[r][c] = None
    
    post = t.cell_count
    
    # Run 3000 more ticks
    deaths_after = 0
    for tick in range(3000):
        before = t.cell_count
        t.step()
        after = t.cell_count
        if after < before:
            deaths_after += (before - after)
    
    final = t.cell_count
    return pre, n_kill, post, final, deaths_after

print("=" * 70)
print("  EXTREME KILL TEST: Can the organism survive near-annihilation?")
print("=" * 70)

levels = [90, 95, 98, 99]
seeds = [42, 7, 13]

for kill_pct in levels:
    results = []
    for seed in seeds:
        pre, killed, post, final, cascade = run_extreme(kill_pct, seed)
        results.append((pre, killed, post, final, cascade))
    
    avg_pre = np.mean([r[0] for r in results])
    avg_killed = np.mean([r[1] for r in results])
    avg_post = np.mean([r[2] for r in results])
    avg_final = np.mean([r[3] for r in results])
    avg_cascade = np.mean([r[4] for r in results])
    
    print(f"\n  Kill {kill_pct}%: Pre={avg_pre:.0f}, Killed={avg_killed:.0f}, "
          f"Post={avg_post:.0f}, Final={avg_final:.0f}, "
          f"Cascade deaths={avg_cascade:.0f}")
    for i, (pre, killed, post, final, cascade) in enumerate(results):
        print(f"    seed {seeds[i]}: {pre} -> kill {killed} -> {post} -> {final} "
              f"(cascade={cascade})")

print("\n" + "=" * 70)
print("  If cascade deaths = 0 at all levels, the organism is truly immortal.")
print("=" * 70)
