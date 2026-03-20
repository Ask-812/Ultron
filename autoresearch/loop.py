"""
The Loop — autonomous research cycle.

This is the main engine. It runs continuously:

  1. Ask the Brain for a hypothesis
  2. Design the experiment from the hypothesis's test_plan
  3. Run the experiment
  4. Ask the Brain to interpret the results
  5. Write findings, questions, knowledge to the Journal
  6. Repeat

Can run indefinitely or for a fixed number of cycles.
All state is persisted in the journal after every cycle,
so it can be stopped and resumed.
"""

import time
import traceback
from datetime import datetime

from .journal import (
    load_journal, save_journal,
    add_hypothesis, add_experiment, add_finding,
    add_question, update_knowledge, journal_summary,
)
from .brain import generate_hypothesis, interpret_results
from .experiment import run_single, run_population, run_tissue
from .sweep import grid_sweep
from .analysis import find_all_boundaries, results_table


def _safe(text):
    """Replace non-ASCII chars for safe Windows console output."""
    return text.encode('ascii', errors='replace').decode('ascii')


# ═══════════════════════════════════════════════════════════════════
# EXPERIMENT EXECUTOR — runs whatever the hypothesis asks for
# ═══════════════════════════════════════════════════════════════════

def _get_runner(scale):
    """Return the appropriate experiment runner function for the scale."""
    return {
        'single': run_single,
        'population': run_population,
        'tissue': run_tissue,
    }.get(scale)


def _execute_hypothesis(hypothesis):
    """
    Execute the experiment described in hypothesis['test_plan'].
    Returns list of aggregated result dicts (from grid_sweep).
    """
    plan = hypothesis['test_plan']
    scale = plan.get('scale', 'single')
    sweep = plan.get('sweep', {})
    base_config = plan.get('base_config', {})
    ticks = plan.get('ticks', 10000)
    n_seeds = plan.get('n_seeds', 3)
    run_kwargs = plan.get('run_kwargs', {})

    # Handle comparison experiments (run at multiple scales)
    if scale == 'comparison':
        return _execute_comparison(hypothesis)

    # Handle multi-experiment stress tests
    if 'multi_experiment' in plan:
        return _execute_multi(hypothesis)

    runner = _get_runner(scale)
    if runner is None:
        print(f'  [!] Unknown scale: {scale}')
        return []

    # Merge ticks into run_kwargs
    run_kwargs['ticks'] = ticks

    results = grid_sweep(
        runner,
        base_config,
        sweep,
        n_seeds=n_seeds,
        **run_kwargs,
    )
    return results


def _execute_comparison(hypothesis):
    """Run the same parameter sweep at multiple scales and combine results."""
    plan = hypothesis['test_plan']
    scales = plan.get('compare', ['single', 'population'])
    sweep = plan.get('sweep', {})
    n_seeds = plan.get('n_seeds', 3)
    all_results = []

    for sc in scales:
        runner = _get_runner(sc)
        if not runner:
            continue
        base = plan.get(f'base_{sc}', {})
        if not base:
            from .brain import _base_for_scale
            base = _base_for_scale(sc)
        ticks = plan.get(f'ticks_{sc}', plan.get('ticks', 10000))
        run_kwargs = plan.get(f'run_kwargs_{sc}', {})
        run_kwargs['ticks'] = ticks

        # Add fixed params to config
        config = base.copy()
        for k, v in plan.items():
            if k not in ('scale', 'compare', 'sweep', 'n_seeds', 'ticks',
                         'run_kwargs') and not k.startswith(('ticks_', 'base_', 'run_kwargs_')):
                if isinstance(v, (int, float)):
                    config[k] = v

        results = grid_sweep(runner, config, sweep, n_seeds=n_seeds, **run_kwargs)
        # Tag results with scale
        for r in results:
            r['scale'] = sc
        all_results.extend(results)

    return all_results


def _execute_multi(hypothesis):
    """Run multiple sub-experiments (e.g. stress tests)."""
    plan = hypothesis['test_plan']
    scale = plan.get('scale', 'single')
    base_config = plan.get('base_config', {})
    ticks = plan.get('ticks', 10000)
    n_seeds = plan.get('n_seeds', 3)
    run_kwargs = plan.get('run_kwargs', {})
    run_kwargs['ticks'] = ticks

    runner = _get_runner(scale)
    if not runner:
        return []

    all_results = []
    for sub in plan['multi_experiment']:
        label = sub.get('label', 'unnamed')
        overrides = sub.get('override', {})
        print(f'  Sub-experiment: {label}')
        for param_name, values in overrides.items():
            results = grid_sweep(
                runner, base_config, {param_name: values},
                n_seeds=n_seeds, **run_kwargs,
            )
            for r in results:
                r['stress_label'] = label
            all_results.extend(results)

    return all_results


# ═══════════════════════════════════════════════════════════════════
# THE MAIN LOOP
# ═══════════════════════════════════════════════════════════════════

def run_loop(max_cycles=None, verbose=True):
    """
    The autonomous research loop.

    Args:
        max_cycles:  Stop after this many cycles. None = run forever.
        verbose:     Print detailed output.
    """
    journal = load_journal()
    cycle = journal.get('cycle_count', 0)

    # Resume: reset any hypotheses stuck in "testing" from interrupted runs
    for h in journal['hypotheses']:
        if h.get('status') == 'testing':
            h['status'] = 'untested'
    save_journal(journal)

    print('=' * 70)
    print('  ULTRON AUTORESEARCH - Autonomous Research Loop')
    print('=' * 70)
    print(f'  Starting from cycle {cycle}')
    print(f'  Journal: {journal_summary(journal)}')
    print('=' * 70)
    print()

    try:
        while True:
            if max_cycles is not None and cycle >= max_cycles:
                print(f'\n[Loop] Completed {max_cycles} cycles. Stopping.')
                break

            cycle += 1
            journal['cycle_count'] = cycle

            print(f'\n{"-" * 70}')
            print(f'  CYCLE {cycle}')
            print(f'{"-" * 70}')

            # ── 1. Generate hypothesis ─────────────────────────────
            t0 = time.time()
            hypothesis = generate_hypothesis(journal)

            if hypothesis is None:
                print('  [Brain] No more hypotheses to generate. Research complete!')
                break

            print(_safe(f'  [Brain] Hypothesis: {hypothesis["statement"][:80]}...'))
            print(_safe(f'          Reasoning:  {hypothesis.get("reasoning", "")[:60]}'))
            print(f'          Priority:   {hypothesis.get("priority", 0):.2f}')

            # Record hypothesis
            add_hypothesis(journal, hypothesis, source='brain')
            # Mark it as testing
            for h in journal['hypotheses']:
                if h['id'] == hypothesis['id']:
                    h['status'] = 'testing'
            save_journal(journal)

            # ── 2. Run experiment ──────────────────────────────────
            print(f'\n  [Lab] Running experiment...')
            try:
                results = _execute_hypothesis(hypothesis)
            except Exception:
                tb = traceback.format_exc()
                print(_safe(f'  [Lab] EXPERIMENT FAILED:\n{tb}'))
                results = []
                # Mark hypothesis as inconclusive
                for h in journal['hypotheses']:
                    if h['id'] == hypothesis['id']:
                        h['status'] = 'inconclusive'
                add_finding(journal, {
                    'statement': f'Experiment failed for: {hypothesis["statement"][:60]}',
                    'evidence': f'Error: {tb[-200:]}',
                    'confidence': 0.0,
                    'tags': ['error'],
                    'experiment_ref': hypothesis['id'],
                })
                save_journal(journal)
                continue

            if not results:
                print('  [Lab] No results produced.')
                for h in journal['hypotheses']:
                    if h['id'] == hypothesis['id']:
                        h['status'] = 'inconclusive'
                save_journal(journal)
                continue

            # Show results
            elapsed = time.time() - t0
            print(f'  [Lab] {len(results)} configs completed in {elapsed:.1f}s')
            if verbose:
                table = results_table(results)
                print()
                for line in table.split('\n')[:15]:  # cap at 15 rows
                    print(f'    {line}')
                if len(results) > 15:
                    print(f'    ... ({len(results) - 15} more rows)')
                print()

            # Log experiment
            add_experiment(journal, {
                'hypothesis_id': hypothesis['id'],
                'original_plan': hypothesis.get('test_plan', {}),
                'n_results': len(results),
                'elapsed_s': elapsed,
            })

            # ── 3. Interpret results ───────────────────────────────
            print(f'  [Brain] Interpreting results...')
            findings, questions, knowledge_updates = interpret_results(
                hypothesis, results, journal
            )

            for f in findings:
                print(_safe(f'    Finding: {f["statement"][:70]}'))
                add_finding(journal, f)

            for q in questions:
                print(_safe(f'    Question: {q[:70]}'))
                add_question(journal, q)

            for topic, facts in knowledge_updates.items():
                update_knowledge(journal, topic, facts)

            # Mark hypothesis status
            has_boundary = any('boundary' in f.get('statement', '').lower() for f in findings)
            has_effect = any('parameter_effect' in f.get('tags', []) for f in findings)
            for h in journal['hypotheses']:
                if h['id'] == hypothesis['id']:
                    if has_boundary or has_effect:
                        h['status'] = 'supported'
                    else:
                        h['status'] = 'completed'

            # ── 4. Save and summarize ──────────────────────────────
            save_journal(journal)
            print(f'\n  [Journal] {journal_summary(journal)}')

    except KeyboardInterrupt:
        print('\n\n[Loop] Interrupted by user. Saving journal...')
        journal['cycle_count'] = cycle
        save_journal(journal)
        print(f'  Saved at cycle {cycle}. Resume by running again.')

    # Final summary
    print(f'\n{"=" * 70}')
    print(f'  RESEARCH SESSION SUMMARY')
    print(f'{"=" * 70}')
    _print_session_summary(journal)
    print(f'{"=" * 70}')

    return journal


def _print_session_summary(journal):
    """Print a human-readable summary of the journal."""
    print(f'  Cycles completed:   {journal.get("cycle_count", 0)}')
    print(f'  Hypotheses:         {len(journal["hypotheses"])}')

    status_counts = {}
    for h in journal['hypotheses']:
        s = h.get('status', 'unknown')
        status_counts[s] = status_counts.get(s, 0) + 1
    for s, c in sorted(status_counts.items()):
        print(f'    {s}: {c}')

    print(f'  Experiments:        {len(journal["experiments"])}')
    print(f'  Findings:           {len(journal["findings"])}')

    # Top findings by confidence
    sorted_findings = sorted(journal['findings'], key=lambda f: f.get('confidence', 0), reverse=True)
    top = sorted_findings[:5]
    if top:
        print(f'\n  Top findings:')
        for f in top:
            print(_safe(f'    [{f.get("confidence", 0):.1f}] {f["statement"][:65]}'))

    open_q = [q for q in journal['open_questions'] if not q.get('resolved')]
    if open_q:
        print(f'\n  Open questions ({len(open_q)}):')
        for q in open_q[:5]:
            print(_safe(f'    ? {q["question"][:65]}'))

    explored = journal.get('knowledge', {}).get('explored_params', [])
    if explored:
        print(f'\n  Parameters explored: {", ".join(explored)}')
