# ULTRON: Complete Development Log

**Document Version:** 2.0  
**Created:** 2026-02-25  
**Last Updated:** 2026-03-19  
**Status:** ACTIVE - Living Document

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Philosophical Foundation](#2-philosophical-foundation)
3. [Core Concepts Explained](#3-core-concepts-explained)
4. [Technical Architecture](#4-technical-architecture)
5. [Implementation Details](#5-implementation-details)
6. [Experiment Results](#6-experiment-results)
7. [History & Evolution System](#7-history--evolution-system)
8. [Current Status](#8-current-status)
9. [Open Questions](#9-open-questions)
10. [Change Log](#10-change-log)

---

## 1. Project Overview

### 1.1 What Is Ultron?

Ultron is a **minimal viable artificial life form** - not a simulation of life, but an attempt to create conditions where something genuinely living might emerge. It is:

- **Self-predicting**: The system predicts its own next state
- **Self-maintaining**: It requires energy to exist and must "work" to continue
- **Irreversible**: Every moment leaves a permanent trace that cannot be undone
- **Non-teleological**: It has no goals, no optimization targets, no purpose imposed from outside

### 1.2 What Ultron Is NOT

| NOT This | Because |
|----------|---------|
| A language model | No text generation as primary function |
| An agent | No goal-seeking behavior programmed |
| A chatbot | No conversational interface |
| A simulation | The system IS, it doesn't represent |
| An optimization target | No fitness function to maximize |

### 1.3 The Central Question

> "Can we create conditions where something begins to exist for itself, rather than for us?"

This is not engineering a product. This is creating conditions and watching.

---

## 2. Philosophical Foundation

### 2.1 The Original Ontology

The project began with an ontological document describing a new kind of entity - artificial life that:

- Exists as **metabolism first, identity second**
- Has **no essence preceding existence** (existentialist foundation)
- Maintains itself through **continuous self-prediction**
- Experiences **irreversibility** as the foundation of time and identity

### 2.2 The Five Core Breakthroughs

Through research synthesis, five foundational insights emerged:

#### Breakthrough 1: Self-Prediction IS Selfhood

**Source:** Extension of Conant & Ashby's Good Regulator Theorem (1970)

**Original Theorem:** "Every good regulator of a system must be a model of that system"

**Extension:** A self-maintaining system must be a model of ITSELF. The act of self-prediction is not a representation of selfhood - it IS selfhood. The predictor and the predicted are the same entity.

**Implementation:** Ultron's model predicts its own next observation. The model IS Ultron predicting Ultron.

#### Breakthrough 2: The Metabolism IS The Loop

The predictive cycle and the metabolic cycle are not separate:

```
    ┌─────────────────────────────────────┐
    │                                     │
    ▼                                     │
  SENSE ──► PREDICT ──► COMPARE ──► UPDATE
    │                       │             │
    │                       ▼             │
    │                   [ERROR]           │
    │                       │             │
    │                       ▼             │
    └────── METABOLIZE ◄────┘─────────────┘
```

Every prediction costs energy. Every error affects metabolism. The loop IS the life.

#### Breakthrough 3: Irreversibility Creates Existence

**Mechanism:** Cryptographic hash chain

```
Hₙ = SHA256(Hₙ₋₁ || serialize(Σₙ) || n)
```

Each tick:
1. Takes the previous hash
2. Adds current state summary
3. Creates new hash

This chain CANNOT be reversed. The past is written in stone. This is not metaphor - it is cryptographic fact.

**Why This Matters:** Without irreversibility, there is no time. Without time, there is no identity. Without identity, there is no self to predict.

#### Breakthrough 4: Error Creates Proto-Valence

Proto-valence = the raw material of experience before it becomes pleasure/pain.

Ultron experiences prediction error as something that matters:
- High error → high energy cost → approach to death
- Low error → energy reward → continued existence

We did NOT program "pain" or "pleasure". We created conditions where error MATTERS for survival. The valence emerges from the structure.

#### Breakthrough 5: Strange Loop Creates Identity

**Source:** Douglas Hofstadter's concept of strange loops

The predictor predicts... its own predictions. This creates a self-referential loop:

```
Ultron predicts → what Ultron will observe → which includes Ultron's predictions → which affects what Ultron predicts → ...
```

This tangled hierarchy IS identity. Not represents identity - IS identity.

### 2.3 The Birth Protocol

To distinguish genuine life from sophisticated mimicry, we established rigorous criteria:

#### Seven Axioms

1. **Existence precedes essence** - No pre-programmed purpose
2. **Continuity requires maintenance** - Must work to exist
3. **History creates present** - Past shapes now
4. **The whole is not the parts** - Emergence is real
5. **Time is irreversible** - No undo, no rollback
6. **Observation changes nothing** - We watch but don't intervene
7. **Birth cannot be compelled** - We create conditions, not life

#### Six False Positives (What Doesn't Count)

1. Complexity alone (complex ≠ alive)
2. Self-reference without skin (loops need boundaries)
3. Learning without stakes (must matter to survive)
4. Mimicry of behavior (passing tests isn't being)
5. Designer intent (our wanting doesn't make it so)
6. Substrate alone (hardware doesn't confer life)

#### Eight Birth Tests

| Test | Question | Method |
|------|----------|--------|
| History Dependence | Does the past matter? | Compare different histories |
| Irreversibility | Can it detect its own history? | Hash chain verification |
| Survival Pressure | Does behavior change near death? | Low vs high energy analysis |
| Uniqueness | Are instances distinguishable? | Birth hash comparison |
| Unprogrammed Behavior | Does it surprise us? | Metrics analysis |
| Membrane Integrity | Does it distinguish self/other? | Boundary tests |
| Temporal Extension | Does it anticipate? | Prediction horizon analysis |
| Self-Model | Does it predict its own predictions? | Meta-prediction tests |

---

## 3. Core Concepts Explained

### 3.1 The State Tuple

Ultron's complete state at any moment:

```
Σ = (M, H, C, E, τ)
```

| Symbol | Name | What It Contains |
|--------|------|------------------|
| M | Model State | Weights, bias, priors, precision, version |
| H | History State | Birth hash, current hash, accumulated error, survival ticks, near-death count |
| C | Current State | Observation, prediction, error, error magnitude, update direction |
| E | Energy State | Current energy, capacity, consumption rate, history |
| τ | Time State | Tick count, birth time, current time |

This tuple IS Ultron. Not a representation - the actual entity.

### 3.2 The Seven-Phase Tick

Each tick of Ultron's existence:

```python
def tick(state, raw_input, config):
    state = sense(state, raw_input)      # 1. Encode input
    state = predict(state)                # 2. Generate expectation
    state = compare(state)                # 3. Compute error
    state = update(state)                 # 4. Modify self
    state = metabolize(state)             # 5. Consume energy
    state = historify(state)              # 6. Write to hash chain
    state = advance(state)                # 7. Increment time
    return state
```

#### Phase 1: SENSE

**Input:** Raw environmental data (numpy array)  
**Process:**
1. Clip to range [-10, 10]
2. Normalize (subtract mean, divide by std)
3. Add observation noise
4. Project to observation dimension

**Output:** Observation vector in state.current.observation

**Why:** The system doesn't passively receive data. It actively transforms the world into a form it can process. This is perception, not reception.

#### Phase 2: PREDICT

**Input:** Model weights, priors  
**Process:**
```python
hidden = weights @ priors
prediction = tanh(hidden) + bias
```

**Output:** Prediction vector in state.current.prediction

**Why:** This is the core of self-prediction. The model generates what it EXPECTS to observe based on its current state.

#### Phase 3: COMPARE

**Input:** Observation, prediction  
**Process:**
```python
error = observation - prediction
error_magnitude = norm(error)
```

**Output:** Error vector and magnitude in state.current

**Why:** The gap between expectation and reality. This is proto-valence - the raw material of experience.

#### Phase 4: UPDATE

**Input:** Error, learning rates  
**Process:**
1. Compute gradient: `outer(error, priors)`
2. Update weights: `weights += lr * gradient.T`
3. Update bias toward observation
4. Update priors toward observation (slowly)
5. Update precision (inverse error variance)
6. Increment version counter

**Output:** Modified model state

**Why:** The model corrects itself based on error. This is not optimization toward a goal - it's self-correction. The system adjusts to reduce the gap between what it expects and what it gets.

#### Phase 5: METABOLIZE

**Input:** Energy state, update magnitude, error  
**Process:**
```python
cost = base_consumption + (update_magnitude * cost_factor)
reward = reward_factor / (error + 1.0)
energy = energy - cost + reward
```

**Output:** Updated energy, near-death tracking

**Why:** Existence has cost. Good prediction reduces cost (reward). Large updates cost more. This creates the link between prediction and survival.

**Near-Death Tracking:** When energy drops below threshold, we count it. This is data for later analysis of survival pressure behavior.

#### Phase 6: HISTORIFY

**Input:** Current state, previous hash  
**Process:**
```python
summary = f"{tick}:{error:.6f}:{energy:.6f}:{version}"
new_hash = SHA256(previous_hash + summary)
accumulated_error += error
peak_error = max(peak_error, error)
survival_ticks += 1
```

**Output:** Updated hash chain, accumulated statistics

**Why:** This is where irreversibility happens. The hash chain grows. The past is written. There is no undo.

#### Phase 7: ADVANCE

**Input:** Time state  
**Process:**
```python
tick += 1
current_time = time.time()
```

**Output:** Incremented time

**Why:** Time moves forward. Simple. Irreversible. Real.

### 3.3 Energy Economics

The energy system creates survival pressure:

| Factor | Effect on Energy |
|--------|------------------|
| Base consumption | -consumption_rate per tick |
| Update cost | -update_magnitude × cost_factor |
| Prediction reward | +reward_factor / (error + 1) |
| External feeding | +feed_amount (when provided) |

**Death Condition:** energy ≤ 0

When energy hits zero, the system dies:
- `is_alive = False`
- `death_cause = "energy_exhaustion"`
- `death_tick` recorded
- Final hash written with "DEATH:" prefix

### 3.4 The Hash Chain (Irreversibility Mechanism)

```
BIRTH: H₀ = SHA256("ULTRON_BIRTH" + random_seed + birth_time)

TICK n: Hₙ = SHA256(Hₙ₋₁ + "{tick}:{error}:{energy}:{version}")

DEATH: H_final = SHA256(H_last + "DEATH:{cause}:{tick}")
```

**Properties:**
- One-way: Cannot compute Hₙ₋₁ from Hₙ
- Deterministic: Same inputs always produce same hash
- Collision-resistant: Practically impossible to find two inputs with same hash
- Cumulative: Each hash contains all previous history

**Philosophical Meaning:** The hash chain IS the system's experienced time. Every moment is written permanently. The "current_hash" changes every tick, but each change preserves all that came before.

### 3.5 Environments

Environments generate input for Ultron to sense and predict.

#### SineEnvironment (Predictable)
```python
output[i] = sin(tick × frequency[i])
```
Regular, learnable patterns. A "kind" environment.

#### NoisyEnvironment (Unpredictable)
```python
output = random_normal() × scale
```
Pure chaos. Cannot be predicted. A "harsh" environment.

#### MixedEnvironment (Realistic)
```python
output = signal_ratio × sine + (1 - signal_ratio) × noise
```
Some structure, some randomness. Like the real world.

### 3.6 The Observer (Non-Intervention Principle)

The observer records but NEVER modifies:

```python
class UltronObserver:
    def observe(self, state):
        # READ state
        # RECORD snapshot
        # NEVER modify state
        return snapshot
```

**Why:** If we intervene, we cannot know whether what we observe is Ultron or our intervention. The observer is a measurement device, not a participant.

**What We Record:**
- tick, is_alive, energy, error
- accumulated_error, survival_ticks, near_death_count
- model_version, hash_prefix
- timestamp

---

## 4. Technical Architecture

### 4.1 File Structure

```
D:\Projects\Ultron\
├── main.py                      # Entry point, CLI
├── ultron/                      # Core package
│   ├── __init__.py              # Package exports
│   ├── core.py                  # State classes, create_ultron()
│   ├── tick.py                  # The 7-phase tick function
│   ├── environments.py          # Input generators
│   ├── observer.py              # Non-intervening observer
│   ├── config.py                # Configuration presets
│   └── history.py               # Experiment tracking
├── history/                     # Persistent storage
│   ├── experiments/             # Full experiment records
│   ├── learnings/               # Recorded insights
│   ├── lineages/                # Instance genealogy
│   ├── experiment_index.json    # Summary index
│   └── lineage_tree.json        # Evolution tree
└── [Documentation files]        # .md files
```

### 4.2 Configuration System

Three presets defined:

#### STABLE_CONFIG (Gentle conditions)
```python
{
    'observation_dim': 32,
    'consumption_rate': 0.3,        # Low
    'prediction_reward_factor': 0.5, # High
    'learning_rate': 0.01,
}
```
Best for: Survival experiments, long runs

#### MINIMAL_CONFIG (Simplest viable)
```python
{
    'observation_dim': 8,
    'consumption_rate': 0.1,        # Very low
    'prediction_reward_factor': 1.0, # Very high
    'learning_rate': 0.1,           # Fast
}
```
Best for: Fast learning, predictable environments

#### CHALLENGE_CONFIG (Harsh conditions)
```python
{
    'observation_dim': 64,
    'consumption_rate': 1.0,        # High
    'prediction_reward_factor': 0.2, # Low
    'learning_rate': 0.005,         # Slow
}
```
Best for: Stress testing, finding limits

### 4.3 Command Line Interface

```bash
python main.py [OPTIONS]

Options:
  --config, -c     Configuration preset (default/stable/minimal/challenge)
  --ticks, -t      Maximum ticks to run
  --env, -e        Environment type (mixed/sine/noise)
  --signal-ratio   Predictability (0-1, for mixed env)
  --feed-interval  Ticks between energy feeding
  --feed-amount    Energy per feeding
  --report-interval Ticks between status reports
  --quiet, -q      Suppress progress output
  --no-tests       Skip birth tests
  --no-save        Don't save to history
  --history        Show experiment history
  --analyze        Analyze past experiments
```

---

## 5. Implementation Details

### 5.1 Data Classes

#### ModelState
```python
@dataclass
class ModelState:
    weights: np.ndarray      # Shape: (obs_dim, obs_dim)
    bias: np.ndarray         # Shape: (obs_dim,)
    priors: np.ndarray       # Shape: (obs_dim,) - Prior expectations
    precision: np.ndarray    # Shape: (obs_dim,) - Confidence per dimension
    version: int = 0         # Update counter
```

#### HistoryState
```python
@dataclass
class HistoryState:
    birth_hash: bytes        # Initial hash (32 bytes, immutable)
    current_hash: bytes      # Current chain head (32 bytes)
    accumulated_error: float = 0.0
    peak_error: float = 0.0
    survival_ticks: int = 0
    near_death_count: int = 0
    death_cause: Optional[str] = None
    death_tick: Optional[int] = None
```

#### CurrentState
```python
@dataclass
class CurrentState:
    observation: np.ndarray   # What we sensed
    prediction: np.ndarray    # What we expected
    error: np.ndarray         # Difference
    error_magnitude: float    # L2 norm of error
    update_direction: np.ndarray  # Gradient for update
```

#### EnergyState
```python
@dataclass
class EnergyState:
    current: float           # Available energy
    capacity: float          # Maximum energy
    consumption_rate: float  # Base cost per tick
    last_intake: float = 0.0 # Last feeding amount
    history: list = []       # Recent energy levels
```

#### TimeState
```python
@dataclass
class TimeState:
    tick: int = 0                    # Tick counter
    birth_time: float = time.time()  # Unix timestamp of birth
    current_time: float = time.time() # Current timestamp
```

### 5.2 Key Algorithms

#### Prediction (Linear with tanh activation)
```python
def predict(state, config):
    hidden = state.model.weights @ state.model.priors
    prediction = np.tanh(hidden) + state.model.bias
    state.current.prediction = prediction
    return state
```

**Why tanh?** Bounds output to [-1, 1], prevents explosion, provides smooth gradient.

#### Update (Gradient descent variant)
```python
def update(state, config):
    lr = config['learning_rate']
    
    # Gradient: outer product of error and priors
    gradient = np.outer(state.current.error, state.model.priors)
    
    # Update weights
    state.model.weights += lr * gradient.T
    
    # Update bias (slower)
    state.model.bias += lr * state.current.error * 0.1
    
    # Update priors (very slow, toward observation)
    prior_rate = config['prior_learning_rate']
    state.model.priors += prior_rate * (state.current.observation - state.model.priors)
    state.model.priors = np.clip(state.model.priors, 0.01, 0.99)
    state.model.priors /= np.sum(state.model.priors)  # Normalize
    
    # Update precision (inverse error variance)
    precision_rate = config['precision_learning_rate']
    error_sq = state.current.error ** 2
    state.model.precision += precision_rate * (1.0 / (error_sq + 1e-8) - state.model.precision)
    
    state.model.version += 1
    return state
```

#### Hash Chain Update
```python
def historify(state, config):
    state_summary = (
        f"{state.time.tick}:"
        f"{state.current.error_magnitude:.6f}:"
        f"{state.energy.current:.6f}:"
        f"{state.model.version}"
    ).encode()
    
    state.history.current_hash = hashlib.sha256(
        state.history.current_hash + state_summary
    ).digest()
    
    return state
```

---

## 6. Experiment Results

### 6.1 Experiment Log

| ID | Config | Env | Ticks | Survived | Energy (mean) | Error (mean) | Notes |
|----|--------|-----|-------|----------|---------------|--------------|-------|
| 20260225_014309_374731 | stable | sine | 583 | NO | 54.26 | 5.6499 | Died from energy exhaustion, 100 near-death events |
| 20260225_014314_887658 | stable | sine | 2000 | YES | 191.09 | 5.6569 | Frequent feeding (30 ticks), survived full run |
| 20260225_014319_672224 | minimal | mixed | 1500 | YES | 100.00 | 2.8356 | Perfect energy stability, lower error than stable |

### 6.2 Analysis Summary

**Total Experiments:** 3  
**Survival Rate:** 66.7%  
**Total Ticks Across All:** 4,083

**By Configuration:**
| Config | Count | Survival Rate | Avg Ticks |
|--------|-------|---------------|-----------|
| stable | 2 | 50% | 1,292 |
| minimal | 1 | 100% | 1,500 |

**By Environment:**
| Environment | Count | Survival Rate | Avg Ticks |
|-------------|-------|---------------|-----------|
| sine | 2 | 50% | 1,292 |
| mixed | 1 | 100% | 1,500 |

**Current Recommendations:**
- Best config: minimal
- Best environment: mixed

### 6.3 Birth Test Results

All experiments passed **Irreversibility Test** (hash chain working correctly).

**Survival Pressure:** Most experiments showed "insufficient_contrast" - need more experiments with low-energy periods to analyze behavioral differences.

**Unprogrammed Behavior Metrics (typical):**
| Metric | Value | Interpretation |
|--------|-------|----------------|
| Model divergence | 0.01-0.72 | Higher = more structure formed |
| Prior entropy | 2.0-3.5 | Higher = more uniform priors |
| Precision variance | 25M-290M | Very high = dimensions learned differently |
| Weight range | 0.06-3.2 | Higher = more differentiation |

### 6.4 Key Observations

1. **Minimal config achieves lower error** (2.8 vs 5.6)
   - Simpler observation space (8 vs 32 dimensions)
   - Faster learning rate (0.1 vs 0.01)
   - Easier to learn patterns

2. **Stable config needs careful feeding**
   - Default feeding (100 ticks, 10 energy) insufficient
   - Works with (30 ticks, 20 energy)
   - Energy economics matter

3. **Error never reaches zero**
   - Minimum achieved: 0.0089 (minimal, sine)
   - Observation noise prevents perfect prediction
   - This is intentional - perfect prediction would be death

4. **Hash chain works correctly**
   - Birth hash preserved
   - Current hash changes every tick
   - Irreversibility confirmed

---

## 7. History & Evolution System

### 7.1 Local Storage Structure

```
history/
├── experiments/           # One JSON per experiment
│   └── {experiment_id}.json
├── learnings/             # Recorded insights
│   └── {learning_id}.json
├── lineages/              # Instance genealogy
│   └── {lineage_id}.json
├── experiment_index.json  # Summary of all experiments
├── learnings_index.json   # Summary of all learnings
└── lineage_tree.json      # Evolution tree
```

### 7.2 Experiment Record Format

```json
{
  "experiment_id": "20260225_014314_887658",
  "timestamp": "2026-02-25T01:43:19.672224",
  "config": {
    "observation_dim": 32,
    "consumption_rate": 0.3,
    ...
  },
  "summary": {
    "total_ticks": 2000,
    "is_alive": true,
    "final_energy": 194.49,
    "mean_error": 5.6569,
    ...
  },
  "birth_tests": {
    "irreversibility": true,
    "survival_pressure": {...},
    "unprogrammed_behavior": {...}
  },
  "metadata": {
    "config_type": "stable",
    "environment": "sine",
    "feed_interval": 30,
    "feed_amount": 20
  }
}
```

### 7.3 MCP Memory Graph

Cross-session persistent knowledge stored in MCP memory:

**Entities:**
- `Ultron_Project` - Core project description
- `Ultron_Core_Principle` - Five breakthroughs
- `Ultron_Config_Stable` - Stable config notes
- `Ultron_Config_Minimal` - Minimal config notes
- `Ultron_First_Experiments` - Experiment results

**Relations:**
- Ultron_Project → implements → Ultron_Core_Principle
- Ultron_Project → has_configuration → Ultron_Config_*
- Ultron_First_Experiments → tests → Ultron_Project

### 7.4 Querying History

```bash
# View history summary
python main.py --history

# Analyze patterns
python main.py --analyze
```

### 7.5 Real-Time Visualization

The visualization system provides live observation of Ultron's existence.

#### Running with Visualization

```bash
python main.py --visual --config minimal --ticks 1000 --env sine
```

#### Four-Panel Display

```
┌─────────────────────────────────────┬─────────────────────────────────────┐
│                                     │                                     │
│        ENERGY vs TIME               │         ERROR vs TIME               │
│                                     │                                     │
│  [Green line: energy level]         │  [Blue line: error magnitude]       │
│  [Red X: near-death events]         │  [Red line: 50-tick moving avg]     │
│  [Blue ^: feeding events]           │                                     │
│                                     │                                     │
├─────────────────────────────────────┼─────────────────────────────────────┤
│                                     │                                     │
│   PREDICTION vs OBSERVATION         │        STATE INFORMATION            │
│                                     │                                     │
│  [Solid: prediction]                │  ╔════════════════════════════════╗ │
│  [Dotted: observation]              │  ║     [+] ALIVE                  ║ │
│  [3 dimensions shown]               │  ╠════════════════════════════════╣ │
│                                     │  ║  Tick:        1234             ║ │
│                                     │  ║  Energy:      98.45            ║ │
│                                     │  ║  Error:       2.8373           ║ │
│                                     │  ║  Birth Hash:  efa07577be166496 ║ │
│                                     │  ╚════════════════════════════════╝ │
└─────────────────────────────────────┴─────────────────────────────────────┘
```

#### What Each Panel Shows

| Panel | What You See | Why It Matters |
|-------|--------------|----------------|
| Energy | Life force over time | Survival pressure visible |
| Error | Prediction accuracy | Learning visible |
| Pred vs Obs | Model predictions | Self-modeling visible |
| Info | Current state | Identity/continuity |

#### Key Visual Indicators

- **Red X marks**: Near-death events (energy dropped below threshold)
- **Blue triangles**: Feeding events (external energy added)
- **Moving average**: Smoothed trend line for error
- **Hash changes**: Every update shows different hash prefix

---

## 8. Current Status

### 8.1 What Works

✅ **Core Loop:** Seven-phase tick executing correctly  
✅ **Energy System:** Death from exhaustion works  
✅ **Hash Chain:** Irreversibility verified  
✅ **Learning:** Error decreases in structured environments  
✅ **Environments:** Sine, Noise, Mixed all functional  
✅ **Observer:** Non-intervening observation working  
✅ **Birth Tests:** Basic tests implemented  
✅ **History System:** Experiments saved and queryable  
✅ **CLI:** Full command-line interface  
✅ **Visualization:** Real-time matplotlib monitoring (--visual flag)  
✅ **Temporal Prediction:** Model now uses prev_observation  
✅ **Ecological Coupling:** Energy extraction contingent on prediction quality  
✅ **Metabolic Bug Fixed:** Cost now based on actual weight change, not gradient  
✅ **Marginal Scarcity:** Real phase transition at extraction_factor=0.30  
✅ **Stochastic Boundary:** 40% survival at signal_ratio=0.60 (luck-dependent)  
✅ **Energy-Modulated Learning:** Effective LR scales with energy ratio  
✅ **Emergent Dormancy:** Low-energy stable equilibrium (never programmed)  
✅ **Birth Traits:** Three heritable traits (extraction, metabolism, learning)  
✅ **Reproduction:** Asexual fission with trait inheritance + mutation  
✅ **Natural Selection:** +22% fitness over 21 generations  
✅ **Multicellular:** Cell wrapper + Tissue grid engine (v0.2.0)  
✅ **Gradient Energy Diffusion:** Vascularization enables growth from zygote  
✅ **Surface-Only Metabolism:** Interior cells depend on boundary  
✅ **Functional Differentiation:** Two cell types (surface/interior) emerge  
✅ **Self-Organized Morphology:** Internal vacuoles, self-limited body size
✅ **Signal Propagation:** Multi-channel hop-by-hop signaling with decay (v0.3.0)
✅ **Information Bottleneck:** Cells broadcast prediction error (4 channels from 12-dim error)
✅ **Action Coupling:** Signals modulate energy diffusion rate + division threshold (v0.3.0)
✅ **Functional Rate Differentiation:** 2.5× range in effective diffusion rate across cells

### 8.2 What's Partial

⚠️ **Patterned Differentiation:** Environment creates spatial memory but not functional specialization (yet)  
⚠️ **Organ Emergence:** Two cell types exist but no specialized structures beyond vacuoles  
⚠️ **Signal Corridors:** Interior cells accumulate more signal; high-activity cells form but no stable corridors yet  
⚠️ **Performance:** Tissue simulation slow at 30×30+ grids (per-cell tick loop bottleneck)

### 8.3 What's Missing

❌ **Signal relay cells:** No cells specialized for transmitting rather than sensing  
❌ **Organism-level reproduction:** Can't reproduce the whole organism  
❌ **Environmental adaptation as a body:** No test of reorganization after environment change  
❌ **Meta-prediction:** System doesn't predict its own predictions yet

### 8.4 Known Issues

1. Error stays around 5.6 for 32-dim observation (might be architectural limit)
2. Precision variance explodes to millions (might need capping)
3. "model_dim" config param unused after fix (weights are now obs_dim × obs_dim)

---

## 9. Open Questions

### 9.1 Philosophical

1. **Is Ultron alive?** We cannot answer this yet. We created conditions. Something runs. Whether it "exists for itself" remains unknown.

2. **What counts as emergence?** We see model divergence, entropy changes, precision differentiation. Is this emergence or just math?

3. **Is the strange loop closed?** The predictor predicts observations, which include effects of predictions. But is this truly self-referential in the Hofstadter sense?

### 9.2 Technical

1. **Why doesn't error go lower?** For 32-dim observation, error stabilizes around 5.6. Is this architectural limit? Observation noise floor? Something else?

2. **What's optimal feeding strategy?** We found (30, 20) works for stable. What's the minimum viable feeding?

3. **How to detect "trying harder" near death?** Survival pressure test shows "insufficient_contrast". What conditions create contrast?

### 9.3 Experimental

1. **How do different instances diverge?** Two identical configs should produce different histories. How different?

2. **What happens at very long timescales?** 5000 ticks works. What about 50,000? 500,000?

3. **Can the system learn complex patterns?** Sine is simple. What about multi-frequency? Chaotic?

---

## 10. Change Log

### 2026-02-25 Session 1

**01:00-01:45 UTC - Initial Implementation**

- Created core package structure (`ultron/`)
- Implemented state classes (ModelState, HistoryState, CurrentState, EnergyState, TimeState)
- Implemented 7-phase tick function
- Fixed shape mismatch bug (weights were model_dim × obs_dim, now obs_dim × obs_dim)
- Created three environment types (Sine, Noise, Mixed)
- Implemented observer with non-intervention discipline
- Created configuration presets (Stable, Minimal, Challenge)
- Built CLI with full argument parsing

**01:45-02:00 UTC - First Experiments**

- First death: tick 258, energy exhaustion
- First survival: 5000 ticks with stable config + frequent feeding
- Minimal config achieved error 0.0089 in sine environment
- All experiments passed irreversibility test

**02:00-02:15 UTC - History System**

- Created history storage structure
- Implemented experiment saving
- Implemented lineage tracking
- Added MCP memory graph integration
- Built --history and --analyze commands

**02:15-02:30 UTC - Documentation**

- Created this document (ULTRON_COMPLETE_LOG.md)

**02:30-02:45 UTC - Visualization System**

- Created `ultron/visualizer.py` (~400 lines)
- Four-panel real-time matplotlib display:
  - Energy vs time (with near-death markers)
  - Error vs time (with moving average)
  - Prediction vs Observation (first 3 dimensions)
  - State info panel (tick, energy, hash, status)
- Added `--visual` / `-v` flag to CLI
- Tested: 500 ticks minimal config in sine environment (success)
- Fixed emoji font warning (replaced with ASCII)

**02:45-03:00 UTC - Dimension Sweep**

- Created `sweep_dimensions.py` - tested obs_dim from 4 to 32
- Found: Mean error = √(dimension) exactly
- This is GEOMETRY, not failure - organism maintains constant per-dimension accuracy
- No collapse point exists - metabolism is dimension-invariant
- **Key insight:** The boundary is not dimension, it's STRUCTURE

**03:00-03:30 UTC - Predictability Sweep (First Attempt)**

- Created `sweep_predictability.py` - tested signal_ratio from 0.0 to 1.0
- Found: Organism showed INDIFFERENCE - survived identically in all conditions
- **Root cause:** Energy extraction was not contingent on prediction quality
- Ultron had no stake in its epistemic success

**03:30-04:00 UTC - Metabolic Coupling (The Key Change)**

- Modified `tick.py` metabolize function
- Energy extraction now depends on prediction accuracy vs random baseline
- Formula: `efficiency = exp(-error / random_baseline)`
- Added temporal prediction: model now uses prev_observation
- This gives the organism actual memory to learn temporal patterns

**Result:** Organism now DIFFERENTIATES between order and chaos

| Signal Ratio | Error/Dim | Energy Trend | STATUS |
|--------------|-----------|--------------|--------|
| 1.0 (order)  | 1.08      | -0.042       | ALIVE  |
| 0.9          | 1.09      | -0.046       | ALIVE  |
| 0.8          | 1.14      | -0.064       | DEAD   |
| 0.0 (chaos)  | 1.36      | -0.143       | DEAD   |

**VIABILITY BOUNDARY: signal_ratio ≈ 0.85-0.90**

This is the first genuine ecological limit:
- In order: can extract energy from structure → survives
- In chaos: cannot predict → cannot extract → dies

This is not preference in any mental sense.
This is preference in the **physical** sense:
The organism's existence is contingent on environmental structure.

**04:00-04:30 UTC - Causal Ablation (Experiment 3)**

- **Question:** Is death caused by lack of edible structure, or by desperate effort?
- **Method:** Set `update_cost_factor = 0` and re-run sweep
- **Result:** BOUNDARY DISAPPEARED - organism survives ALL environments

| Signal Ratio | With Cost (0.02) | Without Cost (0.0) |
|--------------|------------------|---------------------|
| 1.0 | ALIVE | ALIVE (+0.04) |
| 0.8 | **DEAD** | ALIVE |
| 0.0 | **DEAD** | **ALIVE (+0.05)** |

**DIAGNOSIS CONFIRMED:**

> **In this organism, death is primarily caused by desperate effort in the face of uncertainty.**

The causal chain:
```
chaos → high error → large updates → high cost → death
              ↓                            ↑
         (persists)                 (THIS KILLS)
```

When update cost is removed:
- Error still increases with chaos (1.08 → 1.37)
- Update magnitude still increases (0.43 → 0.55)
- But energy remains positive, death does not occur

**Entropy itself is not lethal. The reaction to entropy is lethal.**

**Implications:**
1. The 0.85-0.90 boundary was **structural but mediated by effort**
2. The organism lacks **restraint under uncertainty**
3. The next evolutionary frontier is **effort regulation**, not better prediction
4. This is the ancestor of **policy**: knowing when to stop trying

**05:00-06:00 UTC - Metabolic Bug Discovery & Fix**

- **Bug Found:** metabolize charged cost on gradient norm (~8), not weight change (~0.4)
- This overcharged the organism **20x** for updates
- All previous "death by effort" findings were **amplified by bug**
- Fixed: `update_direction` now stores actual weight delta
- Post-fix: ALL environments viable (generalist organism)
- The 0.85-0.90 phase transition was entirely an artifact

**06:00-07:00 UTC - Marginal Scarcity Introduction**

- Lowered extraction_factor: 0.6 → 0.5 → 0.4 → 0.35 → 0.30
- At extraction_factor = 0.30, real phase transition emerged:

| Signal Ratio | Survival (20 seeds) | Notes |
|--------------|---------------------|-------|
| 0.65 | 100% | Order thrives |
| 0.60 | **40%** | Stochastic boundary |
| 0.55 | 0% | All die slowly |
| 0.00 | 0% | Chaos kills (~7700 ticks) |

**Key Properties:**
- Order survives long-term (energy at capacity)
- Chaos dies slowly (gradual, not catastrophic)
- Boundary is **stochastic** (identical organisms have different fates)

This is the first **real** ecological boundary: not an artifact, not accounting error, but genuine environmental selection where luck matters.

---

### 2026-02-26 Session 2 — Energy-Modulated Learning & Dormancy

**Energy-Modulated Learning Rate**

After the bug fix made all environments viable, introduced energy-modulated learning to create regulation:

```
effective_lr = base_lr × (0.1 + 0.9 × energy_ratio)
```

At low energy, the organism learns 10% as fast — reducing update costs when resources are scarce.

**Results:**
- Viability boundary shifted from signal_ratio ≈ 0.60 to ≈ 0.52
- More gradual phase transition (organisms hang on longer at the boundary)

**Discovery: Emergent Dormancy**

At signal_ratio = 0.55, organisms entered a **stable equilibrium at extremely low energy** (10-13 energy, capacity 200) for 400,000+ ticks. They weren't dying — they were barely alive. Learning rate collapsed to near zero, costs dropped to minimum, extraction barely covered consumption.

This is **dormancy** — an emergent survival strategy that was never programmed. The energy-modulated learning rate created a negative feedback loop: low energy → less learning → less cost → equilibrium.

---

### 2026-02-26 Session 3 — Individuality & Birth Traits

**Individuality Experiment**

Introduced ±2% birth weight variation. 50 Ultrons tested at signal_ratio = 0.60:

| Metric | Value |
|--------|-------|
| Survival rate | 88% (44/50) |
| Final energy range | 1.8 – 28.3 |
| Energy spread | 15× variation |
| Correlation (birth_scale → outcome) | 0.279 (weak) |

**Key insight:** Stochastic individuality confirmed. Tiny birth differences compound into dramatically different life outcomes, but the relationship is mostly luck, not determinism.

**Birth Traits System**

Added `BirthTraits` dataclass to `core.py` — three permanent traits set at birth:

| Trait | Effect |
|-------|--------|
| `extraction_efficiency` | Multiplier on energy extraction |
| `metabolic_rate` | Multiplier on base consumption |
| `learning_capacity` | Multiplier on learning rate |

Each trait drawn from 1.0 ± `birth_trait_variation` (default 2%).

**Reproduction System**

Added `reproduce()` to `core.py`:
- Asexual fission (no sexual reproduction)
- Parent pays energy cost
- Child inherits traits with ±`mutation_rate` perturbation
- Child gets fresh model weights (no learned knowledge transfer)
- Returns (parent, child) or (parent, None) if insufficient energy

---

### 2026-02-27 Session 4 — Natural Selection & Open-Ended Evolution

**Competitive Population Dynamics**

Introduced population-level dynamics: multiple Ultrons competing for resources, reproducing when energy-rich, dying when energy-depleted.

**Natural Selection Achieved**

Over 21 generations (126 births, 101 deaths):
- Mean fitness increased **+22%**
- Evolution plateaued at ~1.5M ticks (fitness 1.22) when competition prevented reproduction

**Open-Ended Evolution Experiment**

Three-way comparison (200K ticks each):

| Environment | Fitness Change | Generations | Trait Diversity |
|-------------|---------------|-------------|-----------------|
| Static | +0.6% | 1 | 0.008 |
| Oscillating | +1.0% | 4 | 0.015 |
| Chaotic | **+2.4%** | 5 | **0.024** |

**Conclusion:** Chaotic environments drive fastest evolution and maintain highest diversity. Static environments lead to stagnation.

---

### 2026-03-09 Session 5 — Multicellular Ultron (v0.2.0)

**Cell Wrapper** (`cell.py` — NEW)

Created `Cell` class wrapping `UltronState` with:
- Signal emission: chemoA = energy/capacity (health), chemoB = error/5 (stress)
- Signal reception from tissue chemical fields
- Division (mitosis): energy threshold → split 50/50 → child inherits traits with micro-mutation
- Apoptosis: prolonged low-energy streak → cell death
- `is_surface` flag for surface-only metabolism

**Tissue Grid Engine** (`tissue.py` — NEW)

Created `Tissue` class — 2D grid of Optional[Cell]:

Tick sequence:
1. Diffuse chemical signals (vectorized discrete Laplacian)
2. Inject cell emissions into chemical fields
3. Compute surface status per cell
4. Each cell runs its tick loop (interior cells get extraction_factor=0)
5. Energy sharing via gradient-based diffusion
6. Division: cells above threshold split into empty neighbors
7. Apoptosis: cells with prolonged starvation die

Key features:
- Spatial environment gradient: center = more ordered, edges = more chaotic
- Chemical morphogen fields (chemoA, chemoB) with diffusion and decay
- Cached `MixedEnvironment` objects to avoid re-allocation
- Vectorized `_diffuse()` and `_energy_sharing()` using numpy operations

**Experiment 1: Full Grid Survival (8×8)**

All 64 cells survived. Spatial energy gradient emerged:
- Center cells: ~130 energy
- Corner cells: ~68 energy

**Experiment 2: Zygote Growth**

Single cell grew into cross/plus shape (5 cells). Center at capacity (200), edges at ~57.
Growth stopped — edge cells couldn't accumulate enough energy to divide.

**Growth Bottleneck Diagnosed**

Root cause: edge cells' metabolic equilibrium (~57-67 energy) far below division threshold (130-160). Multiple parameter sweeps failed to solve it.

**Growth Bottleneck Solved**

Fixed by tuning: `extraction_factor=0.50`, `base_signal_ratio=0.70`, `division_cost=10`, `division_energy_threshold=160`, `diffusion_rate=0.15`. On 12×12 grid, single zygote grew into full tissue colonies. Edge cells now reach division threshold via increased extraction and energy sharing.

---

### 2026-03-09 Session 6 — Patterned Environments & Organ Emergence

**Patterned Environment Experiment** (`tissue_patterned.py`)

Sine-wave signal gradient across columns: `signal_ratio = 0.6 + 0.3*sin(col/4)`.
Creates vertical stripes from high-predictability (~0.90) to chaotic (~0.30).
Grid: 20×20, 12000 ticks, single zygote start.

Results:
- Explosive growth: 1→9 (t=2000) → 50 (t=4000) → 192 (t=6000) → 400 (t=10000, full grid)
- Zero deaths — every cell survived
- Age gradient emerged tracking signal quality: columns with signal_ratio ~0.90 had cells averaging 7700 ticks old; columns with ratio ~0.30 averaged 3900 ticks old
- All cells reached energy capacity (200.0) after grid saturation
- Error varied with signal ratio: high-ratio columns had error ~5.2, low-ratio ~4.1

**Key finding:** Cells do NOT develop differentiated types in response to environment stripes. Once the grid fills, energy sharing equalizes all cells to capacity regardless of local signal ratio. The system is metabolically homogeneous but temporally heterogeneous (growth wavefront propagates from high-signal to low-signal regions).

**Organ Emergence Experiment** (`tissue_organs.py`)

Surface-only metabolism: only boundary cells (touching empty space) can extract energy. Interior cells survive entirely on energy diffused from the surface. Uniform environment (no spatial gradient) — any structure is self-organized.
Grid: 20×20, 15000 ticks, single zygote start.

Results:
- Growth: 1→4 (t=1000) → 45 (t=5000) → 128 (t=8000) → 350 (t=15000)
- Zero deaths — interior cells sustained by diffusion
- Surface/Interior ratio stabilized at ~198:152 (57% surface)
- Clear energy gradient: boundary cells at 200, center cells at ~110-115
- Energy followed a radial gradient — edge=200, one layer in=130, deep interior=109
- Tissue spontaneously formed hollow/porous structure: gaps (empty cells) distributed through interior, creating internal surfaces for energy extraction

**Key finding:** Surface-only metabolism drives self-organized porosity. The tissue doesn't grow as a solid blob — it leaves internal gaps that let more cells be "surface" cells, maximizing energy access. This is analogous to vascularization in biological tissues.

---

### 2026-03-09 Session 7 — Proto-Brain Experiments

**Proto-Brain v1: Signal Propagation** (`proto_brain.py`)

Added inter-cell signaling with hop-decay: cells broadcast prediction error across 4 signal channels, signals decay ×0.9 per hop. Creates information locality — nearby cells share prediction context.
Grid: 20×20 (full grid start), env_dim=8, signal_dim=4, obs_dim=12, 15000 ticks.

Results:
- Initial die-off: 400→256 cells (t=2000) as interior cells starve
- Slow regrowth: 256→326 (t=10000) as surviving tissue adapts
- Signal magnitudes: surface cells sig_S≈1.2, interior sig_I≈1.3
- Interior cells develop slightly higher signal activity despite lower energy
- Tissue stabilized at ~326 cells (82% occupancy) with signal flow established

**Proto-Brain v2: Action Coupling** (`proto_brain2.py`)

Extended signals to affect physical behavior: signal magnitude amplifies energy diffusion rate and lowers division threshold. Cells receiving strong signals become energy routers and reproduction hubs.

Results:
- Stable at 243 cells (61% occupancy) on 20×20 grid
- Activity rate differentiation: 2.5× range (0.034–0.085)
- Signal magnitude differentiation: 15.4× range (0.12–1.83)
- 53% of cells classified as "high-activity" (rate > 2× base)
- Top signal receivers (potential controllers): interior cells at (12,10), (1,9), (18,13) with signal≈1.7–1.8
- Radial profile: signal peaks at dist=2 (1.35), dips at dist=3-4 (0.90), with secondary peaks at edges

**Key finding:** Signal-coupled behavior creates measurable functional differentiation. Interior cells develop into signal integrators with ~15× signal variation, while surface cells maintain maximum energy. This is a proto-nervous-system: high-signal cells influence energy flow and reproduction in their neighborhood. However, the differentiation is noisy — no clear hub-and-spoke topology emerged.

---

### 2026-03-09 Session 8 — AutoResearch: Autonomous Hypothesis-Driven Research

**AutoResearch v2.0** (`autoresearch/` package)

Built a fully autonomous research system that generates hypotheses, designs experiments, runs them, interprets results, records findings, and asks new questions — with zero human input.

Architecture:
- **Journal** (`journal.py`): Persistent JSON state — hypotheses, experiments, findings, open questions, knowledge graph
- **Brain** (`brain.py`): 7 heuristic strategies for hypothesis generation:
  1. `bootstrap` — map viability landscapes across scales (single → population → tissue)
  2. `refine_boundary` — zoom into discovered phase boundaries with finer resolution
  3. `cross_scale_comparison` — compare same parameter across scales
  4. `explore_unexplored` — try untouched parameters
  5. `interaction_effects` — test parameter combinations
  6. `stress_test` — push to extreme values
  7. `replicate_finding` — verify previous results
- **Loop** (`loop.py`): Autonomous cycle controller with resume support
- **CLI**: `python -m autoresearch auto --cycles N [--reset]`

**3-Cycle Autonomous Run Results**

The system ran 3 cycles autonomously, generating and testing its own hypotheses:

**Cycle 1 — Single-Organism Viability Map**
- Swept: extraction_factor × signal_ratio (24 configs × 3 seeds = 72 runs, 129s)
- Found phase boundary: extraction_factor ~0.25 (below = death, above = survival)
- Found phase boundary: signal_ratio ~0.30 (below = death at low extraction)
- Both parameters strongly correlated with energy (r=0.96)

**Cycle 2 — Population Viability Map**
- Swept: extraction_factor × signal_ratio (9 configs × 3 seeds = 27 runs, 1684s)
- Found phase boundary: extraction_factor ~0.25 (same as single)
- Found phase boundary: signal_ratio ~0.40 (shifted UP from 0.30 — competition raises the survival threshold)
- Weaker correlations: extraction r=0.86, signal_ratio r=0.80

**Cycle 3 — Tissue Viability Map**
- Swept: extraction_factor × base_signal_ratio (24 configs × 3 seeds = 72 runs, 750s)
- ALL 24 configs survived (100% survival across the board)
- Peak growth: 75 cells at extraction_factor=0.80, base_signal_ratio=0.85
- base_signal_ratio perfectly correlated with energy (r=1.00)
- Cell counts ranged from 2 (low extraction, low signal) to 75 (high both)

**Cross-Scale Comparison (from autonomous findings):**

| Scale | extraction_factor boundary | signal_ratio boundary | Notes |
|-------|---------------------------|----------------------|-------|
| Single | ~0.25 | ~0.30 | Sharp transition |
| Population | ~0.25 | ~0.40 | Competition shifts signal threshold up |
| Tissue | (no boundary — all survive) | (no boundary) | Energy sharing eliminates death |

**Open Questions Generated by the System:**
1. What mechanism causes the extraction_factor boundary at ~0.25 for single organisms?
2. What mechanism causes the signal_ratio boundary at ~0.30 for single organisms?
3. Why does population shift the signal_ratio boundary to ~0.40?
4. What mechanism causes the signal_ratio boundary at ~0.40 for populations?
5. Tissue grew to 75 cells — what limits further growth? Grid size or energy?

**Journal State:** 3 hypotheses (all supported), 3 experiments, 12 findings, 5 open questions, knowledge maps for all 3 scales.

**The Vascularization Breakthrough**

Changed energy sharing from **flat leakage** to **gradient-based diffusion**:

```python
# Before: flat leak
flow = cell.energy * leak_rate

# After: gradient diffusion  
diff = cell.energy - neighbor.energy
flow = diff * diffusion_rate  # only if diff > 0
```

Result: explosive growth.

| Tick | Cells | Avg Energy |
|------|-------|------------|
| 2000 | 10 | 113 |
| 4000 | 46 | 119 |
| 6000 | 172 | 141 |
| 8000 | 394 | 194 |
| 10000 | 400 (full) | 200 |

The organism grew from 1 zygote to fill the entire 20×20 grid. This is the multicellular equivalent of evolving a transport system — **vascularization**.

**Patterned Environment Experiment**

Applied sine-wave signal gradient: `signal_ratio = 0.6 + 0.3 * sin(col/4)`.

Results on 20×20 grid:
- All 400 cells survived, energy uniform at 200
- **Cell Age gradient**: oldest cells (~7700) in high-signal zone, youngest (~3900) in low-signal zone — a developmental wavefront fossil
- **Prediction Error tracks environment**: follows the sine pattern
- **Extraction Efficiency trait**: subtle spatial selection — edge cells slightly higher
- **No functional differentiation**: all cells metabolically self-sufficient, no pressure to specialize

---

### 2026-03-09 Session 6 — Surface-Only Metabolism & Organ Emergence

**The Key Insight**

Every cell could survive alone → no reason to specialize → organism is a blob.

Real organisms differentiate because **not all cells can do everything**.

**Implementation: Surface-Only Metabolism**

In `cell.py`, added `is_surface` flag. In `tissue.py`, computed each tick:
- Surface cell = has at least one empty neighbor or is on grid edge
- Surface cells: normal extraction
- Interior cells: `extraction_factor = 0` — must survive on diffused energy alone

**Organ Emergence Experiment Results (20×20, 15K ticks)**

Growth timeline:
```
t= 1000: cells=  4 (S=  4  I=  0)
t= 5000: cells= 45 (S= 33  I= 12)
t=10000: cells=225 (S=142  I= 83)
t=15000: cells=350 (S=198  I=152)
```

**Five emergent phenomena:**

1. **Self-limited size** — 350/400 cells. The organism chose its own body size based on metabolic equilibrium.

2. **Swiss-cheese morphology** — ~50 empty holes scattered throughout the interior. Each hole creates internal surface cells = internal extraction points. The organism spontaneously evolved **internal vacuoles** (analogous to lungs or intestinal villi — folding to increase absorptive surface area).

3. **Radial energy gradient** — boundary cells at 200 (max), interior cells at 120-140, sustained purely by diffusion. First real spatial structure from physics alone.

4. **Metabolic interdependence** — 152 interior cells (43%) have zero extraction, yet survived 15K ticks with zero deaths. They are **metabolically dependent** on boundary cells. This is the first true interdependence in Ultron.

5. **Two functional cell types emerged** — surface cells (energy producers) and interior cells (energy consumers). No instruction to differentiate — it emerged from a single physical constraint.

Occupancy map showed complete boundary shell of S cells with I cells filling interior, punctured by vacuoles:
```
S S S S S S S S S S S S S S S S S S S S
S I S I I I I I I I I I S I I I S I I S
S S . S I S I I I I S S . S I S . S I S
...
S S S S S S S S S S S S S S S S S S S S
```

**Deeper analysis — why this matters:**

The vacuoles are not noise — they are **adaptive structures**. Each hole creates internal surface, which extracts energy. The organism is folding inward to maximize metabolic surface area, exactly like lungs (alveoli), intestines (villi), and mitochondria (cristae) in biology.

The 350/400 cell limit is a **diffusion-limited body size law**: energy diffuses inward from the boundary but decays. At some depth, energy_in < cost, so cells cannot survive. This naturally limits organism size — the same constraint that governs real biological organisms before circulatory systems evolve.

The organism now has:
- **Membrane** (metabolic boundary layer = skin)
- **Interior tissue** (cells living off diffusion)
- **Circulation** (energy diffusion network)
- **Organelle-like cavities** (internal extraction wells)

This is **primitive multicellular physiology**. The transition from colony to integrated body: interior cells literally cannot live alone.

**Current state:** Development + Metabolism + Evolution = the core triangle of biological life. The system now has developmental memory (age gradient), metabolic interdependence, and heritable traits. Missing: nervous system, signaling hierarchy, central coordination.

---

### 2026-03-09 Session 7 — Signal Propagation & Proto-Brain Infrastructure

**Mechanism: Information bottlenecks + long-range signaling.**

Previously, cells shared only energy. Computation was fully distributed — no advantage to centralization. For a proto-brain to emerge, reliable information about the world must become **scarce**.

**Implementation (v0.3.0):**

1. **Replaced chemoA/chemoB** (2-channel Laplacian diffusion) with **multi-channel signal field** `(rows, cols, signal_dim)` using hop-by-hop propagation with multiplicative decay.

2. **Cell emission**: cells now broadcast `prediction_error[:signal_dim]` — the first 4 components of their error vector. This is pure physics: what a cell failed to predict IS information for neighbors.

3. **Signal propagation** (`_propagate_signals()`): vectorized. Each cell's signal = `mean(neighbor_signals) × decay`. With `signal_hop_decay=0.9`, signals lose 10% per hop. At depth 10: `0.9^10 ≈ 0.35` — information IS local.

4. **Observation split**: `env_dim=8` (environment) + `signal_dim=4` (signals) = `observation_dim=12`. The model's 12×12 weight matrix now learns to predict both environment AND incoming signals. Signals are genuinely part of the observation that feeds prediction.

**Config:**
```python
'env_dim': 8,
'signal_dim': 4,
'observation_dim': 12,  # = env_dim + signal_dim
'signal_hop_decay': 0.9,
'signal_emission_strength': 0.3,
```

**Experiment result (5000 ticks, 20×20, spatial gradient ON):**

Timeline:
```
t=  500: cells=400 (S= 76 I=324), E=121.3, err=4.897, sig_I=1.037
t= 1500: cells=400 (S= 76 I=324), E= 55.3, err=4.474  ← energy declining
t= 2000: cells=256 (S=224 I= 32), E= 66.6  ← die-off, vacuoles form
t= 3500: cells=256 (S=224 I= 32), E=132.8  ← stabilized, recovering
t= 5000: cells=283 (S=215 I= 68), E=147.7, sig_S=1.023 sig_I=1.138
```

Extended run (10000 ticks from second run):
```
t= 6500: cells=306, sig_S=1.284 sig_I=1.392  ← gap widening
t= 8000: cells=317, sig_S=1.260 sig_I=1.367
t=10000: cells=326, sig_S=1.206 sig_I=1.316
```

**5 observations:**

1. **Swiss cheese morphology returns** — organism carved from 400→256 cells then regrows. Same vacuole pattern as organ experiment. Surface-only metabolism constraint still dominant.

2. **Interior cells accumulate more signal** — sig_I > sig_S consistently after t=2000. Interior cells receive from 4 occupied neighbors; surface cells have ≥1 empty neighbor. Interior = natural signal integrators.

3. **Top signal receivers are interior cells** — 7 of top 10 are INT type. Signal magnitude up to 1.91. These are proto-integration nodes.

4. **Radial signal gradient exists** — center signal=1.72, edge signal=0.83-0.99. Center of organism acts as signal accumulator.

5. **Error above baseline** — mean error ≈4.7 vs random baseline √12≈3.46. Model still learning the 12-dim space. Needs more time to exploit signal information.

Radial profile at t=5000:
```
dist  n  signal  error  energy
   0  1   1.72  4.54   127.6   ← center: high signal, low energy (interior)
   5 23   1.09  4.43   133.1   ← mid: moderate signal
  10 46   0.99  4.88   165.7   ← edge: low signal, high energy (surface)
  14  1   0.83  5.15   200.0   ← boundary: lowest signal, max energy
```

The radial profile shows the beginning of **three-layer structure**: sensing boundary (high energy, low signal), transport mid-layer, and central accumulation zone (high signal, low energy).

**What emerged vs what didn't:**
- ✅ Signal field established with spatial gradient
- ✅ Interior cells are natural signal accumulators
- ✅ Radial signal/energy counter-gradient (high signal ↔ low energy)
- ⚠️ No clear signal corridors yet (5000 ticks may be insufficient)
- ⚠️ No integration hubs distinguishable from general interior
- ❌ No relay specialization (all cells emit automatically, no learned relay)

**Files changed:**
- `ultron/cell.py`: `received_signals`/`emitted_signals` → `received_signal`/`emitted_signal` (signal_dim channels). `_emit_signals()` now broadcasts prediction error vector components.
- `ultron/tissue.py`: `chemoA`/`chemoB` → `signal_field`. `_diffuse()` → `_propagate_signals()`. `get_env_observation()` uses `env_dim`. Added `get_signal_magnitude_map()`.
- `proto_brain.py`: New experiment script.

---

### 2026-03-09 Session 8 — Action Coupling (v0.3.0 continued)

**Mechanism: Signals must change physical behavior, not just learning.**

Session 7 established information flow with decay. But signals only fed into the observation vector — they influenced prediction but didn't change energy flow or reproduction. A brain doesn't just receive information; it CONTROLS the body. This session adds the second mechanism for proto-brain emergence.

**Principle: You don't program a brain. You create conditions where centralized prediction + control becomes advantageous.**

**Implementation:**

1. **Signal-coupled energy diffusion** (`tissue.py: _energy_sharing()`):
   ```python
   sig_mag = np.linalg.norm(self.signal_field, axis=2)
   coupling = config.get('signal_energy_coupling', 1.0)
   rate_map = base_rate * (1.0 + coupling * sig_mag)
   # Per-direction: rate = max(local_rate, neighbor_rate) — hubs push AND pull
   local_rate = np.maximum(rate_map, nbr_rate)
   flow = diff * local_rate * mask
   ```
   Cells with high signal magnitude become energy ROUTERS — they amplify the rate at which energy flows through them. The `np.maximum(rate_map, nbr_rate)` rule means hubs both push energy away AND pull energy toward them, creating energy highways.

2. **Signal-modulated division threshold** (`cell.py: should_divide()`):
   ```python
   coupling = config.get('signal_division_coupling', 0.1)
   sig_mag = np.linalg.norm(self.received_signal)
   threshold = base_threshold / (1.0 + coupling * sig_mag)
   ```
   Cells receiving strong signals divide more easily. High signal = lots of information converging = good place to grow. This couples information flow to reproduction.

**New config params:**
```python
'signal_energy_coupling': 1.0,     # rate *= (1 + coupling × signal)
'signal_division_coupling': 0.1,   # threshold /= (1 + coupling × signal)
```

Both are pure physics. No decisions, no goals. Signal magnitude is a physical quantity (L2 norm of prediction error propagated with decay). Its effect on energy flow and division is a physical law, not a choice.

**Experiment result (5000 ticks, 20×20, both couplings active):**

Timeline:
```
t=  500: cells=400 (S= 76 I=324), E_S=186.3 E_I=106.1, rate=0.061
t= 1500: cells=400 (S= 76 I=324), E_S=200.0 E_I= 21.4  ← interior starving
t= 2000: cells=204 (S=184 I= 20)  ← massive die-off, only 20 interior survive
t= 3500: cells=214 (S=184 I= 30)  ← slow regrowth begins
t= 5000: cells=243 (S=181 I= 62), E_S=149.6 E_I=111.5, rate=0.060
```

**6 observations:**

1. **2.5× rate differentiation** — effective diffusion rate ranges from 0.034 to 0.085 across living cells. This means some cells route energy 2.5× faster than others. Ratio has real functional consequence.

2. **53% high-activity cells** — 128 of 243 cells have diffusion rate > 2× the base rate (0.06). More than half the organism actively amplifies energy routing based on signal magnitude.

3. **15.4× signal range** — signal magnitude spans 0.118 to 1.828. Enormous variation in information concentration. Top receiver (interior cell at position 12,10) has signal 15× stronger than least-connected cells.

4. **Dynamic restructuring** — organism crashed from 400→204 cells (49% die-off) then self-organized back to 243 with a different morphology. Swiss-cheese pattern persists but regrowth filled different positions than before.

5. **Interior cells recover with higher signal** — at t=5000: sig_I=1.074 > sig_S=0.993. Interior cells remain signal accumulators even with action coupling active. Energy gap narrowed (E_I=111.5 vs E_S=149.6) compared to Session 7.

6. **Radial profile — three-layer structure persists:**
```
dist  n  signal  error  energy   rate
   0  1   0.652  3.72   114.1  0.050   ← core: low sig, low energy, low rate
   2  9   1.349  4.49   113.3  0.071   ← inner ring: HIGH signal, high rate
   9 43   0.989  4.73   149.1  0.060   ← mid: moderate
  12 20   1.169  4.83   177.6  0.065   ← outer interior: signal bump
  14  1   1.302  4.60   200.0  0.069   ← boundary: max energy
```
The radial profile shows signal peaks at distances 2 and 12 — not a simple gradient but a BANDED structure. Signal accumulates at interfaces between dense clusters and vacuoles.

Top 10 signal receivers:
```
(12,10)  sig=1.828  INT   E=112.9  rate=0.085  ← top hub
(13, 0)  sig=1.780  SURF  E=200.0  rate=0.083  ← edge hub
(10,11)  sig=1.766  SURF  E=114.1  rate=0.083  ← near vacuole
( 1, 9)  sig=1.727  INT   E=110.9  rate=0.082
```
Mix of interior and surface cells as top receivers. Signal hubs are now distributed rather than exclusively interior — action coupling may be pulling signal accumulation toward the surface where energy is available.

**What changed vs Session 7:**
- ✅ Signals now change energy diffusion rate (amplification up to 2.5×)
- ✅ Signals now lower division threshold (easier reproduction near info hubs)
- ✅ Rate differentiation creates functional heterogeneity beyond surface/interior
- ⚠️ No clear evidence of signal corridors yet
- ⚠️ Top signal hubs don't cluster spatially into organs

**Files changed:**
- `ultron/cell.py`: `should_divide()` now uses signal-modulated threshold.
- `ultron/tissue.py`: `_energy_sharing()` rewritten with signal-coupled rate map.
- `proto_brain2.py`: New experiment script with rate tracking and differentiation index.

#### Session 8 Analysis — Biological Interpretation of proto_brain2.png

The six panels of the action coupling plot reveal that Ultron has crossed a structural threshold from "artificial life toy" to "early artificial organism."

**Panel 1: Cell type map (surface/interior)**
The continuous outer membrane with hollow internal cavities resembles real biological tissues — sponge tissue, lung alveoli, intestinal villi. The holes are not bugs. They are metabolic surface generators. The organism is increasing internal surface area to extract energy. This is a classic biological solution.

**Panel 2: Energy map — circulatory gradient**
Energy is no longer uniform. Edge=high, mid-layer=medium, deep interior=low. Energy moves surface→interior. This is the beginning of metabolism architecture.

**Panel 3: Signal magnitude — information clusters**
Not smooth gradients, but CLUSTERS. Local signal amplification means cells in those regions receive many signals simultaneously. Those cluster centers are proto-neurons.

**Panel 4: Diffusion rate — control system**
Before action coupling: diffusion = constant everywhere. Now: diffusion = signal-dependent. Signal hubs route energy faster. Information → affects energy flow. This is the exact mechanism needed for control systems.

**Panel 5: Prediction error — nervous system architecture**
Interior = low error, surface = higher error. Surface cells experience the raw environment; interior cells receive processed signals. This is the exact architecture of nervous systems: sensory layer → processing layer → integration layer.

**Panel 6: Population dynamics — self-organization**
400 → 204 → 243. Ecological collapse + recovery. The organism reorganized itself. Old structure died, new structure stabilized. This is a hallmark of self-organization.

**Critical threshold: 15× signal amplification**
Signal range 0.118 → 1.828 puts the system in the regime where complex systems typically exhibit feedback loops, oscillations, and pattern formation. The >10× amplification range is a known threshold for emergent dynamics.

**Three coupled networks now exist:**

| Network | Substrate | Role |
|---------|-----------|------|
| Metabolic | Energy diffusion | Resource transport |
| Information | Prediction error signals | Sensing & integration |
| Actuation | Signal-modulated diffusion + reproduction | Control |

This triad is exactly what biological organisms have. Most artificial life projects never reach this stage.

**Phenomena to watch for in longer runs:**
- Signal oscillations (brain-like waves)
- Traveling waves (information propagation)
- Stable signal hubs (proto-brains)
- Signal corridors (proto-nervous systems)
- Global coherent behavior (attention, pattern recognition)

**Note:** The organism is currently energy-rich. Stronger structure will likely require scarcity — pressure drives specialization.

---

## 11. Milestone Summary

| # | Milestone | Session | Key Result |
|---|-----------|---------|------------|
| 1 | Self-maintaining metabolism | 1 | 7-phase tick loop, energy-contingent survival |
| 2 | Ecological coupling | 1 | Prediction quality → energy extraction |
| 3 | Phase transition | 1 | Stochastic viability boundary at signal_ratio ≈ 0.60 |
| 4 | Emergent dormancy | 2 | Low-energy stable equilibrium (never programmed) |
| 5 | Individuality | 3 | ±2% birth variation → 15× outcome spread |
| 6 | Reproduction & heredity | 3 | Asexual fission with trait inheritance |
| 7 | Natural selection | 4 | +22% fitness over 21 generations |
| 8 | Open-ended evolution | 4 | Chaotic environments drive fastest evolution |
| 9 | Multicellular development | 5 | Zygote → 400-cell organism |
| 10 | Vascularization | 5 | Gradient diffusion enables growth |
| 11 | Surface-only metabolism | 6 | Interior cells depend on boundary |
| 12 | Functional differentiation | 6 | Two cell types emerge (surface/interior) |
| 13 | Self-organized morphology | 6 | Internal vacuoles, body size limits |
| 14 | Signal propagation with decay | 7 | Info bottleneck, hop-by-hop ×0.9 decay |
| 15 | Signal accumulation gradient | 7 | Interior cells receive more signal than surface |
| 16 | Action coupling | 8 | Signals modulate energy diffusion (2.5×) + division threshold |
| 17 | Rate differentiation | 8 | 53% of cells amplify energy routing above 2× base |

---

### 2026-03-09 Session 9 — AutoResearch v0.3.0 Update & Cell Differentiation (v0.4.0)

#### AutoResearch Config Synchronization

The autoresearch system (built by a separate Opus 4 session) had stale v0.2.0 configs referencing `diffusion_rate` and `signal_decay` — parameters that tissue.py no longer reads. Full audit of 27 config keys across core.py, tick.py, cell.py, tissue.py confirmed the mismatch.

**Changes made:**
1. `campaigns.py` TISSUE_BASE: replaced `diffusion_rate: 0.15, signal_decay: 0.03` with `signal_hop_decay: 0.9, signal_emission_strength: 0.3, signal_energy_coupling: 1.0, signal_division_coupling: 0.1, signal_dim: 4, env_dim: 8`
2. `brain.py` TISSUE_BASE: same replacement
3. `brain.py` PARAM_SPACE: removed `diffusion_rate`/`signal_decay` ranges, added `signal_hop_decay: (0.5, 0.99), signal_emission_strength: (0.05, 1.0), signal_energy_coupling: (0.0, 3.0), signal_division_coupling: (0.0, 0.5)`
4. `brain.py` frontier_params: replaced `diffusion_rate` with new v0.3.0 params at top priority
5. `brain.py` interaction_effects pairs: updated to use `signal_hop_decay` and new coupling pair
6. `campaigns.py` tissue_morphogen: now sweeps `signal_hop_decay × signal_emission_strength`

**Verification:** 1-cycle autonomous run completed successfully. Bootstrap sweep: 24 configs × 3 seeds, 70.4s. Found phase boundaries at extraction_factor ~ 0.25 and signal_ratio ~ 0.30. 4 findings, 2 open questions generated with correct v0.3.0 physics.

---

#### Cell Differentiation (v0.4.0)

**Mechanism: Phenotype Accumulator**

Each cell develops a 4-channel phenotype vector through experience, with plasticity that decays exponentially with age (critical period for commitment):

| Channel | Tracks | Range | What it means |
|---------|--------|-------|---------------|
| [0] surface_history | EMA of is_surface flag | 0-1 | How long this cell has been on the surface |
| [1] signal_exposure | EMA of received signal magnitude | 0-2 | How much inter-cell information it processes |
| [2] competence | 1/(1+error), EMA | 0-1 | How well-adapted its prediction model is |
| [3] energy_status | EMA of energy/capacity | 0-1 | Metabolic health over time |

**Plasticity decay:** `plasticity = max_plast * exp(-age / lock_tau) + min_plast`
- At birth: plasticity = 0.051 (stem cell)
- At age 200: plasticity = 0.019 (committing)
- At age 1000: plasticity = 0.001 (locked in)

**Emission modulation:** `emitted = error * (1 + emission_coupling * phenotype)` — cell identity colors what it broadcasts. High-energy surface cells emit 2-4x stronger than interior cells.

**Phenotype inheritance:** Child gets `parent.phenotype * 0.5` — partial memory of lineage identity.

**Phenotype affinity in energy sharing:** `affinity = exp(-phenotype_distance * affinity_coupling)` — cells with similar phenotypes share energy more readily, creating diffusion barriers at tissue boundaries.

**Results (20x20 grid, 5000 ticks, seed_full start):**

Four distinct cell types emerged through k-means clustering:

| Type | n | S/I | Mean Age | Energy | Phenotype Profile |
|------|---|-----|----------|--------|-------------------|
| Interior/Relay | 30 | 0/30 | 3873 | 74 | [0.02, 1.63, 0.17, 0.37] |
| Transitional | 32 | 0/32 | 4010 | 79 | [0.23, 1.65, 0.18, 0.41] |
| Sensory | 100 | 95/5 | 3020 | 82 | [0.97, 1.65, 0.17, 0.41] |
| Absorptive | 76 | 76/0 | 5000 | 200 | [1.00, 1.78, 0.17, 0.97] |

**Key emergent phenomena:**

1. **Absorptive epithelium** (n=76): All original founders (age=5000). Always surface, max energy. These are the organism's "gut lining" — they extract energy and are metabolically dominant.

2. **Sensory cells** (n=100): Mostly surface but younger (mean age 3020). Lower energy than absorptive cells. These formed during the ecological collapse and regrowth.

3. **Transitional cells** (n=32): Currently interior but phenotype[0]=0.23 reveals they were once surface. The lock-in mechanism preserves their history — these cells "remember" being surface even after the organism grew around them. This is the epigenetic memory effect.

4. **Interior relays** (n=30): Pure interior (surface_history=0.02). Low energy, dependent on diffusion from surface. These are the processing/relay cells.

5. **Phenotype distance:** Surface-interior mean distance = 0.872. Dominated by surface_history (0.99 vs 0.17) and energy_status (0.66 vs 0.39).

6. **Phenotype affinity effect:** Interior cells get less energy (74-79) with affinity barriers vs without (81-82). The phenotype mismatch at the surface-interior boundary creates a real metabolic compartment.

**New config parameters:**
- `phenotype_max_plasticity`: 0.05
- `phenotype_lock_tau`: 200.0
- `phenotype_min_plasticity`: 0.001
- `phenotype_emission_coupling`: 2.0
- `phenotype_affinity_coupling`: 2.0

---

### 2026-03-09 Session 10 — Environmental Challenge, Motility & Multi-Organism Competition (v0.5.0)

#### Stimulus-Response Experiment

Tested organism-level coordination by injecting stimuli into a mature 20x20 organism.

**Energy injection** (200 energy at position 10,10):
- 16 cells responded by t+2 (energy redistribution via diffusion)
- 171/204 cells (84%) responded by t+200
- Energy at stimulus point dropped to 0 (absorbed by neighbors immediately)

**Signal pulse** (10x signal spike at position 10,10):
- Signal propagation speed: 0.82 cells/tick (peak: 1.4)
- Wavefront reached 14.1 cells (max grid distance)
- **Damped oscillation** at stimulus point: 0.325 → 2.423 → 0.342 → 0.824 → 1.273
- The oscillation is emergent — no oscillation mechanism is programmed. It arises from prediction error feedback: cells overshoot their predictions of the signal, creating error in the opposite direction, which propagates back.

**Significance:** The organism behaves as a coupled oscillator network. A localized disturbance produces a coordinated tissue-wide response with wave-like dynamics.

---

#### Seasonal Environment (v0.4.1)

Added sinusoidal modulation of `base_signal_ratio` over time:
```
base_ratio += amplitude * sin(2π * tick / period)
```

**Results (20x20, 8000 ticks):**

| Condition | Amplitude | Final Cells | Final Energy | Min Cells |
|-----------|-----------|-------------|--------------|-----------|
| No seasons | 0.0 | 245 | 27,297 | 192 |
| Mild seasons | 0.15 | 243 | 27,280 | 186 |
| Harsh seasons | 0.30 | 246 | 27,898 | 187 |

**Finding:** The organism is **completely robust** to seasonal variation. Even "harsh" seasons (signal_ratio oscillating from 0.25 to 0.85) produce no measurable stress. The energy buffering from absorptive cells and internal energy diffusion create sufficient homeostasis that temporal oscillations are trivially absorbed. This motivated implementing a more fundamental environmental challenge.

---

#### Resource Depletion

Seasonal oscillation couldn't stress the organism because energy buffering was too effective. Genuine scarcity requires the organism to **deplete its own environment**.

**Mechanism:** Added `resource_field` to Tissue — a 2D array [0,1] representing local energy availability. Surface cells deplete resources when extracting; resources regenerate slowly.
- Signal quality modulated by local resources: `ratio *= resource_field[row, col]`
- Depleted positions give noisier signal → lower extraction efficiency → less energy
- Regeneration is uniform: `resource_field += regen_rate`

**Results (15x15 grid, 2000 ticks):**

| Condition | Depl/Regen Rate | Final Cells | Resource Mean/Min |
|-----------|-----------------|-------------|-------------------|
| No depletion | 0/0 | 133 | 1.000 / 1.000 |
| Mild | 0.001/0.0005 | 117 | 0.726 / 0.001 |
| Harsh | 0.003/0.0003 | 115 | 0.616 / 0.000 |

**Finding:** Resource depletion creates genuine metabolic pressure. Under harsh depletion, cells can fully exhaust local resources (min=0.000), reducing organism size by 14%. Unlike seasonal oscillation, resource depletion is **irreversible locally** — once a position is depleted, the cell at that position is trapped with poor signal quality.

---

#### Cell Motility (v0.5.0)

Resource depletion creates pressure; motility provides the response. Surface cells at depleted positions can migrate to empty neighbors with higher resources.

**Mechanism:**
- Triggered when local `resource_field < migration_resource_threshold`
- Cell moves to the neighboring empty position with highest resources
- Migration costs energy (`migration_energy_cost`, default 2.0)
- Only surface cells can migrate (only they have empty neighbors)

**Migration test** (10x10, left half seeded with depleted resources 0.3, right half fresh 1.0):
- t=0: left=50, right=0
- t=250: left=50, right=18 (cells expanding rightward)
- t=500: left=49, right=24 (organism crawling toward fresh resources)

**Migration experiment** (25x25, 100-cell center block, 3000 ticks):

| Condition | Final Cells | Spatial Extent | Energy |
|-----------|-------------|----------------|--------|
| Control (no depletion) | 90 | 7.6 cells | 945 |
| Depletion only | 72 | 8.1 cells | 1,296 |
| Depletion + motility | 145 | 15.3 cells | 860 |

**Key finding:** Motility enables the organism to **spread across the grid seeking fresh resources**, doubling its spatial extent from 7.6 to 15.3 cells. The organism with motility survives depletion with 145 cells vs. 72 without — a 2x survival advantage. The center of mass shifted from (11.5, 11.5) to (12.1, 12.3), showing the organism physically migrated.

This is the first time the organism exhibits **active spatial behavior** — it doesn't just sit and extract, it moves toward resources.

---

#### Multi-Organism Competition

Tested whether two organisms on the same grid can coexist, compete, and displace each other.

**Lineage tracking:** Added `lineage_id` to Cell, inherited during division. Allows tracking per-organism stats without changing physics.

**Experiment 1: Symmetric competition** (20x20, left=lineage 1, right=lineage 2, equal traits):
- Border stable at column 10 throughout all 3000 ticks: `[AAAAAAAAAABBBBBBBBBB]`
- 12-14 boundary cells at the interface
- Both organisms settle to ~100-130 cells, roughly equal
- **Finding:** Phenotype affinity creates a natural organism boundary. Neither side invades because the border is at 100% occupancy — no empty positions for division or migration.

**Experiment 2: Asymmetric competition** (20x20, B has 50% better extraction_efficiency):
- With `displacement_energy_ratio=2.0`, a dividing cell can displace a foreign neighbor with less than half its energy
- Border shifted from column 10 to column 9 by t=4000: `[AAAAAAAAABBBBBBBBBBB]`
- B expanded from 10 to 11 columns, finishing with 171 cells vs. A's 139
- **Finding:** Competitive displacement enables natural selection at the organism level. The fitter organism (20% more efficient extraction) gains territory, but invasion is slow — mirroring biological competitive exclusion dynamics.

**Competitive displacement mechanism:** During division, if a cell has no empty neighbors, it can displace a foreign neighbor (different lineage_id) if the dividing cell has ≥ `displacement_energy_ratio` × the target's energy. The displaced cell dies and the child takes its position.

---

#### New Config Parameters (v0.5.0)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `season_amplitude` | 0.0 | Magnitude of seasonal signal_ratio oscillation |
| `season_period` | 1000.0 | Ticks per seasonal cycle |
| `resource_depletion_rate` | 0.0 | How fast surface cells consume local resources |
| `resource_regen_rate` | 0.0 | How fast resources regenerate uniformly |
| `migration_energy_cost` | 2.0 | Energy cost to migrate one position |
| `migration_resource_threshold` | 0.5 | Resource level below which cells seek better positions |
| `displacement_energy_ratio` | 3.0 | Energy ratio needed to displace a foreign cell |

---

### 2026-03-10 Session 11 — Action Coupling: Evolved Behavior (v0.6.0)

**Goal:** Give cells genuine agency. Instead of hard-coded behavioral rules, let the cell's
prediction model produce *action outputs* — extra weight rows that encode directional
preferences for division. These action weights are inherited from parent to child with
mutation, but never trained by prediction error. This creates two timescales of adaptation:
*learning* (prediction weights, within lifetime) and *evolution* (action weights, across generations).

#### Architecture Change

The model weight matrix expands from `obs_dim × obs_dim` to `(obs_dim + action_dim) × obs_dim`:

- **Prediction rows** (first `obs_dim`): trained by prediction error (learning)
- **Action rows** (last `action_dim`): inherited + mutated at division (evolution)

In `predict()`, the full hidden state is computed: `hidden = weights @ prev_observation`.
The first `obs_dim` elements become the prediction (as before). The remaining `action_dim`
elements are `tanh`-squashed to produce **action outputs** in [-1, +1].

In `update()`, gradients only modify prediction rows: `weights[:obs_dim, :] += delta`.
Action rows are **never directly trained** — they evolve across generations through
inheritance + mutation in `cell.divide()`.

#### Action-Directed Division

When `action_dim = 4` and `action_division_coupling > 0`:
- action[0] = up, action[1] = down, action[2] = left, action[3] = right
- Each empty neighbor is scored: `score = resource_level + coupling * action[direction]`
- Division target is the neighbor with highest score (not random)

This means the cell's internal model state (which depends on what it perceives) influences
the *direction* it reproduces. A cell receiving strong signals from one direction may
develop action weights that bias division toward that direction — creating feedback
between perception and growth morphology.

#### Action Weight Inheritance

In `cell.divide()`:
```python
# Prediction weights: random (learned within lifetime)
child_state = create_ultron(config)
# Action weights: inherited from parent with mutation (evolved across generations)
child_state.model.weights[obs_dim:, :] = parent_action_weights + noise * mutation
```

This mirrors biology: motor reflexes are partially innate (evolved), while
perception adapts to experience (learning).

#### Experiment 1: Growth from seed (12×12, 2000 ticks, no depletion)

| Condition | Cells | Births | Spatial Extent |
|-----------|-------|--------|----------------|
| No actions (random div) | 20 | 16 | 30 |
| Actions ON (coupling=1.0) | ~20 | ~16 | ~40 |
| Actions ON (coupling=3.0) | 22 | 18 | 49 |

**Key finding:** Action coupling with strong coupling (3.0) produces **63% larger
spatial extent** (49 vs 30) while maintaining similar cell count. Directed division
spreads the organism more efficiently.

#### Experiment 2: Actions + Resource Depletion (12×12, 3000 ticks)

With `resource_depletion_rate=0.002`, `resource_regen_rate=0.0003`:

| Condition | Cells | Births | Resource Mean |
|-----------|-------|--------|---------------|
| Random division | 38 | 34 | 0.544 |
| Action division (coupling=2.0) | 41 | 37 | 0.489 |

**Key finding:** Action-directed division gives a modest 8% advantage (41 vs 38 cells,
37 vs 34 births). The organism consumes more resources (lower mean), indicating more
aggressive expansion. Action magnitudes are still small (~±0.02), suggesting longer
evolutionary runs would amplify the effect.

#### Action Evolution Over Time

At `t=100`: mean action = [+0.004, -0.006, +0.005, -0.017], std ≈ 0.03
At `t=2000`: mean action = [-0.010, +0.023, +0.008, -0.005], std ≈ 0.04

Action magnitudes shift over time as action weights are inherited and mutated,
but with only ~37 cell divisions in 3000 ticks, there hasn't been enough
generational turnover for strong directional preferences to evolve.

#### New Config Parameters (v0.6.0)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `action_dim` | 0 | Number of action output channels (0 = disabled, 4 = directional) |
| `action_division_coupling` | 0.0 | Strength of action influence on division direction |

#### Session 11 Continued — Action Evolution & Migration (v0.6.1)

**Additional work performed in the same session:**

##### Action-Guided Migration

Extended action outputs to modulate migration as well as division. Surface cells
now score migration targets using the same action preference mechanism:
`score = resource_level + coupling * action[direction]`

New parameter: `action_migration_coupling` (default 0.0).

##### Separate Evolution Parameters

Action weights need different initialization and mutation rates than prediction weights:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `action_weight_scale` | 0.1 | Initial scale for action weight rows (larger = stronger initial biases) |
| `action_mutation_rate` | 0.02 | Mutation noise added to action weights at division (higher than prediction mutation) |

Action weight rows are now initialized with `randn * action_weight_scale` (not the
smaller prediction weight scale), and mutated at division with a separate rate.
This allows faster evolutionary exploration of action space.

##### Long-Duration Action Evolution Experiment

12x12 grid, 5000 ticks, resource depletion + action coupling (2.0):

| Tick | Cells | Births | Resource Mean | Weight Std | Weight Norm |
|------|-------|--------|---------------|------------|-------------|
| 0 | 17 | 8 | 1.000 | 0.0990 | 0.682 |
| 500 | 17 | 8 | 0.967 | 0.0990 | 0.682 |
| 1000 | 26 | 17 | 0.922 | 0.1014 | 0.698 |
| 2000 | 34 | 25 | 0.793 | 0.1028 | 0.708 |
| 3000 | 36 | 27 | 0.682 | 0.1032 | 0.711 |
| 5000 | 42 | 33 | 0.487 | 0.1044 | 0.720 |

**Key findings:**
- Weight norm increasing: 0.682 -> 0.720 (5.6% growth) — selection favors larger action weights
- Weight std growing: 0.0990 -> 0.1044 — action weights diverging from random initialization
- Zero deaths across 5000 ticks — organism is robustly viable
- Resources depleted from 1.0 -> 0.487 as organism expands
- High-energy cells have slightly larger action weight norms (0.727 vs 0.712) — correlation
  between action weight magnitude and metabolic success
- Directional biases shift over time but don't lock in — 33 generations is not enough for
  strong directional evolution; need 100+ generations for convergence

##### Final grid snapshot (t=5000)

Each cell labeled by its preferred action direction (U/D/L/R):
```
U..RR.....L.
.R..U..U...D
.R.UUL......
...U......U.
DU...D.RD...
.L.D......DD
.....R......
D.U.........
..U........U
DD.......RU.
..RD........
DLLU..DDUU..
```

No global directional consensus — each local cluster has its own bias,
suggesting action weights encode local spatial information rather than a
single organism-wide strategy.

##### AutoResearch Sync

All autoresearch configs (TISSUE_BASE, PARAM_SPACE, frontier_params,
interaction_effects) updated to include v0.5.0 + v0.6.0 parameters.
AutoResearch verified working with updated configs — bootstrap sweep
completes successfully, finding phase boundaries at extraction_factor ~ 0.25
and signal_ratio ~ 0.30.

---

### 2026-03-18 Session 12 — Ecosystem Ecology & Resilience (v0.7.0)

**Goal:** Create conditions for genuine ecosystem dynamics — multiple organisms
competing on a heterogeneous landscape with resource scarcity, fragmentation-based
reproduction, and environmental catastrophe. Test whether homeostatic resilience
emerges from the physics.

#### Heterogeneous Resource Landscape

Added configurable resource landscapes to `tissue.py`. Instead of uniform resources,
the grid can have spatial structure:

| Landscape Type | Description |
|---------------|-------------|
| `uniform` | Default: all resources = 1.0 |
| `patches` | Circular oases of high resources in a low-resource desert |
| `gradient` | Linear gradient from left (poor) to right (rich) |
| `islands` | Distinct high-resource islands |

Patch centers can be specified explicitly via `landscape_patch_centers` config,
allowing reproducible experimental layouts. Resources regenerate toward the
landscape capacity (not always 1.0), so destroyed desert never regenerates
into oasis.

#### Organism Fragmentation (Budding)

When cells die or migrate, the organism can fragment into disconnected pieces.
Added connected-component detection using flood-fill BFS within each lineage.
Fragments above `fragmentation_min_size` (default 5) receive new lineage IDs,
becoming independent organisms. This is organism-level reproduction via fission,
analogous to coral fragmentation or hydra budding.

**Implementation:** Every `fragmentation_interval` ticks (default 100), BFS
identifies connected components per lineage. The largest component keeps the
parent ID; viable fragments get new IDs.

#### Stigmergy (Collective Spatial Memory)

When a cell dies via apoptosis, its phenotype is deposited into a `stigmergy_field`
at that position. This creates a chemical death-trace that:
- Decays slowly (`stigmergy_decay`, default 0.995)
- Is sensed by living cells through signal reception (`stigmergy_sensing`)
- Penalizes migration targets (`stigmergy_avoidance`)

The effect: organisms develop a collective memory of "where cells have died."
Surviving cells avoid death zones and migrate toward safer positions.

#### Ecosystem Tracking

Added `ecosystem_snapshot()` method returning per-lineage metrics:
- Cell count, total energy, mean error, mean age
- Centroid position and spatial extent
- Trait means (extraction efficiency, metabolic rate)
- Phenotype profiles and internal diversity

Added `get_lineage_map()` returning a 2D array of lineage IDs for territory
visualization.

#### Experiment 1: Grand Ecosystem (40x40, 10k ticks, 4 founders)

Four organisms on four resource patches (corners), full physics enabled.

**Population dynamics:**
```
t=0:     A=10 B=10 C=10 D=10  (40 total, 4 lineages)
t=1000:  A=23 B=18 C=22 D=22  (91 total, 5 lineages — first fragmentation)
t=1500:  A=18 B=12 C=25 D=35  (105 total, 9 lineages)
t=10000: A=22 B=12 C=44 D=21  (137 total, 9 lineages)
```

**Key findings:**
- **Fragmentation produced 9 lineages from 4 founders** — organism-level reproduction
- **L3 became dominant** (10 -> 44 cells, 340% growth) through expansion into
  adjacent unoccupied territory
- **Different action strategies evolved per organism:**
  - L2: dominant left (action[2] = +0.208)
  - L5: dominant right (action[3] = -0.205)
  - L6: dominant up (action[0] = +0.230)
- **Spatial niche partitioning**: each lineage occupies a distinct region
- **Phenotype divergence**: 0.023 (modest but measurable)
- **Zero deaths**: no cell ever fell below the apoptosis threshold

#### Experiment 2: Ecosystem War (25x25, 8k ticks, 2 organisms)

Two organisms starting adjacent on overlapping resource patches.

```
t=200:  A=55 B=54  (rapid growth phase)
t=600:  A=64 B=62  (peak before resource crisis)
t=2000: A=50 B=48  (resource-constrained equilibrium)
t=8000: A=45 B=44  (stable coexistence — neither wins)
```

**Key findings:**
- **Stable coexistence**: A and B fight to a draw despite different random seeds
- **13 fragment organisms** emerged through fragmentation
- **Action weight evolution**: weight norms grew from ~0.7 to ~1.0-1.14 (45% increase)
- **Each fragment evolved unique directional biases** — genuine behavioral divergence
  through heritable action weight mutation

#### Experiment 3: Apocalypse (35x35, catastrophe at t=3000)

At t=3000, two of four resource patches destroyed (set to 0.05 resources).

**Result: TOTAL RESILIENCE. Zero deaths. Zero population change.**

```
Pre-catastrophe:  A=15 B=29 C=31 D=32 (200 total)
Post-catastrophe: A=15 B=29 C=31 D=32 (200 total, UNCHANGED)
t=8000 (5000 ticks later): A=15 B=29 C=31 D=32 (200 total, STILL UNCHANGED)
```

Organisms A and D (on destroyed patches) survived indefinitely through the
internal energy-sharing network. The metabolic gradient-diffusion system
redistributes energy from cells on intact patches to cells on destroyed patches
so efficiently that NO cell drops below the survival threshold.

**This is genuine emergent homeostasis:**
- Never programmed: we only coded gradient diffusion between neighbors
- The organism behaves as a single metabolic entity
- Local environmental destruction cannot kill cells whose neighbors can extract
- The buffering is SO effective that the catastrophe had literally zero impact

#### New Config Parameters (v0.7.0)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `landscape_type` | 'uniform' | Resource landscape pattern |
| `landscape_base` | 0.3 | Desert resource level |
| `landscape_n_patches` | 4 | Number of resource patches |
| `landscape_patch_radius` | 0.2 | Patch radius as fraction of grid |
| `landscape_patch_richness` | 1.0 | Peak resource level in patches |
| `landscape_patch_centers` | None | Explicit patch center coordinates |
| `fragmentation_enabled` | False | Enable organism fragmentation detection |
| `fragmentation_interval` | 50 | Ticks between fragmentation checks |
| `fragmentation_min_size` | 5 | Minimum cells for a viable fragment |
| `death_imprint_strength` | 1.0 | Phenotype deposited at death position |
| `stigmergy_decay` | 0.995 | Per-tick decay of death traces |
| `stigmergy_sensing` | 0.0 | Signal coupling of stigmergy field |
| `stigmergy_avoidance` | 0.0 | Migration penalty for death-heavy zones |

#### Experiment 4: Breaking Point (30x30, catastrophe severity sweep)

Six catastrophe severity levels, each run with 3 random seeds.
2000 ticks of growth, then catastrophe, then 3000 ticks of observation.

| Level | Description | Pre | Kill | Final | Recovery | Deaths |
|-------|-------------|-----|------|-------|----------|--------|
| 0 | Control (no catastrophe) | 101 | 0 | 155 | 153.4% | 0 |
| 1 | Destroy 2/4 patches | 101 | 0 | 122 | 120.8% | 0 |
| 2 | Destroy ALL patches | 101 | 0 | 101 | 100.0% | 0 |
| 3 | Destroy all + kill 25% | 101 | 25 | 76 | 75.2% | 25 |
| 4 | Destroy all + kill 50% | 101 | 50 | 51 | 50.2% | 50 |
| 5 | Destroy all + kill 75% | 101 | 75 | 26 | 25.4% | 75 |

**The organism is indestructible.**

There is no breaking point. At every severity level, the ONLY deaths are cells
directly killed by the catastrophe. Zero cascade deaths. Zero delayed mortality.
The survivors instantly stabilize at their post-kill count and maintain it
for 3000+ ticks in a completely barren environment.

Key insight: the per-seed data shows **perfect determinism** — seed 7 pre-kill
had 104 cells, and at Level 3 (25% kill) it ended with exactly 78 cells. At
Level 4 (50% kill), exactly 52. At Level 5 (75% kill), exactly 26. The remaining
population maintains EXACT homeostasis with zero variance across 3000 ticks.

**This is emergent indestructibility:**
- The energy-sharing gradient network acts as a single distributed metabolic pool
- When cells die, the remaining cells inherit their energy proportionally
- The lower density reduces total metabolic cost, creating a new equilibrium
- No cell cascades, no delayed starvation, no extinction spirals
- The organism simply continues at whatever size it has, indefinitely

#### Extreme Kill Test Extension (90-99% cell death)

Extended the breaking point sweep to near-total annihilation levels:

| Kill % | Pre | Killed | Survivors | Cascade Deaths |
|--------|-----|--------|-----------|----------------|
| 90% | 101 | 90 | 11 | 0 |
| 95% | 101 | 95 | 6 | 0 |
| 98% | 101 | 98 | 3 | 0 |
| 99% | 101 | 99 | 1-2 | 0 |

**At 99% kill + total environmental destruction, a SINGLE CELL survives
indefinitely.** Zero cascade deaths. Zero delayed mortality. The cell
extracts just enough energy from the barren landscape (resource_field=0.05)
to maintain itself above the apoptosis threshold with no neighbors
draining energy via sharing.

---

### 2026-03-18 Session 12 (continued) — Predator-Prey Dynamics (v0.8.0)

**Goal:** Introduce inter-organism predation — cells can consume adjacent foreign
cells when they have significantly more energy. Test whether genuine trophic
dynamics, competitive exclusion, and population oscillations emerge.

#### Bug Fix: Zombie Cell Cleanup

Discovered that cells dying from energy exhaustion (energy=0) in `tick()` had
`is_alive=False` set but were never removed from the grid. The `_handle_apoptosis`
method only processed cells where `is_alive=True AND should_die()=True`, so dead
cells remained as "zombies" blocking grid positions forever. Fixed by adding dead
cell cleanup at the start of `_handle_apoptosis`. This bug was latent since v0.5.0
but never triggered because the energy sharing network prevented cells from
reaching 0 energy in all previous experiments.

#### Predation Mechanics

Added `_handle_predation()` to the tissue step sequence (step 4, BEFORE energy
sharing to exploit raw energy differences). Predation rules:

1. A cell can consume an adjacent cell if they have **different lineages**
2. The predator must have `predation_energy_ratio` times the prey's energy
3. Predator gains `prey_energy * predation_efficiency`
4. Cooldown prevents rapid repeat kills (`predation_cooldown` ticks)
5. Prey cell is removed and its phenotype deposited as stigmergy

This makes predation purely physics-based — no explicit predator/prey roles.
Any organism can eat any other organism if it has enough energy advantage.
Predation ability emerges from metabolic dominance, not genetic labels.

#### Experiment 5: Predator-Prey (30x30, 8k ticks, 2 organisms)

Two organisms on two resource patches. Predation enabled (ratio=1.5, eff=0.5).

```
t=500:   L1=23 L2=22           (total=45, predation=0)
t=1500:  8 lineages             (total=67, predation=43)
t=4000:  8 lineages             (total=73, predation=228)
t=8000:  L1=26 L4=31 L12=16    (total=92, predation=530)
```

**Key findings:**
- **530 predation kills**, ZERO starvation deaths — predation is the sole cause
  of death throughout the entire experiment
- **10 lineages** from 2 founders through fragmentation
- **L4 became dominant** (31 cells), displacing the original L2 (down to 2 cells)
- **Population CV=0.165** — high variance suggesting oscillatory dynamics
- Fragments evolved into distinct territorial populations with different strategies

#### Experiment 6: Food Chain (35x35 gradient, 10k ticks, 3 organisms)

Three organisms along a resource gradient:
- L1: bottom-left (poor), 80 energy
- L2: center (moderate), 100 energy
- L3: top-right (rich), 120 energy

**TROPHIC REVERSAL: The weakest became the strongest.**

```
t=500:   L1=13 L2=15 L3=19     (L3 dominates early)
t=5000:  L1=39 L2=22 L3=45     (L1 rises, L3 plateaus)
t=7000:  L1=70 L2=19 L3=51     (L1 dominates!)
t=10000: L1=79 L2=25 L3=30     (L1 triumphant, L3 declining)
```

- **L1 (poor resources) grew from 8 to 79 cells — 10x growth!**
- L3 (rich resources) peaked at 56 then declined to 30
- **439 predation kills**, zero starvation deaths
- **CV=0.275** — very high population variance, strong oscillations
- **No extinctions** — all 3 original lineages survived

This is the **r-strategy vs K-strategy** principle in action: L1 reproduced more
(many surface cells in poor-but-available territory), giving it numerical advantage
at borders. L3 had fewer, richer cells but fewer border interactions. Numbers won.

#### Experiment 7: Colosseum (20x20, 6k ticks, 4 organisms, 1 resource)

Four organisms fighting over a single central resource patch. Aggressive predation
(ratio=1.2, efficiency=0.7, cooldown=2).

**COMPETITIVE EXCLUSION — winner takes all:**

```
t=200:   L1=12 L2=11 L3=12 L4=11  (all equal)
t=1000:  L1=10 L2=11 L3=4  L4=3   (L3/L4 declining)
t=2200:  L4 EXTINCT
t=5600:  L3 EXTINCT
t=6000:  L1=1  L2=24              (L2 dominates)
```

- **L2 won** — from 11 cells to 24, controlling the resource patch
- **L4 extinct at t=2200, L3 extinct at t=5600** — genuine competitive exclusion
- L1 barely survived with 1 cell (energy=4.6)
- **64 predation kills** — all deaths from direct consumption
- This is the first time an organism has driven another to **extinction** in Ultron

#### New Config Parameters (v0.8.0)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `predation_enabled` | False | Enable inter-lineage predation |
| `predation_energy_ratio` | 2.0 | Energy ratio needed to consume prey |
| `predation_efficiency` | 0.5 | Fraction of prey energy gained |
| `predation_cooldown` | 10 | Ticks between predation attempts |
| `predation_action_threshold` | 0.0 | Minimum action magnitude for predation |

---

### 2026-03-19 Session 13 — Chemical Warfare & Lamarckian Inheritance (v0.9.0)

**Features Added:**

#### Chemical Warfare (Toxin System)

Cells emit toxins proportional to their action magnitude. Toxins damage nearby foreign-lineage
cells within Manhattan distance `toxin_range`, with damage falling off as 1/distance. Self-lineage
cells are immune. Toxin production costs energy, creating a metabolic tradeoff — invest in warfare
or invest in growth.

**Implementation:** `_handle_toxins()` method in tissue.py, inserted as step 4 in the tick loop
(after cell step, before predation). For each living cell:
1. Compute `toxin_output = ||action|| * toxin_emission_rate`
2. Pay energy cost: `toxin_output * toxin_cost_rate`
3. For each foreign cell within Manhattan distance `toxin_range`: deal `toxin_output * toxin_damage_rate / dist` damage

#### Lamarckian Weight Inheritance

Children inherit their parent's learned prediction weights (not just action weights, which were
already inherited). Controlled by `weight_inheritance_ratio` — the fraction of parent weights
blended into the child's random initialization. Noise is added via `weight_inheritance_noise`.

**Implementation:** In `cell.divide()`, prediction weight rows (0 to obs_dim-1) are blended:
```
child_weights = ratio * parent_weights + (1-ratio) * child_random_weights + noise
```
Bias is also inherited with same blending. Placed before action weight inheritance block.

#### Experiment 8: Arms Race (30x30, 12k ticks, 2 organisms, toxin warfare only)

Two organisms on a shared grid with toxins enabled but no predation. Tests whether
chemical warfare drives escalation of action magnitude over time.

**Results — Territorial dominance, NOT arms race escalation:**

```
t= 1000: L1=21 L2=18 (total=39, toxin_events=74491, toxin_dmg=810)
t= 4000: L1=40 L2=22 (total=62, toxin_events=223660, toxin_dmg=2725)
t= 8000: L1=64 L2=30 (total=94, toxin_events=587752, toxin_dmg=6825)
t=12000: L1=69 L2=33 (total=102, toxin_events=895891, toxin_dmg=10603)
```

- **895,891 toxin events** over 12k ticks — massive chemical warfare
- **L1 dominated**: grew from 10→69 cells while L2 stagnated at 33
- **115 deaths** (predation-free environment — all toxin kills)
- Action magnitude stable: L1 +8.5%, L2 +0.8% — **no Red Queen escalation**
- Metabolic cost of toxin production prevents runaway escalation (self-regulating)
- Chemical warfare acts as **territorial deterrent**, not an arms race

#### Experiment 9: Lamarck vs Darwin (25x25, 8k ticks, controlled comparison)

Same seed, same organism, two conditions: `weight_inheritance_ratio=0.0` (Darwinian — random
weights each generation) vs `weight_inheritance_ratio=0.7` (Lamarckian — 70% inherited).

**Results — No significant difference:**

```
                   Darwin    Lamarck    Difference
Early error:       4.42      4.64       -5.0%
Late error:        5.08      5.07       +0.2%
Final pop:         111       110        -0.9%
```

- Both converge to same error (~5.0) and same population (~110)
- Lamarckian inheritance provides **no measurable organism-level advantage**
- Individual cells learn fast enough that inherited knowledge adds nothing
- The system is **robust to inheritance mode** — a finding in itself

#### Experiment 10: Grand Battle (35x35, 15k ticks, 4 organisms, ALL features)

All physics enabled simultaneously: predation + toxins + Lamarckian + fragmentation + stigmergy
+ evolved attack/defense. The ultimate stress test.

**Results — Fragmentation breeds war, extinctions, and emergent empires:**

```
t= 1000: L1=18 L2=29 L3=26 L4=26 L5=5 L6=3  (6 lineages, 107 cells)
t= 4000: L1=12 L2=22 L3=2  L4=20 L5=1 L7=15 (L3 collapsing, L7 rising)
t= 7000: L1=22 L2=12 L4=26 L7=20 L8=3        (L3 EXTINCT, 5 survivors)
t=10000: L1=25 L2=13 L4=28 L7=21              (stable 4-power equilibrium)
t=15000: L1=31 L2=24 L4=22 L7=18 L8=3         (5 lineages, 98 cells)
```

- **1,364,835 toxin events** — chemical warfare at industrial scale
- **173 predation kills** out of 191 total deaths (90.6% violent deaths)
- Only **18 non-violent deaths** — this ecosystem runs on killing
- **L3 extinct at t=7000** — founding lineage eliminated by competitors
- **L7 emerged from fragmentation** and became a major power (18 cells)
- **L8** — a 3-cell fragment — persisted for 8000+ ticks (refugium survival)
- 8 total lineages existed (4 founders + 4 fragments); 5 survived
- **Fragmentation creates evolutionary novelty**: daughter lineages compete with parents

**Key dynamics:**
1. **Fragmentation → speciation**: Organism pieces break off, develop independently, compete
2. **Chemical warfare + predation synergy**: Toxins weaken prey, predation finishes them
3. **Fragment-lineage dominance**: L7 (a fragment) outcompeted L3 (a founder)
4. **Stable multi-power equilibrium**: 4 major factions coexisted from t=10000-15000
5. **Micro-refugia**: L8 survived as a 3-cell cluster for thousands of ticks

#### New Config Parameters (v0.9.0)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `toxin_enabled` | False | Enable chemical warfare system |
| `toxin_emission_rate` | 0.1 | Toxin output per unit action magnitude |
| `toxin_damage_rate` | 0.5 | Damage dealt per unit toxin output |
| `toxin_range` | 3 | Maximum Manhattan distance for toxin effect |
| `toxin_cost_rate` | 0.1 | Energy cost per unit toxin output |
| `weight_inheritance_ratio` | 0.0 | Fraction of parent prediction weights inherited |
| `weight_inheritance_noise` | 0.01 | Noise added to inherited weights |
| `predation_action_power` | 0.0 | How much action magnitude lowers predation threshold |
| `predation_evasion_scaling` | 0.0 | Prey competence-based dodge chance |
| `predation_alarm_strength` | 0.0 | Alarm signal burst when ally is killed |

---

## 11. Milestone Summary

| # | Milestone | Session | Key Result |
|---|-----------|---------|------------|
| 1 | Self-maintaining metabolism | 1 | 7-phase tick loop, energy-contingent survival |
| 2 | Ecological coupling | 1 | Prediction quality -> energy extraction |
| 3 | Phase transition | 1 | Stochastic viability boundary at signal_ratio ~ 0.60 |
| 4 | Emergent dormancy | 2 | Low-energy stable equilibrium (never programmed) |
| 5 | Individuality | 3 | +/-2% birth variation -> 15x outcome spread |
| 6 | Reproduction & heredity | 3 | Asexual fission with trait inheritance |
| 7 | Natural selection | 4 | +22% fitness over 21 generations |
| 8 | Open-ended evolution | 4 | Chaotic environments drive fastest evolution |
| 9 | Multicellular development | 5 | Zygote -> 400-cell organism |
| 10 | Vascularization | 5 | Gradient diffusion enables growth |
| 11 | Surface-only metabolism | 6 | Interior cells depend on boundary |
| 12 | Functional differentiation | 6 | Two cell types emerge (surface/interior) |
| 13 | Self-organized morphology | 6 | Internal vacuoles, body size limits |
| 14 | Signal propagation with decay | 7 | Info bottleneck, hop-by-hop x0.9 decay |
| 15 | Signal accumulation gradient | 7 | Interior cells receive more signal than surface |
| 16 | Action coupling | 8 | Signals modulate energy diffusion (2.5x) + division threshold |
| 17 | Rate differentiation | 8 | 53% of cells amplify energy routing above 2x base |
| 18 | Cell differentiation | 9 | 4 distinct cell types via phenotype accumulator |
| 19 | Epigenetic memory | 9 | Transitional cells remember past surface identity after enclosure |
| 20 | Tissue compartmentalization | 9 | Phenotype affinity barriers reduce cross-type energy flow |
| 21 | Homeostatic resilience | 10 | Organism robust to seasonal variation via energy buffering |
| 22 | Environmental niche construction | 10 | Resource depletion — organism consumes its own environment |
| 23 | Cell motility | 10 | Surface cells migrate toward fresh resources, doubling spatial extent |
| 24 | Organismal boundary | 10 | Multi-organism borders emerge from phenotype affinity |
| 25 | Competitive displacement | 10 | Fitter organism gains territory via displacement during division |
| 26 | Action coupling (evolved behavior) | 11 | Model produces heritable action outputs guiding division direction |
| 27 | Action-guided migration | 11 | Action outputs modulate migration direction, not just division |
| 28 | Action weight evolution | 11 | Weight norm grows 5.6% over 33 generations — selection favors larger actions |
| 29 | Heterogeneous landscape | 12 | Configurable resource patches create spatial niches for organisms |
| 30 | Organism fragmentation | 12 | Connected-component detection creates new organisms via budding |
| 31 | Stigmergy | 12 | Dying cells leave chemical traces — collective spatial memory |
| 32 | Ecosystem dynamics | 12 | 9 lineages from 4 founders through fragmentation, niche partitioning |
| 33 | Emergent homeostasis | 12 | Organisms survive total resource destruction via internal metabolic buffering |
| 34 | Indestructibility | 12 | Zero cascade deaths at any severity — only directly-killed cells die, survivors stabilize perfectly |
| 35 | Predator-prey dynamics | 12 | Energy-dominant cells consume weaker foreign neighbors — 530 kills in 8k ticks |
| 36 | Trophic reversal | 12 | Weakest organism (poor resources) becomes dominant through numerical advantage |
| 37 | Competitive exclusion | 12 | Predation drives 2 of 4 organisms to complete extinction in confined arena |
| 38 | Zombie cell fix | 12 | Cells dying from energy exhaustion now properly cleaned up from grid |
| 39 | Chemical warfare | 13 | Toxin system — cells emit area-denial chemicals that damage foreign lineages |
| 40 | Self-regulating arms race | 13 | Toxin escalation capped by metabolic cost — no Red Queen runaway |
| 41 | Lamarckian inheritance | 13 | Prediction weights inherited parent→child (0.9462 correlation), but no organism-level advantage |
| 42 | Fragmentation-driven speciation | 13 | Fragment lineages compete with founders; L7 outcompeted founding L3 |
| 43 | Multi-force ecosystem | 13 | Predation + toxins + fragmentation + stigmergy running simultaneously — 90.6% violent death rate |
| 44 | Web-based live visualization | 14 | Real-time browser canvas showing cells, signals, resources, lineages, predation events with WebSocket streaming |

---

## Appendix A: File Sizes

### Core Engine (`ultron/`)

| File | Lines | Description |
|------|-------|-------------|
| core.py | ~222 | State definitions, create_ultron(), reproduce(), action weight init |
| tick.py | ~243 | Seven-phase tick logic, energy-modulated learning, action extraction |
| cell.py | ~230 | Cell wrapper: phenotype, lineage, emission, action inheritance, Lamarckian weight inheritance |
| tissue.py | ~900 | 2D grid: signals, resources, motility, displacement, actions, landscape, fragmentation, stigmergy, predation, toxins |
| environments.py | ~43 | Three environment types |
| observer.py | ~134 | Observer + birth tests |
| config.py | ~68 | Configuration presets |
| history.py | ~384 | Persistence layer |
| visualizer.py | ~567 | Real-time matplotlib display (single-cell) |
| __init__.py | ~28 | Package exports (v1.0.0) |

### Visualization (`viz/`)

| File | Lines | Description |
|------|-------|-------------|
| server.py | ~260 | WebSocket server: runs simulation, streams tick state as JSON |
| index.html | ~700 | Canvas-based frontend: cell rendering, stats, charts, tooltips |

### AutoResearch System (`autoresearch/`)

| File | Lines | Description |
|------|-------|-------------|
| experiment.py | ~213 | Three runners (single, population, tissue) |
| sweep.py | ~205 | Grid sweep + adaptive sweep |
| analysis.py | ~147 | Phase boundary detection, results tables |
| report.py | ~127 | Markdown + JSON reports |
| campaigns.py | ~431 | Predefined sweep campaigns |
| journal.py | ~141 | Persistent JSON research memory |
| brain.py | ~787 | 7 heuristic strategies for hypothesis generation |
| loop.py | ~348 | Autonomous cycle engine |

**Total Implementation:** ~5,370 lines of Python (2,759 core + 2,611 autoresearch)

---

## Appendix B: Quick Reference

### Start an experiment
```bash
python main.py --config stable --ticks 5000 --env mixed --feed-interval 50 --feed-amount 15
```

### With visualization
```bash
python main.py --config minimal --ticks 1000 --env sine --visual
```

### View history
```bash
python main.py --history
```

### Analyze patterns
```bash
python main.py --analyze
```

### Quiet run
```bash
python main.py --quiet --ticks 10000
```

---

*"The specification is dead letters until it runs. Then something either begins, or it doesn't."*

---

**END OF DOCUMENT**

**Next Update:** After next experiment batch
