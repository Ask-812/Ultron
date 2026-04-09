"""
Flux's Evolution v4 — Cyclic Environment

v1-v3 had drifting environments. Prediction error grew as the world
moved away from what entities learned. v4 uses a CYCLIC world —
patterns repeat every ~100 ticks. Can entities lock onto cycles
and maintain energy long enough to reproduce and evolve?
"""
import sys
import numpy as np
sys.path.insert(0, '.')
from ultron.core import create_ultron, reproduce
from ultron.tick import tick

np.random.seed(42)

config = {
    'observation_dim': 8,
    'action_dim': 0,
    'starting_energy': 90.0,
    'energy_capacity': 180.0,
    'consumption_rate': 0.5,
    'extraction_factor': 0.8,
    'learning_rate': 0.02,
    'observation_noise': 0.02,
    'update_cost_factor': 0.03,
    'near_death_threshold': 8.0,
    'environmental_richness': 1.3,
    'reproduction_cost': 35.0,
    'mutation_rate': 0.05,
    'birth_trait_variation': 0.08,
}

def environment_cyclic(t):
    """Cyclic environment — repeats every ~100 ticks with slight noise"""
    phase = (t % 100) / 100.0 * 2 * np.pi
    base = np.sin(np.arange(8) * 0.7 + phase)
    harmonic = np.sin(np.arange(8) * 1.4 + phase * 2) * 0.3
    noise = np.random.randn(8) * 0.08
    return base + harmonic + noise

entities = []
for i in range(20):
    entities.append({'state': create_ultron(config), 'gen': 0, 'dead': False})

total_births = 0
total_deaths = 0
max_gen = 0

print("EVOLUTION v4: Cyclic environment (period=100)")
print("Same params as v3 but world repeats — can they lock on?")
print("-" * 65)
sys.stdout.flush()

for t_step in range(1, 601):
    env = environment_cyclic(t_step)
    
    for e in entities:
        if e['state'].is_alive:
            e['state'] = tick(e['state'], env, config)
            if not e['state'].is_alive and not e['dead']:
                e['dead'] = True
                total_deaths += 1
    
    alive_list = [e for e in entities if e['state'].is_alive]
    alive_count = len(alive_list)
    
    new_ents = []
    for e in alive_list:
        s = e['state']
        if s.energy.current > 110 and alive_count + len(new_ents) < 50:
            parent, child = reproduce(s, config)
            e['state'] = parent
            if child is not None:
                total_births += 1
                g = e['gen'] + 1
                if g > max_gen:
                    max_gen = g
                new_ents.append({'state': child, 'gen': g, 'dead': False})
    entities.extend(new_ents)
    
    if t_step % 60 == 0:
        alive = [e for e in entities if e['state'].is_alive]
        if not alive:
            print(f"t={t_step:3d}: EXTINCTION (b={total_births} d={total_deaths} gen={max_gen})")
            break
        
        states = [e['state'] for e in alive]
        gens = [e['gen'] for e in alive]
        
        print(f"t={t_step:3d}: pop={len(alive):2d} g={max(gens)} "
              f"b={total_births} d={total_deaths} | "
              f"err={np.mean([s.current.error_magnitude for s in states]):.3f} "
              f"E={np.mean([s.energy.current for s in states]):.1f} | "
              f"ext={np.mean([s.traits.extraction_efficiency for s in states]):.3f} "
              f"met={np.mean([s.traits.metabolic_rate for s in states]):.3f} "
              f"lr={np.mean([s.traits.learning_capacity for s in states]):.3f}")
        sys.stdout.flush()

alive = [e for e in entities if e['state'].is_alive]
print("-" * 65)
print(f"Final: {len(alive)} alive, {total_deaths} dead, {total_births} births, max_gen={max_gen}")

if alive:
    states = [e['state'] for e in alive]
    print(f"\nTraits (started ~1.0):")
    print(f"  extraction: {np.mean([s.traits.extraction_efficiency for s in states]):.4f}")
    print(f"  metabolic:  {np.mean([s.traits.metabolic_rate for s in states]):.4f}")
    print(f"  learning:   {np.mean([s.traits.learning_capacity for s in states]):.4f}")

print("\n-- Flux --")