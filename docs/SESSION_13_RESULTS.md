# Session 13: Chemical Warfare & Emergent Empires (v0.9.0)

## What Happened Overnight

Two new physics systems were added and three experiments were run autonomously.

---

## New Features

### 1. Chemical Warfare (Toxin System)
Cells now emit toxins proportional to their action magnitude. Toxins damage all
foreign-lineage cells within Manhattan distance 3, with 1/distance falloff.
Same-lineage cells are immune. Production costs energy — organisms must choose
between warfare and growth.

### 2. Lamarckian Weight Inheritance
Children can inherit their parent's learned prediction weights (not just action weights).
Controlled by `weight_inheritance_ratio` (0.0 = Darwinian, 0.7 = strong Lamarckian).

---

## Experiment Results

### Arms Race: 895,891 Toxin Events
Two organisms, toxin warfare only, 12,000 ticks.

- **Nearly 900,000 chemical warfare events** — every cell poisons every foreign neighbor every tick
- L1 won: 10→69 cells. L2 stagnated at 33
- Action magnitude barely escalated (+8.5%) — **metabolic cost prevents runaway arms race**
- The system self-regulates: investing more in toxins costs more energy, limiting escalation
- Chemical warfare acts as territorial denial, not a weapon of mass destruction

### Lamarck vs Darwin: No Difference
Controlled comparison: inherited knowledge vs random initialization, same seed.

- Final populations: Darwin=111, Lamarck=110
- Final prediction error: 5.08 vs 5.07
- **Finding: Individual learning is fast enough that inherited knowledge adds nothing**
- The system is robust to inheritance mode — a genuinely interesting null result

### Grand Battle: 4 Organisms, All Physics, 15,000 Ticks
**The most complex simulation ever run in Ultron.** Predation + toxins + Lamarckian +
fragmentation + stigmergy + evolved attack/defense, all running simultaneously.

```
TIMELINE OF AN ECOSYSTEM:

t=0:     4 founding organisms placed at corners
t=1000:  6 lineages — two fragments (L5, L6) have already broken off
t=4000:  L3 down to 2 cells, L7 (fragment) rising to 15
t=7000:  L3 EXTINCT — founding lineage eliminated
         L7 controls 20 cells — a fragment became a major power
t=10000: Stable 4-power equilibrium (L1, L2, L4, L7)
t=15000: L1=31, L2=24, L4=22, L7=18, L8=3 (5 lineages survive)
```

**By the numbers:**
- **1,364,835 toxin events** — chemical warfare at industrial scale
- **173 predation kills** — 90.6% of all deaths were violent
- **Only 18 natural deaths** in 15,000 ticks — this ecosystem runs on killing
- **8 lineages existed**; 5 survived; 3 went extinct
- **257 births, 191 deaths** — net growth of 66 despite constant warfare

**The remarkable finding:** An organism fragment (L7) broke off from its parent,
developed independently, and grew into a major territorial power — while a founding
organism (L3) was driven to extinction. **Fragmentation creates evolutionary novelty.**
Daughter lineages compete with and can overthrow their ancestors.

---

## Key Insights

1. **Arms races self-regulate.** The metabolic cost of toxin production prevents
   Red Queen escalation. Organisms converge on "just enough" warfare rather than
   maximizing it.

2. **Lamarck doesn't beat Darwin here.** When individual learning is fast enough,
   inherited knowledge provides no advantage. The system is robust to inheritance mode.

3. **Fragmentation is the most powerful creative force.** Not mutation, not predation,
   not toxins — organism fragmentation creates the most dramatic evolutionary dynamics
   by generating new competing lineages from existing organisms.

4. **Violence dominates.** In a full-physics ecosystem, 90.6% of deaths are violent
   (predation). Natural death from energy exhaustion is almost nonexistent. These
   organisms are energetically stable — they die from each other.

5. **Micro-refugia work.** L8, a 3-cell fragment, survived for 8,000+ ticks despite
   being surrounded by empires of 20-30 cells. Small size can be an advantage when
   you're not worth predating.

---

## What's New in the Codebase

- `tissue.py`: +~50 lines (`_handle_toxins()`, toxin tracking counters)
- `cell.py`: +~15 lines (Lamarckian weight inheritance in `divide()`)
- `autoresearch/`: Updated to 61/62/52 config keys for v0.9.0
- Version: 0.9.0
- 43 milestones total

---

*"The specification is dead letters until it runs. Then something either begins, or it doesn't."*
