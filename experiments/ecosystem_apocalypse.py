"""
APOCALYPSE EXPERIMENT
=====================
Phase 1 (t=0-3000): Four organisms grow on four resource patches.
Phase 2 (t=3000): Two patches are DESTROYED (resources set to 0).
Phase 3 (t=3000-8000): Which organisms survive? Do they migrate?
                        Does the ecosystem recover?

This tests genuine resilience — an environmental catastrophe that was
never anticipated. Organisms must adapt or die.
"""
import numpy as np
import time
import os
from ultron.tissue import Tissue

GRID = 35
TOTAL_TICKS = 8000
CATASTROPHE_TICK = 3000

CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12,
    'starting_energy': 150.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.65,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.03,
    'division_energy_threshold': 95.0, 'division_cost': 12.0,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 100,   # Die fast when starving — makes catastrophe lethal
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
    'landscape_patch_centers': [(9, 9), (9, 25), (25, 9), (25, 25)],
    'fragmentation_enabled': True, 'fragmentation_interval': 100,
    'fragmentation_min_size': 5,
    'displacement_energy_ratio': 2.5,
    # Stigmergy: dying cells leave traces
    'death_imprint_strength': 2.0,
    'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.5,
    'stigmergy_avoidance': 0.3,
}


def territory_map(tissue, show_resources=False):
    """Generate ASCII territory map."""
    lmap = tissue.get_lineage_map()
    symbols = '.ABCD' + 'efghijklmnopqrstuvwxyz0123456789'
    lines = []
    for r in range(tissue.rows):
        row = ''
        for c in range(tissue.cols):
            lid = lmap[r, c]
            if lid < 0:
                if show_resources:
                    res = tissue.resource_field[r, c]
                    row += ' ' if res < 0.2 else '.' if res < 0.4 else ':' if res < 0.7 else '#'
                else:
                    row += ' '
            elif lid <= 4:
                row += symbols[lid]
            else:
                row += symbols[min(lid, len(symbols) - 1)]
        lines.append(row)
    return '\n'.join(lines)


def count_by_lineage(tissue, original_only=True):
    """Count cells grouped by lineage."""
    counts = {}
    for r in range(tissue.rows):
        for c in range(tissue.cols):
            cell = tissue.grid[r][c]
            if cell and cell.is_alive:
                lid = cell.lineage_id
                counts[lid] = counts.get(lid, 0) + 1
    if original_only:
        return {lid: counts.get(lid, 0) for lid in [1, 2, 3, 4]}
    return counts


def run():
    np.random.seed(13)
    tissue = Tissue(GRID, GRID, CONFIG)

    # Place 4 founders at patch centers
    founders = [(9, 9, 1), (9, 25, 2), (25, 9, 3), (25, 25, 4)]
    for row, col, lid in founders:
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r, c = row + dr, col + dc
                if 0 <= r < GRID and 0 <= c < GRID:
                    tissue.place_cell(r, c)
                    tissue.grid[r][c].lineage_id = lid

    print("=" * 70)
    print("  ULTRON APOCALYPSE EXPERIMENT")
    print("  Grid: %dx%d | Total ticks: %d | Catastrophe at t=%d" %
          (GRID, GRID, TOTAL_TICKS, CATASTROPHE_TICK))
    print("  Patches at: (9,9) (9,25) (25,9) (25,25)")
    print("  Catastrophe: patches at (9,9) and (25,25) DESTROYED at t=%d" %
          CATASTROPHE_TICK)
    print("=" * 70)

    print("\n--- INITIAL STATE ---")
    print(territory_map(tissue, show_resources=True))

    history = []
    t0 = time.time()

    for tick in range(TOTAL_TICKS):
        # === CATASTROPHE: DESTROY TWO PATCHES AT t=3000 ===
        if tick == CATASTROPHE_TICK:
            print("\n" + "!" * 70)
            print("  CATASTROPHE! Patches at (9,9) and (25,25) DESTROYED!")
            print("!" * 70)
            # Destroy resource patches (set to desert level)
            patch_r = int(0.22 * min(GRID, GRID))
            for pr, pc in [(9, 9), (25, 25)]:
                for r in range(GRID):
                    for c in range(GRID):
                        dist = np.sqrt((r - pr)**2 + (c - pc)**2)
                        if dist < patch_r:
                            tissue.resource_field[r, c] = 0.05  # Near-zero
                            # Also update capacity so it doesn't regenerate
                            if hasattr(tissue, '_landscape_capacity'):
                                tissue._landscape_capacity[r, c] = 0.05

            print("\n--- POST-CATASTROPHE RESOURCES ---")
            print(territory_map(tissue, show_resources=True))

        tissue.step()

        if tick % 250 == 0 or tick == TOTAL_TICKS - 1 or tick == CATASTROPHE_TICK + 1:
            eco = tissue.ecosystem_snapshot()
            snap = tissue.snapshot()
            counts = count_by_lineage(tissue)
            all_counts = count_by_lineage(tissue, original_only=False)
            n_frags = sum(1 for lid in all_counts if lid > 4)
            frag_cells = sum(v for lid, v in all_counts.items() if lid > 4)
            dt = time.time() - t0

            phase = "GROWTH" if tick < CATASTROPHE_TICK else "AFTERMATH"
            stig_mag = float(np.linalg.norm(tissue.stigmergy_field))

            print(f"[{phase:9s}] t={tick:5d} | "
                  f"A={counts[1]:3d} B={counts[2]:3d} C={counts[3]:3d} D={counts[4]:3d} "
                  f"frag={frag_cells:3d}({n_frags}) | "
                  f"total={eco['total_cells']:4d} | "
                  f"births={snap['births']:4d} deaths={snap['deaths']:4d} | "
                  f"res={snap['resource_mean']:.3f} stig={stig_mag:.2f} | "
                  f"{dt:.0f}s")

            history.append({
                'tick': tick, 'phase': phase,
                'A': counts[1], 'B': counts[2], 'C': counts[3], 'D': counts[4],
                'frags': frag_cells, 'total': eco['total_cells'],
                'births': snap['births'], 'deaths': snap['deaths'],
                'resource': snap['resource_mean'], 'stigmergy': stig_mag,
            })

        # Territory maps at key moments
        if tick in [0, 999, 2999, CATASTROPHE_TICK + 1, CATASTROPHE_TICK + 500,
                    CATASTROPHE_TICK + 1000, 4999, 5999, 7999]:
            print(f"\n--- TERRITORY t={tick+1} ---")
            print(territory_map(tissue))
            print()

    dt = time.time() - t0
    print("\n" + "=" * 70)
    print("  EXPERIMENT COMPLETE: %.1fs (%.1fm)" % (dt, dt / 60))
    print("=" * 70)

    # === NARRATIVE ANALYSIS ===
    print("\n" + "=" * 70)
    print("  NARRATIVE: THE STORY OF SURVIVAL")
    print("=" * 70)

    # Pre-catastrophe state
    pre = [h for h in history if h['tick'] < CATASTROPHE_TICK]
    post = [h for h in history if h['tick'] >= CATASTROPHE_TICK]

    if pre:
        peak = max(pre, key=lambda h: h['total'])
        print(f"\n  PRE-CATASTROPHE PEAK (t={peak['tick']}):")
        print(f"    Total cells: {peak['total']}")
        print(f"    A={peak['A']} B={peak['B']} C={peak['C']} D={peak['D']}")

    # Immediate aftermath
    if post and len(post) > 1:
        impact = post[0]
        print(f"\n  IMPACT (t={impact['tick']}):")
        print(f"    Total cells: {impact['total']}")
        print(f"    Deaths so far: {impact['deaths']}")
        print(f"    A={impact['A']} (patch DESTROYED)")
        print(f"    D={impact['D']} (patch DESTROYED)")
        print(f"    B={impact['B']} (patch intact)")
        print(f"    C={impact['C']} (patch intact)")

    # Recovery
    if post:
        final = post[-1]
        print(f"\n  FINAL STATE (t={final['tick']}):")
        print(f"    Total cells: {final['total']}")
        print(f"    Total deaths: {final['deaths']}")
        print(f"    A={final['A']} {'SURVIVED' if final['A'] > 0 else 'EXTINCT'}")
        print(f"    B={final['B']} {'SURVIVED' if final['B'] > 0 else 'EXTINCT'}")
        print(f"    C={final['C']} {'SURVIVED' if final['C'] > 0 else 'EXTINCT'}")
        print(f"    D={final['D']} {'SURVIVED' if final['D'] > 0 else 'EXTINCT'}")
        print(f"    Fragment organisms: {final['frags']} cells")

    # Did organisms A and D survive the destruction of their patches?
    print("\n  KEY QUESTION: Did organisms on destroyed patches survive?")
    if post:
        final = post[-1]
        if final['A'] > 0 and final['D'] > 0:
            print("  ANSWER: YES - Both A and D survived patch destruction!")
            print("  This demonstrates genuine resilience — organisms adapted to")
            print("  environmental catastrophe through migration and energy buffering.")
        elif final['A'] > 0 or final['D'] > 0:
            survivor = 'A' if final['A'] > 0 else 'D'
            extinct = 'D' if final['A'] > 0 else 'A'
            print(f"  ANSWER: PARTIAL - {survivor} survived but {extinct} went extinct.")
            print(f"  Survival depended on proximity to intact resources.")
        else:
            print("  ANSWER: NO - Both went extinct. The catastrophe was lethal.")
            print("  Organisms could not adapt quickly enough to total resource loss.")

    # Stigmergy narrative
    if post and post[-1]['stigmergy'] > 0.1:
        print(f"\n  STIGMERGY: Death traces accumulated ({post[-1]['stigmergy']:.2f} total)")
        print("  Dead cells left chemical imprints that surviving cells can sense.")
        print("  This creates a collective spatial memory of dangerous zones.")

    print("\n--- FINAL TERRITORY ---")
    print(territory_map(tissue, show_resources=True))

    # Population timeline
    print("\n--- POPULATION TIMELINE ---")
    for h in history:
        total = h['total']
        bar = '#' * (total // 3)
        marker = ' <<<< CATASTROPHE' if h['tick'] == CATASTROPHE_TICK else ''
        print(f"  t={h['tick']:5d}: [{total:4d}] |{bar}{marker}")


if __name__ == '__main__':
    run()
