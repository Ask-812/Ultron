#!/usr/bin/env python3
"""
TISSUE EXPERIMENT 1: Can an 8×8 tissue survive?

Fill an 8×8 grid with cells. Run 2000 ticks.
Watch: cell count, energy distribution, signal fields, specialization.
"""

import sys
import time
import numpy as np
from ultron.tissue import Tissue

CONFIG = {
    # Cell parameters (same as single-cell Ultron)
    'observation_dim': 10,       # 8 env dims + 2 signal dims
    'model_dim': 20,
    'initial_energy': 100.0,
    'starting_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.35,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,

    # Tissue parameters
    'base_signal_ratio': 0.55,
    'spatial_gradient': 0.20,
    'diffusion_rate': 0.15,
    'signal_decay': 0.03,
    'energy_leak_rate': 0.005,

    # Division / apoptosis
    'division_energy_threshold': 160.0,
    'division_cost': 10.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 300,
}

TICKS = 2000
REPORT_INTERVAL = 200


def main():
    np.random.seed(42)

    print('=' * 70, flush=True)
    print('TISSUE EXPERIMENT 1: 8×8 Full Grid Survival', flush=True)
    print('=' * 70, flush=True)
    print(f'Grid: 8×8 = 64 cells', flush=True)
    print(f'Ticks: {TICKS}', flush=True)
    print(f'Signal ratio: center ~0.65, edge ~0.35', flush=True)
    print(flush=True)

    tissue = Tissue(8, 8, CONFIG)
    tissue.seed_full()

    print(f't=0: cells={tissue.cell_count}, energy={tissue.total_energy:.0f}', flush=True)

    t0 = time.time()

    for t in range(TICKS):
        tissue.step()

        if (t + 1) % REPORT_INTERVAL == 0:
            snap = tissue.snapshot()
            elapsed = time.time() - t0
            print(f't={snap["tick"]:5d}: cells={snap["cell_count"]:2d}, '
                  f'E_tot={snap["total_energy"]:7.0f}, '
                  f'E_avg={snap.get("mean_energy", 0):5.1f}±{snap.get("std_energy", 0):4.1f}, '
                  f'err={snap.get("mean_error", 0):.2f}, '
                  f'b={snap["births"]}, d={snap["deaths"]}, '
                  f'A={snap.get("chemoA_max", 0):.2f}, B={snap.get("chemoB_max", 0):.2f} '
                  f'[{elapsed:.0f}s]', flush=True)

    print(flush=True)
    print('─' * 70, flush=True)
    print('FINAL STATE', flush=True)
    print('─' * 70, flush=True)

    snap = tissue.snapshot()
    for k, v in snap.items():
        print(f'  {k}: {v}', flush=True)

    # Energy map
    print(flush=True)
    print('Energy map (rounded):', flush=True)
    emap = tissue.get_energy_map()
    for r in range(8):
        row_str = ' '.join(f'{emap[r, c]:5.0f}' if emap[r, c] > 0 else '    .' for c in range(8))
        print(f'  {row_str}', flush=True)

    # Occupancy
    print(flush=True)
    print('Occupancy:', flush=True)
    omap = tissue.get_occupancy_map()
    for r in range(8):
        row_str = ' '.join('■' if omap[r, c] else '·' for c in range(8))
        print(f'  {row_str}', flush=True)

    elapsed = time.time() - t0
    print(flush=True)
    print(f'Total time: {elapsed:.0f}s', flush=True)


if __name__ == '__main__':
    main()
