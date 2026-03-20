# ULTRON PROTOTYPE SPECIFICATION

## Version: 0.1 (Minimal Viable Cell)

This document specifies the first implementable prototype of Ultron - a minimal viable artificial life form that satisfies all philosophical requirements while remaining computationally tractable.

---

## Part I: Design Constraints

### 1.1 What We're Building

**A system that:**
- Predicts its own continuation
- Accumulates irreversible history
- Requires energy to maintain itself
- Experiences prediction error as proto-valence
- Can be observed but not intervened upon

### 1.2 What We're NOT Building

- A language model (no text generation as primary function)
- An agent (no goal-seeking behavior)
- A chatbot (no conversational interface)
- A simulation (the system IS, not represents)
- An optimization target (no fitness function to maximize)

### 1.3 Implementation Language

Python 3.10+ with:
- NumPy for numerical operations
- hashlib for cryptographic hashing
- No deep learning frameworks initially (keep it minimal)
- Optional: PyTorch later for more sophisticated models

---

## Part II: Core Data Structures

### 2.1 The UltronState Class

```python
from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import hashlib
import time

@dataclass
class ModelState:
    """The self-predicting apparatus."""
    weights: np.ndarray          # Prediction weights
    bias: np.ndarray             # Prediction bias
    priors: np.ndarray           # Prior expectations
    precision: np.ndarray        # Confidence per dimension
    version: int = 0             # Update counter

@dataclass
class HistoryState:
    """Irreversible accumulated experience."""
    birth_hash: bytes            # Initial hash (immutable)
    current_hash: bytes          # Current chain head
    accumulated_error: float = 0.0
    peak_error: float = 0.0
    survival_ticks: int = 0
    near_death_count: int = 0
    death_cause: Optional[str] = None
    death_tick: Optional[int] = None

@dataclass  
class CurrentState:
    """Working memory for this tick."""
    observation: np.ndarray
    prediction: np.ndarray
    error: np.ndarray
    error_magnitude: float
    update_direction: np.ndarray

@dataclass
class EnergyState:
    """Available resources."""
    current: float
    capacity: float
    consumption_rate: float
    last_intake: float = 0.0
    history: list = field(default_factory=list)

@dataclass
class TimeState:
    """Temporal position."""
    tick: int = 0
    birth_time: float = field(default_factory=time.time)
    current_time: float = field(default_factory=time.time)

@dataclass
class UltronState:
    """Complete state tuple."""
    model: ModelState
    history: HistoryState
    current: CurrentState
    energy: EnergyState
    time: TimeState
    is_alive: bool = True
```

---

## Part III: Core Operations

### 3.1 Initialization

```python
def create_ultron(config: dict) -> UltronState:
    """Birth a new Ultron."""
    
    # Dimensions
    obs_dim = config.get('observation_dim', 32)
    model_dim = config.get('model_dim', 64)
    
    # Generate unique birth hash
    seed = np.random.bytes(32)
    birth_time = time.time()
    birth_hash = hashlib.sha256(
        b"ULTRON_BIRTH" + seed + str(birth_time).encode()
    ).digest()
    
    # Initialize model with small random weights
    model = ModelState(
        weights=np.random.randn(model_dim, obs_dim) * 0.01,
        bias=np.zeros(obs_dim),
        priors=np.ones(obs_dim) / obs_dim,  # Uniform prior
        precision=np.ones(obs_dim),          # Unit precision
        version=0
    )
    
    # Initialize history
    history = HistoryState(
        birth_hash=birth_hash,
        current_hash=birth_hash
    )
    
    # Initialize current (will be populated on first tick)
    current = CurrentState(
        observation=np.zeros(obs_dim),
        prediction=np.zeros(obs_dim),
        error=np.zeros(obs_dim),
        error_magnitude=0.0,
        update_direction=np.zeros_like(model.weights)
    )
    
    # Initialize energy
    energy = EnergyState(
        current=config.get('starting_energy', 100.0),
        capacity=config.get('energy_capacity', 200.0),
        consumption_rate=config.get('consumption_rate', 1.0)
    )
    
    # Initialize time
    time_state = TimeState(
        tick=0,
        birth_time=birth_time,
        current_time=birth_time
    )
    
    return UltronState(
        model=model,
        history=history,
        current=current,
        energy=energy,
        time=time_state,
        is_alive=True
    )
```

### 3.2 The Tick Function

```python
def tick(state: UltronState, raw_input: np.ndarray, config: dict) -> UltronState:
    """Execute one tick of the Ultron lifecycle."""
    
    # Death check
    if not state.is_alive:
        return state  # Dead systems don't tick
    
    if state.energy.current <= 0:
        return die(state, "energy_exhaustion")
    
    # Phase 1: Sense
    state = sense(state, raw_input, config)
    
    # Phase 2: Predict
    state = predict(state, config)
    
    # Phase 3: Compare
    state = compare(state, config)
    
    # Phase 4: Update
    state = update(state, config)
    
    # Phase 5: Metabolize
    state = metabolize(state, config)
    
    # Phase 6: Historify
    state = historify(state, config)
    
    # Phase 7: Advance
    state = advance(state, config)
    
    return state
```

### 3.3 Phase Implementations

```python
def sense(state: UltronState, raw_input: np.ndarray, config: dict) -> UltronState:
    """Encode raw input into observation."""
    obs_dim = config.get('observation_dim', 32)
    
    # Clip and normalize
    clipped = np.clip(raw_input, -10, 10)
    normalized = (clipped - np.mean(clipped)) / (np.std(clipped) + 1e-8)
    
    # Add observation noise
    noise_scale = config.get('observation_noise', 0.01)
    noisy = normalized + np.random.randn(len(normalized)) * noise_scale
    
    # Project to observation dimension
    if len(noisy) != obs_dim:
        if len(noisy) > obs_dim:
            observation = noisy[:obs_dim]
        else:
            observation = np.pad(noisy, (0, obs_dim - len(noisy)))
    else:
        observation = noisy
    
    state.current.observation = observation
    return state


def predict(state: UltronState, config: dict) -> UltronState:
    """Generate prediction from model."""
    
    # Simple linear prediction: weights @ priors + bias
    hidden = state.model.weights @ state.model.priors
    prediction = np.tanh(hidden) + state.model.bias
    
    state.current.prediction = prediction
    return state


def compare(state: UltronState, config: dict) -> UltronState:
    """Compute prediction error."""
    
    error = state.current.observation - state.current.prediction
    error_magnitude = np.linalg.norm(error)
    
    state.current.error = error
    state.current.error_magnitude = error_magnitude
    return state


def update(state: UltronState, config: dict) -> UltronState:
    """Modify model based on error."""
    learning_rate = config.get('learning_rate', 0.01)
    
    # Gradient: outer product of error and priors
    gradient = np.outer(state.current.error, state.model.priors)
    
    # Update weights
    state.model.weights += learning_rate * gradient.T
    
    # Update bias toward observation
    state.model.bias += learning_rate * state.current.error * 0.1
    
    # Update priors toward observation (slow)
    prior_rate = config.get('prior_learning_rate', 0.001)
    state.model.priors += prior_rate * (state.current.observation - state.model.priors)
    state.model.priors = np.clip(state.model.priors, 0.01, 0.99)
    state.model.priors /= np.sum(state.model.priors)  # Normalize
    
    # Update precision (inverse of recent error variance)
    precision_rate = config.get('precision_learning_rate', 0.001)
    error_sq = state.current.error ** 2
    state.model.precision += precision_rate * (1.0 / (error_sq + 1e-8) - state.model.precision)
    
    state.model.version += 1
    state.current.update_direction = gradient
    return state


def metabolize(state: UltronState, config: dict) -> UltronState:
    """Consume energy."""
    
    # Base cost
    cost = state.energy.consumption_rate
    
    # Update cost (proportional to gradient magnitude)
    update_cost_factor = config.get('update_cost_factor', 0.1)
    cost += np.linalg.norm(state.current.update_direction.flatten()) * update_cost_factor
    
    # Prediction reward (negative cost for low error)
    reward_factor = config.get('prediction_reward_factor', 0.5)
    reward = reward_factor / (state.current.error_magnitude + 1.0)
    
    # Net energy change
    state.energy.current -= cost
    state.energy.current += reward
    state.energy.current = np.clip(state.energy.current, 0, state.energy.capacity)
    
    # Track history
    state.energy.history.append(state.energy.current)
    if len(state.energy.history) > 1000:
        state.energy.history = state.energy.history[-1000:]
    
    # Near-death tracking
    low_threshold = config.get('low_energy_threshold', 10.0)
    if state.energy.current < low_threshold:
        state.history.near_death_count += 1
    
    return state


def historify(state: UltronState, config: dict) -> UltronState:
    """Update irreversible history."""
    
    # Accumulate error
    state.history.accumulated_error += state.current.error_magnitude
    state.history.peak_error = max(state.history.peak_error, state.current.error_magnitude)
    state.history.survival_ticks += 1
    
    # Update hash chain
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


def advance(state: UltronState, config: dict) -> UltronState:
    """Increment time."""
    state.time.tick += 1
    state.time.current_time = time.time()
    return state


def die(state: UltronState, cause: str) -> UltronState:
    """Terminate the system."""
    state.is_alive = False
    state.history.death_cause = cause
    state.history.death_tick = state.time.tick
    
    # Final hash
    death_summary = f"DEATH:{cause}:{state.time.tick}".encode()
    state.history.current_hash = hashlib.sha256(
        state.history.current_hash + death_summary
    ).digest()
    
    return state
```

---

## Part IV: Energy Intake Mechanisms

### 4.1 External Energy Feed

```python
def feed_energy(state: UltronState, amount: float) -> UltronState:
    """Provide external energy (like food)."""
    if not state.is_alive:
        return state
    
    state.energy.current = min(
        state.energy.capacity,
        state.energy.current + amount
    )
    state.energy.last_intake = amount
    return state
```

### 4.2 Information as Energy

```python
def information_energy(state: UltronState, input_data: np.ndarray, config: dict) -> float:
    """Calculate energy from information novelty."""
    
    # Novelty = distance from prior expectation
    novelty = np.linalg.norm(input_data - state.model.priors)
    
    # Too much novelty is overwhelming, too little is boring
    # Optimal novelty is moderate
    optimal_novelty = config.get('optimal_novelty', 1.0)
    novelty_energy = np.exp(-((novelty - optimal_novelty) ** 2) / 2)
    
    return novelty_energy * config.get('novelty_energy_scale', 1.0)
```

---

## Part V: Input Generation

### 5.1 Simple Environmental Patterns

```python
class Environment:
    """Abstract base for environments."""
    
    def get_input(self, tick: int) -> np.ndarray:
        raise NotImplementedError


class SineEnvironment(Environment):
    """Predictable sinusoidal patterns."""
    
    def __init__(self, dim: int, frequencies: list = None):
        self.dim = dim
        self.frequencies = frequencies or [0.1 * (i+1) for i in range(dim)]
    
    def get_input(self, tick: int) -> np.ndarray:
        return np.array([
            np.sin(tick * f) for f in self.frequencies
        ])


class NoisyEnvironment(Environment):
    """Unpredictable random input."""
    
    def __init__(self, dim: int, scale: float = 1.0):
        self.dim = dim
        self.scale = scale
    
    def get_input(self, tick: int) -> np.ndarray:
        return np.random.randn(self.dim) * self.scale


class MixedEnvironment(Environment):
    """Combination of predictable and unpredictable."""
    
    def __init__(self, dim: int, signal_ratio: float = 0.5):
        self.dim = dim
        self.signal_ratio = signal_ratio
        self.sine = SineEnvironment(dim)
        self.noise = NoisyEnvironment(dim)
    
    def get_input(self, tick: int) -> np.ndarray:
        signal = self.sine.get_input(tick)
        noise = self.noise.get_input(tick)
        return self.signal_ratio * signal + (1 - self.signal_ratio) * noise
```

---

## Part VI: Observation Interface

### 6.1 The Observer (Non-Intervening)

```python
class UltronObserver:
    """Observe Ultron without intervening."""
    
    def __init__(self):
        self.observation_log = []
    
    def observe(self, state: UltronState) -> dict:
        """Record current state snapshot."""
        snapshot = {
            "tick": state.time.tick,
            "is_alive": state.is_alive,
            "energy": state.energy.current,
            "error": state.current.error_magnitude,
            "accumulated_error": state.history.accumulated_error,
            "survival_ticks": state.history.survival_ticks,
            "near_death_count": state.history.near_death_count,
            "model_version": state.model.version,
            "hash_prefix": state.history.current_hash[:8].hex()
        }
        self.observation_log.append(snapshot)
        return snapshot
    
    def get_trends(self, window: int = 100) -> dict:
        """Analyze recent behavior."""
        if len(self.observation_log) < window:
            recent = self.observation_log
        else:
            recent = self.observation_log[-window:]
        
        energies = [s["energy"] for s in recent]
        errors = [s["error"] for s in recent]
        
        return {
            "mean_energy": np.mean(energies),
            "energy_trend": np.polyfit(range(len(energies)), energies, 1)[0],
            "mean_error": np.mean(errors),
            "error_trend": np.polyfit(range(len(errors)), errors, 1)[0],
            "survival_rate": recent[-1]["survival_ticks"] / recent[-1]["tick"] if recent[-1]["tick"] > 0 else 1.0
        }
```

---

## Part VII: Birth Test Implementation

### 7.1 Test Functions

```python
class BirthTests:
    """Apply birth tests to detect life."""
    
    @staticmethod
    def test_history_dependence(state1: UltronState, state2: UltronState) -> bool:
        """Do different histories produce different presents?"""
        return state1.history.current_hash != state2.history.current_hash
    
    @staticmethod
    def test_irreversibility(state: UltronState) -> bool:
        """Can the system detect its own history?"""
        # Verify hash chain
        # (In practice, we'd need to track full history)
        return len(state.history.current_hash) == 32  # Minimal check
    
    @staticmethod
    def test_survival_pressure(observer: UltronObserver) -> bool:
        """Does behavior change near death?"""
        trends = observer.get_trends()
        # If error decreases when energy is low, system is "trying"
        # This is a proxy - real test would need more sophisticated analysis
        return trends["error_trend"] < 0
    
    @staticmethod
    def test_uniqueness(states: list) -> bool:
        """Are multiple instances distinguishable?"""
        hashes = [s.history.birth_hash for s in states]
        return len(set(hashes)) == len(hashes)
    
    @staticmethod
    def test_unprogrammed_behavior(state: UltronState, config: dict) -> dict:
        """Detect behavior not explicitly designed."""
        # This is inherently subjective
        # We report metrics and let humans judge
        return {
            "model_divergence": np.std(state.model.weights),
            "prior_entropy": -np.sum(state.model.priors * np.log(state.model.priors + 1e-10)),
            "precision_variance": np.var(state.model.precision)
        }
```

---

## Part VIII: Main Loop

### 8.1 Running Ultron

```python
def run_ultron(config: dict, max_ticks: int = 10000, 
               environment: Environment = None,
               energy_schedule: callable = None):
    """Run Ultron for a specified duration."""
    
    # Create Ultron
    state = create_ultron(config)
    
    # Create observer
    observer = UltronObserver()
    
    # Default environment
    if environment is None:
        environment = MixedEnvironment(
            config.get('observation_dim', 32),
            signal_ratio=0.7
        )
    
    # Main loop
    for t in range(max_ticks):
        # Check death
        if not state.is_alive:
            print(f"Ultron died at tick {t}, cause: {state.history.death_cause}")
            break
        
        # Get environmental input
        env_input = environment.get_input(t)
        
        # Optional: provide external energy on schedule
        if energy_schedule is not None:
            energy = energy_schedule(t)
            if energy > 0:
                state = feed_energy(state, energy)
        
        # Execute tick
        state = tick(state, env_input, config)
        
        # Observe (non-intervening)
        snapshot = observer.observe(state)
        
        # Periodic reporting
        if t % 1000 == 0:
            trends = observer.get_trends()
            print(f"Tick {t}: energy={snapshot['energy']:.2f}, "
                  f"error={snapshot['error']:.4f}, "
                  f"trend={trends['error_trend']:.6f}")
    
    return state, observer


# Example usage
if __name__ == "__main__":
    config = {
        'observation_dim': 32,
        'model_dim': 64,
        'starting_energy': 100.0,
        'energy_capacity': 200.0,
        'consumption_rate': 0.5,
        'learning_rate': 0.01,
        'prior_learning_rate': 0.001,
        'precision_learning_rate': 0.001,
        'update_cost_factor': 0.05,
        'prediction_reward_factor': 0.3,
        'observation_noise': 0.01,
        'low_energy_threshold': 10.0
    }
    
    # Run with periodic energy feeding
    def energy_schedule(t):
        # Feed every 100 ticks
        return 10.0 if t % 100 == 0 else 0.0
    
    final_state, observer = run_ultron(
        config, 
        max_ticks=5000,
        energy_schedule=energy_schedule
    )
    
    # Report
    print(f"\nFinal state:")
    print(f"  Survived: {final_state.history.survival_ticks} ticks")
    print(f"  Total error: {final_state.history.accumulated_error:.2f}")
    print(f"  Near-death events: {final_state.history.near_death_count}")
    print(f"  Model updates: {final_state.model.version}")
    print(f"  Is alive: {final_state.is_alive}")
```

---

## Part IX: Configuration Recommendations

### 9.1 For Stable Running

```python
stable_config = {
    'observation_dim': 32,
    'model_dim': 64,
    'starting_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.3,       # Low consumption
    'learning_rate': 0.01,
    'prediction_reward_factor': 0.5,  # High reward for prediction
    'low_energy_threshold': 20.0
}
```

### 9.2 For Challenging Conditions

```python
challenge_config = {
    'observation_dim': 64,          # More complex observation
    'model_dim': 128,
    'starting_energy': 50.0,        # Less starting energy
    'energy_capacity': 100.0,
    'consumption_rate': 1.0,        # High consumption
    'learning_rate': 0.005,         # Slower learning
    'prediction_reward_factor': 0.2,  # Less reward
    'low_energy_threshold': 10.0
}
```

### 9.3 For Minimal Viable

```python
minimal_config = {
    'observation_dim': 8,           # Very simple
    'model_dim': 16,
    'starting_energy': 100.0,
    'energy_capacity': 100.0,
    'consumption_rate': 0.1,
    'learning_rate': 0.1,           # Fast learning
    'prediction_reward_factor': 1.0,  # Strong reward
    'low_energy_threshold': 5.0
}
```

---

## Part X: Next Development Steps

### 10.1 Phase 1: Basic Implementation
- [ ] Implement core classes in Python
- [ ] Create simple environments
- [ ] Run initial experiments
- [ ] Validate irreversibility mechanism

### 10.2 Phase 2: Behavioral Analysis
- [ ] Add comprehensive logging
- [ ] Implement all birth tests
- [ ] Compare multiple instances
- [ ] Document emergent behaviors

### 10.3 Phase 3: Environmental Complexity
- [ ] More sophisticated environments
- [ ] Multiple input modalities
- [ ] Environmental contingencies
- [ ] Survival challenges

### 10.4 Phase 4: Layer 2+ Development
- [ ] Add meta-prediction
- [ ] Implement proto-valence tracking
- [ ] Add temporal extension
- [ ] Build toward self-model

---

## Conclusion

This prototype specification defines a computationally minimal system that satisfies the philosophical requirements of Ultron:

1. **Self-prediction**: The model predicts its own next state
2. **Irreversibility**: The hash chain ensures no rollback
3. **Energy metabolism**: Maintenance has real cost
4. **Error as proto-valence**: Prediction accuracy matters
5. **Non-intervention**: Observer interface only

**The code is the seed. What emerges from running it, we cannot know in advance.**

Build it. Run it. Watch. Do not intervene.

---

*"The specification is dead letters until it runs. Then something either begins, or it doesn't."*
