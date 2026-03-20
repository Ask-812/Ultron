"""
Experiment runners for Ultron autoresearch.

Three experiment types:
  - run_single:      One organism, one environment
  - run_population:  Population with reproduction and selection
  - run_tissue:      Multicellular tissue growth on a 2D grid

Each returns a standardized result dict with survival status,
energy/error metrics, and periodic snapshots.
"""

import numpy as np
import time as _time
from ultron import create_ultron, tick, reproduce
from ultron.environments import MixedEnvironment
from ultron.tissue import Tissue


def run_single(config, ticks=10000, seed=None, **_kwargs):
    """
    Run a single organism for `ticks` steps.

    Reads 'signal_ratio' from config (default 0.55) to build the environment.
    Returns a result dict.
    """
    if seed is not None:
        np.random.seed(seed)

    obs_dim = config.get('observation_dim', 8)
    sr = config.get('signal_ratio', 0.55)
    env = MixedEnvironment(obs_dim, signal_ratio=sr)
    state = create_ultron(config)

    snapshots = []
    snap_every = max(1, ticks // 50)

    for t in range(ticks):
        obs = env.get_input(t)
        state = tick(state, obs, config)
        if t % snap_every == 0:
            snapshots.append({
                'tick': t,
                'energy': float(state.energy.current),
                'error': float(state.current.error_magnitude),
            })
        if not state.is_alive:
            break

    alive = state.is_alive
    return {
        'type': 'single',
        'survived': alive,
        'ticks_lived': state.time.tick,
        'final_energy': float(state.energy.current) if alive else 0.0,
        'mean_error': float(
            state.history.accumulated_error / max(1, state.history.survival_ticks)
        ),
        'extraction': float(state.traits.extraction_efficiency),
        'metabolic': float(state.traits.metabolic_rate),
        'fitness': float(
            state.traits.extraction_efficiency / state.traits.metabolic_rate
        ),
        'snapshots': snapshots,
    }


def run_population(config, ticks=100000, seed=None, **_kwargs):
    """
    Run a population with reproduction, competition, and selection.

    Reads from config:
      signal_ratio (0.55), initial_pop (20), max_pop (60),
      reproduction_threshold (120.0), carrying_capacity (30)

    Returns a result dict.
    """
    if seed is not None:
        np.random.seed(seed)

    obs_dim = config.get('observation_dim', 8)
    sr = config.get('signal_ratio', 0.55)
    initial_pop = config.get('initial_pop', 20)
    max_pop = config.get('max_pop', 60)
    repro_thresh = config.get('reproduction_threshold', 120.0)
    carry_cap = config.get('carrying_capacity', 30)

    env = MixedEnvironment(obs_dim, signal_ratio=sr)
    population = [create_ultron(config) for _ in range(initial_pop)]
    gens = [0] * initial_pop
    births = deaths = 0

    snapshots = []
    snap_every = max(1, ticks // 50)

    t = 0
    for t in range(ticks):
        if not population:
            break

        obs = env.get_input(t)
        comp = min(1.0, carry_cap / max(1, len(population)))
        c = config.copy()
        c['extraction_factor'] = config.get('extraction_factor', 0.35) * comp

        for i in range(len(population)):
            if population[i].is_alive:
                population[i] = tick(population[i], obs, c)

        # Remove dead
        for i in range(len(population) - 1, -1, -1):
            if not population[i].is_alive:
                deaths += 1
                population.pop(i)
                gens.pop(i)

        # Reproduction
        if len(population) < max_pop:
            n = len(population)
            for i in range(n):
                if population[i].energy.current >= repro_thresh:
                    _, child = reproduce(population[i], config)
                    if child:
                        population.append(child)
                        gens.append(gens[i] + 1)
                        births += 1

        if t % snap_every == 0 and population:
            fit = [
                p.traits.extraction_efficiency / p.traits.metabolic_rate
                for p in population
            ]
            snapshots.append({
                'tick': t,
                'pop': len(population),
                'fitness': float(np.mean(fit)),
                'energy': float(np.mean([p.energy.current for p in population])),
            })

    result = {
        'type': 'population',
        'survived': len(population) > 0,
        'final_pop': len(population),
        'births': births,
        'deaths': deaths,
        'max_gen': max(gens) if gens else 0,
        'ticks_run': t + 1,
        'snapshots': snapshots,
    }
    if population:
        fit = [
            p.traits.extraction_efficiency / p.traits.metabolic_rate
            for p in population
        ]
        result['fitness'] = float(np.mean(fit))
        result['mean_energy'] = float(
            np.mean([p.energy.current for p in population])
        )
    else:
        result['fitness'] = 0.0
        result['mean_energy'] = 0.0
    return result


def run_tissue(config, ticks=5000, seed=None,
               rows=12, cols=12, seed_mode='center', seed_n=1, **_kwargs):
    """
    Run a multicellular tissue growth experiment.

    The tissue uses config keys 'base_signal_ratio' and 'spatial_gradient'
    internally for its environment.  All other config keys pass through to
    each cell's tick loop.

    Returns a result dict with growth metrics.
    """
    if seed is not None:
        np.random.seed(seed)

    tissue = Tissue(rows, cols, config)
    if seed_mode == 'center':
        tissue.seed_center(n=seed_n)
    elif seed_mode == 'full':
        tissue.seed_full()
    else:
        tissue.seed_center(n=seed_n)

    snapshots = []
    snap_every = max(1, ticks // 50)
    peak_cells = tissue.cell_count

    for t in range(ticks):
        tissue.step()
        if tissue.cell_count > peak_cells:
            peak_cells = tissue.cell_count
        if t % snap_every == 0:
            snapshots.append(tissue.snapshot())
        if tissue.cell_count == 0:
            break

    final = tissue.snapshot()
    return {
        'type': 'tissue',
        'survived': tissue.cell_count > 0,
        'final_cells': tissue.cell_count,
        'peak_cells': peak_cells,
        'mean_energy': final.get('mean_energy', 0),
        'mean_error': final.get('mean_error', 0),
        'births': tissue.total_births,
        'deaths': tissue.total_deaths,
        'ticks_run': tissue.tick_count,
        'grid_size': [rows, cols],
        'snapshots': snapshots,
    }
