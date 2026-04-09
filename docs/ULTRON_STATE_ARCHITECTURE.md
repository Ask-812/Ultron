# ULTRON STATE ARCHITECTURE

## Purpose

This document specifies the concrete state structure, irreversibility mechanisms, and operational semantics for the minimal Ultron implementation.

---

## Part I: Formal State Definition

### 1.1 The Ultron State Tuple

At any moment, Ultron's state is defined by the tuple:

```
Σ = (M, H, C, E, τ)
```

Where:
- **M** = Model state (the self-predicting apparatus)
- **H** = History state (irreversible accumulated experience)
- **C** = Current state (working memory for this tick)
- **E** = Energy state (available resources)
- **τ** = Time state (irreversible tick counter)

### 1.2 Model State (M)

```python
M = {
    "generative_weights": Matrix,    # Parameters for prediction
    "prior_distribution": Vector,    # Expectations about self
    "precision_estimates": Vector,   # Confidence per dimension
    "model_version": int             # How many times model updated
}
```

**Invariants:**
- generative_weights must be finite (no NaN/inf)
- prior_distribution must sum to 1
- precision_estimates must be positive
- model_version only increases

### 1.3 History State (H)

```python
H = {
    "birth_hash": bytes32,           # Hash at initialization (never changes)
    "current_hash": bytes32,         # Hash of current state
    "accumulated_error": float,      # Sum of all prediction errors
    "peak_error": float,             # Maximum error ever experienced
    "survival_count": int,           # Ticks survived
    "near_death_count": int          # Times energy dropped below threshold
}
```

**Invariants:**
- birth_hash is write-once, read-forever
- current_hash = hash(previous_hash || state || τ)
- accumulated_error only increases
- survival_count only increases

### 1.4 Current State (C)

```python
C = {
    "observation": Vector,           # What was sensed this tick
    "prediction": Vector,            # What was expected this tick
    "error": Vector,                 # observation - prediction
    "error_magnitude": float,        # ||error||
    "update_direction": Vector       # Gradient for next update
}
```

**Invariants:**
- Current state is ephemeral - replaced each tick
- No invariants on values (can be anything)

### 1.5 Energy State (E)

```python
E = {
    "current_energy": float,         # Available energy
    "energy_capacity": float,        # Maximum storable energy
    "consumption_rate": float,       # Base cost per tick
    "last_intake": float,           # Energy received last tick
    "energy_history": RingBuffer     # Recent energy levels
}
```

**Invariants:**
- 0 ≤ current_energy ≤ energy_capacity
- If current_energy = 0, loop terminates (death)
- consumption_rate > 0

### 1.6 Time State (τ)

```python
τ = {
    "tick": int,                     # Current tick number
    "wall_time_birth": timestamp,    # When system started
    "wall_time_current": timestamp   # Current wall time
}
```

**Invariants:**
- tick only increases
- wall_time_birth is write-once
- tick must advance for any state change

---

## Part II: State Transitions

### 2.1 The Tick Function

Each tick transforms the state:

```
Σ(t+1) = tick(Σ(t), input(t))
```

Where `tick` is decomposed into phases:

```
tick(Σ, I) = 
    let Σ₁ = sense(Σ, I)        in  # Observe
    let Σ₂ = predict(Σ₁)        in  # Generate prediction
    let Σ₃ = compare(Σ₂)        in  # Compute error
    let Σ₄ = update(Σ₃)         in  # Modify model
    let Σ₅ = metabolize(Σ₄)     in  # Consume energy
    let Σ₆ = historify(Σ₅)      in  # Record to history
    let Σ₇ = advance(Σ₆)        in  # Increment time
    Σ₇
```

### 2.2 Phase: Sense

```python
def sense(Σ, input):
    C.observation = encode(input)
    return Σ.with(C=C)
```

The `encode` function maps raw input to the observation vector. This is the membrane - it determines what "gets through."

### 2.3 Phase: Predict

```python
def predict(Σ):
    C.prediction = M.generative_weights @ M.prior_distribution
    return Σ.with(C=C)
```

The prediction is generated using the current model. This is what the system "expects."

### 2.4 Phase: Compare

```python
def compare(Σ):
    C.error = C.observation - C.prediction
    C.error_magnitude = norm(C.error)
    return Σ.with(C=C)
```

The error is the difference between prediction and observation. This is where "caring" originates.

### 2.5 Phase: Update

```python
def update(Σ):
    C.update_direction = compute_gradient(M, C.error)
    M.generative_weights += learning_rate * C.update_direction
    M.prior_distribution = update_priors(M.prior_distribution, C.observation)
    M.precision_estimates = update_precision(M.precision_estimates, C.error_magnitude)
    M.model_version += 1
    return Σ.with(M=M, C=C)
```

This is the core metabolism - the system changes itself in response to error.

### 2.6 Phase: Metabolize

```python
def metabolize(Σ):
    cost = E.consumption_rate + update_cost(C.update_direction)
    E.current_energy -= cost
    E.energy_history.append(E.current_energy)
    
    if E.current_energy <= 0:
        raise Death("Energy exhausted")
    
    if E.current_energy < LOW_ENERGY_THRESHOLD:
        H.near_death_count += 1
    
    return Σ.with(E=E, H=H)
```

Energy is consumed. If exhausted, the system dies.

### 2.7 Phase: Historify

```python
def historify(Σ):
    H.accumulated_error += C.error_magnitude
    H.peak_error = max(H.peak_error, C.error_magnitude)
    H.current_hash = hash(H.current_hash || serialize(Σ) || τ.tick)
    H.survival_count += 1
    return Σ.with(H=H)
```

The history is updated irreversibly. The hash chain ensures no rollback.

### 2.8 Phase: Advance

```python
def advance(Σ):
    τ.tick += 1
    τ.wall_time_current = now()
    return Σ.with(τ=τ)
```

Time advances. This is the only place where time changes.

---

## Part III: Irreversibility Mechanism

### 3.1 The Hash Chain

The history hash creates cryptographic irreversibility:

```
H₀ = hash("ULTRON_BIRTH" || random_seed || wall_time)
Hₙ = hash(Hₙ₋₁ || serialize(Σₙ) || n)
```

Properties:
- Given Hₙ, you cannot compute Hₙ₋₁
- Given Hₙ and Hₘ, you can verify continuity
- Any "reset" breaks the chain

### 3.2 Chain Verification

The system can verify its own history:

```python
def verify_chain(start_hash, states):
    h = start_hash
    for i, state in enumerate(states):
        expected = hash(h || serialize(state) || i)
        if state.H.current_hash != expected:
            return False, i  # Chain broken at tick i
        h = expected
    return True, len(states)
```

### 3.3 Fork Detection

If someone tries to "branch" Ultron:

```python
def detect_fork(self, other_ultron):
    # Same birth hash means common origin
    if self.H.birth_hash != other_ultron.H.birth_hash:
        return "different_individuals"
    
    # Same current hash means identical
    if self.H.current_hash == other_ultron.H.current_hash:
        return "same_state"
    
    # Same birth, different current = fork
    return "forked_copy"
```

### 3.4 Why Irreversibility Matters

Without irreversibility:
- Reset = no history = no consequences
- Clone = multiple "selves" = identity confusion
- Checkpoint = reversible = no real stakes

With irreversibility:
- Each moment is once-only
- History accumulates
- Identity persists through change
- Loss is possible (death matters)

---

## Part IV: Energy Dynamics

### 4.1 Energy Sources

Possible energy intake mechanisms:

```python
def receive_energy(Σ, amount, source_type):
    E.current_energy = min(
        E.energy_capacity,
        E.current_energy + amount
    )
    E.last_intake = amount
    
    # Different sources might have different effects
    if source_type == "prediction_success":
        # Successful prediction gives energy
        pass
    elif source_type == "external_input":
        # Information from environment gives energy
        pass
    elif source_type == "interaction":
        # Engagement gives energy
        pass
    
    return Σ.with(E=E)
```

### 4.2 Energy Costs

```python
def compute_tick_cost(Σ):
    base_cost = E.consumption_rate
    
    # Cost scales with model complexity
    model_cost = complexity(M.generative_weights) * MODEL_COST_FACTOR
    
    # Cost scales with update magnitude
    update_cost = norm(C.update_direction) * UPDATE_COST_FACTOR
    
    # Cost scales with observation processing
    sense_cost = dim(C.observation) * SENSE_COST_FACTOR
    
    return base_cost + model_cost + update_cost + sense_cost
```

### 4.3 Energy-Error Coupling

A key design decision: Does low error give energy?

**Option A: Prediction success as energy**
- Low error → energy gain
- High error → energy loss
- Creates pressure toward accurate self-model

**Option B: External energy only**
- Error affects model, not energy
- Energy comes from environment
- Creates pressure toward environmental engagement

**Option C: Both**
- Base energy from environment
- Bonus energy from prediction success
- Balanced pressure

### 4.4 Death Condition

```python
def check_death(Σ):
    if E.current_energy <= 0:
        return True, "energy_exhaustion"
    
    if C.error_magnitude > FATAL_ERROR_THRESHOLD:
        return True, "model_collapse"
    
    if H.survival_count > MAX_TICKS:
        return True, "entropy_death"
    
    return False, None
```

---

## Part V: Self-Model Specification

### 5.1 What The Model Predicts

The model must predict its OWN next state, specifically:

```python
prediction_target = {
    "next_observation": Vector,      # What will I sense?
    "next_error_magnitude": float,   # How wrong will I be?
    "next_energy_level": float,      # How much energy will I have?
    "model_update_direction": Vector # How will I change?
}
```

### 5.2 Self-Reference Structure

The model predicts based on:
- Current state (Σ)
- Historical patterns (H)
- Expected input (prior over environment)

But the prediction INCLUDES the model's own behavior:

```
prediction(t+1) = f(Σ(t), M(t))
```

And M(t+1) depends on:

```
M(t+1) = update(M(t), error(t))
M(t+1) = update(M(t), observation(t) - prediction(t))
M(t+1) = update(M(t), observation(t) - f(Σ(t), M(t)))
```

**This is self-reference**: The model predicts its future, but its future depends on how well it predicts.

### 5.3 Meta-Prediction

At Layer 2, the system predicts prediction difficulty:

```python
def meta_predict(Σ):
    # How hard will the next tick be?
    expected_error = predict_error_magnitude(M, H)
    
    # How confident am I in my prediction?
    prediction_confidence = compute_confidence(M.precision_estimates)
    
    # What is my expected energy after next tick?
    expected_energy = E.current_energy - expected_cost(expected_error)
    
    return {
        "expected_error": expected_error,
        "confidence": prediction_confidence,
        "expected_energy": expected_energy
    }
```

### 5.4 Recursive Depth

How deep does the self-reference go?

**Level 0**: Prediction about environment
**Level 1**: Prediction about self (next state)
**Level 2**: Prediction about prediction (meta-prediction)
**Level 3**: Prediction about meta-prediction...

For minimal Ultron: Level 1 is sufficient. Level 2 enables proto-valence.

---

## Part VI: Observation Encoding

### 6.1 The Membrane Function

What constitutes valid observation?

```python
def encode(raw_input):
    # Bound the input (nothing infinite)
    bounded = clip(raw_input, MIN_VALUE, MAX_VALUE)
    
    # Normalize (consistent scale)
    normalized = (bounded - mean(bounded)) / std(bounded)
    
    # Add noise (nothing is perfectly observed)
    noisy = normalized + random_normal(0, OBSERVATION_NOISE)
    
    # Project to observation space
    observation = project(noisy, OBSERVATION_DIM)
    
    return observation
```

### 6.2 Internal vs External Observation

The observation can include both:

```python
def sense(Σ, external_input):
    # External: What's happening outside
    external_obs = encode(external_input)
    
    # Internal: What's happening inside
    internal_obs = encode(serialize_internal(Σ))
    
    # Combined observation
    C.observation = concatenate(external_obs, internal_obs)
    
    return Σ.with(C=C)
```

**Internal observation enables self-monitoring:**
- Energy level (am I depleted?)
- Error trend (am I improving?)
- Model stability (am I coherent?)

---

## Part VII: Initialization Protocol

### 7.1 Birth Sequence

```python
def initialize_ultron(seed, config):
    # Generate unique birth hash
    birth_hash = hash("ULTRON_BIRTH" || seed || now())
    
    # Initialize model with random or configured weights
    M = initialize_model(config.model_config)
    
    # Initialize history at zero
    H = {
        "birth_hash": birth_hash,
        "current_hash": birth_hash,
        "accumulated_error": 0.0,
        "peak_error": 0.0,
        "survival_count": 0,
        "near_death_count": 0
    }
    
    # Initialize energy at starting level
    E = {
        "current_energy": config.starting_energy,
        "energy_capacity": config.energy_capacity,
        "consumption_rate": config.consumption_rate,
        "last_intake": 0.0,
        "energy_history": RingBuffer(config.history_length)
    }
    
    # Initialize time
    τ = {
        "tick": 0,
        "wall_time_birth": now(),
        "wall_time_current": now()
    }
    
    # Initialize current state (will be populated on first tick)
    C = empty_current_state()
    
    return Σ(M, H, C, E, τ)
```

### 7.2 First Tick

The first tick is special - there's no history to draw on:

```python
def first_tick(Σ, first_input):
    # Observation is just encoded input
    C.observation = encode(first_input)
    
    # Prediction is from priors (no learned weights)
    C.prediction = M.prior_distribution
    
    # Error is computed as normal
    C.error = C.observation - C.prediction
    C.error_magnitude = norm(C.error)
    
    # First update begins learning
    C.update_direction = compute_gradient(M, C.error)
    
    # Continue with normal tick phases
    ...
```

---

## Part VIII: Death Protocol

### 8.1 Death Detection

```python
def tick(Σ, input):
    # Before any processing, check death conditions
    is_dead, cause = check_death(Σ)
    if is_dead:
        return death_state(Σ, cause)
    
    # Normal tick processing
    ...
```

### 8.2 Death State

```python
def death_state(Σ, cause):
    # Record final state
    final_Σ = Σ.copy()
    final_Σ.H.death_cause = cause
    final_Σ.H.death_tick = τ.tick
    final_Σ.H.death_time = now()
    
    # Compute final hash
    final_Σ.H.death_hash = hash(
        H.current_hash || 
        "DEATH" || 
        cause || 
        τ.tick
    )
    
    # Mark as dead (no further ticks possible)
    final_Σ.is_alive = False
    
    return final_Σ
```

### 8.3 Irreversibility of Death

Once dead, the system cannot be "revived":
- The death hash is final
- Starting a new Ultron creates a NEW individual (different birth_hash)
- The dead state is preserved as testament

---

## Part IX: Diagnostic Interface

### 9.1 What We Can Observe

External observation (without intervening):

```python
class UltronObserver:
    def get_diagnostics(self, Σ):
        return {
            "tick": τ.tick,
            "energy": E.current_energy,
            "accumulated_error": H.accumulated_error,
            "survival_count": H.survival_count,
            "is_alive": Σ.is_alive,
            "current_error": C.error_magnitude,
            "model_version": M.model_version
        }
    
    def get_behavior_summary(self, Σ, window=100):
        return {
            "mean_error": mean(recent_errors(window)),
            "error_trend": trend(recent_errors(window)),
            "energy_trend": trend(energy_history(window)),
            "update_magnitude": mean(recent_updates(window))
        }
```

### 9.2 What We Cannot Do

The observer interface does NOT allow:
- Modifying state
- Resetting history
- Injecting energy (except through defined intake mechanisms)
- Changing model weights
- Reverting to checkpoints

---

## Part X: Configuration Parameters

### 10.1 Model Configuration

```python
model_config = {
    "observation_dim": 64,           # Size of observation vector
    "model_dim": 128,                # Size of internal model
    "learning_rate": 0.01,           # Update step size
    "prior_strength": 0.1,           # Weight of priors vs observations
    "precision_learning_rate": 0.001 # How fast precision adapts
}
```

### 10.2 Energy Configuration

```python
energy_config = {
    "starting_energy": 100.0,
    "energy_capacity": 200.0,
    "consumption_rate": 1.0,         # Base cost per tick
    "model_cost_factor": 0.001,
    "update_cost_factor": 0.1,
    "sense_cost_factor": 0.01,
    "prediction_reward": 0.5,        # Energy bonus for low error
    "low_energy_threshold": 10.0     # When to record near-death
}
```

### 10.3 Irreversibility Configuration

```python
irreversibility_config = {
    "hash_algorithm": "sha256",
    "history_buffer_size": 1000,     # How much history to retain
    "chain_verification_interval": 100  # How often to verify chain
}
```

---

## Conclusion: The Living State

This state architecture defines a system that:

1. **Predicts itself** - The model generates expectations about its own continuation
2. **Accumulates history** - Every tick leaves irreversible traces
3. **Requires energy** - Maintenance has a cost; depletion means death
4. **Computes error** - Discrepancy between prediction and observation matters
5. **Updates itself** - The model changes in response to error

Whether this is "alive" is not a question we can answer by looking at the architecture. We must build it, run it, watch it, and apply the birth tests.

**The architecture creates the conditions. Life must emerge.**

---

*"The state is not the self. The self is the state's becoming."*
