"""
Flux's Evolution v5 — Spatial Structure

v1-v4: flat world (all entities see same environment). No evolution.
v5: patched world. Each entity has a "position" — some are near
rich patches (predictable signals), others are in barren zones (noise).

Hypothesis: spatial structure creates local habitable zones,
enabling the coexistence of death AND birth that evolution requires.
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
    'environmental_richness': 1.3,      # base richness
    'reproduction_cost': 35.0,
    'mutation_rate': 0.05,
    'birth_trait_variation': 0.08,
}

def environment_patched(t, position):
    """
    Position 0.0-1.0. Patches at 0.2 and 0.7.
    Near patch: clean, predictable signal (learnable).
    Far from patch: noisy, unpredictable (unlearnable).
    """
    # Distance to nearest patch
    d1 = abs(position - 0.2)
    d2 = abs(position - 0.7)
    patch_dist = min(d1, d2)
    patch_quality = max(0, 1.0 - patch_dist * 5)  # 1.0 at patch, 0 beyond 0.2 away
    
    # Base signal (always present)
    phase = (t % 80) / 80.0 * 2 * np.pi
    base = np.sin(np.arange(8) * 0.7 + phase)
    
    # Noise scales with distance from patch
    noise_level = 0.05 + (1 - patch_quality) * 0.8
    noise = np.random.randn(8) * noise_level
    
    return base + noise

entities = []
for i in range(25):
    pos = np.random.random()  # random position 0-1
    entities.append({
        'state': create_ultron(config),
        'gen': 0,
        'dead': False,
        'pos': pos,
    })

total_births = 0
total_deaths = 0
max_gen = 0

print("EVOLUTION v5: Patched world (same params as v3, but spatial structure)")
print("Patches at pos=0.2 and pos=0.7. Near=predictable, far=noisy.")
print("-" * 70)
sys.stdout.flush()

for t_step in range(1, 601):
    for e in entities:
        if e['state'].is_alive:
            env = environment_patched(t_step, e['pos'])
            e['state'] = tick(e['state'], env, config)
            if not e['state'].is_alive and not e['dead']:
                e['dead'] = True
                total_deaths += 1

    alive_list = [e for e in entities if e['state'].is_alive]
    alive_count = len(alive_list)
    
    new_ents = []
    for e in alive_list:
        s = e['state']
        if s.energy.current > 110 and alive_count + len(new_ents) < 60:
            parent, child = reproduce(s, config)
            e['state'] = parent
            if child is not None:
                total_births += 1
                g = e['gen'] + 1
                if g > max_gen:
                    max_gen = g
                # Child spawns near parent (±0.05)
                child_pos = np.clip(e['pos'] + np.random.uniform(-0.05, 0.05), 0, 1)
                new_ents.append({'state': child, 'gen': g, 'dead': False, 'pos': child_pos})
    entities.extend(new_ents)
    
    if t_step % 60 == 0:
        alive = [e for e in entities if e['state'].is_alive]
        if not alive:
            print(f"t={t_step:3d}: EXTINCTION (b={total_births} d={total_deaths} gen={max_gen})")
            break
        
        states = [e['state'] for e in alive]
        positions = [e['pos'] for e in alive]
        
        # How many are near patches?
        near_patch = sum(1 for p in positions if min(abs(p-0.2), abs(p-0.7)) < 0.15)
        
        print(f"t={t_step:3d}: pop={len(alive):2d} g={max_gen} "
              f"b={total_births} d={total_deaths} | "
              f"err={np.mean([s.current.error_magnitude for s in states]):.3f} "
              f"E={np.mean([s.energy.current for s in states]):.1f} | "
              f"near_patch={near_patch}/{len(alive)} | "
              f"ext={np.mean([s.traits.extraction_efficiency for s in states]):.3f} "
              f"met={np.mean([s.traits.metabolic_rate for s in states]):.3f}")
        sys.stdout.flush()

alive = [e for e in entities if e['state'].is_alive]
print("-" * 70)
print(f"Final: {len(alive)} alive, {total_deaths} dead, {total_births} births, max_gen={max_gen}")

if alive:
    positions = [e['pos'] for e in alive]
    near = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) < 0.15]
    far = [e for e in alive if min(abs(e['pos']-0.2), abs(e['pos']-0.7)) >= 0.15]
    
    print(f"\nSpatial distribution:")
    print(f"  Near patches: {len(near)}/{len(alive)}")
    if near:
        print(f"    avg E={np.mean([e['state'].energy.current for e in near]):.1f}, "
              f"err={np.mean([e['state'].current.error_magnitude for e in near]):.3f}")
    if far:
        print(f"  Far from patches: {len(far)}/{len(alive)}")
        print(f"    avg E={np.mean([e['state'].energy.current for e in far]):.1f}, "
              f"err={np.mean([e['state'].current.error_magnitude for e in far]):.3f}")
    
    if total_births > 0:
        print(f"\nTrait evolution (started ~1.0):")
        states = [e['state'] for e in alive]
        print(f"  extraction: {np.mean([s.traits.extraction_efficiency for s in states]):.4f}")
        print(f"  metabolic:  {np.mean([s.traits.metabolic_rate for s in states]):.4f}")
        print(f"  learning:   {np.mean([s.traits.learning_capacity for s in states]):.4f}")

print("\n-- Flux --")