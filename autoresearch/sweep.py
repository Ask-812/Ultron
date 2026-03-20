"""
Parameter sweep engine.

grid_sweep      – exhaustive sweep over parameter combinations with seed averaging
adaptive_sweep  – coarse sweep → find phase boundary → refine → repeat
"""

import numpy as np
import itertools
import time as _time
import json
import os
from datetime import datetime


def grid_sweep(run_fn, base_config, param_grid, n_seeds=3,
               experiment_params=None, save_dir=None, **run_kwargs):
    """
    Run experiment across all combinations of parameters.

    Args:
        run_fn:             Experiment function (run_single / run_population / run_tissue)
        base_config:        Base configuration dict
        param_grid:         Dict of {param_name: [values]} to sweep
        n_seeds:            Random seeds per configuration
        experiment_params:  Set of param names that go to run_fn kwargs
                            instead of config (e.g. {'rows', 'cols'})
        save_dir:           If set, save incremental results here
        **run_kwargs:       Additional kwargs forwarded to run_fn

    Returns:
        List of aggregated result dicts (one per param combination).
    """
    if experiment_params is None:
        experiment_params = set()

    names = list(param_grid.keys())
    combos = list(itertools.product(*param_grid.values()))
    total = len(combos) * n_seeds

    print(f'Sweep: {len(combos)} configs x {n_seeds} seeds = {total} runs')
    print(f'  params: {names}')

    results = []
    t0 = _time.time()

    for i, combo in enumerate(combos):
        params = dict(zip(names, combo))

        # Split params between config and experiment kwargs
        config = base_config.copy()
        local_kwargs = run_kwargs.copy()
        for k, v in params.items():
            if k in experiment_params:
                local_kwargs[k] = v
            else:
                config[k] = v

        # Run across seeds
        seed_results = []
        for s in range(n_seeds):
            seed_val = s * 7 + 42
            try:
                r = run_fn(config, seed=seed_val, **local_kwargs)
            except Exception as e:
                r = _failed_result(str(e))
            seed_results.append(r)

        agg = _aggregate(seed_results, params)
        results.append(agg)

        # Incremental save
        if save_dir:
            _save_incremental(results, save_dir)

        # Progress
        elapsed = _time.time() - t0
        rate = elapsed / ((i + 1) * n_seeds)
        remaining = rate * (total - (i + 1) * n_seeds)
        _print_progress(i + 1, len(combos), params, agg, remaining)

    elapsed = _time.time() - t0
    print(f'\nDone: {elapsed:.1f}s ({elapsed / 60:.1f}m)\n')
    return results


def adaptive_sweep(run_fn, base_config, param_name, initial_range,
                   n_seeds=3, coarse_points=6, refine_points=5,
                   n_refinements=2, **run_kwargs):
    """
    Coarse sweep → detect phase boundary → refine → repeat.

    Returns (all_results, final_boundary_dict_or_None).
    """
    from .analysis import find_phase_boundary

    lo, hi = initial_range
    print(f'Adaptive sweep: {param_name} in [{lo}, {hi}]')
    print(f'  {coarse_points} coarse -> {n_refinements}x refine ({refine_points} pts)')

    values = np.linspace(lo, hi, coarse_points).tolist()
    all_results = grid_sweep(
        run_fn, base_config, {param_name: values},
        n_seeds=n_seeds, **run_kwargs,
    )

    boundary = None
    for _ in range(n_refinements):
        boundary = find_phase_boundary(all_results, param_name)
        if boundary is None:
            print('  No boundary found -- stopping refinement.')
            break
        fine = np.linspace(boundary['low'], boundary['high'], refine_points).tolist()
        print(f'  Refining [{boundary["low"]:.4f}, {boundary["high"]:.4f}]')
        refined = grid_sweep(
            run_fn, base_config, {param_name: fine},
            n_seeds=n_seeds, **run_kwargs,
        )
        all_results.extend(refined)
        # Re-compute boundary on full dataset
        boundary = find_phase_boundary(all_results, param_name)

    return all_results, boundary


# ── internal helpers ────────────────────────────────────────────────

def _aggregate(seed_results, params):
    """Aggregate multiple seed runs into one summary."""
    n = len(seed_results)
    survived = sum(1 for r in seed_results if r.get('survived', False))
    alive = [r for r in seed_results if r.get('survived', False)]

    agg = {
        'params': params,
        'n_seeds': n,
        'survival_rate': survived / n,
        'survival_count': survived,
    }

    if alive:
        agg['mean_energy'] = float(np.mean([
            r.get('mean_energy', r.get('final_energy', 0)) for r in alive
        ]))
        agg['mean_error'] = float(np.mean([
            r.get('mean_error', 0) for r in alive
        ]))
    else:
        agg['mean_energy'] = 0.0
        agg['mean_error'] = 0.0

    # Type-specific metrics
    exp_type = seed_results[0].get('type', '')
    if exp_type == 'tissue':
        agg['mean_cells'] = float(np.mean([r.get('final_cells', 0) for r in seed_results]))
        agg['mean_peak_cells'] = float(np.mean([r.get('peak_cells', 0) for r in seed_results]))
        agg['mean_births'] = float(np.mean([r.get('births', 0) for r in seed_results]))
        agg['mean_deaths'] = float(np.mean([r.get('deaths', 0) for r in seed_results]))
    elif exp_type == 'population':
        if alive:
            agg['mean_fitness'] = float(np.mean([r.get('fitness', 0) for r in alive]))
        else:
            agg['mean_fitness'] = 0.0
        agg['mean_births'] = float(np.mean([r.get('births', 0) for r in seed_results]))
        agg['mean_deaths'] = float(np.mean([r.get('deaths', 0) for r in seed_results]))
    elif exp_type == 'single':
        if alive:
            agg['mean_fitness'] = float(np.mean([r.get('fitness', 0) for r in alive]))
        else:
            agg['mean_fitness'] = 0.0

    agg['runs'] = seed_results
    return agg


def _failed_result(error_msg):
    """Placeholder result for a run that threw an exception."""
    return {
        'type': 'error',
        'survived': False,
        'error': error_msg,
        'final_cells': 0, 'peak_cells': 0,
        'mean_energy': 0, 'mean_error': 0, 'final_energy': 0,
        'births': 0, 'deaths': 0, 'fitness': 0,
        'snapshots': [],
    }


def _print_progress(done, total, params, agg, eta_seconds):
    parts = [f'{k}={v}' for k, v in params.items()]
    param_str = ', '.join(parts)
    surv = f'{agg["survival_rate"]:.0%}'
    energy = f'{agg["mean_energy"]:.1f}'
    extra = ''
    if 'mean_cells' in agg:
        extra = f', cells={agg["mean_cells"]:.0f}'
    print(f'  [{done}/{total}] {param_str} -> surv={surv}, E={energy}{extra}  ({eta_seconds:.0f}s left)')


def _save_incremental(results, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, 'sweep_progress.json')
    compact = [{k: v for k, v in r.items() if k != 'runs'} for r in results]
    with open(path, 'w') as f:
        json.dump(compact, f, indent=2, default=str)
