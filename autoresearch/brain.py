"""
The Brain — autonomous hypothesis generation and experiment design.

This is the core intelligence of autoresearch. It reads the journal
(all past findings, knowledge, open questions) and decides:
  1. What hypothesis to generate next
  2. How to design an experiment to test it
  3. How to interpret results
  4. What new questions to ask

The brain uses heuristic reasoning strategies, not an LLM.
Each strategy is a function that looks at journal state and
may produce a hypothesis with an experiment plan.

Strategies are tried in priority order. The first one that
produces a hypothesis wins. This makes the system predictable
and debuggable while still being genuinely exploratory.
"""

import numpy as np
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
# PARAMETER SPACE — what the brain knows it can explore
# ═══════════════════════════════════════════════════════════════════

# Every parameter the system knows about, with sensible ranges
PARAM_SPACE = {
    # Metabolic
    'extraction_factor':        (0.10, 1.00),
    'consumption_rate':         (0.02, 0.30),
    'update_cost_factor':       (0.005, 0.10),
    # Learning
    'learning_rate':            (0.005, 0.20),
    'observation_dim':          (4, 24),
    # Environment
    'signal_ratio':             (0.20, 1.00),
    'base_signal_ratio':        (0.20, 1.00),
    'spatial_gradient':         (0.0, 0.40),
    # Energy
    'starting_energy':          (50.0, 300.0),
    'energy_capacity':          (100.0, 500.0),
    # Trait variation
    'birth_trait_variation':    (0.0, 0.10),
    'mutation_rate':            (0.001, 0.05),
    # Tissue-specific
    'division_energy_threshold':(100.0, 200.0),
    'division_cost':            (5.0, 80.0),
    'energy_leak_rate':         (0.0, 0.10),
    'signal_hop_decay':         (0.5, 0.99),
    'signal_emission_strength': (0.05, 1.0),
    'signal_energy_coupling':   (0.0, 3.0),
    'signal_division_coupling': (0.0, 0.5),
    'apoptosis_streak':         (100, 2000),
    # Phenotype (v0.4.0)
    'phenotype_max_plasticity': (0.01, 0.20),
    'phenotype_lock_tau':       (50.0, 1000.0),
    'phenotype_emission_coupling': (0.0, 5.0),
    'phenotype_affinity_coupling': (0.0, 5.0),
    # Resource & motility (v0.5.0)
    'resource_depletion_rate':  (0.0, 0.01),
    'resource_regen_rate':      (0.0, 0.005),
    'migration_energy_cost':    (0.5, 10.0),
    'migration_resource_threshold': (0.1, 0.9),
    'displacement_energy_ratio': (1.5, 5.0),
    # Action coupling (v0.6.0)
    'action_dim':               (0, 8),
    'action_division_coupling': (0.0, 5.0),
    'action_weight_scale':       (0.01, 0.5),
    'action_mutation_rate':       (0.001, 0.1),
    # v0.7.0 landscape & stigmergy
    'landscape_base':            (0.1, 0.5),
    'death_imprint_strength':    (0.0, 5.0),
    'stigmergy_decay':           (0.9, 0.999),
    'stigmergy_sensing':         (0.0, 2.0),
    'stigmergy_avoidance':       (0.0, 1.0),
    # v0.8.0 predation
    'predation_energy_ratio':    (1.1, 3.0),
    'predation_efficiency':      (0.2, 0.8),
    'predation_cooldown':        (1, 20),
    'predation_action_power':     (0.0, 2.0),
    'predation_evasion_scaling':  (0.0, 0.5),
    # v0.9.0 toxins & Lamarckian
    'toxin_emission_rate':        (0.01, 0.5),
    'toxin_damage_rate':          (0.1, 2.0),
    'toxin_range':                (1, 5),
    'toxin_cost_rate':            (0.01, 0.3),
    'weight_inheritance_ratio':   (0.0, 0.9),
    'weight_inheritance_noise':   (0.001, 0.05),
    # v1.0.0 quorum sensing & toxin resistance
    'quorum_threshold':           (2, 8),
    'quorum_boost':               (0.1, 1.0),
    'quorum_radius':              (1, 4),
    'toxin_resistance_scaling':   (0.0, 1.0),
    # Population-specific
    'carrying_capacity':        (10, 80),
    'reproduction_threshold':   (80.0, 200.0),
    'reproduction_cost':        (20.0, 100.0),
}

# Sensible base configs per scale
SINGLE_BASE = {
    'observation_dim': 8, 'model_dim': 16,
    'initial_energy': 100.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'update_cost_factor': 0.02,
    'learning_rate': 0.05, 'birth_trait_variation': 0.02,
}

POPULATION_BASE = {
    'observation_dim': 8, 'model_dim': 16,
    'initial_energy': 100.0, 'energy_capacity': 200.0,
    'consumption_rate': 0.08, 'extraction_factor': 0.35,
    'update_cost_factor': 0.02, 'learning_rate': 0.05,
    'birth_trait_variation': 0.03, 'reproduction_cost': 60.0,
    'mutation_rate': 0.015, 'initial_pop': 20, 'max_pop': 60,
    'reproduction_threshold': 120.0, 'carrying_capacity': 30,
}

TISSUE_BASE = {
    'env_dim': 8, 'signal_dim': 4,
    'observation_dim': 12, 'model_dim': 20,
    'initial_energy': 100.0, 'starting_energy': 180.0,
    'energy_capacity': 200.0, 'consumption_rate': 0.08,
    'extraction_factor': 0.60, 'update_cost_factor': 0.015,
    'learning_rate': 0.05, 'birth_trait_variation': 0.02,
    'base_signal_ratio': 0.70, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.1,
    'energy_leak_rate': 0.02, 'division_energy_threshold': 140.0,
    'division_cost': 30.0, 'cell_mutation_rate': 0.005,
    'apoptosis_threshold': 3.0, 'apoptosis_streak': 500,
    # v0.4.0 phenotype
    'phenotype_max_plasticity': 0.05, 'phenotype_lock_tau': 200.0,
    'phenotype_min_plasticity': 0.001, 'phenotype_emission_coupling': 2.0,
    'phenotype_affinity_coupling': 2.0,
    # v0.5.0 environment & motility
    'resource_depletion_rate': 0.0, 'resource_regen_rate': 0.0,
    'migration_energy_cost': 2.0, 'migration_resource_threshold': 0.5,
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


# ===================================================================
# RESEARCH STRATEGIES -- each can generate a hypothesis
# ===================================================================

def strategy_bootstrap(journal):
    """
    If journal is nearly empty, generate foundational mapping experiments.
    Run the three scales (single, population, tissue) to build baseline knowledge.
    """
    n_exp = len(journal['experiments'])
    knowledge = journal.get('knowledge', {})

    # Phase 1: Single-organism viability map
    if 'single_viability_map' not in knowledge:
        return {
            'id': f'bootstrap_single_{n_exp}',
            'statement': (
                'Map single-organism viability across extraction_factor x signal_ratio '
                'to establish baseline survival landscape.'
            ),
            'test_plan': {
                'scale': 'single',
                'sweep': {
                    'extraction_factor': [0.15, 0.20, 0.25, 0.30, 0.40, 0.50],
                    'signal_ratio': [0.30, 0.50, 0.70, 0.90],
                },
                'base_config': SINGLE_BASE,
                'ticks': 15000,
                'n_seeds': 3,
            },
            'priority': 1.0,
            'reasoning': 'Need baseline single-organism data before anything else.',
        }

    # Phase 2: Population viability map
    if 'population_viability_map' not in knowledge:
        return {
            'id': f'bootstrap_pop_{n_exp}',
            'statement': (
                'Map population viability across extraction_factor x signal_ratio '
                'to see how competition changes the survival landscape.'
            ),
            'test_plan': {
                'scale': 'population',
                'sweep': {
                    'extraction_factor': [0.25, 0.35, 0.50],
                    'signal_ratio': [0.40, 0.60, 0.85],
                },
                'base_config': POPULATION_BASE,
                'ticks': 15000,
                'n_seeds': 3,
            },
            'priority': 0.95,
            'reasoning': 'Need population baseline to compare against single-organism.',
        }

    # Phase 3: Tissue viability map
    if 'tissue_viability_map' not in knowledge:
        return {
            'id': f'bootstrap_tissue_{n_exp}',
            'statement': (
                'Map tissue viability across extraction_factor x base_signal_ratio '
                'to find where multicellular growth is possible.'
            ),
            'test_plan': {
                'scale': 'tissue',
                'sweep': {
                    'extraction_factor': [0.30, 0.40, 0.50, 0.60, 0.70, 0.80],
                    'base_signal_ratio': [0.40, 0.55, 0.70, 0.85],
                },
                'base_config': TISSUE_BASE,
                'ticks': 5000,
                'n_seeds': 3,
                'run_kwargs': {'rows': 12, 'cols': 12},
            },
            'priority': 0.9,
            'reasoning': 'Need tissue baseline — this is the multicellular frontier.',
        }

    return None


def strategy_refine_boundary(journal):
    """
    If we found a phase boundary, zoom in with finer resolution.
    """
    findings = journal.get('findings', [])
    knowledge = journal.get('knowledge', {})

    for f in reversed(findings):
        if 'boundary' not in f.get('statement', '').lower():
            continue
        tags = f.get('tags', [])
        bdry = f.get('data', {})
        param = bdry.get('param')
        lo, hi = bdry.get('low'), bdry.get('high')
        scale = bdry.get('scale', 'single')

        if param is None or lo is None or hi is None:
            continue

        # Check if we already refined this
        refined_key = f'refined_{scale}_{param}_{lo:.3f}_{hi:.3f}'
        if refined_key in knowledge:
            continue

        # Generate 7 points in the boundary zone
        step = (hi - lo) / 8
        values = [round(lo + step * i, 5) for i in range(1, 8)]

        base = _base_for_scale(scale)
        ticks = _ticks_for_scale(scale)

        return {
            'id': f'refine_{param}_{scale}_{len(journal["experiments"])}',
            'statement': (
                f'Refine {param} phase boundary in [{lo:.4f}, {hi:.4f}] '
                f'for {scale} scale. Where exactly does viability flip?'
            ),
            'test_plan': {
                'scale': scale,
                'sweep': {param: values},
                'base_config': base,
                'ticks': ticks,
                'n_seeds': 5,
                'run_kwargs': {'rows': 12, 'cols': 12} if scale == 'tissue' else {},
            },
            'priority': 0.85,
            'reasoning': f'Found boundary at {param}~{bdry.get("boundary", "?")}, need finer resolution.',
        }

    return None


def strategy_cross_scale_comparison(journal):
    """
    If we have viability data at two scales, compare them.
    Does the survival boundary shift between single → population → tissue?
    """
    knowledge = journal.get('knowledge', {})

    has_single = 'single_viability_map' in knowledge
    has_pop = 'population_viability_map' in knowledge
    has_tissue = 'tissue_viability_map' in knowledge

    if has_single and has_pop and 'cross_scale_single_vs_pop' not in knowledge:
        single_bdry = knowledge.get('single_viability_map', {}).get('extraction_boundary')
        pop_bdry = knowledge.get('population_viability_map', {}).get('extraction_boundary')
        return {
            'id': f'cross_scale_sp_{len(journal["experiments"])}',
            'statement': (
                f'Compare single-organism vs population survival boundaries. '
                f'Single boundary ~ {single_bdry}, Population boundary ~ {pop_bdry}. '
                f'Does competition shift the viability threshold?'
            ),
            'test_plan': {
                'scale': 'comparison',
                'compare': ['single', 'population'],
                'sweep': {
                    'extraction_factor': [0.20, 0.22, 0.25, 0.27, 0.30, 0.32, 0.35],
                },
                'signal_ratio': 0.55,
                'ticks_single': 20000,
                'ticks_pop': 100000,
                'n_seeds': 5,
            },
            'priority': 0.80,
            'reasoning': 'Cross-scale comparison reveals emergent effects of competition.',
        }

    if has_pop and has_tissue and 'cross_scale_pop_vs_tissue' not in knowledge:
        return {
            'id': f'cross_scale_pt_{len(journal["experiments"])}',
            'statement': (
                'Compare population vs tissue survival. '
                'Does spatial structure change what environments are viable?'
            ),
            'test_plan': {
                'scale': 'comparison',
                'compare': ['population', 'tissue'],
                'sweep': {
                    'extraction_factor': [0.30, 0.40, 0.50, 0.60, 0.70],
                },
                'base_signal_ratio': 0.70,
                'ticks_pop': 100000,
                'ticks_tissue': 5000,
                'n_seeds': 3,
                'run_kwargs_tissue': {'rows': 12, 'cols': 12},
            },
            'priority': 0.75,
            'reasoning': 'Spatial structure may enable or constrain viability.',
        }

    return None


def strategy_explore_unexplored(journal):
    """
    Pick a parameter we haven't tested yet and do a sweep.
    Prioritizes parameters relevant to current research frontier.
    """
    knowledge = journal.get('knowledge', {})
    explored = set(knowledge.get('explored_params', []))

    # Parameters ordered by scientific interest
    frontier_params = [
        # Phenotype & differentiation (v0.4.0) — new physics, top priority
        ('phenotype_emission_coupling', 'tissue', 'How strongly does cell identity modulate signal emission?'),
        ('phenotype_affinity_coupling', 'tissue', 'How much do similar cells prefer sharing energy?'),
        ('phenotype_lock_tau', 'tissue', 'How quickly do cells commit to their identity?'),
        ('phenotype_max_plasticity', 'tissue', 'How plastic are young cells in developing identity?'),
        # Resource & motility (v0.5.0)
        # Action coupling (v0.6.0)
        ('action_division_coupling', 'tissue', 'How strongly do evolved action outputs guide division direction?'),
        # Resource & motility (v0.5.0)
        ('resource_depletion_rate', 'tissue', 'How fast do cells consume local resources?'),
        ('resource_regen_rate', 'tissue', 'How fast do depleted resources recover?'),
        ('migration_resource_threshold', 'tissue', 'When do cells decide to migrate?'),
        ('displacement_energy_ratio', 'tissue', 'How easy is competitive displacement between organisms?'),
        # Tissue-frontier priorities
        ('signal_energy_coupling', 'tissue', 'How strongly should signals amplify energy routing?'),
        ('signal_division_coupling', 'tissue', 'How much should signals lower the division threshold?'),
        ('signal_hop_decay', 'tissue', 'How far should signals propagate? Low decay = long range.'),
        ('division_cost', 'tissue', 'How does the cost of division affect tissue growth?'),
        ('energy_leak_rate', 'tissue', 'Does energy sharing between cells help or hurt tissue?'),
        ('spatial_gradient', 'tissue', 'How does environmental heterogeneity affect tissue morphology?'),
        ('signal_emission_strength', 'tissue', 'How loudly should cells broadcast prediction error?'),
        ('apoptosis_streak', 'tissue', 'How quickly should failing cells die?'),
        # Learning dynamics
        ('learning_rate', 'single', 'Is there an optimal learning rate or does it not matter?'),
        ('update_cost_factor', 'single', 'How does the cost of learning affect survival strategy?'),
        # Population dynamics
        ('mutation_rate', 'population', 'Does higher mutation help or hurt evolution?'),
        ('carrying_capacity', 'population', 'How does population density affect evolution?'),
        ('reproduction_cost', 'population', 'Is cheaper reproduction always better?'),
        # Energy architecture
        ('starting_energy', 'tissue', 'Does initial energy determine tissue fate?'),
        ('energy_capacity', 'single', 'Does storage capacity create qualitative behavior shifts?'),
        ('consumption_rate', 'single', 'How sensitive is survival to base metabolic cost?'),
        # Trait variation
        ('birth_trait_variation', 'population', 'Does more heritable variation accelerate evolution?'),
    ]

    for param, scale, question in frontier_params:
        if param in explored:
            continue

        lo, hi = PARAM_SPACE.get(param, (0, 1))
        base = _base_for_scale(scale)
        ticks = _ticks_for_scale(scale)

        # Generate sweep values across the range
        if isinstance(lo, int) and isinstance(hi, int):
            n_pts = min(6, hi - lo + 1)
            values = [int(v) for v in np.linspace(lo, hi, n_pts)]
        else:
            values = [round(v, 5) for v in np.linspace(lo, hi, 6)]

        return {
            'id': f'explore_{param}_{len(journal["experiments"])}',
            'statement': question,
            'test_plan': {
                'scale': scale,
                'sweep': {param: values},
                'base_config': base,
                'ticks': ticks,
                'n_seeds': 3,
                'run_kwargs': {'rows': 12, 'cols': 12} if scale == 'tissue' else {},
            },
            'priority': 0.60,
            'reasoning': f'Parameter {param} has never been systematically tested.',
        }

    return None


def strategy_interaction_effects(journal):
    """
    If we know individual effects of two parameters, test their interaction.
    Does A x B produce unexpected combined effects?
    """
    knowledge = journal.get('knowledge', {})
    explored = set(knowledge.get('explored_params', []))
    interactions_tested = set(knowledge.get('interactions_tested', []))

    # Interesting parameter pairs to test together
    pairs = [
        ('extraction_factor', 'division_cost', 'tissue',
         'Does extraction interact with division cost? Maybe cheap division only works in rich environments.'),
        ('learning_rate', 'consumption_rate', 'single',
         'Trade-off: faster learning costs more energy. Is there an optimal balance?'),
        ('mutation_rate', 'carrying_capacity', 'population',
         'Does mutation matter more in small or large populations?'),
        ('spatial_gradient', 'signal_hop_decay', 'tissue',
         'Does signal range interact with environmental heterogeneity?'),
        ('signal_energy_coupling', 'signal_division_coupling', 'tissue',
         'Do the two action coupling mechanisms interact? Energy routing vs reproduction control.'),
        ('energy_leak_rate', 'division_cost', 'tissue',
         'Energy sharing vs division cost: cooperative vs competitive tissue growth.'),
        # v0.4.0 phenotype interactions
        ('phenotype_emission_coupling', 'phenotype_affinity_coupling', 'tissue',
         'Does identity-colored emission interact with affinity-based sharing? Self-reinforcing vs self-limiting.'),
        ('phenotype_lock_tau', 'apoptosis_streak', 'tissue',
         'Critical period vs cell death: do fast-committing cells survive better?'),
        # v0.5.0 resource interactions
        ('resource_depletion_rate', 'resource_regen_rate', 'tissue',
         'Depletion vs regeneration: what balance creates interesting dynamics?'),
        ('resource_depletion_rate', 'migration_resource_threshold', 'tissue',
         'Does motility sensitivity interact with depletion rate? Eager vs lazy migration.'),
        # v0.6.0 action coupling interactions
        ('action_division_coupling', 'resource_depletion_rate', 'tissue',
         'Does action-directed division help more when resources are scarce?'),
    ]

    for p1, p2, scale, question in pairs:
        pair_key = f'{p1}_x_{p2}'
        if pair_key in interactions_tested:
            continue
        # Only test interactions for params we've explored individually
        if p1 not in explored and p2 not in explored:
            continue

        lo1, hi1 = PARAM_SPACE.get(p1, (0, 1))
        lo2, hi2 = PARAM_SPACE.get(p2, (0, 1))
        base = _base_for_scale(scale)
        ticks = _ticks_for_scale(scale)

        v1 = _make_sweep_values(lo1, hi1, 4)
        v2 = _make_sweep_values(lo2, hi2, 4)

        return {
            'id': f'interact_{p1}_{p2}_{len(journal["experiments"])}',
            'statement': question,
            'test_plan': {
                'scale': scale,
                'sweep': {p1: v1, p2: v2},
                'base_config': base,
                'ticks': ticks,
                'n_seeds': 3,
                'run_kwargs': {'rows': 12, 'cols': 12} if scale == 'tissue' else {},
            },
            'priority': 0.50,
            'reasoning': f'Testing interaction between {p1} and {p2}.',
        }

    return None


def strategy_stress_test(journal):
    """
    Take the best-known config and push it to extremes.
    What kills a thriving organism/tissue? What are the limits?
    """
    knowledge = journal.get('knowledge', {})
    if 'stress_tests' in knowledge:
        return None

    findings = journal.get('findings', [])
    # Find the richest surviving condition
    best_energy = 0
    best_scale = 'single'
    for f in findings:
        e = f.get('data', {}).get('mean_energy', 0)
        if e > best_energy:
            best_energy = e
            best_scale = f.get('data', {}).get('scale', 'single')

    if best_energy < 10:
        return None  # nothing survived well enough to stress-test

    base = _base_for_scale(best_scale)
    ticks = _ticks_for_scale(best_scale)

    # Stress dimensions: make things harder along multiple axes
    return {
        'id': f'stress_{best_scale}_{len(journal["experiments"])}',
        'statement': (
            f'Stress-test the {best_scale} scale. '
            f'Which parameter breaks survival fastest: '
            f'high consumption, low extraction, high noise, or high update cost?'
        ),
        'test_plan': {
            'scale': best_scale,
            'multi_experiment': [
                {'label': 'high_consumption',
                 'override': {'consumption_rate': [0.10, 0.15, 0.20, 0.25, 0.30]}},
                {'label': 'low_extraction',
                 'override': {'extraction_factor': [0.10, 0.15, 0.20, 0.25, 0.30]}},
                {'label': 'high_update_cost',
                 'override': {'update_cost_factor': [0.02, 0.04, 0.06, 0.08, 0.10]}},
                {'label': 'low_signal',
                 'override': {
                     ('signal_ratio' if best_scale != 'tissue' else 'base_signal_ratio'):
                     [0.20, 0.30, 0.40, 0.50, 0.60]}},
            ],
            'base_config': base,
            'ticks': ticks,
            'n_seeds': 3,
            'run_kwargs': {'rows': 12, 'cols': 12} if best_scale == 'tissue' else {},
        },
        'priority': 0.55,
        'reasoning': 'Knowing what kills the system reveals its real constraints.',
    }


def strategy_replicate_finding(journal):
    """
    Pick a low-confidence finding and re-test with more seeds.
    Science needs replication.
    """
    for f in journal.get('findings', []):
        if f.get('confidence', 1.0) < 0.6 and not f.get('replicated'):
            # Re-run the original experiment with more seeds
            orig = f.get('experiment_ref')
            if not orig:
                continue
            # Find the original experiment
            for exp in journal['experiments']:
                if exp.get('hypothesis_id') == orig:
                    plan = exp.get('original_plan', {})
                    if plan:
                        new_plan = dict(plan)
                        new_plan['n_seeds'] = max(plan.get('n_seeds', 3) * 2, 7)
                        return {
                            'id': f'replicate_{orig}_{len(journal["experiments"])}',
                            'statement': f'Replicate: {f["statement"]}',
                            'test_plan': new_plan,
                            'priority': 0.45,
                            'reasoning': f'Confidence={f["confidence"]:.2f}, needs replication.',
                        }
    return None


# ═══════════════════════════════════════════════════════════════════
# RESULT INTERPRETATION — turns raw numbers into findings
# ═══════════════════════════════════════════════════════════════════

def interpret_results(hypothesis, results, journal):
    """
    Read experiment results and produce findings + new questions.

    Returns (findings_list, questions_list, knowledge_updates).
    """
    findings = []
    questions = []
    knowledge_updates = {}

    plan = hypothesis.get('test_plan', {})
    scale = plan.get('scale', 'single')
    sweep = plan.get('sweep', {})
    param_names = list(sweep.keys())

    # Basic statistics
    n_configs = len(results)
    all_dead = all(r.get('survival_rate', 0) == 0 for r in results)
    all_alive = all(r.get('survival_rate', 0) == 1.0 for r in results)
    survival_rates = [r.get('survival_rate', 0) for r in results]
    has_transition = not all_dead and not all_alive

    # ── Finding: overall viability statement ────────────────────
    if all_alive:
        findings.append({
            'statement': f'{scale}: All {n_configs} configs survived.',
            'evidence': f'hypothesis={hypothesis["id"]}',
            'confidence': 0.8,
            'tags': [scale, 'viability', 'all_survived'],
            'data': {'scale': scale, 'n_configs': n_configs},
            'experiment_ref': hypothesis['id'],
        })
    elif all_dead:
        findings.append({
            'statement': f'{scale}: All {n_configs} configs died.',
            'evidence': f'hypothesis={hypothesis["id"]}',
            'confidence': 0.8,
            'tags': [scale, 'viability', 'all_dead'],
            'data': {'scale': scale, 'n_configs': n_configs},
            'experiment_ref': hypothesis['id'],
        })

    # ── Finding: phase boundaries ───────────────────────────────
    if has_transition:
        from .analysis import find_phase_boundary
        for pname in param_names:
            bdry = find_phase_boundary(results, pname)
            if bdry:
                findings.append({
                    'statement': (
                        f'{scale}: Phase boundary in {pname} ~ {bdry["boundary"]:.4f} '
                        f'(between {bdry["low"]:.4f} and {bdry["high"]:.4f})'
                    ),
                    'evidence': f'hypothesis={hypothesis["id"]}',
                    'confidence': 0.7,
                    'tags': [scale, 'boundary', pname],
                    'data': {**bdry, 'scale': scale},
                    'experiment_ref': hypothesis['id'],
                })
                questions.append(
                    f'What mechanism causes the {pname} boundary at ~{bdry["boundary"]:.4f} '
                    f'for {scale}?'
                )

    # ── Finding: parameter effects ──────────────────────────────
    for pname in param_names:
        vals = sorted(set(r['params'][pname] for r in results))
        if len(vals) < 3:
            continue
        # Get mean energy at each value
        energies = []
        for v in vals:
            matching = [r for r in results if r['params'][pname] == v]
            energies.append(np.mean([r.get('mean_energy', 0) for r in matching]))

        # Compute correlation
        if np.std(energies) > 0.01:
            corr = np.corrcoef(vals, energies)[0, 1]
            direction = 'increases' if corr > 0.3 else ('decreases' if corr < -0.3 else 'no clear effect on')
            findings.append({
                'statement': f'{scale}: {pname} {direction} mean energy (r={corr:.2f})',
                'evidence': f'hypothesis={hypothesis["id"]}',
                'confidence': min(0.9, 0.4 + abs(corr) * 0.5),
                'tags': [scale, 'parameter_effect', pname],
                'data': {'param': pname, 'correlation': float(corr), 'scale': scale,
                         'values': [float(v) for v in vals],
                         'energies': [float(e) for e in energies]},
                'experiment_ref': hypothesis['id'],
            })

    # ── Finding: tissue-specific metrics ────────────────────────
    if scale == 'tissue':
        cells_list = [r.get('mean_cells', 0) for r in results if 'mean_cells' in r]
        if cells_list:
            max_cells = max(cells_list)
            best_r = max(results, key=lambda r: r.get('mean_cells', 0))
            findings.append({
                'statement': (
                    f'tissue: Peak growth = {max_cells:.0f} cells '
                    f'at {best_r["params"]}'
                ),
                'evidence': f'hypothesis={hypothesis["id"]}',
                'confidence': 0.7,
                'tags': ['tissue', 'growth', 'peak'],
                'data': {'peak_cells': float(max_cells), 'best_params': best_r['params'],
                         'scale': 'tissue'},
                'experiment_ref': hypothesis['id'],
            })
            if max_cells <= 2:
                questions.append(
                    'Tissue barely grew beyond zygote. '
                    'Is division_cost too high or extraction too low?'
                )
            elif max_cells > 20:
                questions.append(
                    f'Tissue grew to {max_cells:.0f} cells. '
                    f'What limits further growth? Grid size or energy?'
                )

    # ── Knowledge updates ───────────────────────────────────────
    # Mark parameters as explored
    explored = list(journal.get('knowledge', {}).get('explored_params', []))
    for p in param_names:
        if p not in explored:
            explored.append(p)
    knowledge_updates['explored_params'] = explored

    # Store viability map if this was a bootstrap
    hyp_id = hypothesis.get('id', '')
    if 'bootstrap_single' in hyp_id:
        bdry_val = None
        from .analysis import find_phase_boundary
        b = find_phase_boundary(results, 'extraction_factor')
        if b:
            bdry_val = b['boundary']
        knowledge_updates['single_viability_map'] = {
            'extraction_boundary': bdry_val,
            'n_configs': n_configs,
            'survival_rates': survival_rates,
        }
    elif 'bootstrap_pop' in hyp_id:
        bdry_val = None
        from .analysis import find_phase_boundary
        b = find_phase_boundary(results, 'extraction_factor')
        if b:
            bdry_val = b['boundary']
        knowledge_updates['population_viability_map'] = {
            'extraction_boundary': bdry_val,
            'n_configs': n_configs,
        }
    elif 'bootstrap_tissue' in hyp_id:
        bdry_val = None
        from .analysis import find_phase_boundary
        b = find_phase_boundary(results, 'extraction_factor')
        if b:
            bdry_val = b['boundary']
        knowledge_updates['tissue_viability_map'] = {
            'extraction_boundary': bdry_val,
            'n_configs': n_configs,
        }

    # Mark stress tests done
    if 'stress' in hyp_id:
        knowledge_updates['stress_tests'] = True

    # Mark refinements
    if 'refine_' in hyp_id:
        for pname in param_names:
            vals = sorted(set(r['params'][pname] for r in results))
            if len(vals) >= 2:
                key = f'refined_{scale}_{pname}_{vals[0]:.3f}_{vals[-1]:.3f}'
                knowledge_updates[key] = True

    # Mark interactions tested
    if 'interact_' in hyp_id and len(param_names) == 2:
        pair_key = f'{param_names[0]}_x_{param_names[1]}'
        tested = list(journal.get('knowledge', {}).get('interactions_tested', []))
        tested.append(pair_key)
        knowledge_updates['interactions_tested'] = tested

    return findings, questions, knowledge_updates


# ═══════════════════════════════════════════════════════════════════
# MAIN BRAIN FUNCTION — pick the next hypothesis
# ═══════════════════════════════════════════════════════════════════

# Strategy order matters — early strategies take priority
STRATEGIES = [
    strategy_bootstrap,
    strategy_refine_boundary,
    strategy_cross_scale_comparison,
    strategy_explore_unexplored,
    strategy_interaction_effects,
    strategy_stress_test,
    strategy_replicate_finding,
]


def generate_hypothesis(journal):
    """
    The brain's main function. Read the journal, return the next hypothesis to test.
    Returns None if (somehow) all strategies are exhausted.
    """
    for strategy in STRATEGIES:
        hypothesis = strategy(journal)
        if hypothesis is not None:
            return hypothesis
    return None


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def _base_for_scale(scale):
    return {'single': SINGLE_BASE, 'population': POPULATION_BASE,
            'tissue': TISSUE_BASE}.get(scale, SINGLE_BASE)

def _ticks_for_scale(scale):
    return {'single': 15000, 'population': 15000, 'tissue': 3000}.get(scale, 15000)

def _make_sweep_values(lo, hi, n):
    if isinstance(lo, int) and isinstance(hi, int):
        return [int(v) for v in np.linspace(lo, hi, n)]
    return [round(float(v), 5) for v in np.linspace(lo, hi, n)]
