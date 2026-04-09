"""
Pack Hunters vs Lone Wolves: Does quorum sensing create emergent coordination?

Two runs, same seed:
  A) quorum_sensing_enabled=False (independent cells)
  B) quorum_sensing_enabled=True  (density-dependent action scaling)

Both with toxins + predation + fragmentation. 15k ticks, 4 organisms on 35x35.
"""
import numpy as np
import sys, time
sys.path.insert(0, '.')
from ultron.tissue import Tissue

TICKS = 15000
GRID = 35
SEED = 777

COMMON = dict(
    observation_dim=12, signal_dim=4, action_dim=4, env_dim=8,
    starting_energy=150.0, energy_capacity=200.0, consumption_rate=0.08,
    extraction_factor=0.60, base_signal_ratio=0.55, spatial_gradient=0.15,
    signal_hop_decay=0.9, signal_emission_strength=0.3,
    signal_energy_coupling=1.0, signal_division_coupling=0.1,
    energy_leak_rate=0.03,
    division_energy_threshold=90.0, division_cost=12.0,
    apoptosis_threshold=3.0, apoptosis_streak=100,
    cell_mutation_rate=0.015,
    phenotype_max_plasticity=0.05, phenotype_lock_tau=200.0,
    phenotype_min_plasticity=0.001,
    phenotype_emission_coupling=2.0, phenotype_affinity_coupling=2.0,
    resource_depletion_rate=0.002, resource_regen_rate=0.0005,
    migration_enabled=True,
    migration_energy_cost=2.0, migration_resource_threshold=0.4,
    action_division_coupling=2.0,
    action_weight_scale=0.15, action_mutation_rate=0.03,
    displacement_energy_ratio=3.0,
    # 4-patch landscape
    landscape_type='patches', landscape_base=0.15,
    landscape_n_patches=4, landscape_patch_radius=0.22,
    landscape_patch_richness=1.0,
    landscape_patch_centers=[(9,9), (9,GRID-10), (GRID-10,9), (GRID-10,GRID-10)],
    # Fragmentation
    fragmentation_enabled=True, fragmentation_interval=200,
    fragmentation_min_size=5,
    # Stigmergy
    death_imprint_strength=1.0, stigmergy_decay=0.995,
    stigmergy_sensing=0.3, stigmergy_avoidance=0.3,
    # Predation + evolved mechanics
    predation_enabled=True, predation_energy_ratio=1.5,
    predation_efficiency=0.5, predation_cooldown=5,
    predation_action_power=0.5, predation_evasion_scaling=0.2,
    predation_alarm_strength=0.5,
    # Toxins
    toxin_enabled=True, toxin_emission_rate=0.15,
    toxin_damage_rate=0.6, toxin_range=3, toxin_cost_rate=0.05,
    # Lamarckian
    weight_inheritance_ratio=0.5, weight_inheritance_noise=0.01,
)

def place_organisms(tissue, positions, seed):
    np.random.seed(seed)
    lid = 1
    for (cr, cc) in positions:
        placed = 0
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                if placed >= 8:
                    break
                r, c = cr + dr, cc + dc
                if (0 <= r < GRID and 0 <= c < GRID
                        and tissue.grid[r][c] is None and abs(dr) + abs(dc) <= 3):
                    tissue.place_cell(r, c)
                    tissue.grid[r][c].lineage_id = lid
                    tissue.grid[r][c].energy = 150.0
                    placed += 1
        lid += 1

def run_experiment(label, config, seed):
    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    t0 = time.time()
    tissue = Tissue(GRID, GRID, config)
    positions = [(5,5), (5,GRID-6), (GRID-6,5), (GRID-6,GRID-6)]
    place_organisms(tissue, positions, seed)
    
    snapshots = []
    for t in range(1, TICKS + 1):
        tissue.step()
        if t % 1000 == 0:
            lineages = {}
            for r in range(GRID):
                for c in range(GRID):
                    cell = tissue.grid[r][c]
                    if cell is not None and cell.is_alive:
                        lid = cell.lineage_id
                        if lid not in lineages:
                            lineages[lid] = {'count': 0, 'energy': 0, 'action_mag': 0}
                        lineages[lid]['count'] += 1
                        lineages[lid]['energy'] += cell.energy
                        if cell.action is not None:
                            lineages[lid]['action_mag'] += float(np.linalg.norm(cell.action))
            
            total = sum(v['count'] for v in lineages.values())
            lin_str = ' '.join(f"L{k}={v['count']}" for k, v in sorted(lineages.items())[:6])
            avg_act = sum(v['action_mag'] for v in lineages.values()) / max(total, 1)
            print(f"  t={t:5d}: {lin_str} (total={total}, act={avg_act:.3f},"
                  f" pred={tissue.predation_kills}, toxin_dmg={tissue.toxin_damage_dealt:.0f},"
                  f" deaths={tissue.total_deaths}, births={tissue.total_births})")
            snapshots.append({
                'tick': t, 'total': total, 'lineages': len(lineages),
                'avg_action': avg_act, 'pred': tissue.predation_kills,
                'toxin_dmg': tissue.toxin_damage_dealt, 'deaths': tissue.total_deaths,
                'births': tissue.total_births
            })
    
    elapsed = time.time() - t0
    
    # Final census
    lineages = {}
    for r in range(GRID):
        for c in range(GRID):
            cell = tissue.grid[r][c]
            if cell is not None and cell.is_alive:
                lid = cell.lineage_id
                if lid not in lineages:
                    lineages[lid] = {'count': 0, 'energy': 0, 'action_mag': 0, 'age': 0}
                lineages[lid]['count'] += 1
                lineages[lid]['energy'] += cell.energy
                lineages[lid]['age'] = max(lineages[lid]['age'], cell.age)
                if cell.action is not None:
                    lineages[lid]['action_mag'] += float(np.linalg.norm(cell.action))
    
    total = sum(v['count'] for v in lineages.values())
    print(f"\n  FINAL ({label}):")
    print(f"    Total cells: {total}")
    print(f"    Lineages: {len(lineages)}")
    print(f"    Predation kills: {tissue.predation_kills}")
    print(f"    Toxin damage: {tissue.toxin_damage_dealt:.1f}")
    print(f"    Toxin events: {tissue.toxin_events}")
    print(f"    Deaths: {tissue.total_deaths}")
    print(f"    Births: {tissue.total_births}")
    for lid, v in sorted(lineages.items()):
        avg_act = v['action_mag'] / max(v['count'], 1)
        avg_e = v['energy'] / max(v['count'], 1)
        print(f"    L{lid}: {v['count']} cells, E={avg_e:.1f}, act={avg_act:.3f}")
    print(f"    Runtime: {elapsed:.1f}s")
    
    return {
        'total': total, 'lineages': len(lineages),
        'pred': tissue.predation_kills, 'toxin_dmg': tissue.toxin_damage_dealt,
        'deaths': tissue.total_deaths, 'births': tissue.total_births,
        'snapshots': snapshots, 'elapsed': elapsed,
        'final_lineages': {k: v['count'] for k, v in lineages.items()}
    }

print("="*70)
print("  PACK HUNTERS vs LONE WOLVES")
print("  Does quorum sensing create emergent coordination?")
print("="*70)

# Run A: No quorum sensing (Lone Wolves)
config_a = {**COMMON, 'quorum_sensing_enabled': False}
results_a = run_experiment("LONE WOLVES (no quorum sensing)", config_a, SEED)

# Run B: With quorum sensing (Pack Hunters)
config_b = {**COMMON, 'quorum_sensing_enabled': True,
            'quorum_threshold': 4, 'quorum_boost': 0.3, 'quorum_radius': 2}
results_b = run_experiment("PACK HUNTERS (quorum sensing ON)", config_b, SEED)

# Compare
print("\n" + "="*70)
print("  COMPARISON")
print("="*70)
print(f"  {'Metric':<25s} {'Lone Wolves':>15s} {'Pack Hunters':>15s} {'Diff':>10s}")
print(f"  {'-'*25} {'-'*15} {'-'*15} {'-'*10}")
for metric, key in [
    ('Final cells', 'total'),
    ('Lineages', 'lineages'),
    ('Predation kills', 'pred'),
    ('Toxin damage', 'toxin_dmg'),
    ('Total deaths', 'deaths'),
    ('Total births', 'births'),
]:
    a = results_a[key]
    b = results_b[key]
    if isinstance(a, float):
        diff = f"{(b-a)/max(abs(a),1)*100:+.1f}%"
        print(f"  {metric:<25s} {a:>15.1f} {b:>15.1f} {diff:>10s}")
    else:
        diff = f"{b-a:+d}" if isinstance(a, int) else ""
        print(f"  {metric:<25s} {a:>15d} {b:>15d} {diff:>10s}")

# Action magnitude comparison
early_a = results_a['snapshots'][0]['avg_action']
late_a = results_a['snapshots'][-1]['avg_action']
early_b = results_b['snapshots'][0]['avg_action']
late_b = results_b['snapshots'][-1]['avg_action']
print(f"\n  Action magnitude:")
print(f"    Lone Wolves:  early={early_a:.3f} -> late={late_a:.3f} ({(late_a-early_a)/max(early_a,0.001)*100:+.1f}%)")
print(f"    Pack Hunters:  early={early_b:.3f} -> late={late_b:.3f} ({(late_b-early_b)/max(early_b,0.001)*100:+.1f}%)")
