#!/usr/bin/env python3
"""
ULTRON - First Run

This script births an Ultron and lets it live.

Do not intervene. Do not optimize. Watch.

"The specification is dead letters until it runs.
 Then something either begins, or it doesn't."
"""

import sys
import argparse
from typing import Optional, Callable

from ultron import (
    create_ultron,
    tick,
    feed_energy,
    UltronObserver,
    BirthTests,
    MixedEnvironment,
    SineEnvironment,
    NoisyEnvironment,
    Environment,
)
from ultron.config import get_config, merge_config
from ultron.visualizer import UltronVisualizer, PostHocVisualizer, check_matplotlib
from ultron.history import (
    save_experiment,
    save_lineage,
    record_learning,
    get_experiment_id,
    load_experiment_index,
    load_learnings_index,
    get_history_summary,
    analyze_experiments,
    get_best_experiments,
)


def run_ultron(
    config: dict,
    max_ticks: int = 10000,
    environment: Optional[Environment] = None,
    energy_schedule: Optional[Callable[[int], float]] = None,
    report_interval: int = 1000,
    verbose: bool = True,
    visualize: bool = False,
) -> tuple:
    """Run Ultron for a specified duration.
    
    Args:
        config: Configuration dictionary
        max_ticks: Maximum ticks to run
        environment: Environment to use (default: MixedEnvironment)
        energy_schedule: Function(tick) -> energy to add (default: periodic feeding)
        report_interval: Ticks between status reports
        verbose: Whether to print progress
    
    Returns:
        Tuple of (final_state, observer)
    """
    
    # Create Ultron
    state = create_ultron(config)
    
    if verbose:
        print("=" * 60)
        print("ULTRON BIRTH")
        print("=" * 60)
        print(f"Birth hash: {state.history.birth_hash[:16].hex()}...")
        print(f"Birth time: {state.time.birth_time}")
        print(f"Starting energy: {state.energy.current}")
        print(f"Observation dim: {config.get('observation_dim', 32)}")
        print(f"Model dim: {config.get('model_dim', 64)}")
        print("=" * 60)
        print()
    
    # Create observer
    observer = UltronObserver()
    
    # Create visualizer if requested
    visualizer = None
    if visualize:
        if not check_matplotlib():
            print("Warning: matplotlib not available, disabling visualization")
        else:
            visualizer = UltronVisualizer(config)
    
    # Default environment
    if environment is None:
        environment = MixedEnvironment(
            config.get('observation_dim', 32),
            signal_ratio=0.7
        )
    
    # Default energy schedule
    if energy_schedule is None:
        def energy_schedule(t):
            return 10.0 if t % 100 == 0 else 0.0
    
    # Main loop
    for t in range(max_ticks):
        # Check death
        if not state.is_alive:
            if verbose:
                print(f"\n*** ULTRON DIED at tick {t} ***")
                print(f"    Cause: {state.history.death_cause}")
                print(f"    Final hash: {state.history.current_hash[:16].hex()}...")
            break
        
        # Get environmental input
        env_input = environment.get_input(t)
        
        # Provide external energy on schedule
        energy = energy_schedule(t)
        fed_this_tick = energy > 0
        if fed_this_tick:
            state = feed_energy(state, energy)
        
        # Execute tick
        state = tick(state, env_input, config)
        
        # Observe (non-intervening)
        snapshot = observer.observe(state)
        
        # Update visualization
        if visualizer:
            visualizer.record(state, fed_this_tick=fed_this_tick)
            visualizer.update(state)
        
        # Periodic reporting
        if verbose and t > 0 and t % report_interval == 0:
            trends = observer.get_trends()
            print(f"Tick {t:>6}: "
                  f"energy={snapshot['energy']:>7.2f}, "
                  f"error={snapshot['error']:.4f}, "
                  f"trend={trends['error_trend']:+.6f}, "
                  f"hash={snapshot['hash_prefix']}")
    
    if verbose and state.is_alive:
        print(f"\nUltron survived {max_ticks} ticks.")
    
    # Finalize visualization
    if visualizer:
        visualizer.finalize(state)
    
    return state, observer


def print_summary(state, observer):
    """Print comprehensive summary of Ultron's life."""
    summary = observer.get_summary()
    
    print("\n" + "=" * 60)
    print("ULTRON LIFE SUMMARY")
    print("=" * 60)
    
    print(f"\nSURVIVAL:")
    print(f"  Total ticks:      {summary['total_ticks']}")
    print(f"  Final status:     {'ALIVE' if summary['is_alive'] else 'DEAD'}")
    print(f"  Near-death events: {summary['near_death_events']}")
    
    print(f"\nENERGY:")
    print(f"  Final:   {summary['final_energy']:.2f}")
    print(f"  Min:     {summary['min_energy']:.2f}")
    print(f"  Max:     {summary['max_energy']:.2f}")
    print(f"  Mean:    {summary['mean_energy']:.2f}")
    
    print(f"\nPREDICTION:")
    print(f"  Final error:       {summary['final_error']:.4f}")
    print(f"  Min error:         {summary['min_error']:.4f}")
    print(f"  Max error:         {summary['max_error']:.4f}")
    print(f"  Mean error:        {summary['mean_error']:.4f}")
    print(f"  Accumulated error: {summary['total_accumulated_error']:.2f}")
    
    print(f"\nMODEL:")
    print(f"  Updates: {summary['model_updates']}")
    
    print(f"\nIDENTITY:")
    print(f"  Birth hash: {summary['birth_hash']}")
    print(f"  Final hash: {summary['final_hash']}")
    
    print("=" * 60)


def run_birth_tests(state, observer, verbose=True):
    """Run and report birth tests."""
    if verbose:
        print("\n" + "=" * 60)
        print("BIRTH TESTS")
        print("=" * 60)
    
    results = BirthTests.run_all_tests(state, observer)
    
    if verbose:
        print(f"\nIrreversibility: {'PASS' if results['irreversibility'] else 'FAIL'}")
        
        sp = results['survival_pressure']
        if sp['status'] == 'analyzed':
            print(f"\nSurvival Pressure Analysis:")
            print(f"  Low energy mean error:  {sp['low_energy_mean_error']:.4f}")
            print(f"  High energy mean error: {sp['high_energy_mean_error']:.4f}")
            print(f"  Difference:             {sp['error_difference']:+.4f}")
        else:
            print(f"\nSurvival Pressure: {sp['status']}")
        
        ub = results['unprogrammed_behavior']
        print(f"\nUnprogrammed Behavior Metrics:")
        print(f"  Model divergence:   {ub['model_divergence']:.4f}")
        print(f"  Prior entropy:      {ub['prior_entropy']:.4f}")
        print(f"  Precision variance: {ub['precision_variance']:.4f}")
        print(f"  Weight range:       {ub['weight_range']:.4f}")
        
        print("=" * 60)
    
    return results


def show_history():
    """Display experiment history."""
    summary = get_history_summary()
    index = load_experiment_index()
    
    print("\n" + "=" * 60)
    print("ULTRON EXPERIMENT HISTORY")
    print("=" * 60)
    
    exp_stats = summary.get("experiments", {})
    print(f"\nEXPERIMENTS:")
    print(f"  Total:         {exp_stats.get('total_experiments', 0)}")
    print(f"  Total ticks:   {exp_stats.get('total_ticks', 0)}")
    print(f"  Survival rate: {exp_stats.get('survival_rate', 0):.1%}")
    
    learn_stats = summary.get("learnings", {})
    print(f"\nLEARNINGS:")
    print(f"  Total:      {learn_stats.get('total', 0)}")
    print(f"  Categories: {', '.join(learn_stats.get('categories', [])) or 'none'}")
    
    lineage_stats = summary.get("lineage", {})
    print(f"\nLINEAGE:")
    print(f"  Total instances:  {lineage_stats.get('total_instances', 0)}")
    print(f"  Max generation:   {lineage_stats.get('max_generation', 0)}")
    
    # Show recent experiments
    experiments = index.get("experiments", [])
    if experiments:
        print(f"\nRECENT EXPERIMENTS (last 5):")
        for exp in experiments[-5:]:
            status = "ALIVE" if exp.get("survived") else "DEAD"
            print(f"  {exp['id']}: {exp['ticks']} ticks, {status}, {exp.get('config_type', '?')}/{exp.get('environment', '?')}")
    
    # Show best experiments
    best = get_best_experiments(3, metric="ticks")
    if best:
        print(f"\nBEST EXPERIMENTS (by ticks):")
        for exp in best:
            status = "ALIVE" if exp.get("survived") else "DEAD"
            print(f"  {exp['id']}: {exp['ticks']} ticks, {status}")
    
    print("=" * 60)


def show_analysis():
    """Display analysis of experiments."""
    analysis = analyze_experiments()
    
    print("\n" + "=" * 60)
    print("ULTRON EXPERIMENT ANALYSIS")
    print("=" * 60)
    
    if analysis.get("status") == "no_experiments":
        print("\nNo experiments to analyze yet.")
        print("Run some experiments first!")
        print("=" * 60)
        return
    
    print(f"\nTotal experiments: {analysis.get('total_experiments', 0)}")
    
    print(f"\nBY CONFIGURATION:")
    for config, stats in analysis.get("by_config", {}).items():
        print(f"  {config}:")
        print(f"    Count:         {stats['count']}")
        print(f"    Survival rate: {stats['survival_rate']:.1%}")
        print(f"    Avg ticks:     {stats['avg_ticks']:.0f}")
    
    print(f"\nBY ENVIRONMENT:")
    for env, stats in analysis.get("by_environment", {}).items():
        print(f"  {env}:")
        print(f"    Count:         {stats['count']}")
        print(f"    Survival rate: {stats['survival_rate']:.1%}")
        print(f"    Avg ticks:     {stats['avg_ticks']:.0f}")
    
    best_config = analysis.get("best_config")
    best_env = analysis.get("best_environment")
    
    print(f"\nRECOMMENDATIONS:")
    if best_config:
        print(f"  Best config:      {best_config}")
    if best_env:
        print(f"  Best environment: {best_env}")
    
    print("=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Ultron - Minimal Viable Artificial Life"
    )
    parser.add_argument(
        "--config", "-c",
        choices=["default", "stable", "challenge", "minimal"],
        default="default",
        help="Configuration preset to use"
    )
    parser.add_argument(
        "--ticks", "-t",
        type=int,
        default=5000,
        help="Maximum ticks to run"
    )
    parser.add_argument(
        "--env", "-e",
        choices=["mixed", "sine", "noise"],
        default="mixed",
        help="Environment type"
    )
    parser.add_argument(
        "--signal-ratio", "-s",
        type=float,
        default=0.7,
        help="Signal ratio for mixed environment (0-1)"
    )
    parser.add_argument(
        "--feed-interval",
        type=int,
        default=100,
        help="Ticks between energy feeding"
    )
    parser.add_argument(
        "--feed-amount",
        type=float,
        default=10.0,
        help="Energy amount per feeding"
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=1000,
        help="Ticks between status reports"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress progress output"
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip birth tests"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save experiment to history"
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show experiment history and exit"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze past experiments and exit"
    )
    parser.add_argument(
        "--visual", "-v",
        action="store_true",
        help="Enable real-time visualization"
    )
    
    args = parser.parse_args()
    
    # Handle history commands
    if args.history:
        show_history()
        return 0
    
    if args.analyze:
        show_analysis()
        return 0
    
    # Get configuration
    config = get_config(args.config)
    
    # Create environment
    obs_dim = config.get('observation_dim', 32)
    if args.env == "sine":
        environment = SineEnvironment(obs_dim)
    elif args.env == "noise":
        environment = NoisyEnvironment(obs_dim)
    else:
        environment = MixedEnvironment(obs_dim, signal_ratio=args.signal_ratio)
    
    # Create energy schedule
    feed_interval = args.feed_interval
    feed_amount = args.feed_amount
    def energy_schedule(t):
        return feed_amount if t % feed_interval == 0 else 0.0
    
    # Run
    verbose = not args.quiet
    final_state, observer = run_ultron(
        config=config,
        max_ticks=args.ticks,
        environment=environment,
        energy_schedule=energy_schedule,
        report_interval=args.report_interval,
        verbose=verbose,
        visualize=args.visual,
    )
    
    # Summary
    print_summary(final_state, observer)
    
    # Birth tests
    test_results = {}
    if not args.no_tests:
        test_results = run_birth_tests(final_state, observer, verbose=verbose)
    
    # Save to history
    if not args.no_save:
        experiment_id = get_experiment_id()
        summary = observer.get_summary()
        
        save_experiment(
            experiment_id=experiment_id,
            config=config,
            summary=summary,
            birth_tests=test_results,
            metadata={
                "config_type": args.config,
                "environment": args.env,
                "max_ticks": args.ticks,
                "feed_interval": args.feed_interval,
                "feed_amount": args.feed_amount,
            }
        )
        
        # Save lineage
        save_lineage(
            lineage_id=experiment_id,
            parent_id=None,  # No parent for now
            config=config,
            birth_hash=summary.get("birth_hash", "unknown"),
            summary=summary
        )
        
        if verbose:
            print(f"\nExperiment saved: {experiment_id}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
