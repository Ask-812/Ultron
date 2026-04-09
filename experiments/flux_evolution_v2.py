"""
Flux's Evolution Experiment v2 — Finding the Habitable Zone
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
    'starting_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.3,
    'extraction_factor': 1.0,
    'learning_rate': 0.02,
    'observation_noise': 0.02,
    'update_cost_factor': 0.02,
    'near_death_threshold': 8.0,
    'environmental_richness': 1.5,
    'reproduction_cost': 35.0,
    'mutation_rate': 0.05,
    'birth_trait_variation': 0.08,
}

def environment(t):
    base = np.sin(np.arange(8) * 0.7 + t * 0.05)
    drift = np.sin(np.arange(8) * 0.3 + t * 0.01) * 0.3
    noise = np.random.randn(8) * 0.1
    return base + drift + noise

# Track generation externally
entities = []
for i in range(15):
    u = create_ultron(config)
    entities.append({'state': u, 'gen': 0})

total_births = 0
max_gen = 0

print("EVOLUTION v2: Finding the habitable zone")
print("consumption=0.3 extraction=1.0 richness=1.5 repro_cost=35")
print("-" * 60)
sys.stdout.flush()

for t_step in range(1, 501):
    env = environment(t_step)
    
    for e in entities:
        if e['state'].is_alive:
            e['state'] = tick(e['state'], env, config)
    
    new_ents = []
    for e in entities:
        s = e['state']
        if s.is_alive and s.energy.current > 120 and len(entities) + len(new_ents) < 60:
            parent, child = reproduce(s, config)
            e['state'] = parent
            if child is not None:
                total_births += 1
                g = e['gen'] + 1
                if g > max_gen:
                    max_gen = g
                new_ents.append({'state': child, 'gen': g})
    entities.extend(new_ents)
    
    if t_step % 50 == 0:
        alive = [e for e in entities if e['state'].is_alive]
        if not alive:
            print(f"t={t_step:3d}: EXTINCTION (births={total_births}, max_gen={max_gen})")
            break
        
        states = [e['state'] for e in alive]
        gens = [e['gen'] for e in alive]
        errors = [s.current.error_magnitude for s in states]
        energies = [s.energy.current for s in states]
        
        print(f"t={t_step:3d}: pop={len(alive):2d} gen={max(gens)} | "
              f"err={np.mean(errors):.3f} E={np.mean(energies):.1f} | "
              f"ext={np.mean([s.traits.extraction_efficiency for s in states]):.3f} "
              f"met={np.mean([s.traits.metabolic_rate for s in states]):.3f} "
              f"lr={np.mean([s.traits.learning_capacity for s in states]):.3f}")
        sys.stdout.flush()

alive = [e for e in entities if e['state'].is_alive]
dead = [e for e in entities if not e['state'].is_alive]
print("-" * 60)
print(f"Final: {len(alive)} alive, {len(dead)} dead, {total_births} births, max_gen={max_gen}")

if alive and total_births > 0:
    states = [e['state'] for e in alive]
    print(f"\nTrait evolution (started ~1.0):")
    print(f"  extraction: {np.mean([s.traits.extraction_efficiency for s in states]):.4f}")
    print(f"  metabolic:  {np.mean([s.traits.metabolic_rate for s in states]):.4f}")
    print(f"  learning:   {np.mean([s.traits.learning_capacity for s in states]):.4f}")
    
    founders = [e for e in alive if e['gen'] == 0]
    children = [e for e in alive if e['gen'] > 0]
    if founders and children:
        print(f"\n  Founders alive: {len(founders)}, avg_E={np.mean([e['state'].energy.current for e in founders]):.1f}")
        print(f"  Offspring alive: {len(children)}, avg_E={np.mean([e['state'].energy.current for e in children]):.1f}")
elif alive:
    print("No reproduction occurred — still in habitable zone but not fertile.")
    states = [e['state'] for e in alive]
    print(f"  avg energy: {np.mean([s.energy.current for s in states]):.1f}")
    print(f"  avg error:  {np.mean([s.current.error_magnitude for s in states]):.3f}")

print("\n-- Flux --")