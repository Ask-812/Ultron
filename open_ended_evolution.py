#!/usr/bin/env python3
"""
OPEN-ENDED EVOLUTION EXPERIMENT

Three conditions, same physics, same initial population:
  1. STATIC   — fixed signal_ratio=0.55
  2. OSCILLATING — signal_ratio = 0.45 + 0.20 × sin(t / 50000)
  3. CHAOTIC  — signal_ratio redrawn every 10000 ticks from U(0.30, 0.70)

Question: Does Ultron support open-ended evolution,
          or only finite optimization?

Metrics tracked per condition:
  - mean fitness over time
  - trait diversity (std of extraction, metabolic, learning)
  - population size
  - birth/death rates
  - generation depth
  - whether evolution plateaus or continues
"""

from ultron import create_ultron, tick, reproduce
from ultron.environments import MixedEnvironment
import numpy as np
import json
from datetime import datetime

# ─── Shared parameters ───────────────────────────────────────────────
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

TICKS = 2_000_000
MAX_POP = 60
REPRODUCTION_THRESHOLD = 120.0
CARRYING_CAPACITY = 30
INITIAL_POP = 20
SAMPLE_INTERVAL = 25_000
REPORT_INTERVAL = 100_000
SEED = 42


# ─── Environment strategies ─────────────────────────────────────────
def static_ratio(t):
    return 0.55

def oscillating_ratio(t):
    return 0.45 + 0.20 * np.sin(t / 50000)

class ChaioticRatio:
    def __init__(self, rng):
        self._rng = rng
        self._current = 0.55
        self._next_change = 0
    def __call__(self, t):
        if t >= self._next_change:
            self._current = self._rng.uniform(0.30, 0.70)
            self._next_change = t + 10000
        return self._current


# ─── Run one condition ───────────────────────────────────────────────
def run_condition(name, ratio_fn, seed):
    """Run a full evolutionary simulation under one environment strategy."""
    rng = np.random.RandomState(seed)
    np.random.seed(seed)

    population = [create_ultron(CONFIG) for _ in range(INITIAL_POP)]
    gens = [0] * INITIAL_POP
    births = 0
    deaths = 0

    samples = []

    for t in range(TICKS):
        if not population:
            print(f'  [{name}] t={t}: EXTINCTION')
            samples.append({
                'tick': t, 'pop': 0, 'extinct': True,
            })
            break

        # Environment for this tick
        sr = ratio_fn(t)
        env = MixedEnvironment(8, signal_ratio=sr)
        obs = env.get_input(t)
        competition = min(1.0, CARRYING_CAPACITY / max(1, len(population)))

        # Tick all organisms
        for i in range(len(population)):
            if population[i].is_alive:
                comp_config = CONFIG.copy()
                comp_config['extraction_factor'] = CONFIG['extraction_factor'] * competition
                population[i] = tick(population[i], obs, comp_config)

        # Remove dead
        alive = []
        alive_gens = []
        for i, p in enumerate(population):
            if p.is_alive:
                alive.append(p)
                alive_gens.append(gens[i])
            else:
                deaths += 1

        # Reproduction
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

        # Sample
        if t > 0 and t % SAMPLE_INTERVAL == 0:
            if population:
                ext = [p.traits.extraction_efficiency for p in population]
                met = [p.traits.metabolic_rate for p in population]
                lrn = [p.traits.learning_capacity for p in population]
                fit = [e / m for e, m in zip(ext, met)]
                energies = [p.energy.current for p in population]

                sample = {
                    'tick': t,
                    'pop': len(population),
                    'signal_ratio': sr,
                    'mean_fitness': float(np.mean(fit)),
                    'std_fitness': float(np.std(fit)),
                    'mean_extraction': float(np.mean(ext)),
                    'std_extraction': float(np.std(ext)),
                    'mean_metabolic': float(np.mean(met)),
                    'std_metabolic': float(np.std(met)),
                    'mean_learning': float(np.mean(lrn)),
                    'std_learning': float(np.std(lrn)),
                    'mean_energy': float(np.mean(energies)),
                    'births': births,
                    'deaths': deaths,
                    'max_gen': max(gens) if gens else 0,
                }
                samples.append(sample)

                if t % REPORT_INTERVAL == 0:
                    print(f'  [{name}] t={t//1000}K: pop={len(population):2d}, '
                          f'fit={np.mean(fit):.4f}±{np.std(fit):.4f}, '
                          f'b={births}, d={deaths}, gen={max(gens)}, '
                          f'sr={sr:.3f}', flush=True)

    return samples, births, deaths


# ─── Main ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 70)
    print('OPEN-ENDED EVOLUTION: THREE-WAY COMPARISON')
    print('=' * 70)
    print(f'Ticks per condition: {TICKS:,}')
    print(f'Initial pop: {INITIAL_POP}, Carrying cap: {CARRYING_CAPACITY}')
    print(f'Reproduction threshold: {REPRODUCTION_THRESHOLD}')
    print(f'Mutation rate: {CONFIG["mutation_rate"]}')
    print()

    results = {}

    # ── 1. Static ────────────────────────────────────────────────────
    print('─' * 70)
    print('CONDITION 1: STATIC (signal_ratio=0.55)')
    print('─' * 70)
    s1, b1, d1 = run_condition('STATIC', static_ratio, SEED)
    results['static'] = {'samples': s1, 'births': b1, 'deaths': d1}
    print()

    # ── 2. Oscillating ───────────────────────────────────────────────
    print('─' * 70)
    print('CONDITION 2: OSCILLATING (0.45 + 0.20×sin(t/50000))')
    print('─' * 70)
    s2, b2, d2 = run_condition('OSCIL', oscillating_ratio, SEED)
    results['oscillating'] = {'samples': s2, 'births': b2, 'deaths': d2}
    print()

    # ── 3. Chaotic ───────────────────────────────────────────────────
    print('─' * 70)
    print('CONDITION 3: CHAOTIC (random ratio every 10K ticks)')
    print('─' * 70)
    chaotic_rng = np.random.RandomState(SEED + 1)
    s3, b3, d3 = run_condition('CHAOS', ChaioticRatio(chaotic_rng), SEED)
    results['chaotic'] = {'samples': s3, 'births': b3, 'deaths': d3}
    print()

    # ── Comparison ───────────────────────────────────────────────────
    print('=' * 70)
    print('COMPARISON')
    print('=' * 70)

    for cond_name in ['static', 'oscillating', 'chaotic']:
        data = results[cond_name]
        samples = data['samples']
        if not samples or samples[-1].get('extinct'):
            print(f'  {cond_name:12s}: EXTINCT')
            continue

        last = samples[-1]
        first_fit = samples[0]['mean_fitness'] if samples else 0
        last_fit = last['mean_fitness']
        delta_fit = last_fit - first_fit

        # Check for plateau: did fitness change in last 20% of run?
        n = len(samples)
        late_start = int(n * 0.8)
        late_samples = samples[late_start:]
        if len(late_samples) >= 2:
            late_fits = [s['mean_fitness'] for s in late_samples]
            late_slope = (late_fits[-1] - late_fits[0]) / max(1, late_samples[-1]['tick'] - late_samples[0]['tick'])
        else:
            late_slope = 0

        # Trait diversity at end
        ext_div = last.get('std_extraction', 0)
        met_div = last.get('std_metabolic', 0)

        print(f'  {cond_name:12s}: '
              f'fit={last_fit:.4f} (Δ={delta_fit:+.4f}), '
              f'pop={last["pop"]}, '
              f'b={data["births"]}, d={data["deaths"]}, '
              f'gen={last["max_gen"]}, '
              f'ext_div={ext_div:.4f}, met_div={met_div:.4f}, '
              f'late_slope={late_slope:.2e}')

    print()

    # ── Diagnosis ────────────────────────────────────────────────────
    for cond_name in ['static', 'oscillating', 'chaotic']:
        data = results[cond_name]
        samples = data['samples']
        if not samples or samples[-1].get('extinct'):
            continue
        n = len(samples)
        late_start = int(n * 0.8)
        late_samples = samples[late_start:]
        if len(late_samples) >= 2:
            late_fits = [s['mean_fitness'] for s in late_samples]
            late_slope = (late_fits[-1] - late_fits[0]) / max(1, late_samples[-1]['tick'] - late_samples[0]['tick'])
        else:
            late_slope = 0

        if abs(late_slope) < 1e-9:
            verdict = 'PLATEAU (evolutionary equilibrium)'
        elif late_slope > 1e-9:
            verdict = 'STILL EVOLVING (open-ended?)'
        else:
            verdict = 'DECLINING (evolutionary collapse?)'
        print(f'  {cond_name:12s}: {verdict}')

    # ── Save ─────────────────────────────────────────────────────────
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    outfile = f'history/open_ended_evolution_{ts}.json'
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f'\nSaved to {outfile}')
