#!/usr/bin/env python3
"""
OPEN-ENDED EVOLUTION: Fast comparison (reduced scale).

3 conditions × 200K ticks × 10 organisms.
Should complete in ~20 minutes total.
"""

import sys
import time
from ultron import create_ultron, tick, reproduce
from ultron.environments import MixedEnvironment
import numpy as np

CONFIG = {
    'observation_dim': 8,
    'model_dim': 16,
    'initial_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'extraction_factor': 0.35,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.03,
    'reproduction_cost': 60.0,
    'mutation_rate': 0.015,
}

TICKS = 200_000
MAX_POP = 30
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 15
INITIAL_POP = 10
REPORT_INTERVAL = 25_000
SEED = 42


def static_ratio(t):
    return 0.55

def oscillating_ratio(t):
    return 0.45 + 0.20 * np.sin(t / 50000)

class ChaoticRatio:
    def __init__(self, rng):
        self._rng = rng
        self._current = 0.55
        self._next_change = 0
    def __call__(self, t):
        if t >= self._next_change:
            self._current = self._rng.uniform(0.30, 0.70)
            self._next_change = t + 10000
        return self._current


def run_condition(name, ratio_fn, seed):
    rng = np.random.RandomState(seed)
    np.random.seed(seed)

    population = [create_ultron(CONFIG) for _ in range(INITIAL_POP)]
    gens = [0] * INITIAL_POP
    births = 0
    deaths = 0
    samples = []
    start = time.time()

    for t in range(TICKS):
        if not population:
            print(f'  [{name}] t={t}: EXTINCTION', flush=True)
            break

        sr = ratio_fn(t)
        env = MixedEnvironment(8, signal_ratio=sr)
        obs = env.get_input(t)
        competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))

        for i in range(len(population)):
            if population[i].is_alive:
                comp_config = CONFIG.copy()
                comp_config['extraction_factor'] = CONFIG['extraction_factor'] * competition
                population[i] = tick(population[i], obs, comp_config)

        alive = []
        alive_gens = []
        for i, p in enumerate(population):
            if p.is_alive:
                alive.append(p)
                alive_gens.append(gens[i])
            else:
                deaths += 1

        n = len(alive)
        for i in range(n):
            if alive[i].energy.current >= REPRODUCTION_THRESHOLD and len(alive) < MAX_POP:
                parent, child = reproduce(alive[i], CONFIG)
                if child:
                    alive.append(child)
                    alive_gens.append(alive_gens[i] + 1)
                    births += 1

        population = alive
        gens = alive_gens

        if t > 0 and t % REPORT_INTERVAL == 0 and population:
            ext = [p.traits.extraction_efficiency for p in population]
            met = [p.traits.metabolic_rate for p in population]
            fit = [e / m for e, m in zip(ext, met)]
            energies = [p.energy.current for p in population]

            elapsed = time.time() - start
            print(f'  [{name}] t={t//1000}K: pop={len(population):2d}, '
                  f'fit={np.mean(fit):.4f}±{np.std(fit):.4f}, '
                  f'E={np.mean(energies):.1f}, '
                  f'b={births}, d={deaths}, gen={max(gens)}, '
                  f'sr={sr:.3f} [{elapsed:.0f}s]', flush=True)

            samples.append({
                'tick': t,
                'pop': len(population),
                'mean_fitness': float(np.mean(fit)),
                'std_fitness': float(np.std(fit)),
                'mean_extraction': float(np.mean(ext)),
                'std_extraction': float(np.std(ext)),
                'mean_metabolic': float(np.mean(met)),
                'std_metabolic': float(np.std(met)),
                'mean_energy': float(np.mean(energies)),
                'births': births,
                'deaths': deaths,
                'max_gen': max(gens),
            })

    return samples, births, deaths


if __name__ == '__main__':
    print('=' * 70, flush=True)
    print('OPEN-ENDED EVOLUTION: FAST THREE-WAY COMPARISON', flush=True)
    print('=' * 70, flush=True)
    print(f'Ticks: {TICKS:,}, Pop: {INITIAL_POP}, Cap: {CARRYING_CAPACITY}', flush=True)
    print(flush=True)

    all_results = {}

    for cond_name, ratio_fn in [
        ('STATIC', static_ratio),
        ('OSCIL', oscillating_ratio),
        ('CHAOS', ChaoticRatio(np.random.RandomState(SEED + 1))),
    ]:
        print(f'─── {cond_name} ───', flush=True)
        t0 = time.time()
        samples, b, d = run_condition(cond_name, ratio_fn, SEED)
        elapsed = time.time() - t0
        print(f'  Done in {elapsed:.0f}s. Births={b}, Deaths={d}', flush=True)
        all_results[cond_name] = samples
        print(flush=True)

    # Summary
    print('=' * 70, flush=True)
    print('COMPARISON SUMMARY', flush=True)
    print('=' * 70, flush=True)
    for name, samples in all_results.items():
        if samples:
            last = samples[-1]
            first = samples[0]
            print(f'{name:8s}: fitness {first["mean_fitness"]:.4f} → {last["mean_fitness"]:.4f}, '
                  f'diversity {last["std_fitness"]:.4f}, '
                  f'pop={last["pop"]}, gen={last["max_gen"]}, '
                  f'births={last["births"]}, deaths={last["deaths"]}', flush=True)
        else:
            print(f'{name:8s}: EXTINCT', flush=True)
