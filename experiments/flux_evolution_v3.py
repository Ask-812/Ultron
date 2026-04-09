"""
Flux's Evolution Experiment v3 — The Sweet Spot

v1: too harsh, extinction at t=200
v2: too gentle, zero deaths, no selection
v3: medium pressure — can we get death AND birth AND trait shift?
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
    'consumption_rate': 0.5,        # between v1(0.8) and v2(0.3)
    'extraction_factor': 0.8,       # between v1(0.6) and v2(1.0)
    'learning_rate': 0.02,
    'observation_noise': 0.02,
    'update_cost_factor': 0.03,
    'near_death_threshold': 8.0,
    'environmental_richness': 1.3,  # moderate
    'reproduction_cost': 35.0,
    'mutation_rate': 0.05,
    'birth_trait_variation': 0.08,
}

def environment(t):
    base = np.sin(np.arange(8) * 0.7 + t * 0.05)
    drift = np.sin(np.arange(8) * 0.3 + t * 0.01) * 0.3
    noise = np.random.randn(8) * 0.1
    return base + drift + noise

entities = []
for i in range(20):
    entities.append({'state': create_ultron(config), 'gen': 0})

total_births = 0
total_deaths = 0
max_gen = 0

print("EVOLUTION v3: The sweet spot")
print("consumption=0.5 extraction=0.8 richness=1.3")
print("-" * 65)
sys.stdout.flush()

for t_step in range(1, 601):
    env = environment(t_step)
    
    for e in entities:
        if e['state'].is_alive:
            e['state'] = tick(e['state'], env, config)
    
    # Count new deaths this tick
    for e in entities:
        if not e['state'].is_alive and not hasattr(e, 'counted'):
            total_deaths += 1
            e['counted'] = True
    
    # Reproduction
    new_ents = []
    alive_count = sum(1 for e in entities if e['state'].is_alive)
    for e in entities:
        s = e['state']
        if s.is_alive and s.energy.current > 110 and alive_count + len(new_ents) < 50:
            parent, child = reproduce(s, config)
            e['state'] = parent
            if child is not None:
                total_births += 1
                g = e['gen'] + 1
                if g > max_gen:
                    max_gen = g
                new_ents.append({'state': child, 'gen': g})
    entities.extend(new_ents)
    
    if t_step % 60 == 0:
        alive = [e for e in entities if e['state'].is_alive]
        if not alive:
            print(f"t={t_step:3d}: EXTINCTION after {total_births}b/{total_deaths}d, max_gen={max_gen}")
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