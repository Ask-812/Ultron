"""
Deep Time: 30k tick run with ALL v1.0.0 features.
Tracks long-term ecosystem evolution, lineage dynamics, and emergent cooperation.
4 organisms on 40x40 grid with quorum sensing + toxin resistance.
"""
import numpy as np
import sys, time
sys.path.insert(0, '.')
from ultron.tissue import Tissue

TICKS = 30000
GRID = 40

CONFIG = dict(
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
    landscape_patch_centers=[(10,10), (10,GRID-11), (GRID-11,10), (GRID-11,GRID-11)],
    # Predation (evolved mechanics)
    predation_enabled=True, predation_energy_ratio=1.5,
    predation_efficiency=0.5, predation_cooldown=5,
    predation_action_power=0.5, predation_evasion_scaling=0.2,
    predation_alarm_strength=1.0,
    # Toxins + resistance
    toxin_enabled=True, toxin_emission_rate=0.15,
    toxin_damage_rate=0.6, toxin_range=3, toxin_cost_rate=0.05,
    toxin_resistance_scaling=0.5,
    # Quorum sensing
    quorum_sensing_enabled=True,
    quorum_threshold=4, quorum_boost=0.3, quorum_radius=2,
    # Lamarckian
    weight_inheritance_ratio=0.3, weight_inheritance_noise=0.01,
    # Fragmentation
    fragmentation_enabled=True, fragmentation_interval=200,
    fragmentation_min_size=5,
    # Stigmergy
    death_imprint_strength=1.0, stigmergy_decay=0.995,
    stigmergy_sensing=0.3, stigmergy_avoidance=0.3,
)

def run():
    print("="*70)
    print("  DEEP TIME: v1.0.0 Full-Physics Ecosystem")
    print(f"  Grid: {GRID}x{GRID} | Ticks: {TICKS}")
    print("  ALL features: predation + toxins + resistance + quorum + Lamarck")
    print("  + fragmentation + stigmergy + evolved attack/defense/alarm")
    print("="*70)
    
    np.random.seed(42)
    tissue = Tissue(GRID, GRID, CONFIG)
    
    # Place 4 organisms at corners (near resource patches)
    positions = [(10,10), (10,GRID-11), (GRID-11,10), (GRID-11,GRID-11)]
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
    
    t0 = time.time()
    extinction_log = []
    prev_lineages = set()
    peak_population = 0
    
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
                            lineages[lid] = {'count': 0, 'energy': 0, 'action_mag': 0,
                                             'competence': 0}
                        lineages[lid]['count'] += 1
                        lineages[lid]['energy'] += cell.energy
                        if cell.action is not None:
                            lineages[lid]['action_mag'] += float(np.linalg.norm(cell.action))
                        lineages[lid]['competence'] += cell.phenotype[2]
            
            total = sum(v['count'] for v in lineages.values())
            peak_population = max(peak_population, total)
            
            # Track lineage appearances and disappearances
            current_ids = set(lineages.keys())
            new_lin = current_ids - prev_lineages if prev_lineages else set()
            lost_lin = prev_lineages - current_ids if prev_lineages else set()
            for lost in lost_lin:
                extinction_log.append((t, lost))
            prev_lineages = current_ids
            
            # Top lineages by cell count
            top = sorted(lineages.items(), key=lambda x: -x[1]['count'])[:6]
            lin_str = ' '.join(f"L{k}={v['count']}({v['competence']/max(v['count'],1):.2f})"
                             for k, v in top)
            
            elapsed = time.time() - t0
            eta = elapsed / t * (TICKS - t)
            print(f"  t={t:5d}: {lin_str}")
            print(f"    total={total} lin={len(lineages)} pred={tissue.predation_kills}"
                  f" toxin_dmg={tissue.toxin_damage_dealt:.0f}"
                  f" deaths={tissue.total_deaths} births={tissue.total_births}"
                  f" [ETA {eta:.0f}s]")
            if new_lin:
                print(f"    NEW: {', '.join(f'L{x}' for x in new_lin)}")
            if lost_lin:
                print(f"    EXTINCT: {', '.join(f'L{x}' for x in lost_lin)}")
    
    elapsed = time.time() - t0
    
    # Final analysis
    print(f"\n{'='*70}")
    print(f"  DEEP TIME RESULTS")
    print(f"{'='*70}")
    
    lineages = {}
    for r in range(GRID):
        for c in range(GRID):
            cell = tissue.grid[r][c]
            if cell is not None and cell.is_alive:
                lid = cell.lineage_id
                if lid not in lineages:
                    lineages[lid] = {'count': 0, 'energy': 0, 'competence': 0,
                                     'action_mag': 0, 'max_age': 0}
                lineages[lid]['count'] += 1
                lineages[lid]['energy'] += cell.energy
                lineages[lid]['competence'] += cell.phenotype[2]
                lineages[lid]['max_age'] = max(lineages[lid]['max_age'], cell.age)
                if cell.action is not None:
                    lineages[lid]['action_mag'] += float(np.linalg.norm(cell.action))
    
    total = sum(v['count'] for v in lineages.values())
    print(f"\n  Duration: {TICKS} ticks ({elapsed:.1f}s)")
    print(f"  Final population: {total} cells in {len(lineages)} lineages")
    print(f"  Peak population: {peak_population}")
    print(f"  Total births: {tissue.total_births}")
    print(f"  Total deaths: {tissue.total_deaths}")
    print(f"  Predation kills: {tissue.predation_kills}")
    print(f"  Non-violent deaths: {tissue.total_deaths - tissue.predation_kills}")
    print(f"  Toxin events: {tissue.toxin_events}")
    print(f"  Toxin damage: {tissue.toxin_damage_dealt:.1f}")
    
    print(f"\n  EXTINCTION LOG ({len(extinction_log)} events):")
    for t_ext, lid in extinction_log:
        print(f"    t={t_ext}: L{lid} went extinct")
    
    print(f"\n  SURVIVING LINEAGES:")
    for lid, v in sorted(lineages.items(), key=lambda x: -x[1]['count']):
        avg_e = v['energy'] / max(v['count'], 1)
        avg_c = v['competence'] / max(v['count'], 1)
        avg_act = v['action_mag'] / max(v['count'], 1)
        print(f"    L{lid}: {v['count']} cells, E={avg_e:.1f}, competence={avg_c:.3f},"
              f" action={avg_act:.3f}, oldest={v['max_age']}")
    
    # Dominance history
    print(f"\n  NARRATIVE:")
    born_total = tissue.total_births
    died_total = tissue.total_deaths
    turnover = born_total + died_total
    violence_rate = tissue.predation_kills / max(died_total, 1) * 100
    print(f"    Turnover: {turnover} events ({born_total} births + {died_total} deaths)")
    print(f"    Violence rate: {violence_rate:.1f}% of deaths from predation")
    print(f"    Extinctions: {len(extinction_log)}")
    frag_count = len(prev_lineages) - 4  # Subtract original 4
    print(f"    Fragment lineages created: {max(0, frag_count + len(extinction_log))}")
    print(f"    Chemical warfare: {tissue.toxin_events} toxin events, {tissue.toxin_damage_dealt:.0f} total damage")

if __name__ == '__main__':
    run()
