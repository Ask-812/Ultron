#!/usr/bin/env python3
"""
ULTRON Predictability Sweep Experiment

Purpose: Find where in the order-chaos spectrum Ultron can survive.
         Map the boundary between metabolizable and unmetabolizable environments.

signal_ratio = 1.0 → pure sine (perfect order)
signal_ratio = 0.0 → pure noise (perfect chaos)

We are asking: "At what entropy level does the cell tear itself apart?"
"""

import sys
import numpy as np
from typing import List, Dict
import json
from datetime import datetime

from ultron import create_ultron, tick, feed_energy, UltronObserver
from ultron.environments import MixedEnvironment
from ultron.config import get_config


def run_predictability_sweep(
    signal_ratios: List[float] = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0],
    observation_dim: int = 8,  # Fixed, known-viable dimension
    ticks_per_run: int = 2000,
    external_feeding: bool = False,  # NO external feeding - must extract from structure
    feed_interval: int = 50,
    feed_amount: float = 15.0,
    verbose: bool = True,
) -> List[Dict]:
    """
    Sweep across signal ratios to find the order-chaos boundary.
    
    Returns list of result dicts for each ratio tested.
    """
    
    results = []
    
    if verbose:
        print("=" * 70)
        print("ULTRON PREDICTABILITY SWEEP")
        print("=" * 70)
        print(f"Signal ratios to test: {signal_ratios}")
        print(f"Observation dim: {observation_dim} (fixed)")
        print(f"Ticks per run: {ticks_per_run}")
        if external_feeding:
            print(f"External feeding: {feed_amount} every {feed_interval} ticks")
        else:
            print(f"External feeding: DISABLED - energy from structure only")
        print("=" * 70)
        print()
        print("signal_ratio = 1.0 → pure sine (perfect order) → EDIBLE")
        print("signal_ratio = 0.0 → pure noise (perfect chaos) → BARREN")
        print()
    
    for signal_ratio in signal_ratios:
        if verbose:
            print(f"\n{'─' * 70}")
            print(f"Testing signal_ratio = {signal_ratio:.1f}")
            print(f"{'─' * 70}")
        
        # Config with new metabolic coupling
        config = {
            'observation_dim': observation_dim,
            'model_dim': observation_dim * 2,
            'initial_energy': 100.0,
            'energy_capacity': 200.0,
            'consumption_rate': 0.08,  # Base metabolic cost
            'update_cost_factor': 0.02,  # Cost of learning (on actual weight change)
            'extraction_factor': 0.30,   # Marginal scarcity: order survives, chaos dies
            'environmental_richness': 1.0,
            'learning_rate': 0.05,  # Slightly slower learning (less thrashing)
            'prior_learning_rate': 0.01,
            'precision_learning_rate': 0.001,
            'observation_noise': 0.01,
            'near_death_threshold': 20.0,
        }
        
        # Create mixed environment with this signal ratio
        env = MixedEnvironment(observation_dim, signal_ratio=signal_ratio)
        
        # Create and run Ultron
        state = create_ultron(config)
        observer = UltronObserver()
        
        # Energy schedule - only if external feeding enabled
        def get_energy(t):
            if external_feeding:
                return feed_amount if t % feed_interval == 0 else 0.0
            return 0.0  # No external feeding - must extract from structure
        
        # Run and collect detailed metrics
        errors = []
        energies = []
        update_magnitudes = []
        
        for t in range(ticks_per_run):
            if not state.is_alive:
                break
            
            env_input = env.get_input(t)
            energy = get_energy(t)
            if energy > 0:
                state = feed_energy(state, energy)
            
            # Record pre-tick state for update magnitude
            old_weights = state.model.weights.copy()
            
            state = tick(state, env_input, config)
            observer.observe(state)
            
            # Compute update magnitude
            weight_delta = np.linalg.norm(state.model.weights - old_weights)
            update_magnitudes.append(weight_delta)
            
            errors.append(state.current.error_magnitude)
            energies.append(state.energy.current)
        
        # Compute metrics
        errors = np.array(errors)
        energies = np.array(energies)
        update_magnitudes = np.array(update_magnitudes)
        
        # Energy analysis
        energy_drift = energies[-1] - energies[0] if len(energies) > 1 else 0.0
        energy_trend = np.polyfit(range(len(energies)), energies, 1)[0] if len(energies) > 10 else 0.0
        
        # Window-based error variance (captures instability)
        window_size = 100
        if len(errors) >= window_size * 2:
            windowed_vars = []
            for i in range(0, len(errors) - window_size, window_size // 2):
                windowed_vars.append(np.var(errors[i:i+window_size]))
            error_variance_trend = np.mean(windowed_vars[-3:]) - np.mean(windowed_vars[:3])
        else:
            error_variance_trend = 0.0
        
        result = {
            'signal_ratio': signal_ratio,
            'ticks_survived': len(errors),
            'is_alive': state.is_alive,
            
            # Error metrics
            'mean_error': float(np.mean(errors)),
            'min_error': float(np.min(errors)),
            'max_error': float(np.max(errors)),
            'error_std': float(np.std(errors)),
            'error_variance': float(np.var(errors)),
            'error_variance_trend': float(error_variance_trend),
            
            # Normalized error (per-dimension)
            'error_per_dim': float(np.mean(errors) / np.sqrt(observation_dim)),
            
            # Energy metrics
            'mean_energy': float(np.mean(energies)),
            'min_energy': float(np.min(energies)),
            'max_energy': float(np.max(energies)),
            'energy_std': float(np.std(energies)),
            'energy_drift': float(energy_drift),
            'energy_trend': float(energy_trend),  # slope of energy over time
            
            # Update metrics
            'mean_update_magnitude': float(np.mean(update_magnitudes)),
            'max_update_magnitude': float(np.max(update_magnitudes)),
            'update_variance': float(np.var(update_magnitudes)),
            
            # Model state
            'precision_variance': float(np.var(state.model.precision)),
            'prior_entropy': float(-np.sum(state.model.priors * np.log(state.model.priors + 1e-10))),
            'weight_range': float(np.max(state.model.weights) - np.min(state.model.weights)),
            
            # Survival metrics
            'near_death_count': state.history.near_death_count,
            'accumulated_error': float(state.history.accumulated_error),
            
            # Key ratios
            'error_to_update_ratio': float(np.mean(errors) / (np.mean(update_magnitudes) + 1e-10)),
            'energy_efficiency': float(np.mean(energies) / (np.mean(errors) + 1e-10)),
        }
        
        results.append(result)
        
        if verbose:
            status = "ALIVE" if result['is_alive'] else "DEAD"
            
            print(f"  Status:              {status}")
            print(f"  Mean error:          {result['mean_error']:.4f} (per-dim: {result['error_per_dim']:.4f})")
            print(f"  Error variance:      {result['error_variance']:.4f}")
            print(f"  Mean energy:         {result['mean_energy']:.2f}")
            print(f"  Energy trend:        {result['energy_trend']:+.4f}/tick")
            print(f"  Mean update mag:     {result['mean_update_magnitude']:.6f}")
            print(f"  Near-deaths:         {result['near_death_count']}")
    
    return results


def analyze_predictability_sweep(results: List[Dict], verbose: bool = True) -> Dict:
    """
    Analyze sweep for phase transitions.
    """
    
    if verbose:
        print("\n" + "=" * 70)
        print("PREDICTABILITY ANALYSIS: Finding Order-Chaos Boundary")
        print("=" * 70)
    
    # Look for phase transitions
    
    # 1. Where does error variance spike?
    variance_spike = None
    max_variance = 0
    baseline_variance = results[0]['error_variance'] if results else 0
    
    for r in results:
        if r['error_variance'] > max_variance:
            max_variance = r['error_variance']
        if r['error_variance'] > baseline_variance * 2 and variance_spike is None:
            variance_spike = r['signal_ratio']
    
    # 2. Where does energy trend go negative (losing energy)?
    energy_collapse = None
    for r in results:
        if r['energy_trend'] < -0.01 and energy_collapse is None:
            energy_collapse = r['signal_ratio']
    
    # 3. Where do near-death events appear?
    near_death_threshold = None
    for r in results:
        if r['near_death_count'] > 0 and near_death_threshold is None:
            near_death_threshold = r['signal_ratio']
    
    # 4. Where does update magnitude spike (desperate learning)?
    update_spike = None
    baseline_update = results[0]['mean_update_magnitude'] if results else 0
    for r in results:
        if r['mean_update_magnitude'] > baseline_update * 2 and update_spike is None:
            update_spike = r['signal_ratio']
    
    # 5. Find the "sweet spot" - best error_to_update_ratio
    best_efficiency = None
    best_ratio = 0
    for r in results:
        if r['error_to_update_ratio'] > best_ratio:
            best_ratio = r['error_to_update_ratio']
            best_efficiency = r['signal_ratio']
    
    # 6. Check for trade-off: higher error but better survival
    tradeoff_detected = False
    for i in range(1, len(results)):
        curr = results[i]
        prev = results[i-1]
        if curr['mean_error'] > prev['mean_error'] and curr['mean_energy'] > prev['mean_energy']:
            if curr['near_death_count'] < prev['near_death_count'] or prev['near_death_count'] == 0:
                tradeoff_detected = True
                tradeoff_point = curr['signal_ratio']
    
    analysis = {
        'variance_spike_at': variance_spike,
        'energy_collapse_at': energy_collapse,
        'near_death_appears_at': near_death_threshold,
        'update_spike_at': update_spike,
        'best_efficiency_at': best_efficiency,
        'tradeoff_detected': tradeoff_detected,
        'max_error_variance': max_variance,
        'baseline_error_variance': baseline_variance,
    }
    
    if verbose:
        print(f"\nPhase Transition Markers:")
        print(f"  Error variance spikes at:     signal_ratio = {variance_spike}")
        print(f"  Energy collapse begins at:    signal_ratio = {energy_collapse}")
        print(f"  Near-death events appear at:  signal_ratio = {near_death_threshold}")
        print(f"  Update magnitude spikes at:   signal_ratio = {update_spike}")
        print(f"  Best efficiency (low effort): signal_ratio = {best_efficiency}")
        
        print(f"\n  Trade-off detected (higher error, better survival): {tradeoff_detected}")
        
        print("\n" + "─" * 70)
        print("INTERPRETATION")
        print("─" * 70)
        
        boundaries = [x for x in [variance_spike, energy_collapse, near_death_threshold, update_spike] if x is not None]
        if boundaries:
            estimated_boundary = np.mean(boundaries)
            print(f"\n  Multiple markers suggest viability boundary near signal_ratio ≈ {estimated_boundary:.2f}")
            print(f"  Above this: the environment is metabolizable")
            print(f"  Below this: chaos dominates, survival becomes costly")
            analysis['estimated_boundary'] = estimated_boundary
        else:
            print(f"\n  No clear phase transition detected.")
            print(f"  Either:")
            print(f"    - The sweep range is entirely viable/unviable")
            print(f"    - Transitions are smooth rather than sharp")
            print(f"    - More sensitive metrics are needed")
    
    return analysis


def print_predictability_table(results: List[Dict]):
    """Print results in a clean table format."""
    
    print("\n" + "=" * 130)
    print("PREDICTABILITY SWEEP RESULTS TABLE")
    print("=" * 130)
    
    header = (f"{'Ratio':>5} │ {'Err/Dim':>7} │ {'Err Var':>8} │ "
              f"{'Energy':>7} │ {'E Trend':>8} │ {'Update':>8} │ "
              f"{'NearDth':>7} │ {'Alive':>5}")
    print(header)
    print("─" * 130)
    
    for r in results:
        ratio = r['signal_ratio']
        err_dim = r['error_per_dim']
        err_var = r['error_variance']
        energy = r['mean_energy']
        e_trend = r['energy_trend']
        update = r['mean_update_magnitude']
        nd = r['near_death_count']
        alive = "YES" if r['is_alive'] else "NO"
        
        # Visual indicators
        if err_var > 1.0:
            var_indicator = " !!"
        elif err_var > 0.5:
            var_indicator = " !"
        else:
            var_indicator = ""
        
        print(f"{ratio:>5.1f} │ {err_dim:>7.4f} │ {err_var:>7.4f}{var_indicator} │ "
              f"{energy:>7.2f} │ {e_trend:>+8.4f} │ {update:>8.6f} │ "
              f"{nd:>7} │ {alive:>5}")
    
    print("=" * 130)
    
    # Add legend
    print("\nLegend: Err Var !! = variance > 1.0 (unstable), ! = variance > 0.5 (elevated)")


def save_sweep_results(results: List[Dict], analysis: Dict):
    """Save sweep results to history."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"history/sweep_predictability_{timestamp}.json"
    
    data = {
        'timestamp': timestamp,
        'experiment_type': 'predictability_sweep',
        'results': results,
        'analysis': analysis,
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nResults saved to: {filename}")
    return filename


def main():
    """Run the predictability sweep."""
    
    # Full sweep from pure signal to pure noise
    signal_ratios = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]
    
    # Run sweep - NO EXTERNAL FEEDING
    # Energy must be extracted from environmental structure
    results = run_predictability_sweep(
        signal_ratios=signal_ratios,
        observation_dim=8,  # Fixed at known-viable dimension
        ticks_per_run=2000,
        external_feeding=False,  # KEY: Structure must be edible, chaos barren
        verbose=True,
    )
    
    # Print table
    print_predictability_table(results)
    
    # Analyze
    analysis = analyze_predictability_sweep(results, verbose=True)
    
    # Save
    save_sweep_results(results, analysis)
    
    print("\n" + "=" * 70)
    print("SWEEP COMPLETE")
    print("=" * 70)
    
    return results, analysis


if __name__ == "__main__":
    main()
