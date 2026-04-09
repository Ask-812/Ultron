#!/usr/bin/env python3
"""
ULTRON Dimension Sweep Experiment

Purpose: Find the critical dimensionality where learning collapses.
         Map the viability boundary of this organism.

This is NOT optimization. This is ecology.
We are asking: "What environments can this cell metabolize?"
"""

import sys
import numpy as np
from typing import List, Dict
import json
from datetime import datetime

from ultron import create_ultron, tick, feed_energy, UltronObserver
from ultron.environments import SineEnvironment, MixedEnvironment
from ultron.config import get_config


def run_dimension_sweep(
    dimensions: List[int] = [4, 8, 12, 16, 20, 24, 28, 32],
    ticks_per_run: int = 2000,
    environment_type: str = "sine",
    feed_interval: int = 50,
    feed_amount: float = 15.0,
    verbose: bool = True,
) -> List[Dict]:
    """
    Sweep across observation dimensions to find collapse point.
    
    Returns list of result dicts for each dimension tested.
    """
    
    results = []
    
    if verbose:
        print("=" * 70)
        print("ULTRON DIMENSION SWEEP")
        print("=" * 70)
        print(f"Dimensions to test: {dimensions}")
        print(f"Ticks per run: {ticks_per_run}")
        print(f"Environment: {environment_type}")
        print(f"Feeding: {feed_amount} every {feed_interval} ticks")
        print("=" * 70)
        print()
    
    for obs_dim in dimensions:
        if verbose:
            print(f"\n{'─' * 70}")
            print(f"Testing observation_dim = {obs_dim}")
            print(f"{'─' * 70}")
        
        # Create config with this dimension
        # Using minimal-style parameters but varying dimension
        config = {
            'observation_dim': obs_dim,
            'model_dim': obs_dim * 2,  # Keep ratio consistent
            'initial_energy': 100.0,
            'energy_capacity': 200.0,
            'consumption_rate': 0.1,
            'update_cost_factor': 0.01,
            'prediction_reward_factor': 1.0,
            'learning_rate': 0.1,
            'prior_learning_rate': 0.01,
            'precision_learning_rate': 0.001,
            'observation_noise': 0.01,
            'near_death_threshold': 20.0,
        }
        
        # Create environment
        if environment_type == "sine":
            env = SineEnvironment(obs_dim)
        else:
            env = MixedEnvironment(obs_dim, signal_ratio=0.7)
        
        # Create and run Ultron
        state = create_ultron(config)
        observer = UltronObserver()
        
        # Energy schedule
        def get_energy(t):
            return feed_amount if t % feed_interval == 0 else 0.0
        
        # Run
        errors = []
        energies = []
        
        for t in range(ticks_per_run):
            if not state.is_alive:
                break
            
            env_input = env.get_input(t)
            energy = get_energy(t)
            if energy > 0:
                state = feed_energy(state, energy)
            
            state = tick(state, env_input, config)
            observer.observe(state)
            
            errors.append(state.current.error_magnitude)
            energies.append(state.energy.current)
        
        # Compute metrics
        errors = np.array(errors)
        energies = np.array(energies)
        
        # Error trend: compare first half vs second half
        if len(errors) >= 100:
            first_half = np.mean(errors[:len(errors)//2])
            second_half = np.mean(errors[len(errors)//2:])
            error_trend = second_half - first_half
            
            # Also compute last 10% vs first 10%
            early = np.mean(errors[:len(errors)//10])
            late = np.mean(errors[-len(errors)//10:])
            error_improvement = early - late  # positive = improved
        else:
            error_trend = 0.0
            error_improvement = 0.0
        
        result = {
            'observation_dim': obs_dim,
            'ticks_survived': len(errors),
            'is_alive': state.is_alive,
            
            # Error metrics
            'mean_error': float(np.mean(errors)),
            'min_error': float(np.min(errors)),
            'max_error': float(np.max(errors)),
            'std_error': float(np.std(errors)),
            'error_trend': float(error_trend),  # negative = improving
            'error_improvement': float(error_improvement),  # positive = improved
            
            # Energy metrics
            'mean_energy': float(np.mean(energies)),
            'min_energy': float(np.min(energies)),
            'energy_variance': float(np.var(energies)),
            
            # Model metrics
            'precision_variance': float(np.var(state.model.precision)),
            'precision_mean': float(np.mean(state.model.precision)),
            'prior_entropy': float(-np.sum(state.model.priors * np.log(state.model.priors + 1e-10))),
            'weight_range': float(np.max(state.model.weights) - np.min(state.model.weights)),
            'model_version': state.model.version,
            
            # Raw state for analysis
            'near_death_count': state.history.near_death_count,
            'accumulated_error': float(state.history.accumulated_error),
        }
        
        results.append(result)
        
        if verbose:
            status = "ALIVE" if result['is_alive'] else "DEAD"
            trend = "↓ improving" if result['error_trend'] < -0.01 else (
                    "↑ worsening" if result['error_trend'] > 0.01 else "→ flat")
            
            print(f"  Status:           {status}")
            print(f"  Mean error:       {result['mean_error']:.4f}")
            print(f"  Min error:        {result['min_error']:.4f}")
            print(f"  Error trend:      {trend} ({result['error_trend']:+.4f})")
            print(f"  Improvement:      {result['error_improvement']:+.4f}")
            print(f"  Precision var:    {result['precision_variance']:.2e}")
            print(f"  Prior entropy:    {result['prior_entropy']:.4f}")
    
    return results


def analyze_sweep(results: List[Dict], verbose: bool = True) -> Dict:
    """
    Analyze sweep results to find the viability boundary.
    """
    
    if verbose:
        print("\n" + "=" * 70)
        print("SWEEP ANALYSIS: Finding Viability Boundary")
        print("=" * 70)
    
    # Find where learning collapses
    # Criteria: error_improvement drops below threshold
    
    learning_threshold = 0.1  # If improvement < this, learning has collapsed
    
    viable_dims = []
    collapsed_dims = []
    
    for r in results:
        if r['error_improvement'] > learning_threshold:
            viable_dims.append(r['observation_dim'])
        else:
            collapsed_dims.append(r['observation_dim'])
    
    # Find critical point
    if viable_dims and collapsed_dims:
        critical_dim = max(viable_dims)
        collapse_dim = min(collapsed_dims)
        boundary = (critical_dim + collapse_dim) / 2
    else:
        critical_dim = max(viable_dims) if viable_dims else None
        collapse_dim = min(collapsed_dims) if collapsed_dims else None
        boundary = None
    
    # Find where precision explodes
    precision_threshold = 1e6
    precision_explosion = None
    for r in results:
        if r['precision_variance'] > precision_threshold and precision_explosion is None:
            precision_explosion = r['observation_dim']
    
    analysis = {
        'viable_dimensions': viable_dims,
        'collapsed_dimensions': collapsed_dims,
        'critical_dimension': critical_dim,
        'collapse_dimension': collapse_dim,
        'estimated_boundary': boundary,
        'precision_explosion_at': precision_explosion,
        'total_tested': len(results),
    }
    
    if verbose:
        print(f"\nViable dimensions (learning occurs):    {viable_dims}")
        print(f"Collapsed dimensions (no learning):     {collapsed_dims}")
        print(f"\nCritical dimension (last viable):       {critical_dim}")
        print(f"Collapse dimension (first failure):     {collapse_dim}")
        print(f"Estimated boundary:                     {boundary}")
        print(f"\nPrecision explosion occurs at:          {precision_explosion}")
        
        print("\n" + "─" * 70)
        print("INTERPRETATION")
        print("─" * 70)
        
        if boundary:
            print(f"\nUltron's viability boundary is approximately {boundary} dimensions.")
            print(f"Below this: the organism can metabolize its environment.")
            print(f"Above this: ecological mismatch - the world cannot be compressed.")
        else:
            if not collapsed_dims:
                print("\nNo collapse detected - organism viable across all tested dimensions.")
            elif not viable_dims:
                print("\nNo viability detected - organism cannot learn in any tested dimension.")
    
    return analysis


def print_sweep_table(results: List[Dict]):
    """Print results in a clean table format."""
    
    print("\n" + "=" * 100)
    print("DIMENSION SWEEP RESULTS TABLE")
    print("=" * 100)
    
    header = f"{'Dim':>4} │ {'Mean Err':>9} │ {'Min Err':>9} │ {'Improve':>9} │ {'Trend':>9} │ {'Prec Var':>12} │ {'Status':>8}"
    print(header)
    print("─" * 100)
    
    for r in results:
        dim = r['observation_dim']
        mean_err = r['mean_error']
        min_err = r['min_error']
        improve = r['error_improvement']
        trend = r['error_trend']
        prec_var = r['precision_variance']
        
        # Indicators
        if improve > 0.1:
            status = "✓ LEARN"
        elif improve > 0:
            status = "~ WEAK"
        else:
            status = "✗ FLAT"
        
        print(f"{dim:>4} │ {mean_err:>9.4f} │ {min_err:>9.4f} │ {improve:>+9.4f} │ {trend:>+9.4f} │ {prec_var:>12.2e} │ {status:>8}")
    
    print("=" * 100)


def save_sweep_results(results: List[Dict], analysis: Dict):
    """Save sweep results to history."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"history/sweep_{timestamp}.json"
    
    data = {
        'timestamp': timestamp,
        'experiment_type': 'dimension_sweep',
        'results': results,
        'analysis': analysis,
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    return filename


def main():
    """Run the dimension sweep."""
    
    # Standard sweep: 4 to 32 in steps of 4
    dimensions = [4, 8, 12, 16, 20, 24, 28, 32]
    
    # Run sweep
    results = run_dimension_sweep(
        dimensions=dimensions,
        ticks_per_run=2000,  # Enough for patterns to emerge
        environment_type="sine",  # Controlled, learnable
        feed_interval=50,
        feed_amount=15.0,
        verbose=True,
    )
    
    # Print table
    print_sweep_table(results)
    
    # Analyze
    analysis = analyze_sweep(results, verbose=True)
    
    # Save
    save_sweep_results(results, analysis)
    
    print("\n" + "=" * 70)
    print("SWEEP COMPLETE")
    print("=" * 70)
    
    return results, analysis


if __name__ == "__main__":
    main()
