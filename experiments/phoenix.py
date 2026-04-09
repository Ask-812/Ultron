"""
PHOENIX: Death and Rebirth

Phase 1: Grow a healthy organism (2000 ticks)
Phase 2: Destroy ALL resources + kill 99% of cells (apocalypse)  
Phase 3: Wait 1000 ticks in barren wasteland (survival)
Phase 4: RESTORE resources (spring)
Phase 5: Watch the 1-2 surviving cells REGROW into a full organism (3000 ticks)

The question: Can a single surviving cell rebuild an entire organism
from scratch once resources return? Does the reborn organism differ
from the original?
"""
import sys, time
import numpy as np
sys.path.insert(0, '.')
from ultron.tissue import Tissue

GRID = 30
CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'action_dim': 4,
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
    'migration_enabled': True,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_division_coupling': 2.0,
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
    'predation_enabled': False,
}

def get_cells(t):
    positions = []
    for r in range(t.rows):
        for c in range(t.cols):
            if t.grid[r][c] is not None and t.grid[r][c].is_alive:
                positions.append((r, c))
    return positions

def snapshot(t, label):
    cells = get_cells(t)
    n = len(cells)
    if n == 0:
        print(f"  {label}: 0 cells, EXTINCT")
        return 0
    energies = [t.grid[r][c].energy for r, c in cells]
    ages = [t.grid[r][c].age for r, c in cells]
    extractions = [t.grid[r][c].state.traits.extraction_efficiency for r, c in cells]
    errors = [t.grid[r][c].state.current.error_magnitude for r, c in cells]
    actions = [np.linalg.norm(t.grid[r][c].action) for r, c in cells if t.grid[r][c].action is not None]
    print(f"  {label}: {n} cells, E={np.mean(energies):.1f}+/-{np.std(energies):.1f}, "
          f"age={np.mean(ages):.0f}, err={np.mean(errors):.3f}, "
          f"ext={np.mean(extractions):.4f}, "
          f"act={np.mean(actions):.3f}" if actions else
          f"  {label}: {n} cells, E={np.mean(energies):.1f}+/-{np.std(energies):.1f}")
    return n

def run():
    start = time.time()
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)
    
    # Seed center organism
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = GRID // 2 + dr, GRID // 2 + dc
            if 0 <= r < GRID and 0 <= c < GRID and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 1

    print("=" * 70)
    print("  PHOENIX: Death and Rebirth")
    print(f"  Grid: {GRID}x{GRID} | Patches at corners")
    print("=" * 70)

    # ===== PHASE 1: GROWTH (2000 ticks) =====
    print("\n  PHASE 1: GROWTH")
    snapshot(t, "t=0     ")
    for tick in range(1, 2001):
        t.step()
        if tick % 500 == 0:
            snapshot(t, f"t={tick:5d}")

    pre_cells = get_cells(t)
    pre_count = len(pre_cells)
    pre_snap = t.snapshot()
    
    # Record pre-apocalypse traits for comparison
    pre_extraction = np.mean([t.grid[r][c].state.traits.extraction_efficiency for r, c in pre_cells])
    pre_metabolic = np.mean([t.grid[r][c].state.traits.metabolic_rate for r, c in pre_cells])
    pre_action_norms = [np.linalg.norm(t.grid[r][c].action) for r, c in pre_cells if t.grid[r][c].action is not None]
    pre_action_mean = np.mean(pre_action_norms) if pre_action_norms else 0

    # ===== PHASE 2: APOCALYPSE =====
    print(f"\n  PHASE 2: APOCALYPSE (99% kill + destroy all resources)")
    
    # Destroy ALL resources
    t.resource_field[:] = 0.05
    t._landscape_capacity[:] = 0.05
    
    # Kill 99% of cells
    rng = np.random.RandomState(42)
    n_kill = int(pre_count * 0.99)
    if n_kill >= pre_count:
        n_kill = pre_count - 1  # Keep at least 1
    victims = rng.choice(len(pre_cells), size=n_kill, replace=False)
    for idx in victims:
        r, c = pre_cells[idx]
        if t.grid[r][c] is not None:
            t.grid[r][c].state.is_alive = False
            t.grid[r][c] = None

    survivors = get_cells(t)
    print(f"  Killed {n_kill} of {pre_count} cells. {len(survivors)} survivors:")
    for r, c in survivors:
        cell = t.grid[r][c]
        print(f"    ({r},{c}): energy={cell.energy:.1f}, age={cell.age}, "
              f"ext={cell.state.traits.extraction_efficiency:.4f}")

    # ===== PHASE 3: BARREN WASTELAND (1000 ticks) =====
    print(f"\n  PHASE 3: BARREN WASTELAND (1000 ticks, no resources)")
    for tick in range(1, 1001):
        t.step()
        if tick % 250 == 0:
            snapshot(t, f"barren t+{tick}")

    barren_cells = get_cells(t)
    if not barren_cells:
        print("  ORGANISM DIED IN THE WASTELAND. Phoenix failed.")
        return

    # ===== PHASE 4: SPRING — RESTORE RESOURCES =====
    print(f"\n  PHASE 4: SPRING — RESOURCES RESTORED!")
    
    # Restore original landscape
    t._landscape_capacity = np.ones((GRID, GRID)) * 0.25  # base level
    radius = int(0.22 * GRID)
    for pr, pc in [(8, 8), (8, 22), (22, 8), (22, 22)]:
        for r in range(GRID):
            for c in range(GRID):
                dist = np.sqrt((r - pr)**2 + (c - pc)**2)
                if dist < radius:
                    falloff = 1.0 - (dist / radius)**2
                    t._landscape_capacity[r, c] = max(
                        t._landscape_capacity[r, c],
                        0.25 + 0.75 * falloff
                    )
    t.resource_field = t._landscape_capacity.copy()

    # ===== PHASE 5: REBIRTH (3000 ticks) =====
    print(f"\n  PHASE 5: REBIRTH (3000 ticks with restored resources)")
    for tick in range(1, 3001):
        t.step()
        if tick % 500 == 0:
            snapshot(t, f"spring t+{tick}")

    # ===== ANALYSIS =====
    post_cells = get_cells(t)
    post_count = len(post_cells)
    
    print("\n" + "=" * 70)
    print("  PHOENIX RESULTS")
    print("=" * 70)
    
    print(f"\n  Pre-apocalypse:  {pre_count} cells")
    print(f"  Post-kill:       {len(survivors)} cells")
    print(f"  Post-wasteland:  {len(barren_cells)} cells")
    print(f"  Post-rebirth:    {post_count} cells")
    recovery_pct = post_count / pre_count * 100
    print(f"\n  Recovery: {recovery_pct:.1f}% of original population")
    
    if post_count > 0:
        post_extraction = np.mean([t.grid[r][c].state.traits.extraction_efficiency for r, c in post_cells])
        post_metabolic = np.mean([t.grid[r][c].state.traits.metabolic_rate for r, c in post_cells])
        post_action_norms = [np.linalg.norm(t.grid[r][c].action) for r, c in post_cells if t.grid[r][c].action is not None]
        post_action_mean = np.mean(post_action_norms) if post_action_norms else 0
        
        print(f"\n  TRAIT COMPARISON (original vs reborn):")
        print(f"    Extraction: {pre_extraction:.4f} -> {post_extraction:.4f} ({(post_extraction/pre_extraction - 1)*100:+.2f}%)")
        print(f"    Metabolic:  {pre_metabolic:.4f} -> {post_metabolic:.4f} ({(post_metabolic/pre_metabolic - 1)*100:+.2f}%)")
        print(f"    Action mag: {pre_action_mean:.4f} -> {post_action_mean:.4f} ({(post_action_mean/pre_action_mean - 1)*100:+.2f}%)" if pre_action_mean > 0 else "")
        
        # Are traits different? Bottleneck effect
        print(f"\n  BOTTLENECK EFFECT:")
        print(f"    The reborn organism descends from {len(survivors)} cell(s).")
        print(f"    This is a genetic bottleneck — all {post_count} cells share")
        print(f"    the survivor's traits plus accumulated mutations.")
    
    print(f"\n  Total births: {t.total_births}")
    print(f"  Total deaths: {t.total_deaths}")
    
    elapsed = time.time() - start
    print(f"\n  Runtime: {elapsed:.1f}s")
    print("=" * 70)

if __name__ == '__main__':
    run()
