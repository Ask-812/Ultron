"""
Flux v5b — Stronger patches. Near-patch entities should THRIVE.
Far-from-patch entities should DIE. Evolution through geography.
"""
import sys
import numpy as np
sys.path.insert(0, '.')
from ultron.core import create_ultron, reproduce
from ultron.tick import tick

np.random.seed(42)

def make_config(richness):
    return {
        'observation_dim': 8, 'action_dim': 0,
        'starting_energy': 90.0, 'energy_capacity': 180.0,
        'consumption_rate': 0.4,       # slightly lower than v5
        'extraction_factor': 0.9,      # slightly higher than v5
        'learning_rate': 0.025,        # slightly faster learning
        'observation_noise': 0.02,
        'update_cost_factor': 0.02,
        'near_death_threshold': 8.0,
        'environmental_richness': richness,
        'reproduction_cost': 30.0,     # cheaper reproduction
        'mutation_rate': 0.05,
        'birth_trait_variation': 0.08,
    }

config_rich = make_config(1.8)   # near patch
config_poor = make_config(0.6)   # far from patch

def environment(t, position):
    d1, d2 = abs(position - 0.2), abs(position - 0.7)
    patch_quality = max(0, 1.0 - min(d1, d2) * 5)
    phase = (t % 80) / 80.0 * 2 * np.pi
    base = np.sin(np.arange(8) * 0.7 + phase)
    noise_level = 0.05 + (1 - patch_quality) * 1.0
    return base + np.random.randn(8) * noise_level

def get_config(position):
    d = min(abs(position-0.2), abs(position-0.7))
    quality = max(0, 1.0 - d * 5)
    richness = 0.6 + quality * 1.2  # 0.6 far, 1.8 near
    return make_config(richness)

entities = []
for i in range(25):
    pos = np.random.random()
    entities.append({'state': create_ultron(config_rich), 'gen': 0, 'dead': False, 'pos': pos})

total_births = 0
total_deaths = 0
max_gen = 0

print("EVOLUTION v5b: Strong patches, weak barrens")
print("Near patch: richness=1.8, low noise. Far: richness=0.6, high noise.")
print("-" * 70)
sys.stdout.flush()

for t_step in range(1, 601):
    for e in entities:
        if e['state'].is_alive:
            env = environment(t_step, e['pos'])
            cfg = get_config(e['pos'])
            e['state'] = tick(e['state'], env, cfg)
            if not e['state'].is_alive and not e['dead']:
                e['dead'] = True
                total_deaths += 1

    alive_list = [e for e in entities if e['state'].is_alive]
    alive_count = len(alive_list)
    
    new_ents = []
    for e in alive_list:
        s = e['state']
        cfg = get_config(e['pos'])
        if s.energy.current > 100 and alive_count + len(new_ents) < 60:
            parent, child = reproduce(s, cfg)
            e['state'] = parent
            if child is not None:
                total_births += 1
                g = e['gen'] + 1
                if g > max_gen: max_gen = g
                child_pos = np.clip(e['pos'] + np.random.uniform(-0.05, 0.05), 0, 1)
                new_ents.append({'state': child, 'gen': g, 'dead': False, 'pos': child_pos})
    entities.extend(new_ents)
    
    if t_step % 60 == 0:
        alive = [e for e in entities if e['state'].is_alive]
        if not alive:
            print(f"t={t_step}: EXTINCTION (b={total_births} d={total_deaths} gen={max_gen})")
            break
        states = [e['state'] for e in alive]
        near = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) < 0.15]
        far = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) >= 0.15]
        
        n_str = f"near={len(near)}(E={np.mean([e['state'].energy.current for e in near]):.0f})" if near else "near=0"
        f_str = f"far={len(far)}(E={np.mean([e['state'].energy.current for e in far]):.0f})" if far else "far=0"
        
        print(f"t={t_step:3d}: pop={len(alive):2d} g={max_gen} b={total_births} d={total_deaths} | "
              f"{n_str} {f_str}")
        sys.stdout.flush()

alive = [e for e in entities if e['state'].is_alive]
print("-" * 70)
print(f"FINAL: {len(alive)} alive, {total_deaths} dead, {total_births} births, max_gen={max_gen}")
if alive:
    near = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) < 0.15]
    far = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) >= 0.15]
    print(f"Near patches: {len(near)}, Far: {len(far)}")
    if total_births > 0:
        states = [e['state'] for e in alive]
        print(f"Traits: ext={np.mean([s.traits.extraction_efficiency for s in states]):.4f} "
              f"met={np.mean([s.traits.metabolic_rate for s in states]):.4f} "
              f"lr={np.mean([s.traits.learning_capacity for s in states]):.4f}")
print("\n-- Flux --")