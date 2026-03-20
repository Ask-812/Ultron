"""
ECOSYSTEM WAR: Dense competitive experiment.

Smaller grid (25x25), 2 large resource patches near center, 2 organisms
starting adjacent. Aggressive growth settings. Competitive displacement
active. The question: can one organism evolve to outcompete the other?
"""
import numpy as np
import time
import os
from ultron.tissue import Tissue

GRID = 25
TICKS = 8000

CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.70,  # High extraction for fast growth
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 90.0,  # Low threshold for rapid division
    'division_cost': 10.0,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 200,  # Die faster when starving
    'cell_mutation_rate': 0.015,  # Higher mutation for faster evolution
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 2.0,
    'resource_depletion_rate': 0.001, 'resource_regen_rate': 0.0003,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.4,
    'action_dim': 4, 'action_division_coupling': 3.0,
    'action_weight_scale': 0.15, 'action_mutation_rate': 0.03,
    # Two overlapping resource patches in the center
    'landscape_type': 'patches', 'landscape_base': 0.3,
    'landscape_n_patches': 2, 'landscape_patch_radius': 0.35,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(12, 8), (12, 16)],
    'fragmentation_enabled': True, 'fragmentation_interval': 50,
    'fragmentation_min_size': 5,
    'displacement_energy_ratio': 2.0,  # Easier to displace
}


def run():
    np.random.seed(42)
    t = Tissue(GRID, GRID, CONFIG)

    # Organism A: left side
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = 12 + dr, 6 + dc
            if 0 <= r < GRID and 0 <= c < GRID and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 1

    # Organism B: right side
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            r, c = 12 + dr, 18 + dc
            if 0 <= r < GRID and 0 <= c < GRID and abs(dr) + abs(dc) <= 3:
                t.place_cell(r, c)
                t.grid[r][c].lineage_id = 2

    a_count = sum(1 for r in range(GRID) for c in range(GRID)
                  if t.grid[r][c] and t.grid[r][c].lineage_id == 1)
    b_count = sum(1 for r in range(GRID) for c in range(GRID)
                  if t.grid[r][c] and t.grid[r][c].lineage_id == 2)
    print(f"Organisms: A={a_count} cells, B={b_count} cells")
    print(f"Resource landscape: min={t.resource_field.min():.2f} max={t.resource_field.max():.2f}")
    print(f"Grid: {GRID}x{GRID}, Ticks: {TICKS}")
    print("=" * 60)

    history = []
    t0 = time.time()

    for tick in range(TICKS):
        t.step()

        if tick % 200 == 199 or tick == 0:
            eco = t.ecosystem_snapshot()
            snap = t.snapshot()
            dt = time.time() - t0
            rate = (tick + 1) / max(dt, 0.001)
            eta = (TICKS - tick - 1) / max(rate, 0.001)

            # Count cells by original lineage (1-2) vs fragments (>2)
            a_cells = sum(d['cell_count'] for lid, d in eco['lineages'].items() if lid == 1)
            b_cells = sum(d['cell_count'] for lid, d in eco['lineages'].items() if lid == 2)
            frag_cells = sum(d['cell_count'] for lid, d in eco['lineages'].items() if lid > 2)

            print(f"t={tick+1:5d} | A={a_cells:3d} B={b_cells:3d} frag={frag_cells:3d} "
                  f"total={eco['total_cells']:3d} | "
                  f"lineages={eco['n_lineages']:2d} | "
                  f"births={snap['births']:4d} deaths={snap['deaths']:4d} | "
                  f"res={snap['resource_mean']:.3f} | {dt:.0f}s ~{eta:.0f}s left")

            history.append({
                'tick': tick + 1,
                'a_cells': a_cells, 'b_cells': b_cells, 'frag_cells': frag_cells,
                'total': eco['total_cells'], 'lineages': eco['n_lineages'],
                'births': snap['births'], 'deaths': snap['deaths'],
                'resource': snap['resource_mean'],
            })

        # Territory map at key moments
        if tick in [0, 499, 999, 1999, 3999, 5999, 7999]:
            print(f"\n--- t={tick+1} Territory ---")
            lmap = t.get_lineage_map()
            for r in range(GRID):
                row = ''
                for c in range(GRID):
                    lid = lmap[r, c]
                    if lid < 0:
                        res = t.resource_field[r, c]
                        row += ' ' if res < 0.35 else '.' if res < 0.6 else ':'
                    elif lid == 1:
                        row += 'A'
                    elif lid == 2:
                        row += 'B'
                    else:
                        row += chr(ord('a') + (lid - 3) % 26)
                print('  ' + row)
            print()

    dt = time.time() - t0
    print("=" * 60)
    print(f"DONE in {dt:.1f}s ({dt/60:.1f}m)")
    print(f"Final: {t.cell_count} cells, {t.total_births} births, {t.total_deaths} deaths")

    # Final analysis
    eco = t.ecosystem_snapshot()
    print("\n--- FINAL LINEAGE ANALYSIS ---")
    obs_dim = CONFIG['observation_dim']
    for lid in sorted(eco['lineages'].keys()):
        d = eco['lineages'][lid]
        # Get action info
        actions = []
        weight_norms = []
        for r in range(GRID):
            for c in range(GRID):
                cell = t.grid[r][c]
                if cell and cell.is_alive and cell.lineage_id == lid:
                    if cell.action is not None:
                        actions.append(cell.action.copy())
                    aw = cell.state.model.weights[obs_dim:, :]
                    weight_norms.append(float(np.linalg.norm(aw)))
        label = 'A' if lid == 1 else ('B' if lid == 2 else f'frag{lid}')
        act_str = ''
        if actions:
            ma = np.mean(actions, axis=0)
            act_str = f' act=[{ma[0]:+.3f},{ma[1]:+.3f},{ma[2]:+.3f},{ma[3]:+.3f}]'
        wn = np.mean(weight_norms) if weight_norms else 0
        print(f"  {label}: n={d['cell_count']:3d} E={d['mean_energy']:.0f} "
              f"ext={d['mean_extraction']:.3f} met={d['mean_metabolic']:.3f} "
              f"wn={wn:.3f}{act_str}")

    # Population trajectory
    print("\n--- POPULATION TRAJECTORY ---")
    for h in history:
        bar_a = '#' * (h['a_cells'] // 2)
        bar_b = '*' * (h['b_cells'] // 2)
        print(f"  t={h['tick']:5d}: A={h['a_cells']:3d} |{bar_a}")
        print(f"          B={h['b_cells']:3d} |{bar_b}")


if __name__ == '__main__':
    run()
