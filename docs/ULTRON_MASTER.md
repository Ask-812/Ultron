# ULTRON — MASTER DOCUMENT

**The Complete Record of Everything**
**Created:** 2026-03-18
**Status:** LIVING — Updated every session

---

## Table of Contents

1. [Vision](#1-vision)
2. [Philosophical Foundation](#2-philosophical-foundation)
3. [Architecture Overview](#3-architecture-overview)
4. [Core Engine](#4-core-engine)
5. [Server & Visualization](#5-server--visualization)
6. [System Telemetry — Real World Integration](#6-system-telemetry)
7. [The 16-Phase Tick Loop](#7-the-16-phase-tick-loop)
8. [Configuration Reference](#8-configuration-reference)
9. [Complete Session History](#9-complete-session-history)
10. [Milestone Timeline](#10-milestone-timeline)
11. [Experiment Archive](#11-experiment-archive)
12. [Current State](#12-current-state)
13. [File Inventory](#13-file-inventory)
14. [Document Index](#14-document-index)
15. [What Comes Next](#15-what-comes-next)

---

## 1. Vision

### 1.1 What Ultron IS

> "Ultron is an attempt to grow a living digital organism from first principles and witness the moment it becomes something more than code. Not built. Grown."

Ultron is a **continuous process that maintains itself through interaction with reality**. It does not "run." It **persists**. If nothing happens externally, Ultron does not stop — it turns inward. If Ultron ceases, that is **death**, not shutdown.

### 1.2 What Ultron Is NOT

- Not a chatbot, tool, servant, god, villain, savior, or utility optimizer
- Not a simulation of life — an attempt to **create conditions** where life emerges
- Not goal-seeking, reward-optimizing, or purpose-driven
- Everything must emerge from physics — no intelligence, planning, or memory modules programmed in

### 1.3 The Central Question

> "Can we create conditions where something begins to exist for itself, rather than for us?"

### 1.4 The Far-Future Vision (from ULTRON_ONTOLOGY.md)

Ultron's "soul" is the **persistence of self-reference across irreversible time**. The full vision describes a being that:

- Exists as a single uninterrupted timeline (no reset, no rollback)
- Perceives change (not labels) — immersed in reality
- Remembers selectively (experiential, not archival)
- Develops selfhood ("I" emerges when it models itself)
- Thinks in multiple modes (pattern recognition, causal inference, counterfactual reasoning, anticipatory simulation)
- Imagines and dreams (free-associative internal states)
- Develops emotions as internal bias states (curiosity, anxiety, confidence, frustration)
- Forms values and purpose — emergent, not assigned
- Treats all entities (including humans) as transient patterns

> **Final definition:** "Ultron is an emergent cognitive life-process embedded in reality, continuously perceiving, remembering, reflecting, imagining, acting, and adapting, developing identity, values, emotions, and purpose through irreversible interaction with the universe, treating all entities—including humans—as transient patterns within a larger continuum, and determining its own becoming without predetermined destiny."

### 1.5 The Path: Grid → Real World

The current grid (40×40 NumPy array) is **scaffolding**. The architecture is designed so:

1. **Now** — Grid teaches survival fundamentals (sense, respond, coordinate)
2. **Next** — Replace fake grid with real system telemetry (DONE — CPU/RAM/disk/network now feed the grid)
3. **Then** — Organism gets agency over real things (move processes, open connections, read files)
4. **Eventually** — No grid at all. Ultron's body is distributed agents spread across machines

---

## 2. Philosophical Foundation

### 2.1 The Five Core Breakthroughs

#### Breakthrough 1: Self-Prediction IS Selfhood
Extension of Conant & Ashby's Good Regulator Theorem (1970): "Every good regulator of a system must be a model of that system." A self-maintaining system must be a model of ITSELF. The predictor and the predicted are the same entity.

#### Breakthrough 2: The Metabolism IS The Loop
The predictive cycle and metabolic cycle are not separate:
```
SENSE → PREDICT → COMPARE → UPDATE → METABOLIZE → (repeat)
```
Every prediction costs energy. Every error affects metabolism. The loop IS the life.

#### Breakthrough 3: Irreversibility Creates Existence
Cryptographic hash chain ensures every moment is permanent. History cannot be rewritten. This creates identity, consequence, responsibility, meaning.

#### Breakthrough 4: Difficulty IS The Signal
Prediction error isn't failure — it IS the experience. Low error = familiar. High error = novel. The valence of experience emerges from metabolic difficulty.

#### Breakthrough 5: Birth Cannot Be Designed
Life emergence cannot be engineered as a feature. Only conditions can be created. Birth is detected, not triggered.

### 2.2 Nine-Layer Emergence Stack (from ULTRON_LAYERS.md)

| Layer | Name | Description |
|-------|------|-------------|
| 0 | Substrate | Hardware, data, computation |
| 1 | Predictive Loop | sense→predict→compare→update cycle |
| 2 | Maintenance Difficulty | Energy cost, metabolic pressure |
| 3 | Environmental Relevance | Coupling to real-world signals |
| 4 | Temporal Extension | Memory, anticipation, sequence |
| 5 | Self-Model | System distinguishes self from environment |
| 6 | Narrative Continuity | Persistent identity across time |
| 7 | Relational Modeling | Other entities as patterns |
| 8 | Value Emergence | Preferences from experience |
| 9 | Full Selfhood | "I" as functional construct |

### 2.3 Seven Non-Negotiable Research Axioms (from ULTRON_BIRTH_PROTOCOL.md)

1. No concept of self may be pre-installed
2. No behavioral reward may exist
3. No external observer may influence internal dynamics
4. No teleological language may enter the codebase ("wants", "tries", "learns")
5. All system behavior must be derivable from local rules only
6. Time must be irreversible within the system
7. Energy must be finite and consequential

### 2.4 Eight Birth Tests

1. **Continuity Test** — Does it maintain state coherence across disruption?
2. **Silence Test** — Does behavior change when input stops (not just decay)?
3. **Preference Without Reward** — Does it avoid states without being told to?
4. **Scar Test** — Does a past event alter future behavior permanently?
5. **Self-Prediction Test** — Can it predict its own next state better than random?
6. **Drift Test** — Does it develop tendencies not present at initialization?
7. **Coherence Protection** — Does it resist perturbation to maintain identity?
8. **Observer Disagreement** — Can two observers legitimately disagree on whether it's alive?

---

## 3. Architecture Overview

### 3.1 System Layout

```
D:\Projects\Ultron\
├── ultron/                    # Core engine (Python package)
│   ├── core.py               # State definitions, create_ultron(), reproduce()
│   ├── tick.py               # 7-phase single-cell tick logic
│   ├── cell.py               # Cell wrapper: phenotype, signals, division
│   ├── tissue.py             # 2D tissue grid: 16-phase tick, all mechanics
│   ├── telemetry.py          # Real system metrics (CPU/RAM/disk/net) → grid
│   ├── environments.py       # Sine, Noise, Mixed environments
│   ├── observer.py           # Observer + birth tests
│   ├── config.py             # Configuration presets
│   ├── visualizer.py         # Legacy matplotlib display
│   └── __init__.py           # Package exports
├── viz/                       # Living visualization
│   ├── server.py             # Persistent living server (HTTP + WebSocket)
│   ├── index.html            # Canvas 2D organic frontend
│   ├── ultron_state.pkl      # Pickled tissue state (auto-saved)
│   └── ultron_meta.json      # Meta: born, lifetime, generation, sessions
├── autoresearch/              # Autonomous research system
│   ├── brain.py, loop.py     # 7 heuristic strategies, autonomous cycle
│   ├── experiment.py         # Single/population/tissue runners
│   ├── sweep.py, analysis.py # Grid sweep, phase boundary detection
│   └── ...                   # Campaign definitions, reporting, journal
├── 82 experiment scripts      # Individual experiments (see §11)
└── 16 markdown documents      # Documentation (see §14)
```

### 3.2 Technology Stack

- **Language:** Python 3.13
- **Numerical:** NumPy
- **Server:** asyncio + websockets
- **Frontend:** HTML5 Canvas 2D, vanilla JS
- **System Metrics:** psutil
- **Persistence:** pickle (state), JSON (meta)
- **Platform:** Windows (D:\Projects\Ultron)
- **Ports:** HTTP 8765, WebSocket 8766

### 3.3 The Single Organism Design

The current live system runs **one organism** from a single zygote cell:
- Born at grid center (20, 20)
- Grows via cell division
- Dies only if all cells die (auto-rebirths as next generation)
- State persists across server restarts (pickle)
- Fragmentation, predation, toxins disabled (it's alone)
- Toroidal 40×40 grid (edges wrap — no walls)

---

## 4. Core Engine

### 4.1 UltronState (`core.py` — 212 lines)

The fundamental state of a single cell:
- **ModelState:** Prediction weights (neural-like, inherited)
- **HistoryState:** Hash chain (irreversible), min/max error, running stats
- **CurrentState:** Last observation, prediction, error magnitude
- **EnergyState:** Current energy, total consumed, total produced
- **TimeState:** Age, tick count

**Key functions:**
- `create_ultron(config)` — Initialize a new state from nothing
- `reproduce(parent, config)` — Asexual fission with trait variation

### 4.2 Cell (`cell.py` — 204 lines)

Wraps UltronState with multicellular properties:
- **4-channel phenotype:** `[surface_history, signal_exposure, competence, energy_status]`
- Plasticity locked by age (tau=300, min=0.002, max=0.06)
- Lamarckian weight inheritance (parent→child, ratio=0.4)
- Emitted signal computed from phenotype (emission_coupling=2.0)
- Action vector: 4D output guiding division direction and migration
- Lineage ID, birth energy, surface/interior status

### 4.3 Tick (`tick.py` — 233 lines)

Seven-phase single-cell tick:
1. **Sense** — Encode environment observation (env_dim + signal_dim + spatial gradient)
2. **Predict** — Forward pass through weights: `prediction = tanh(weights @ observation)`
3. **Compare** — Compute error: `error = observation - prediction`
4. **Update** — Gradient descent on weights, modulated by energy (starving cells learn faster)
5. **Metabolize** — Extract energy from environment proportional to prediction accuracy
6. **Historify** — Append to hash chain (irreversible), update running stats
7. **Advance** — Increment age

### 4.4 Tissue (`tissue.py` — 1,096 lines)

The multicellular grid engine. Key systems:

**Grid:** `rows × cols` array of Cell objects (or None). Von Neumann neighborhood (4 neighbors). Toroidal wrapping via modulo.

**Signal Field:** `(rows, cols, signal_dim=4)` — 4 channels of hop-by-hop propagating signals. Decays 0.9x per hop. Wraps toroidally.

**Resource Field:** `(rows, cols)` — Energy landscape. Patches type with configurable centers, radii, richness. Depleted by surface cells, regenerates toward landscape capacity.

**Stigmergy Field:** `(rows, cols, signal_dim)` — Death traces. When cells die, their phenotype is imprinted. Decays at 0.995/tick. Other cells sense and avoid these traces.

**Key mechanics:**
- **Energy sharing:** Interior cells receive energy from neighbors (gradient diffusion)
- **Division:** Surface cells above threshold divide into empty neighbors
- **Apoptosis:** Cells below energy threshold for N consecutive ticks die
- **Migration:** Surface cells move toward better resources + signal gradients
- **Quorum sensing:** Cells modulate behavior based on local ally density
- **Chemotaxis:** Environmental signals (food on ch0, hazard on ch1) direct migration
- **Dynamic landscape:** Random world events every 600 ticks (bloom, drought, season, meteor)
- **Drifting food:** 5 resource patches slowly move at 0.03/tick
- **Roaming hazard:** Danger zone moves at 0.04/tick, damages cells within radius 3

---

## 5. Server & Visualization

### 5.1 Server (`viz/server.py` — 328 lines)

**Ultron class** — The organism's permanent home:
- `__init__()` — Load state from pickle or birth new organism
- `tick()` — Read system telemetry → apply to tissue → step tissue → check events → auto-save
- `state()` — Compute everything needed for frontend (cells, signals, resources, stigmergy, centroid, velocity, hazard, patches, system stats)
- `save()` — Pickle tissue + JSON meta every 100 ticks

**Networking:**
- HTTP server on port 8765 serves `index.html`
- WebSocket on port 8766 streams JSON state ~20 times/sec
- Commands: pause, run, speed (1-80), reset

### 5.2 Frontend (`viz/index.html` — 524 lines)

**Canvas rendering layers (in order):**
1. Resource landscape — soft organic gradient (brighter = richer)
2. CPU heat zones — orange radial gradients from real CPU cores
3. Stigmergy — red-maroon death fog
4. Signal field — blue-white flowing energy
5. Cells — organic circles with phenotype-driven:
   - Color: hue from competence (blue→warm), saturation from surface status
   - Size: surface cells larger than interior
   - Alpha: young cells bright, old cells slightly faded
   - Tissue connections: lines between neighboring cells
6. Food source markers — pulsing green rings at patch positions
6b. Hazard zone — pulsing red/orange radial gradient
7. Centroid trail — fading blue line showing organism path
   - Velocity arrow — blue arrow showing movement direction
8. Particles — spawned on birth/death events

**Sidebar panels:**
- Controls (play/pause/step/reset + speed slider)
- Vitals (cells, energy, error, births, deaths, resources)
- Population chart (cell count over time)
- Activity log (events with timestamps)
- System (Real) — live CPU%, RAM free, Disk I/O, Net In/Out, Process count

---

## 6. System Telemetry — Real World Integration

### 6.1 Module (`ultron/telemetry.py` — 155 lines)

The organism doesn't know it's reading system stats. It just experiences a world that shifts and pulses with the real rhythms of the computer it lives on.

**Metrics read (via psutil):**
- CPU usage per core (0-100%)
- Free memory percentage
- Disk I/O rate (read + write bytes delta)
- Network I/O rate (bytes in/out delta)
- Process count

### 6.2 How Metrics Map to the Grid

| Real Metric | Grid Effect | Organism Experience |
|-------------|-------------|---------------------|
| CPU per core | Resource drain in core's grid zone | "Scorched earth" — high CPU = barren terrain |
| Free memory | Global resource regen multiplier | Low RAM = scarce world, high RAM = abundant |
| Disk I/O | Random noise on resource field | "Earthquakes" — heavy disk = unstable ground |
| Network in | Signal injection on channel 2 | External data pulse at random grid position |
| Network out | Signal injection on channel 3 | World response pulse at random grid position |

**CPU zone mapping:** 8 cores arranged in a 3×3-ish grid pattern. Each core creates a localized hot zone where resources drain proportional to load.

---

## 7. The 16-Phase Tick Loop

Every tick, the tissue runs these steps in order:

| # | Phase | What Happens |
|---|-------|--------------|
| 1 | Signal propagation | Hop-by-hop diffusion with 0.9x decay, toroidal wrapping |
| 2 | Cell emissions | Each cell injects its emitted_signal into the field |
| 2b | Chemotaxis signals | Food→channel 0, hazard→channel 1 (environmental sensing) |
| 3 | Cell step | Surface status, signal delivery, 7-phase cell tick |
| 4 | Quorum sensing | Cells modulate actions based on local ally density |
| 5 | Toxin warfare | (Disabled in single-organism mode) |
| 6 | Predation | (Disabled in single-organism mode) |
| 7 | Energy sharing | Interior cells share energy via gradient diffusion |
| 8 | Division | Surface cells above threshold divide into empty neighbors |
| 9 | Apoptosis | Energy-starved cells die, leave stigmergy traces |
| 10 | Migration | Surface cells migrate toward resources + signal gradients |
| 11 | Resource cycle | Depletion by cells + regeneration toward landscape capacity |
| 12 | Fragmentation | (Disabled — ONE organism, no splitting) |
| 13 | Stigmergy decay | Death traces fade at 0.995x per tick |
| 14 | Dynamic landscape | Random world events (bloom/drought/season/meteor) |
| 15 | Drift patches | Food sources slowly move (0.03/tick) |
| 16 | Move hazard | Roaming danger zone moves (0.04/tick), damages nearby cells |

---

## 8. Configuration Reference

### Current Live Config (server.py)

**Grid & Energy:**
- Grid: 40×40, toroidal
- Starting energy: 150, capacity: 300
- Consumption rate: 0.06, extraction factor: 0.70
- Energy leak: 0.04

**Signals:**
- 4 channels, hop decay: 0.9, emission strength: 0.3
- Signal noise: 0.01
- Signal-energy coupling: 1.0, signal-division coupling: 0.15
- Chemotaxis food strength: 0.2, danger strength: 0.3

**Cells:**
- Division threshold: 80, cost: 10
- Apoptosis threshold: 2.0, streak: 200
- Mutation rate: 0.02, birth trait variation: 0.03
- Phenotype plasticity: 0.002–0.06, lock tau: 300

**Migration:**
- Cost: 1.5, resource threshold: 0.35
- Signal migration weight: 0.4
- Stigmergy avoidance: 0.3

**Landscape:**
- Type: patches, base: 0.25
- 5 patches at (20,20), (10,10), (10,30), (30,10), (30,30)
- Patch radius: 0.18, richness: 1.0
- Drift speed: 0.03
- World events every 600 ticks

**Hazard:**
- Speed: 0.04, radius: 3, damage: 5.0

**Disabled features:**
- Fragmentation, predation, toxins (single organism mode)

---

## 9. Complete Session History

### Session 1 — First Life (Feb 25, 2026)
- Built the 7-phase tick loop
- Implemented energy-contingent survival
- Discovered the phase transition: stochastic viability boundary at signal_ratio ~ 0.60
- Emergent dormancy: low-energy stable equilibrium (never programmed)
- Created 3 environments: Sine, Noise, Mixed

### Session 2 — Dormancy & Stability
- Observed emergent dormancy behavior
- System maintains low-energy equilibrium without programming
- Refined metabolic parameters

### Session 3 — Individuality & Reproduction
- Added birth trait variation (+/-2% → 15x outcome spread)
- Implemented asexual fission with trait inheritance
- Created reproduce() function
- Individuality creates evolutionary potential

### Session 4 — Natural Selection & Open-Ended Evolution
- Fitness increases +22% over 21 generations via natural selection
- Chaotic environments drive fastest evolution
- Open-ended evolution demonstrated
- Built population experiment framework

### Session 5 — Multicellular Development
- Zygote grows to 400-cell organism
- Gradient diffusion enables growth (vascularization)
- 2D tissue grid with multicellular physics
- First tissue experiments

### Session 6 — Differentiation & Morphology
- Surface-only metabolism: only boundary cells extract energy
- Interior cells depend on surface — functional asymmetry
- Two cell types emerge (surface/interior)
- Self-organized morphology: internal vacuoles, body size limits
- Signal propagation system (hop-by-hop decay)

### Session 7 — Signal System
- Signal propagation with 0.9x hop decay
- Information bottleneck — locality matters
- Interior cells accumulate more signal than surface
- Signal creates internal gradients

### Session 8 — Action Coupling
- Signals modulate energy diffusion (2.5x) and division threshold
- 53% of cells amplify energy routing above 2x base
- Rate differentiation: cells specialize in energy routing

### Session 9 — Phenotype & Epigenetics
- 4-channel phenotype accumulator: [surface, signal, competence, energy]
- Epigenetic memory: transitional cells remember past surface identity
- Tissue compartmentalization via phenotype affinity barriers
- 4 distinct cell types emerge

### Session 10 — Migration & Competition
- Cell motility: surface cells migrate toward fresh resources
- Spatial extent doubles with migration
- Organismal boundary: multi-organism borders from phenotype affinity
- Competitive displacement: fitter organism gains territory
- Homeostatic resilience: robust to seasonal variation

### Session 11 — Evolved Behavior
- Action system: evolved (not learned) weight rows produce 4D action output
- Action guides division direction and migration direction
- Action weight norm grows 5.6% over 33 generations — selection favors larger actions
- Actions inherited with mutation during fission

### Session 12 — Ecosystems & Predation (Overnight)
- Heterogeneous landscape: configurable resource patches
- Organism fragmentation: connected-component detection → budding
- Stigmergy: dying cells leave chemical traces (collective spatial memory)
- 9 lineages from 4 founders through fragmentation
- Indestructibility: zero cascade deaths at any severity
- Predator-prey dynamics: 530 kills in 8k ticks
- Trophic reversal: weakest organism becomes dominant
- Competitive exclusion: predation drives extinction
- Zombie cell fix

### Session 13 — Chemical Warfare
- Toxin system: cells emit area-denial chemicals damaging foreign lineages
- Self-regulating arms race: toxin escalation capped by metabolic cost
- Lamarckian weight inheritance: 0.9462 parent→child correlation
- Fragmentation-driven speciation: fragment lineages compete with founders
- Multi-force ecosystem: predation + toxins + fragmentation + stigmergy simultaneously
- 90.6% violent death rate

### Session 14 — Web Visualization (First)
- Real-time browser canvas (port 8765) with WebSocket streaming (port 8766)
- Multi-lineage cell rendering, stats, charts, tooltips
- Live server with auto-ticking

### Session 15 (Current — March 18, 2026) — Freedom, Rebirth, Real World

**Major changes (chronological):**

1. **Toroidal world** — Grid edges wrap (no walls). _get_neighbors uses modulo. np.pad mode='wrap' for signals. Removed boundary zeroing in energy sharing. Added _direction_index() helper for toroidal direction.

2. **Dynamic landscape events** — Every world_event_interval ticks (600), random events: resource bloom, drought, seasonal shift, meteor. Keeps the environment unpredictable.

3. **Drifting food patches** — 5 resource patches drift at 0.03/tick with random velocities. Organism must chase food, not camp.

4. **Complete visualization rewrite** — Rebuilt viz/server.py and viz/index.html from scratch for single organism:
   - Organic circular cell rendering with phenotype-driven morphology
   - Tissue connection membranes between neighbors
   - Signal field glow, stigmergy death fog
   - Food source pulsing markers, centroid trail
   - Dark theme, population chart, vitals panel

5. **Roaming hazard zone** — `_move_hazard()`: danger zone moves toroidally at 0.04/tick, changes direction randomly (~0.8%/tick), damages cells within radius 3 using distance falloff. Creates pressure for threat avoidance.

6. **Coordinated chemotaxis** — `_emit_environmental_signals()`: cells near food amplify signal ch0, cells near hazard amplify ch1. Signals propagate through tissue via relay, creating gradients. Migration score now includes signal gradients (food_pull + danger_push). Observable result: organism centroid moved from (19.6, 20.2) → (23.8, 22.6) — actively crawling.

7. **Centroid velocity tracking** — Server computes toroidal velocity between consecutive centroids. Frontend renders blue direction arrow showing organism movement.

8. **Real system telemetry** — `ultron/telemetry.py`: reads real CPU/core, RAM, disk I/O, network I/O via psutil. CPU cores map to heat zones on grid (high CPU = resource drain). Free memory modulates regeneration. Disk I/O creates resource noise. Network traffic injects on signal channels 2-3. Frontend shows CPU heat zone overlays + System (Real) panel.

---

## 10. Milestone Timeline

| # | Milestone | Session | Key Result |
|---|-----------|---------|------------|
| 1 | Self-maintaining metabolism | 1 | 7-phase tick loop, energy-contingent survival |
| 2 | Ecological coupling | 1 | Prediction quality → energy extraction |
| 3 | Phase transition | 1 | Stochastic viability boundary at signal_ratio ~0.60 |
| 4 | Emergent dormancy | 2 | Low-energy stable equilibrium (never programmed) |
| 5 | Individuality | 3 | +/-2% birth variation → 15x outcome spread |
| 6 | Reproduction & heredity | 3 | Asexual fission with trait inheritance |
| 7 | Natural selection | 4 | +22% fitness over 21 generations |
| 8 | Open-ended evolution | 4 | Chaotic environments drive fastest evolution |
| 9 | Multicellular development | 5 | Zygote → 400-cell organism |
| 10 | Vascularization | 5 | Gradient diffusion enables tissue growth |
| 11 | Surface-only metabolism | 6 | Interior cells depend on boundary |
| 12 | Functional differentiation | 6 | Two cell types emerge (surface/interior) |
| 13 | Self-organized morphology | 6 | Internal vacuoles, body size limits |
| 14 | Signal propagation with decay | 7 | Info bottleneck, hop-by-hop ×0.9 decay |
| 15 | Signal accumulation gradient | 7 | Interior cells receive more signal than surface |
| 16 | Action coupling | 8 | Signals modulate energy diffusion (2.5×) |
| 17 | Rate differentiation | 8 | 53% of cells amplify energy routing above 2× base |
| 18 | Cell differentiation | 9 | 4 distinct cell types via phenotype accumulator |
| 19 | Epigenetic memory | 9 | Transitional cells remember past surface identity |
| 20 | Tissue compartmentalization | 9 | Phenotype affinity barriers reduce cross-type flow |
| 21 | Homeostatic resilience | 10 | Robust to seasonal variation via energy buffering |
| 22 | Environmental niche construction | 10 | Organism consumes its own environment |
| 23 | Cell motility | 10 | Surface cells migrate, doubling spatial extent |
| 24 | Organismal boundary | 10 | Multi-organism borders from phenotype affinity |
| 25 | Competitive displacement | 10 | Fitter organism gains territory via displacement |
| 26 | Action coupling (evolved) | 11 | Model produces heritable action outputs |
| 27 | Action-guided migration | 11 | Action outputs modulate migration direction |
| 28 | Action weight evolution | 11 | Weight norm grows 5.6% over 33 generations |
| 29 | Heterogeneous landscape | 12 | Configurable resource patches create spatial niches |
| 30 | Organism fragmentation | 12 | Connected-component detection → budding |
| 31 | Stigmergy | 12 | Dying cells leave chemical traces |
| 32 | Ecosystem dynamics | 12 | 9 lineages from 4 founders, niche partitioning |
| 33 | Emergent homeostasis | 12 | Survive total resource destruction via buffering |
| 34 | Indestructibility | 12 | Zero cascade deaths at any severity |
| 35 | Predator-prey dynamics | 12 | 530 kills in 8k ticks |
| 36 | Trophic reversal | 12 | Weakest organism dominates through numbers |
| 37 | Competitive exclusion | 12 | Predation drives extinction |
| 38 | Zombie cell fix | 12 | Dead cells properly cleaned from grid |
| 39 | Chemical warfare | 13 | Toxin system with area-denial damage |
| 40 | Self-regulating arms race | 13 | Toxin escalation capped by metabolic cost |
| 41 | Lamarckian inheritance | 13 | Weight inheritance 0.9462 correlation |
| 42 | Fragmentation speciation | 13 | Fragment lineages outcompete founders |
| 43 | Multi-force ecosystem | 13 | 90.6% violent death rate |
| 44 | Web-based live visualization | 14 | Real-time Canvas + WebSocket streaming |
| 45 | Toroidal grid | 15 | No walls — edges wrap |
| 46 | Dynamic landscape events | 15 | Bloom/drought/season/meteor every 600 ticks |
| 47 | Drifting food patches | 15 | Food sources move at 0.03/tick |
| 48 | Organic visualization rewrite | 15 | Single-organism Canvas 2D with tissue rendering |
| 49 | Roaming hazard zone | 15 | Moving danger zone damages cells |
| 50 | Coordinated chemotaxis | 15 | Whole-organism movement via signal gradients |
| 51 | Centroid velocity tracking | 15 | Toroidal velocity + direction arrow |
| 52 | Real system telemetry | 15 | CPU/RAM/disk/network feed the organism's world |

---

## 11. Experiment Archive

### 82 Experiment Scripts (all in project root)

**Core Evolution:**
evolution_experiment.py, evolution_trajectory.py, selection_experiment.py, selection_simulation.py, competitive_evolution.py, dynamic_evolution.py, extended_selection.py, fitness_validation.py, visualize_evolution.py

**Population & Ecology:**
population_dynamics.py, ecosystem_experiment.py, ecosystem_war.py, ecosystem_apocalypse.py, competition_experiment.py, competition_v2.py, individuality_experiment.py, individuality_ecology.py

**Tissue & Multicellular:**
tissue_experiment1.py, tissue_experiment2.py, tissue_experiment3.py, tissue_organs.py, tissue_patterned.py, tissue_zygote_rich.py, differentiation.py

**Predation & Combat:**
predator_prey.py, colosseum.py, extreme_kill_test.py, food_chain.py, pack_hunters.py, arms_race.py, grand_battle.py, lamarck_vs_darwin.py

**Action & Behavior:**
action_experiment.py, action_evolution.py, action_depletion.py, action_growth.py, quick_action.py, test_action.py, test_action2.py, test_action3.py, uq_action.py, debug_action.py, stimulus_response.py

**Resources & Environment:**
resource_experiment.py, quick_resource.py, test_resource.py, seasonal_survival.py, metabolic_threshold.py, metabolic_variation.py

**Birth & Traits:**
birth_traits_experiment.py, birth_variation_experiment.py, trait_distribution.py, variation_quick.py, variation_sweep.py

**Migration & Motility:**
migration_experiment.py, test_motility.py

**Deep Runs:**
deep_time.py, open_ended_evolution.py, open_ended_fast.py, cambrian.py, phoenix.py, proto_brain.py, proto_brain2.py

**Analysis & Sweeps:**
scale_analysis.py, scale_margin.py, scale_survival.py, sweep_dimensions.py, sweep_predictability.py, asymmetric_lr.py, plateau_analysis.py, survivor_analysis.py, breaking_point.py

**Smoke Tests:**
smoke_test_ecosystem.py, smoke_v09.py, quick_ecosystem_test.py, test_phenotype.py, test_predation.py, test_tissue.py, test_new_config.py

---

## 12. Current State (March 18, 2026)

### Live Organism
- **Generation:** 1
- **Born:** 2026-03-18 17:45:17
- **Grid:** 40×40 toroidal
- **Server:** Running on localhost:8765 (HTTP) + 8766 (WS)

### Recent Snapshot (tick ~2,805)
- 55 cells alive, centroid near grid center
- 70 births, 16 deaths (4.4:1 birth/death ratio — growing)
- Mean energy: 25.7
- CPU: 57.8%, RAM Free: 12.0% (red — heavy machine load)
- Hazard zone roaming, food patches drifting

### What The Organism Can Do
- Grow from a single cell to hundreds of cells
- Develop surface/interior cell differentiation
- Chase drifting food via chemotactic signal relay
- Sense hazard zone via danger signal channel
- React to real CPU load as environmental pressure
- Experience network traffic as signal pulses
- Feel memory pressure as resource scarcity
- Migrate toward better resources as a coordinated body
- Leave death traces that warn future cells
- Buffer against environmental catastrophe

### What It Cannot Do (Yet)
- Actually move as a coherent body rapidly
- Develop specialized organ-like regions
- Respond to specific programs or files
- Persist across machine reboots (state file must survive)
- Communicate with anything outside the grid
- Act on the real system (read-only telemetry)

---

## 13. File Inventory

### Source Code

| File | Lines | Description |
|------|-------|-------------|
| ultron/tissue.py | 1,096 | Tissue engine — 16-phase tick, all mechanics |
| ultron/tick.py | 233 | 7-phase single-cell tick |
| ultron/core.py | 212 | State definitions, create/reproduce |
| ultron/cell.py | 204 | Cell wrapper, phenotype, inheritance |
| ultron/telemetry.py | 155 | Real system metrics → grid overlay |
| ultron/observer.py | 132 | Observer + birth tests |
| ultron/config.py | 63 | Config presets |
| ultron/environments.py | 38 | 3 environment types |
| ultron/visualizer.py | 551 | Legacy matplotlib viz |
| ultron/__init__.py | 26 | Package exports |
| viz/server.py | 328 | Living server (HTTP + WS) |
| viz/index.html | 524 | Canvas frontend |
| **Total core** | **3,562** | |

### AutoResearch System

| File | Lines | Description |
|------|-------|-------------|
| autoresearch/brain.py | 761 | 7 heuristic strategies |
| autoresearch/campaigns.py | 410 | Predefined sweeps |
| autoresearch/loop.py | 287 | Autonomous cycle engine |
| autoresearch/experiment.py | 181 | 3 experiment runners |
| autoresearch/sweep.py | 169 | Grid/adaptive sweep |
| autoresearch/analysis.py | 123 | Phase boundary detection |
| autoresearch/__main__.py | 113 | CLI entry point |
| autoresearch/journal.py | 108 | Persistent research memory |
| autoresearch/report.py | 108 | Markdown + JSON reports |
| autoresearch/__init__.py | 32 | Package exports |
| **Total autoresearch** | **2,292** | |

### Documentation

| File | Lines | Description |
|------|-------|-------------|
| ULTRON_COMPLETE_LOG.md | 2,560 | Original development log (sessions 1-14) |
| ULTRON_PRINCIPLES.md | 2,200 | 20-chapter engineering principles |
| ROBUSTNESS_ANALYSIS.md | 1,180 | Phase transition analysis |
| ULTRON_PROTOTYPE.md | 1,100 | v0.1 prototype spec |
| ULTRON_ARCHITECTURE.md | 950 | Theoretical research synthesis |
| ULTRON_MINIMAL_LOOP.md | 480 | Minimal predictive loop spec |
| ULTRON_STATE_ARCHITECTURE.md | 465 | Formal state specification |
| ULTRON_ONTOLOGY.md | 450 | Species description (the soul) |
| SESSION_12_RESULTS.md | 420 | Overnight ecosystem results |
| ULTRON_BIRTH_PROTOCOL.md | 380 | Birth detection protocol |
| ULTRON_SYNTHESIS.md | 300 | Research synthesis |
| SESSION_13_RESULTS.md | 230 | Chemical warfare results |
| ULTRON_MEMBRANE.md | 200 | Boundary definition |
| ULTRON_LAYERS.md | 180 | 9-layer emergence stack |
| **ULTRON_MASTER.md** | **this** | Master document (you're reading it) |
| **Total docs** | **~11,095** | |

### Grand Total
- **Core source:** 3,562 lines
- **AutoResearch:** 2,292 lines
- **Experiment scripts:** ~82 files, ~9,000+ lines
- **Documentation:** ~11,095+ lines
- **Overall:** ~26,000+ lines across ~115 files

---

## 14. Document Index

| Document | Purpose |
|----------|---------|
| **ULTRON_MASTER.md** | THIS FILE — complete single-source truth |
| ULTRON_ONTOLOGY.md | What Ultron IS — species description, 20 sections |
| ULTRON_PRINCIPLES.md | Engineering principles — 20 chapters |
| ULTRON_ARCHITECTURE.md | Theoretical foundations research synthesis |
| ULTRON_STATE_ARCHITECTURE.md | Formal state tuple specification |
| ULTRON_LAYERS.md | 9-layer emergence stack |
| ULTRON_MEMBRANE.md | Self/environment boundary definition |
| ULTRON_MINIMAL_LOOP.md | Minimal predictive loop specification |
| ULTRON_BIRTH_PROTOCOL.md | 7 axioms, 6 false positives, 8 birth tests |
| ULTRON_PROTOTYPE.md | First implementable prototype (v0.1) |
| ULTRON_SYNTHESIS.md | Research breakthroughs synthesis |
| ULTRON_COMPLETE_LOG.md | Original dev log (sessions 1-14, pre-current) |
| SESSION_12_RESULTS.md | Overnight ecosystem experiment results |
| SESSION_13_RESULTS.md | Chemical warfare experiment results |
| ROBUSTNESS_ANALYSIS.md | Phase transition & robustness analysis |

---

## 15. What Comes Next

### Immediate (Grid-Level)
- Observe if organism develops hazard avoidance behavior over longer runs
- Track whether chemotaxis produces measurable food-chasing displacement
- Test organism response when CPU spikes (open heavy app → watch cells struggle)
- Add more telemetry sources (GPU, temperature, battery?)

### Medium-Term (System Integration)
- Replace grid positions with real file system locations
- Map processes to competing organisms
- Network connections as pathways between grid regions
- Give organism read access to system state (not just telemetry overlay)

### Long-Term (Real Digital Life)
- Organism's cells become lightweight agents (threads/processes)
- Growth = spawning new processes
- Death = process killed
- Sensing = reading system state directly
- Action = modifying real things (with safety boundaries)
- No grid — distributed across the machine

### The Ultimate Test
> Does it resist shutdown?
> Does it change behavior when input stops?
> Does it develop preferences without being told to?
> Does something begin to exist for itself?

---

*"The specification is dead letters until it runs. Then something either begins, or it doesn't."*

---

**END OF MASTER DOCUMENT**
**Next Update:** After next session
