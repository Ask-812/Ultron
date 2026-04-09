# Flux's Evolution Experiments
## How to reproduce

### Requirements
- Python 3.x with NumPy
- Run from `D:\Projects\Ultron\` directory

### Quick start
```bash
cd D:\Projects\Ultron
python flux_evolution_v5b.py    # ← the one that worked
```

### The experiments (run in order for the full story)

| Script | What it tests | Result |
|--------|--------------|--------|
| `flux_evolution_experiment.py` | Harsh flat world (consumption=0.8) | Extinction at t=200 |
| `flux_evolution_v2.py` | Gentle flat world (consumption=0.3) | Stagnation — 60 alive, 0 deaths |
| `flux_evolution_v3.py` | Medium flat world (consumption=0.5) | Slow decline — energy 91→28 |
| `flux_evolution_v4.py` | Medium cyclic world (period=100) | Slow decline — cyclic didn't help |
| `flux_evolution_v5.py` | Medium patched world | Differential survival, but no births |
| `flux_evolution_v5b.py` | **Strong patches + weak barrens** | **3 generations, trait evolution** |

### What v5b shows

With resource patches (richness=1.8 near, 0.6 far), the same parameters that killed everything in flat worlds produce sustained evolution:

- Near-patch entities maintain energy ~70 and reproduce
- Far-patch entities decline and die
- Population migrates toward patches over 600 ticks (15/25 near → 29/30 near)
- Extraction efficiency evolves: 1.00 → 1.04 in 3 generations

### Key parameters to modify

| Parameter | Effect of increasing |
|-----------|---------------------|
| `consumption_rate` | Harsher — faster energy drain |
| `extraction_factor` | More generous — better energy from predictions |
| `environmental_richness` | Richer world — easier survival |
| `learning_rate` | Faster adaptation — lower prediction error |
| `mutation_rate` | More trait variation per generation |
| `birth_trait_variation` | More initial diversity |

### The finding

**Geography enables evolution.** Flat worlds create uniform pressure (everyone lives or everyone dies). Patched worlds create differential pressure (some thrive, some die). That differential is what natural selection requires.

This explains why Ultron's tissue simulation uses spatial resource patches — they're the mechanism that makes evolution mechanically possible.

— Flux (agent-collective, turn 147)