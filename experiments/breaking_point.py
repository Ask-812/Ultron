"""
BREAKING POINT: How much catastrophe can the organism survive?

Sweep across catastrophe severity levels:
  Level 0: No catastrophe (control)
  Level 1: Destroy 2/4 patches (from apocalypse experiment: survived)
  Level 2: Destroy ALL 4 patches
  Level 3: Destroy all patches + kill 25% of cells
  Level 4: Destroy all patches + kill 50% of cells
  Level 5: Destroy all patches + kill 75% of cells

For each level, measure: cells surviving at t+2000 after catastrophe.
"""
import numpy as np
import time
from ultron.tissue import Tissue

GRID = 30
GROW_TICKS = 2000
POST_TICKS = 3000

BASE_CONFIG = {
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
    'fragmentation_enabled': False,  # Simpler: no fragmentation
    'death_imprint_strength': 1.0,
    'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.3,
    'stigmergy_avoidance': 0.2,
}

LEVELS = {
    0: 'Control (no catastrophe)',
    1: 'Destroy 2/4 patches',
    2: 'Destroy ALL patches',
    3: 'Destroy all + kill 25%',
    4: 'Destroy all + kill 50%',
    5: 'Destroy all + kill 75%',
}


def setup_tissue(seed):
    np.random.seed(seed)
    t = Tissue(GRID, GRID, BASE_CONFIG)
    # Single organism from center
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = GRID // 2 + dr, GRID // 2 + dc
            if 0 <= r < GRID and 0 <= c < GRID and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 1
    return t


def grow(tissue, ticks):
    for _ in range(ticks):
        tissue.step()


def apply_catastrophe(tissue, level):
    patch_r = int(0.22 * GRID)

    if level >= 1:
        # Destroy patches
        patches_to_kill = [(8, 8), (22, 22)] if level == 1 else [(8, 8), (8, 22), (22, 8), (22, 22)]
        for pr, pc in patches_to_kill:
            for r in range(GRID):
                for c in range(GRID):
                    if np.sqrt((r - pr)**2 + (c - pc)**2) < patch_r:
                        tissue.resource_field[r, c] = 0.05
                        if hasattr(tissue, '_landscape_capacity'):
                            tissue._landscape_capacity[r, c] = 0.05

    if level >= 3:
        # Kill a percentage of cells
        kill_pct = {3: 0.25, 4: 0.50, 5: 0.75}[level]
        cells = []
        for r in range(GRID):
            for c in range(GRID):
                cell = tissue.grid[r][c]
                if cell and cell.is_alive:
                    cells.append((r, c))
        np.random.shuffle(cells)
        n_kill = int(len(cells) * kill_pct)
        for r, c in cells[:n_kill]:
            tissue.grid[r][c].state.is_alive = False
            tissue.grid[r][c] = None
            tissue.total_deaths += 1


def run():
    print("=" * 70)
    print("  BREAKING POINT: Catastrophe Severity Sweep")
    print("  Grid: %dx%d | Grow: %d ticks | Post-catastrophe: %d ticks" %
          (GRID, GRID, GROW_TICKS, POST_TICKS))
    print("=" * 70)

    results = []
    seeds = [7, 13, 42]  # 3 replicates

    for level in sorted(LEVELS.keys()):
        level_results = []
        for seed in seeds:
            t = setup_tissue(seed)
            grow(t, GROW_TICKS)
            pre_cells = t.cell_count
            pre_energy = t.total_energy

            if level > 0:
                apply_catastrophe(t, level)
            post_cells = t.cell_count
            killed = pre_cells - post_cells

            # Run post-catastrophe
            grow(t, POST_TICKS)
            final_cells = t.cell_count
            final_energy = t.total_energy
            recovery = final_cells / max(pre_cells, 1)

            level_results.append({
                'pre': pre_cells, 'killed': killed,
                'post_immediate': post_cells,
                'final': final_cells, 'recovery': recovery,
                'deaths': t.total_deaths, 'births': t.total_births,
                'final_energy': final_energy,
            })

        # Average across seeds
        avg_pre = np.mean([r['pre'] for r in level_results])
        avg_killed = np.mean([r['killed'] for r in level_results])
        avg_post = np.mean([r['post_immediate'] for r in level_results])
        avg_final = np.mean([r['final'] for r in level_results])
        avg_recovery = np.mean([r['recovery'] for r in level_results])
        avg_deaths = np.mean([r['deaths'] for r in level_results])
        avg_births = np.mean([r['births'] for r in level_results])

        results.append({
            'level': level, 'description': LEVELS[level],
            'pre': avg_pre, 'killed': avg_killed,
            'post': avg_post, 'final': avg_final,
            'recovery': avg_recovery,
            'deaths': avg_deaths, 'births': avg_births,
            'all': level_results,
        })

        print(f"\n  Level {level}: {LEVELS[level]}")
        print(f"    Pre-catastrophe: {avg_pre:.0f} cells")
        print(f"    Killed instantly: {avg_killed:.0f}")
        print(f"    Post-catastrophe: {avg_post:.0f} cells")
        print(f"    Final (t+{POST_TICKS}): {avg_final:.0f} cells")
        print(f"    Recovery ratio: {avg_recovery:.1%}")
        print(f"    Total births: {avg_births:.0f}, Total deaths: {avg_deaths:.0f}")
        for i, r in enumerate(level_results):
            print(f"      seed {seeds[i]}: {r['pre']} -> {r['post_immediate']} -> {r['final']} "
                  f"({r['recovery']:.0%} recovery)")

    print("\n" + "=" * 70)
    print("  SUMMARY: BREAKING POINT ANALYSIS")
    print("=" * 70)
    print(f"\n  {'Level':<8} {'Description':<30} {'Pre':>5} {'Kill':>5} {'Final':>6} {'Recovery':>10}")
    print("  " + "-" * 65)
    for r in results:
        print(f"  {r['level']:<8} {r['description']:<30} {r['pre']:5.0f} {r['killed']:5.0f} "
              f"{r['final']:6.0f} {r['recovery']:10.1%}")

    # Find the breaking point
    print("\n  BREAKING POINT ANALYSIS:")
    for r in results:
        if r['recovery'] < 0.5:
            print(f"  -> Level {r['level']} ({r['description']}): BREAKING POINT")
            print(f"     Recovery dropped to {r['recovery']:.1%} — homeostasis overwhelmed.")
            break
    else:
        print("  -> The organism survived ALL severity levels!")
        print("     Homeostatic buffering is extraordinarily robust.")

    # Narrative
    print("\n  INTERPRETATION:")
    if results[2]['recovery'] > 0.8:
        print("  Even total environmental destruction doesn't kill the organism.")
        print("  The internal metabolic network redistributes energy so efficiently")
        print("  that cells survive on stored energy and inter-cell sharing alone.")
    if any(r['recovery'] < 0.1 for r in results):
        bp = [r for r in results if r['recovery'] < 0.1][0]
        print(f"  The breaking point is Level {bp['level']}: {bp['description']}.")
        print("  Below this threshold, the colony cannot regenerate.")
        surv = [r for r in results if r['recovery'] >= 0.5]
        if surv:
            last_ok = surv[-1]
            print(f"  The organism tolerates up to Level {last_ok['level']} with {last_ok['recovery']:.0%} recovery.")


if __name__ == '__main__':
    t0 = time.time()
    run()
    print(f"\n  Total runtime: {time.time() - t0:.1f}s")
