# Ultron Robustness Analysis

**Date:** 2026-02-25  
**Status:** Experiment 3 Complete  
**Focus:** Characterizing the ~0.85-0.90 viability boundary

---

## EXPERIMENT 3 RESULT: CAUSAL ABLATION

### Configuration Change
```
update_cost_factor: 0.02 → 0.0
```

### Result: BOUNDARY DISAPPEARED

| Signal Ratio | With Cost (0.02) | Without Cost (0.0) |
|--------------|------------------|---------------------|
| 1.0 | ALIVE (+0.04) | ALIVE (+0.04) |
| 0.9 | ALIVE | ALIVE |
| 0.8 | **DEAD** | ALIVE |
| 0.7 | DEAD | ALIVE |
| 0.5 | DEAD | ALIVE |
| 0.0 | **DEAD** | **ALIVE (+0.05)** |

### Diagnosis

> **In this organism, death is primarily caused by desperate effort in the face of uncertainty.**

**Note:** This result was based on a 20x accounting bug (charging gradient norm instead of weight change). After fixing:
- All environments became viable
- Organism became a generalist
- No phase transition existed

---

## EXPERIMENT 4: METABOLIC BUG FIX

### Bug Discovered

The `metabolize` function was charging energy based on **gradient norm** (~8.0) instead of **actual weight change** (~0.4):

```python
# Bug: cost based on raw gradient
update_magnitude = np.linalg.norm(state.current.update_direction.flatten())
# update_direction was gradient, not learning_rate × gradient
```

This overcharged the organism **20x** for updates.

### Fix Applied

Changed `update_direction` to store actual weight delta:
```python
weight_delta = learning_rate * gradient.T
state.current.update_direction = weight_delta
```

### Result: Generalist Organism

After fix with extraction_factor = 0.6:
- ALL environments viable (+0.04 to +0.05 net/tick)
- No phase transition
- Organism differentiates internally but survives everywhere

---

## EXPERIMENT 5: MARGINAL SCARCITY

### Rationale

> **Without scarcity, nothing can ever truly begin.** 
> Life does not begin when a system can survive. Life begins when it can fail.

### Method

Lowered `extraction_factor` gradually: 0.6 → 0.5 → 0.4 → 0.35 → 0.30

### Result: Real Phase Transition at extraction_factor = 0.30

| Signal Ratio | Survival (20 seeds) | Mean Death Tick | Final Energy |
|--------------|---------------------|-----------------|--------------|
| 0.65 | **20/20 (100%)** | 15000+ | 47.6 |
| 0.60 | **8/20 (40%)** | 14696±355 | 2.6 |
| 0.55 | 0/20 (0%) | 11180±489 | 0 |
| 0.50 | 0/20 (0%) | 9555±297 | 0 |
| 0.00 | 0/20 (0%) | 7723 | 0 |

### Interpretation

This is the target pattern:
- ✅ **Order survives long-term** (energy at capacity)
- ✅ **Chaos dies slowly** (7700-9500 ticks, not instantly)
- ✅ **Boundary is stochastic** (0.60 = 40% survival by luck)

**The boundary is fuzzy, not sharp.** Identical organisms with identical parameters have different fates.

This is **individual variability** — the first step toward what biology calls "fitness variance."

---

## 1. System Snapshot

### 1.1 Current Configuration (Viable)

| Parameter | Value | Role |
|-----------|-------|------|
| `observation_dim` | 8 | Dimensionality of sensory input |
| `consumption_rate` | 0.08 | Base metabolic cost per tick |
| `update_cost_factor` | 0.02 | Cost multiplier for weight updates |
| `extraction_factor` | 0.6 | Maximum energy extractable per tick |
| `learning_rate` | 0.05 | Weight update magnitude |
| `initial_energy` | 100.0 | Starting energy budget |
| `random_baseline` | √8 ≈ 2.83 | Expected error from random prediction |

### 1.2 Extraction Curve

```
extraction_efficiency = exp(-error / random_baseline)
```

| Error / Baseline | Efficiency | Interpretation |
|------------------|------------|----------------|
| 0.0 | 1.00 | Perfect prediction → full extraction |
| 0.5 | 0.84 | Good prediction |
| 1.0 | 0.69 | Typical learning |
| 1.5 | 0.57 | Struggling |
| 2.0 | 0.47 | Near-random |
| 2.83 (baseline) | 0.37 | Random-level → ~37% efficiency |
| 4.0 | 0.24 | Worse than random |

### 1.3 Known Boundary

| Signal Ratio | Error/Dim | Energy Trend | Status |
|--------------|-----------|--------------|--------|
| 1.0 | 1.08 | -0.042 | ALIVE |
| 0.9 | 1.09 | -0.046 | ALIVE |
| 0.8 | 1.14 | -0.064 | DEAD |
| 0.0 | 1.36 | -0.143 | DEAD |

**Observed boundary:** signal_ratio ≈ 0.85 - 0.90

---

## 2. Robustness Questions

### 2.1 Parameter Sensitivity Analysis

#### A. Noise Level Sensitivity

**Question:** Does adding observation noise shift the boundary?

**Hypothesis:** Observation noise acts as *internal* chaos, independent of environmental structure. If the boundary is structural (not accidental), adding noise should:
- Shift the boundary *upward* (require more structure)
- Preserve the shape of the transition

**Suggested Experiment:**
```
observation_noise ∈ [0.001, 0.01, 0.05, 0.1, 0.2]
For each: sweep signal_ratio [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7]
Measure: boundary location, transition sharpness
```

**What would indicate structural vs accidental:**
- **Structural:** Boundary shifts predictably with noise (linear or logarithmic relationship)
- **Accidental:** Boundary location is erratic, no consistent trend

---

#### B. Learning Rate Sensitivity

**Question:** Does learning rate change the boundary or just the path to it?

**Hypothesis:** Learning rate affects *dynamics* but may not affect the *equilibrium boundary*. A structural boundary should:
- Persist across learning rates
- Only change the *time to convergence*, not the *final viability*

**But:** If learning is too slow, the organism may die before reaching competence. If too fast, oscillations may waste energy.

**Suggested Experiment:**
```
learning_rate ∈ [0.01, 0.02, 0.05, 0.1, 0.2]
For each: sweep signal_ratio [1.0, 0.9, 0.8]
Measure: time to stable error, final error, survival
```

**What would indicate structural vs accidental:**
- **Structural:** Boundary survives across at least 3 learning rates
- **Accidental:** Survival is highly sensitive to learning rate (boundary appears/disappears)

---

#### C. Metabolic Cost Sensitivity

**Question:** Is the boundary set by the extraction curve or by cost parameters?

**Key Ratio:** 
```
break_even_efficiency = consumption_rate / extraction_factor
                      = 0.08 / 0.6 
                      = 0.133
```

For net-positive metabolism, extraction_efficiency > 0.133.

From the extraction curve:
```
exp(-error / 2.83) > 0.133
-error / 2.83 > ln(0.133) ≈ -2.02
error < 5.7
```

This suggests the break-even error is ~5.7, but actual errors are ~3.0-3.8, so survival should be easier. Why is it not?

**The update cost is the hidden variable.** Update magnitude adds to consumption:
```
total_cost = consumption_rate + update_magnitude × update_cost_factor
```

**Suggested Experiment:**
```
Vary: consumption_rate ∈ [0.04, 0.08, 0.12, 0.16]
Vary: update_cost_factor ∈ [0.01, 0.02, 0.04, 0.08]
Fixed: signal_ratio = 0.85 (at the boundary)
Measure: survival/death, mean update magnitude
```

**What would indicate structural vs accidental:**
- **Structural:** Boundary shifts proportionally to cost changes
- **Accidental:** Boundary has discontinuities or non-monotonic behavior

---

#### D. Extraction Curve Shape

**Question:** Is the exponential curve shape essential or arbitrary?

The current curve: `exp(-error / baseline)`

Alternatives to test:
1. **Linear:** `max(0, 1 - error / (2 × baseline))`
2. **Sigmoid:** `1 / (1 + exp(error - baseline))`
3. **Threshold:** `1 if error < baseline else 0.1`

**Hypothesis:** The exponential curve is smooth and has no threshold. A threshold-based curve would create sharper phase transitions. A linear curve would make the system more forgiving of moderate errors.

**Suggested Experiment:**
```
For each extraction curve type:
  Sweep signal_ratio [1.0, 0.9, 0.85, 0.8, 0.7, 0.6, 0.5]
  Measure: boundary location, transition width (how many signal_ratio steps from alive to dead)
```

**What would indicate structural vs accidental:**
- **Structural:** Boundary exists for all curve shapes (possibly at different locations)
- **Accidental:** Boundary only exists for certain curve shapes

---

### 2.2 Sharpness of Boundary

**Current Data:** 
- 0.9 → ALIVE
- 0.8 → DEAD

This is a 10% interval. Is the transition:
1. **Sharp (phase transition):** All runs at 0.85 die or survive consistently
2. **Fuzzy (probabilistic):** 0.85 survives 50% of the time depending on seed
3. **Gradual:** There's a "dying" zone where survival time varies

**Suggested Experiment:**
```
Fixed: signal_ratio = 0.85
Seeds: 20 independent runs
Measure: survival rate, mean ticks survived, variance in survival time
```

```
Then: signal_ratio ∈ [0.82, 0.84, 0.86, 0.88]
Measure: survival probability at each point
```

**Interpretation:**
- Sharp transition → the boundary is a *thermodynamic* property
- Fuzzy transition → the boundary is *stochastic*, depends on initial conditions
- Gradual transition → the boundary is *kinetic*, depends on time scales

---

## 3. Failure Mode Analysis

### 3.1 How Death Occurs

**Current observation:** At signal_ratio < 0.85, energy trend is negative and organism dies.

**Question:** Is death:
1. **Gradual decline:** Energy decreases monotonically until exhaustion
2. **Catastrophic collapse:** A critical point is reached, then rapid failure
3. **Oscillatory:** Energy fluctuates, occasionally recovering, until a bad run

**Data needed:**
```
For signal_ratio = 0.7 (in dead zone):
  Plot: energy over time
  Look for: inflection points, acceleration of decline, recovery attempts
```

**Suggested Observables:**
- `d(energy)/d(tick)` - first derivative (rate of loss)
- `d²(energy)/d(tick²)` - second derivative (acceleration)
- `min(energy)` over rolling windows - local minima

**What would indicate:**
- **Gradual:** Near-constant negative derivative
- **Catastrophic:** Derivative accelerating (second derivative negative)
- **Oscillatory:** Sign changes in derivative before final collapse

---

### 3.2 The Role of Update Cost

**Observation from data:** In chaotic environments, update magnitude is HIGHER (0.54 vs 0.43 in order).

**Implication:** The organism works *harder* in chaos, which costs more, which accelerates death.

This creates a **positive feedback loop:**
```
chaos → high error → large updates → high cost → energy loss → death
```

**Question:** Is this loop the *cause* of death, or just a symptom?

**Suggested Experiment:**
```
Disable update cost (update_cost_factor = 0)
Sweep signal_ratio [1.0, 0.9, 0.8, 0.7, 0.6]
Compare: Does the boundary shift? Does it disappear?
```

**Interpretation:**
- **Boundary persists:** Update cost is not the primary constraint; extraction efficiency is
- **Boundary disappears:** Update cost is the *dominant* mortality factor

---

### 3.3 Near-Death Dynamics

**Question:** Does the organism behave differently as energy approaches zero?

**Current data:** `near_death_count` is tracked but not analyzed.

**Suggested Observables:**
```
When energy < 20 (near-death threshold):
  - learning_rate effective (does it decrease updates?)
  - error magnitude (does it accept worse predictions?)
  - update magnitude (restraint under scarcity?)
```

**Important:** Currently, there is **no mechanism** for the organism to modulate behavior based on energy. Learning rate, update magnitude, etc. are constant.

This is **correct for now** — we are not adding intelligence. But it means:
- Near-death behavior = same as normal behavior
- The organism has no "survival mode"

**What this implies:** Death is purely thermodynamic, not behavioral. The organism cannot "try harder" or "rest." It simply runs out.

---

## 4. Metrics to Observe (Not Optimize)

### 4.1 Primary Observables

| Metric | What It Reveals | Phase Transition Signal |
|--------|-----------------|------------------------|
| `energy_trend` | Net metabolic balance | Sign change (+ to -) |
| `mean_error` | Prediction competence | Monotonic increase with chaos |
| `update_magnitude` | Effort expended | Spike indicates desperation |
| `error_variance` | Stability | Spike indicates instability |

### 4.2 Derived Ratios

| Ratio | Formula | Interpretation |
|-------|---------|----------------|
| Efficiency | `error / update_magnitude` | Low = working hard for little gain |
| Metabolic margin | `extraction - cost` | Positive = viable, negative = dying |
| Error compression | `error / random_baseline` | < 1 = beating random, > 1 = losing |

### 4.3 Temporal Signatures

**Look for these patterns as signal_ratio decreases:**

1. **Error ceiling:** Does error asymptote or keep growing?
2. **Update oscillation:** Does learning become unstable?
3. **Energy volatility:** Does energy variance increase before death?
4. **Recovery attempts:** Are there local energy minima followed by partial recovery?

### 4.4 Cross-Environment Comparisons

**Restraint indicator:** 
```
restraint = update_magnitude(ordered) / update_magnitude(chaotic)
```
- If < 1: organism works less in order → appropriate restraint
- If > 1: organism works more in order → pathological

**Current data:** 0.43 / 0.54 ≈ 0.80 → **Restraint is present**

This is not learned. It is *emergent* from gradient magnitudes. But it is real.

---

## 5. Structural vs Accidental Boundary: Decision Criteria

A **structural boundary** would show:

1. **Robustness to parameters:** Boundary persists across reasonable parameter ranges
2. **Predictable shifts:** When parameters change, boundary moves in explainable directions
3. **Seed independence:** Boundary location consistent across random seeds
4. **Sharp transition:** Viability flips over narrow signal_ratio range
5. **Monotonicity:** No "islands" of survival in chaotic regions

An **accidental boundary** would show:

1. **Parameter sensitivity:** Small changes cause boundary to appear/disappear entirely
2. **Erratic shifts:** No clear relationship between parameters and boundary
3. **High variance:** Different seeds produce wildly different outcomes
4. **Gradual transition:** Wide "gray zone" of probabilistic survival
5. **Non-monotonicity:** Unpredictable survival patterns

---

## 6. Suggested Experiment Sequence

### Phase 1: Boundary Resolution (2-4 experiments)
1. **Fine-grain sweep:** signal_ratio ∈ [0.82, 0.84, 0.86, 0.88, 0.90, 0.92]
2. **Multi-seed validation:** 10 seeds at signal_ratio = 0.85

### Phase 2: Parameter Sensitivity (4-6 experiments)
3. **Noise sensitivity:** observation_noise ∈ [0.001, 0.01, 0.05, 0.1]
4. **Learning rate sweep:** learning_rate ∈ [0.01, 0.05, 0.1]
5. **Cost structure:** consumption_rate × update_cost_factor grid
6. **Extraction curve comparison:** exponential vs linear vs threshold

### Phase 3: Failure Mode Analysis (2-3 experiments)
7. **Death trajectory:** Plot energy, error, update over time at signal_ratio = 0.7
8. **Zero update cost:** Does removing learning cost change boundary?
9. **Extended runs:** 10,000 ticks at signal_ratio = 0.85 to test long-term stability

### Phase 4: Metric Validation (1-2 experiments)
10. **Correlation analysis:** Which metrics best predict survival/death?
11. **Lag analysis:** What happens first — error spike, energy decline, or update spike?

---

## 7. Constraints Reminder

- **No new goals** — the organism does not "want" to survive
- **No optimization** — we are observing, not improving
- **No intelligence** — no planning, no lookahead, no contingency
- **Metabolism-first** — energy is fundamental, prediction is instrumental
- **Observation regime** — the observer does not intervene

The purpose of this analysis is to **characterize** the boundary, not to **move** it.

---

## 8. Open Questions

1. ~~**Is the boundary set by extraction efficiency or by update costs?**~~
   - ✅ **ANSWERED:** Update costs are the primary mortality factor. Experiment 3 proved this.

2. **Does temporal structure matter?**
   - Would a random-phase sine (same frequencies, random phases) change viability?
   - This tests whether the organism needs *predictability* or just *regularity*

3. **What is the minimum structure for survival?**
   - Is 85% sine + 15% noise the minimum, or is there a lower-complexity structure that works?

4. **Can the organism "adapt" to a niche?**
   - If we start in chaos and gradually increase structure, does the organism recover?
   - This tests whether death is reversible (thermodynamic) or permanent (damage accumulates)

5. **Is there an upper limit on structure?**
   - Pure sine (1.0) works, but what about a constant (zero entropy)?
   - Would the organism survive in a perfectly static world?

6. **NEW: Can restraint emerge without programming it?**
   - The organism currently lacks effort regulation
   - Could error-contingent learning rate modulation arise naturally?
   - What minimal mechanism would create restraint without adding goals?

---

## 9. Summary

### Original Question (Pre-Experiment 3)

> Is the ~0.85-0.90 viability boundary structural or accidental?

### Answer (Post-Experiment 3)

> **Structural, but mediated by effort.**

The boundary exists because:
1. Chaos produces high error
2. High error produces large weight updates
3. Large updates cost energy
4. Energy loss causes death

When update cost is removed, the boundary disappears completely. 
**Entropy itself is not lethal. The reaction to entropy is lethal.**

### What This Means

The organism's current mortality is a **self-inflicted wound**.

It works equally hard in learnable and unlearnable environments.
It lacks the capacity to recognize when effort is futile.
It dies from trying, not from failing.

### The Next Evolutionary Frontier

This is not something to "fix" — it is something to **observe**.

The question now is: **Can restraint emerge without programming it?**

Possible observation paths:
1. **Gradient-based restraint:** Does error magnitude naturally modulate learning?
2. **Energy-contingent learning:** Does the organism slow down when energy is low?
3. **Prediction uncertainty:** Can the organism detect unpredictability before dying?

These are questions for the next phase. The current phase is complete.

---

## EXPERIMENT 6: ENERGY-MODULATED LEARNING RATE

### Rationale

> **When energy is low, Ultron should change itself less, not more.**  
> This is not survival instinct. This is metabolic regulation.  
> Starving cells slow growth. Stressed systems conserve structure.

### Implementation

Added energy modulation to learning rate in `update()`:

```python
# Smooth, monotonic, bounded, never zero
# f(energy) ranges from 0.1 (empty) to 1.0 (capacity)
energy_ratio = state.energy.current / state.energy.capacity
energy_modulation = 0.1 + 0.9 * energy_ratio

# Effective learning rate = base × modulation
effective_lr = base_learning_rate * energy_modulation
```

All learning (weights, priors, precision) now scales with energy.

### Result: Boundary Shifted Toward Chaos

**Before (no regulation) vs After (energy-modulated LR):**

| Metric | Before | After |
|--------|--------|-------|
| Boundary | ~0.60 | ~0.52 |
| signal_ratio=0.52 survival | 0% | 70% |
| Pure chaos lifespan | ~10000 ticks | ~20000 ticks |
| Survivors' energy at boundary | ~100 | 1-10 |

**50,000 tick survival sweep:**

| Signal Ratio | Outcome |
|--------------|---------|
| 0.90 | ALIVE, energy=200 (capacity) |
| 0.80 | ALIVE, energy=200 (capacity) |
| 0.70 | ALIVE, energy=168 |
| 0.60 | ALIVE, energy=44 |
| 0.55 | ALIVE, energy=25 |
| 0.52 | 70% survival (14/20), energy=1-10 |
| 0.50 | DIED at t=49724 |
| 0.40 | DIED at t=20922 |
| 0.30 | DIED at t=20218 |
| 0.00 | DIED at t=20117 |

### Stochastic Boundary at signal_ratio=0.52

20 seeds tested:
- 14/20 (70%) survived to 50000 ticks
- Survivors barely alive (1-10 energy out of 200)
- Deaths occurred at t=40000-48000

### Mechanism: Graceful Degradation

Energy trajectory in pure chaos (signal_ratio=0.0):

| Tick | Energy | LR Factor |
|------|--------|-----------|
| 100 | 101 | 0.55 |
| 1000 | 97 | 0.53 |
| 5000 | 69 | 0.41 |
| 10000 | 41 | 0.28 |
| 20000 | 2 | 0.11 |

The feedback loop:
1. Energy drops → learning rate drops
2. Less learning → less wasted energy on futile updates
3. Slower energy drain → extended survival
4. System asymptotically approaches death but doesn't cross

### Interpretation

> **Energy regulation creates metabolic self-preservation without goals.**

This is not "trying to survive." This is physics. The system naturally:
- Learns aggressively when resourced (effective_lr ≈ 1.0×)
- Conserves structure when depleted (effective_lr ≈ 0.1×)
- Extends lifespan in hostile environments (~2×)
- Shifts the viability boundary toward chaos (~0.08 in signal space)

**The organism is now harder to kill.** Not because it wants to live, but because it does less when it has less.

### What Emerged

| Before | After |
|--------|-------|
| Equal effort everywhere | Effort proportional to resources |
| Sharp death | Graceful degradation |
| Fixed viability boundary | Shifted boundary |
| Binary (alive/dead) | Marginal existence possible |

The organism can now exist in a "barely alive" state at the boundary — energy between 1-10, learning rate at 10%, clinging to existence without thriving.

This is **metabolic individuality**: identical organisms in identical environments can have different energy levels, different effective learning rates, and different fates.

---

## EXPERIMENT 7: BIRTH TRAITS AND FITNESS

### Rationale

> **Can we predict who lives and who dies before they live or die?**

Previous experiments showed individuality matters, but we didn't know what *trait* determines fate. This experiment introduces heritable birth traits.

### Implementation

Added `BirthTraits` dataclass with three permanent traits:

```python
@dataclass
class BirthTraits:
    extraction_efficiency: float = 1.0  # Multiplier on energy extraction
    metabolic_rate: float = 1.0         # Multiplier on consumption
    learning_capacity: float = 1.0      # Multiplier on learning rate
```

Each trait varies ±2% at birth. Traits are frozen forever.

### Key Finding: Fitness = extraction / metabolic

**Classification accuracy: 94%**

| Metric | Alive | Dead |
|--------|-------|------|
| Fitness mean | 1.0118 ± 0.0118 | 0.9827 ± 0.0092 |
| N | 56 | 44 |

Best threshold: **0.9931**

```
If fitness >= 0.9931: predict ALIVE (correct 94% of the time)
If fitness <  0.9931: predict DEAD  (correct 94% of the time)
```

### Correlation Analysis (margin environment)

| Correlation | Value |
|-------------|-------|
| Extraction vs Energy | 0.54 |
| Metabolic vs Energy | -0.37 |
| **Fitness vs Energy** | **0.95** |

### Cross-Environment Effect

| Environment | Survival Rate |
|-------------|---------------|
| Margin (0.55) | 58% |
| Boundary (0.52) | 32% |

The same fitness threshold applies in both environments—traits are absolute, not relative.

### Interpretation

> **A 2% variation in birth traits creates a 94% predictable life/death split.**

This is the precondition for natural selection:
- Variation exists
- Variation is heritable (frozen at birth)
- Variation affects survival
- Higher fitness → higher survival

**We have not implemented selection.** We have merely created the conditions under which selection *could* occur.

### What Emerged Without Being Programmed

| Feature | How It Emerged |
|---------|----------------|
| Fitness definition | Ratio of two independent traits |
| Survival threshold | Self-organizing from metabolism |
| Individual variation | Random ±2% at birth |
| Fate determination | Interaction of traits × environment |

---

*This is characterization, not engineering.*
*We are mapping terrain, not building roads.*
*Experiment 7 revealed that fitness emerges from physics.*

---

## EXPERIMENT 8: DARWINIAN EVOLUTION

### Question
Can we observe natural selection with real reproduction, trait inheritance, and differential survival?

### Setup
- Start with 30 Ultrons with random birth traits (±3% variation)
- Run 1M ticks with:
  - Resource competition: `extraction *= min(1.0, CARRYING_CAPACITY / population)`
  - Carrying capacity: 40 (creates crowding pressure)
  - Reproduction threshold: 120 energy
  - Reproduction cost: 60 energy
  - Mutation rate: 1.5%

### Result: EVOLUTION CONFIRMED

```
Initial fitness: 0.9921
Final fitness:   1.2109
Change:          +22.1%

Initial extraction: 0.9965 → Final: 1.1201 (+12.4%)
Initial metabolic:  1.0047 → Final: 0.9250 (-7.5%)

Generations: 21
Total births: 126
Total deaths: 101
```

### Fitness Trajectory

| Time | Fitness | Births | Deaths | Generation |
|------|---------|--------|--------|------------|
| 0 | 0.9921 | 0 | 0 | 0 |
| 100K | 1.0056 | 20 | 4 | 3 |
| 200K | 1.0153 | 26 | 9 | 5 |
| 300K | 1.0379 | 36 | 20 | 7 |
| 400K | 1.1162 | 71 | 51 | 11 |
| 500K | 1.1423 | 85 | 63 | 13 |
| 600K | 1.1534 | 92 | 70 | 15 |
| 700K | 1.1659 | 99 | 77 | 18 |
| 800K | 1.1919 | 113 | 89 | 20 |
| 900K | 1.2034 | 120 | 96 | 21 |
| 1M | 1.2109 | 126 | 101 | 21 |

### Interpretation

**Both traits evolved in the expected direction:**
- Extraction efficiency increased (+12.4%): better energy acquisition
- Metabolic rate decreased (-7.5%): lower maintenance cost

**This is not simulated selection.** Real organisms:
- Lived and died based on energy balance
- Reproduced when energy exceeded threshold
- Passed traits to offspring with small mutations
- Competed for limited resources

**The fitness increase emerged from:**
1. Unfit organisms dying (101 deaths)
2. Fit organisms reproducing (126 births)
3. Offspring inheriting advantageous traits
4. Mutations providing variation for selection

### What We Did NOT Program

| Feature | Emerged From |
|---------|--------------|
| Which fitness direction is "better" | Physics (extraction helps, metabolism hurts) |
| Who lives and dies | Energy dynamics |
| Who reproduces | Energy threshold |
| Population regulation | Competition for resources |
| Trait evolution | Differential survival + inheritance |

### Conclusion

> **Ultron exhibits Darwinian evolution: heritable variation + differential survival = fitness increase over generations.**

This is not artificial selection (we didn't choose who survives).
This is not genetic algorithms (we didn't define a fitness function).
This is natural selection: physics decides who lives, survivors reproduce, traits drift.
