#!/usr/bin/env python3
"""
TISSUE EXPERIMENT 2: Zygote Growth

Start with ONE cell in the center of an 8×8 grid.
Can it grow into a multicellular organism through division?

The cell needs enough energy to divide (160), so we use a
favorable environment (higher extraction, ordered center).
"""

import sys
import time
import numpy as np
from ultron.tissue import Tissue

CONFIG = {
    'observation_dim': 10,
    'model_dim': 20,
    'initial_energy': 100.0,
    'starting_energy': 150.0,     # Start with more energy for first division
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.40,    # Slightly richer than marginal
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,

    # Tissue: ordered center, noisy edges
    'base_signal_ratio': 0.65,
    'spatial_gradient': 0.25,
    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.005,

    # Division: achievable threshold
    'division_energy_threshold': 160.0,
    'division_cost': 10.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
}

TICKS = 5000
REPORT_INTERVAL = 250


def main():
    np.random.seed(42)

    print('=' * 70, flush=True)
    print('TISSUE EXPERIMENT 2: Zygote Growth (1 cell → ?)', flush=True)
    print('=' * 70, flush=True)
    print(f'Grid: 8×8, starting with 1 cell at center', flush=True)
    print(f'Ticks: {TICKS}', flush=True)
    print(f'Division threshold: {CONFIG["division_energy_threshold"]}', flush=True)
    print(flush=True)

    tissue = Tissue(8, 8, CONFIG)
    tissue.seed_center(n=1)

    print(f't=0: cells={tissue.cell_count}', flush=True)

    t0 = time.time()

    for t in range(TICKS):
        tissue.step()

        if (t + 1) % REPORT_INTERVAL == 0:
            snap = tissue.snapshot()
            elapsed = time.time() - t0
            print(f't={snap["tick"]:5d}: cells={snap["cell_count"]:2d}, '
                  f'E_tot={snap["total_energy"]:7.0f}, '
                  f'E_avg={snap.get("mean_energy", 0):5.1f}, '
                  f'err={snap.get("mean_error", 0):.2f}, '
                  f'b={snap["births"]}, d={snap["deaths"]} '
                  f'[{elapsed:.0f}s]', flush=True)

        # Early termination if organism dies
        if tissue.cell_count == 0:
            print(f't={t}: ALL CELLS DEAD', flush=True)
            break

    print(flush=True)
    print('─' * 70, flush=True)
    print('FINAL STATE', flush=True)
    print('─' * 70, flush=True)

    snap = tissue.snapshot()
    for k, v in snap.items():
        print(f'  {k}: {v}', flush=True)

    # Occupancy map
    print(flush=True)
    print('Occupancy:', flush=True)
    omap = tissue.get_occupancy_map()
    for r in range(8):
        row_str = ' '.join('■' if omap[r, c] else '·' for c in range(8))
        print(f'  {row_str}', flush=True)

    # Energy map
    print(flush=True)
    print('Energy map:', flush=True)
    emap = tissue.get_energy_map()
    for r in range(8):
        row_str = ' '.join(f'{emap[r, c]:5.0f}' if emap[r, c] > 0 else '    .' for c in range(8))
        print(f'  {row_str}', flush=True)

    elapsed = time.time() - t0
    print(flush=True)
    print(f'Total time: {elapsed:.0f}s', flush=True)


if __name__ == '__main__':
    main()
