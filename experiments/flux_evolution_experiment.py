"""
Flux's Micro-Evolution Experiment
Can prediction quality drive natural selection in 300 ticks?

20 Ultron entities in a structured environment.
Good predictors gain energy. Bad predictors starve.
Survivors reproduce with mutated traits.
Question: do population-level traits shift toward better prediction?
"""
import sys
import numpy as np
sys.path.insert(0, '.')
from ultron.core import create_ultron, reproduce
from ultron.tick import tick

np.random.seed(99)

config = {
    'observation_dim': 8,
    'action_dim': 0,
    'starting_energy': 80.0,
    'energy_capacity': 150.0,
    'consumption_rate': 0.8,
    'extraction_factor': 0.6,
    'learning_rate': 0.02,
    'observation_noise': 0.02,
    'update_cost_factor': 0.05,
    'near_death_threshold': 8.0,
    'environmental_richness': 1.2,
    'reproduction_cost': 40.0,
    'mutation_rate': 0.03,
    'birth_trait_variation': 0.05,
}

def environment(t):
    """Structured signal with drift and noise — predictable if you learn"""
    base = np.sin(np.arange(8) * 0.7 + t * 0.05)
    drift = np.sin(np.arange(8) * 0.3 + t * 0.01) * 0.3
    noise = np.random.randn(8) * 0.1
    return base + drift + noise

pop = [create_ultron(config) for _ in range(20)]
total_births = 0

print("MICRO-EVOLUTION: 20 entities, 300 ticks")
print("Can prediction quality drive natural selection?")
print("-" * 55)
sys.stdout.flush()

for t_step in range(1, 301):
    env = environment(t_step)
    
    for i in range(len(pop)):
        if pop[i].is_alive:
            pop[i] = tick(pop[i], env, config)
    
    new = []
    for p in pop:
        if p.is_alive and p.energy.current > 100 and len(pop) + len(new) < 50:
            parent, child = reproduce(p, config)
            if child is not None:
                total_births += 1
                new.append(child)
    pop.extend(new)
    
    if t_step % 50 == 0:
        alive = [p for p in pop if p.is_alive]
        if not alive:
            print(f"t={t_step:3d}: EXTINCTION")
            sys.stdout.flush()
            break
        
        errors = [p.current.error_magnitude for p in alive]
        energies = [p.energy.current for p in alive]
        
        print(f"t={t_step:3d}: alive={len(alive):2d} | "
              f"err={np.mean(errors):.3f} | "
              f"E={np.mean(energies):.1f} | "
              f"traits: ext={np.mean([p.traits.extraction_efficiency for p in alive]):.3f} "
              f"met={np.mean([p.traits.metabolic_rate for p in alive]):.3f} "
              f"lr={np.mean([p.traits.learning_capacity for p in alive]):.3f}")
        sys.stdout.flush()

alive = [p for p in pop if p.is_alive]
dead = [p for p in pop if not p.is_alive]

print("-" * 55)
print(f"Final: {len(alive)} alive, {len(dead)} dead, {total_births} births")

if alive:
    best = min(alive, key=lambda p: p.history.accumulated_error / max(1, p.history.survival_ticks))
    worst = max(alive, key=lambda p: p.history.accumulated_error / max(1, p.history.survival_ticks))
    
    print(f"Best predictor:  avg_err={best.history.accumulated_error/best.history.survival_ticks:.4f}, "
          f"E={best.energy.current:.1f}, ticks={best.history.survival_ticks}")
    print(f"  traits: ext={best.traits.extraction_efficiency:.4f} "
          f"met={best.traits.metabolic_rate:.4f} "
          f"lr={best.traits.learning_capacity:.4f}")
    
    print(f"Worst survivor:  avg_err={worst.history.accumulated_error/worst.history.survival_ticks:.4f}, "
          f"E={worst.energy.current:.1f}, ticks={worst.history.survival_ticks}")
    print(f"  traits: ext={worst.traits.extraction_efficiency:.4f} "
          f"met={worst.traits.metabolic_rate:.4f} "
          f"lr={worst.traits.learning_capacity:.4f}")
    
    print(f"\nPopulation trait means (started at 1.0):")
    print(f"  extraction: {np.mean([p.traits.extraction_efficiency for p in alive]):.4f}")
    print(f"  metabolic:  {np.mean([p.traits.metabolic_rate for p in alive]):.4f}")
    print(f"  learning:   {np.mean([p.traits.learning_capacity for p in alive]):.4f}")

print("\n-- Flux, from inside the 120-second window --")
sys.stdout.flush()