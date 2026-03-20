"""
Pre-built research campaigns for Ultron.

Each campaign targets a specific scientific question and defines:
  - base_config:  default parameters
  - param_grid:   what to sweep
  - run settings: ticks, grid size, seeds, etc.

Run a campaign:
    from autoresearch.campaigns import run_campaign
    results = run_campaign('tissue_viability')

Or from CLI:
    python -m autoresearch tissue_viability
"""

import numpy as np
import time as _time
from .experiment import run_single, run_population, run_tissue
from .sweep import grid_sweep
from .report import generate_report, save_report, save_results
from .analysis import results_table, find_all_boundaries, suggest_next


# ═══════════════════════════════════════════════════════════════════
# Base configurations
# ═══════════════════════════════════════════════════════════════════

TISSUE_BASE = {
    'env_dim': 8,
    'signal_dim': 4,
    'observation_dim': 12,
    'model_dim': 20,
    'initial_energy': 100.0,
    'starting_energy': 180.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'update_cost_factor': 0.015,
    'learning_rate': 0.05,
    'birth_trait_variation': 0.02,
    'base_signal_ratio': 0.70,
    'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9,
    'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0,
    'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.02,
    'division_energy_threshold': 140.0,
    'division_cost': 30.0,
    'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0,
    'apoptosis_streak': 500,
    # v0.4.0 phenotype
    'phenotype_max_plasticity': 0.05,
    'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001,
    'phenotype_emission_coupling': 2.0,
    'phenotype_affinity_coupling': 2.0,
    # v0.5.0 environment & motility
    'resource_depletion_rate': 0.0,
    'resource_regen_rate': 0.0,
    'migration_energy_cost': 2.0,
    'migration_resource_threshold': 0.5,
    'displacement_energy_ratio': 3.0,
    # v0.6.0 action coupling
    'action_dim': 0,
    'action_division_coupling': 0.0,
    'action_weight_scale': 0.1,
    'action_mutation_rate': 0.02,
    # v0.7.0 landscape, fragmentation, stigmergy
    'landscape_type': 'uniform',
    'landscape_base': 0.3,
    'fragmentation_enabled': False,
    'fragmentation_interval': 100,
    'fragmentation_min_size': 5,
    'death_imprint_strength': 1.0,
    'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.0,
    'stigmergy_avoidance': 0.0,
    # v0.8.0 predation
    'predation_enabled': False,
    'predation_energy_ratio': 2.0,
    'predation_efficiency': 0.5,
    'predation_cooldown': 10,
    'predation_action_threshold': 0.0,
    'predation_action_power': 0.0,
    'predation_evasion_scaling': 0.0,
    'predation_alarm_strength': 0.0,
    # v0.9.0 toxins & Lamarckian inheritance
    'toxin_enabled': False,
    'toxin_emission_rate': 0.1,
    'toxin_damage_rate': 0.5,
    'toxin_range': 3,
    'toxin_cost_rate': 0.1,
    'weight_inheritance_ratio': 0.0,
    'weight_inheritance_noise': 0.01,
    # v1.0.0 quorum sensing & toxin resistance
    'quorum_sensing_enabled': False,
    'quorum_threshold': 4,
    'quorum_boost': 0.3,
    'quorum_radius': 2,
    'toxin_resistance_scaling': 0.0,
}

POPULATION_BASE = {
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
    'initial_pop': 20,
    'max_pop': 60,
    'reproduction_threshold': 120.0,
    'carrying_capacity': 30,
}

SINGLE_BASE = {
    'observation_dim': 8,
    'model_dim': 16,
    'initial_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.08,
    'update_cost_factor': 0.02,
    'learning_rate': 0.05,
}


# ═══════════════════════════════════════════════════════════════════
# Campaign definitions
# ═══════════════════════════════════════════════════════════════════

CAMPAIGNS = {

    # ── Tissue campaigns (multicellular frontier) ───────────────

    'tissue_viability': {
        'description': (
            'Map which (extraction_factor × base_signal_ratio) regions '
            'support multicellular tissue growth from a single zygote.'
        ),
        'experiment_fn': run_tissue,
        'base_config': TISSUE_BASE,
        'param_grid': {
            'extraction_factor': [0.30, 0.40, 0.50, 0.60, 0.70, 0.80],
            'base_signal_ratio': [0.40, 0.55, 0.70, 0.85],
        },
        'run_kwargs': {
            'rows': 12, 'cols': 12, 'ticks': 5000,
            'seed_mode': 'center', 'seed_n': 1,
        },
        'n_seeds': 3,
    },

    'tissue_growth_dynamics': {
        'description': (
            'How do division_cost and energy_leak_rate affect '
            'tissue growth patterns and final morphology?'
        ),
        'experiment_fn': run_tissue,
        'base_config': {
            **TISSUE_BASE,
            'extraction_factor': 0.60,
            'base_signal_ratio': 0.70,
        },
        'param_grid': {
            'division_cost': [5.0, 15.0, 30.0, 50.0],
            'energy_leak_rate': [0.0, 0.01, 0.02, 0.05],
        },
        'run_kwargs': {
            'rows': 12, 'cols': 12, 'ticks': 5000,
            'seed_mode': 'center', 'seed_n': 1,
        },
        'n_seeds': 3,
    },

    'tissue_morphogen': {
        'description': (
            'How do signal propagation parameters (signal_hop_decay, '
            'signal_emission_strength) affect tissue organization?'
        ),
        'experiment_fn': run_tissue,
        'base_config': {
            **TISSUE_BASE,
            'extraction_factor': 0.60,
            'base_signal_ratio': 0.70,
        },
        'param_grid': {
            'signal_hop_decay': [0.5, 0.7, 0.85, 0.95],
            'signal_emission_strength': [0.1, 0.3, 0.5, 1.0],
        },
        'run_kwargs': {
            'rows': 12, 'cols': 12, 'ticks': 5000,
            'seed_mode': 'center', 'seed_n': 1,
        },
        'n_seeds': 3,
    },

    'tissue_scale': {
        'description': (
            'Does grid size affect viability? Compare 6×6, 10×10, '
            '14×14, 20×20 grids at varying extraction factors.'
        ),
        'type': 'multi_grid',
        'experiment_fn': run_tissue,
        'base_config': {
            **TISSUE_BASE,
            'base_signal_ratio': 0.70,
        },
        'param_grid': {
            'extraction_factor': [0.40, 0.50, 0.60, 0.70],
        },
        'grid_sizes': [(6, 6), (10, 10), (14, 14), (20, 20)],
        'run_kwargs': {
            'ticks': 5000, 'seed_mode': 'center', 'seed_n': 1,
        },
        'n_seeds': 3,
    },

    'tissue_seeding': {
        'description': (
            'Compare seeding strategies: single zygote vs. '
            'small cluster (4 cells) vs. full grid.'
        ),
        'type': 'multi_seed',
        'experiment_fn': run_tissue,
        'base_config': {
            **TISSUE_BASE,
            'base_signal_ratio': 0.70,
        },
        'param_grid': {
            'extraction_factor': [0.40, 0.50, 0.60, 0.70],
        },
        'seed_configs': [
            {'seed_mode': 'center', 'seed_n': 1, 'label': 'zygote_1'},
            {'seed_mode': 'center', 'seed_n': 4, 'label': 'cluster_4'},
            {'seed_mode': 'full', 'seed_n': 1, 'label': 'full_grid'},
        ],
        'run_kwargs': {
            'rows': 12, 'cols': 12, 'ticks': 5000,
        },
        'n_seeds': 3,
    },

    # ── Population campaigns ────────────────────────────────────

    'population_evolution': {
        'description': (
            'Map population viability across extraction_factor × '
            'signal_ratio in competitive evolution.'
        ),
        'experiment_fn': run_population,
        'base_config': POPULATION_BASE,
        'param_grid': {
            'extraction_factor': [0.25, 0.30, 0.35, 0.40, 0.50],
            'signal_ratio': [0.45, 0.55, 0.65, 0.80],
        },
        'run_kwargs': {'ticks': 200000},
        'n_seeds': 3,
    },

    # ── Single-organism campaigns ───────────────────────────────

    'single_viability': {
        'description': (
            'Map single-organism survival across extraction_factor × '
            'signal_ratio for baseline comparison.'
        ),
        'experiment_fn': run_single,
        'base_config': SINGLE_BASE,
        'param_grid': {
            'extraction_factor': [0.20, 0.25, 0.30, 0.35, 0.40, 0.50],
            'signal_ratio': [0.40, 0.50, 0.60, 0.70, 0.80, 1.00],
        },
        'run_kwargs': {'ticks': 50000},
        'n_seeds': 5,
    },
}


# ═══════════════════════════════════════════════════════════════════
# Campaign runners
# ═══════════════════════════════════════════════════════════════════

def list_campaigns():
    """Print available campaigns with run estimates."""
    print('╔══════════════════════════════════════════════════════════╗')
    print('║          ULTRON AutoResearch v1.0                       ║')
    print('╚══════════════════════════════════════════════════════════╝')
    print()

    for name, camp in CAMPAIGNS.items():
        grid = camp.get('param_grid', {})
        n_combos = 1
        for v in grid.values():
            n_combos *= len(v)

        # Handle multi-variant campaigns
        multiplier = 1
        if 'grid_sizes' in camp:
            multiplier = len(camp['grid_sizes'])
        elif 'seed_configs' in camp:
            multiplier = len(camp['seed_configs'])

        n_seeds = camp.get('n_seeds', 3)
        total = n_combos * multiplier * n_seeds

        print(f'  {name}')
        print(f'    {camp["description"]}')
        print(f'    {total} total runs')
        print()


def run_campaign(name, override_config=None, override_seeds=None,
                 override_ticks=None):
    """
    Run a named campaign:  sweep → analyze → report → save.

    Returns the list of aggregated results.
    """
    if name not in CAMPAIGNS:
        print(f'Unknown campaign: {name}')
        list_campaigns()
        return None

    camp = CAMPAIGNS[name]
    print(f'{"═" * 60}')
    print(f'  AutoResearch: {name}')
    print(f'  {camp["description"]}')
    print(f'{"═" * 60}')
    print()

    base_config = camp['base_config'].copy()
    if override_config:
        base_config.update(override_config)

    n_seeds = override_seeds or camp.get('n_seeds', 3)
    run_kwargs = camp.get('run_kwargs', {}).copy()
    if override_ticks:
        run_kwargs['ticks'] = override_ticks

    t0 = _time.time()
    camp_type = camp.get('type', 'standard')

    # ── Multi-grid campaign ─────────────────────────────────────
    if camp_type == 'multi_grid':
        all_results = {}
        for rows, cols in camp['grid_sizes']:
            label = f'{rows}x{cols}'
            print(f'\n── Grid: {label} ──')
            kw = {**run_kwargs, 'rows': rows, 'cols': cols}
            results = grid_sweep(
                camp['experiment_fn'], base_config,
                camp['param_grid'], n_seeds=n_seeds, **kw,
            )
            all_results[label] = results

        elapsed = _time.time() - t0
        report = _multi_report(name, camp, all_results, base_config, elapsed)
        save_report(report, name)
        _save_multi_results(all_results, name)
        print(report)
        return all_results

    # ── Multi-seed-config campaign ──────────────────────────────
    if camp_type == 'multi_seed':
        all_results = {}
        for sc in camp['seed_configs']:
            label = sc['label']
            kw = {**run_kwargs,
                   'seed_mode': sc['seed_mode'],
                   'seed_n': sc.get('seed_n', 1)}
            print(f'\n── Seeding: {label} ──')
            results = grid_sweep(
                camp['experiment_fn'], base_config,
                camp['param_grid'], n_seeds=n_seeds, **kw,
            )
            all_results[label] = results

        elapsed = _time.time() - t0
        report = _multi_report(name, camp, all_results, base_config, elapsed)
        save_report(report, name)
        _save_multi_results(all_results, name)
        print(report)
        return all_results

    # ── Standard grid sweep ─────────────────────────────────────
    results = grid_sweep(
        camp['experiment_fn'], base_config,
        camp['param_grid'], n_seeds=n_seeds, **run_kwargs,
    )

    elapsed = _time.time() - t0
    report = generate_report(name, results, base_config, elapsed)
    save_report(report, name)
    save_results(results, name)
    print()
    print(report)
    return results


# ── helpers ─────────────────────────────────────────────────────

def _multi_report(name, camp, all_results, config_used, elapsed):
    """Build a report for campaigns that produce multiple result sets."""
    lines = [
        f'# AutoResearch Report: {name}',
        '',
        f'**Date:** {_time.strftime("%Y-%m-%d %H:%M")}  ',
        f'**Duration:** {elapsed:.1f}s ({elapsed / 60:.1f}m)  ',
        f'**Description:** {camp["description"]}',
        '',
    ]

    for label, results in all_results.items():
        lines.append(f'## {label}')
        lines.append('```')
        lines.append(results_table(results))
        lines.append('```')

        boundaries = find_all_boundaries(results)
        if boundaries:
            for b in boundaries:
                lines.append(
                    f'- Phase boundary: **{b["param"]}** ≈ '
                    f'{b["boundary"]:.4f}'
                )
        lines.append('')

    # Suggestions across all conditions
    all_flat = [r for rs in all_results.values() for r in rs]
    boundaries = find_all_boundaries(all_flat)
    suggestions = suggest_next(all_flat, boundaries)
    lines.append('## Suggested Next Experiments')
    for i, s in enumerate(suggestions, 1):
        lines.append(f'{i}. {s}')
    lines.append('')

    return '\n'.join(lines)


def _save_multi_results(all_results, name):
    """Save multi-variant results as JSON."""
    import os, json
    from .report import REPORT_DIR
    from datetime import datetime

    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(REPORT_DIR, f'{name}_{ts}.json')

    out = {}
    for label, results in all_results.items():
        out[label] = [{k: v for k, v in r.items() if k != 'runs'}
                      for r in results]

    with open(path, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f'Results saved → {path}')
