import numpy as np
import hashlib
import time
from .core import UltronState

def tick(state: UltronState, raw_input: np.ndarray, config: dict) -> UltronState:
    if not state.is_alive:
        return state
    if state.energy.current <= 0:
        return die(state, "energy_exhaustion")
    
    # Save previous observation before sensing new one
    state.current.prev_observation = state.current.observation.copy() if state.current.observation is not None else None
    
    state = sense(state, raw_input, config)
    state = predict(state, config)
    state = compare(state, config)
    state = update(state, config)
    state = metabolize(state, config)
    state = historify(state, config)
    state = advance(state, config)
    return state

def sense(state: UltronState, raw_input: np.ndarray, config: dict) -> UltronState:
    obs_dim = config.get('observation_dim', 32)
    clipped = np.clip(raw_input, -10, 10)
    std = np.std(clipped)
    if std > 1e-8:
        normalized = (clipped - np.mean(clipped)) / std
    else:
        normalized = clipped - np.mean(clipped)
    noise_scale = config.get('observation_noise', 0.01)
    noisy = normalized + np.random.randn(len(normalized)) * noise_scale
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
    """
    Generate prediction for current observation + action outputs.
    
    Uses prev_observation (if available) to enable temporal prediction.
    If action_dim > 0, the model has extra weight rows that produce
    action outputs — these are NOT trained by prediction error but
    evolve across generations through weight inheritance + mutation.
    """
    # Use previous observation if available, otherwise fall back to priors
    if state.current.prev_observation is not None:
        input_signal = state.current.prev_observation
    else:
        input_signal = state.model.priors
    
    hidden = state.model.weights @ input_signal
    obs_dim = config.get('observation_dim', 32)
    action_dim = config.get('action_dim', 0)
    
    # Prediction: first obs_dim outputs
    prediction = np.tanh(hidden[:obs_dim]) + state.model.bias
    state.current.prediction = prediction
    
    # Action: remaining action_dim outputs (if any)
    if action_dim > 0 and len(hidden) > obs_dim:
        state.current.action = np.tanh(hidden[obs_dim:obs_dim + action_dim])
    else:
        state.current.action = None
    
    return state

def compare(state: UltronState, config: dict) -> UltronState:
    error = state.current.observation - state.current.prediction
    error_magnitude = np.linalg.norm(error)
    state.current.error = error
    state.current.error_magnitude = error_magnitude
    return state

def update(state: UltronState, config: dict) -> UltronState:
    """
    Update model based on prediction error.
    
    Uses the same input signal as prediction for gradient computation.
    
    REGULATION: Learning rate is modulated by energy level.
    High energy → can afford aggressive change (effective_lr ≈ base_lr)
    Low energy → conserve structure (effective_lr ≈ 0.1 × base_lr)
    
    BIRTH TRAIT: learning_capacity multiplies base learning rate.
    
    This is not goal-seeking. This is metabolic regulation:
    starving cells slow growth, stressed systems conserve structure.
    """
    base_learning_rate = config.get('learning_rate', 0.01)
    
    # Apply birth trait: learning capacity
    birth_lr = base_learning_rate * state.traits.learning_capacity
    
    # === ENERGY MODULATION ===
    # Smooth, monotonic, bounded, never zero
    # f(energy) ranges from 0.1 (empty) to 1.0 (capacity)
    energy_ratio = state.energy.current / state.energy.capacity
    energy_modulation = 0.1 + 0.9 * energy_ratio
    
    # Effective learning rate = birth_lr × modulation
    effective_lr = birth_lr * energy_modulation
    
    # Use same input as prediction
    if state.current.prev_observation is not None:
        input_signal = state.current.prev_observation
    else:
        input_signal = state.model.priors
    
    gradient = np.outer(state.current.error, input_signal)
    weight_delta = effective_lr * gradient.T
    # Only update prediction rows — action rows evolve, not learn
    obs_dim = config.get('observation_dim', 32)
    state.model.weights[:obs_dim, :] += weight_delta
    state.model.bias += effective_lr * state.current.error * 0.1
    
    # Update priors (slow adaptation toward recent observations)
    # Also modulated by energy
    base_prior_rate = config.get('prior_learning_rate', 0.001)
    prior_rate = base_prior_rate * energy_modulation
    state.model.priors += prior_rate * (state.current.observation - state.model.priors)
    state.model.priors = np.clip(state.model.priors, 0.01, 0.99)
    state.model.priors /= np.sum(state.model.priors)
    
    # Update precision (also modulated)
    base_precision_rate = config.get('precision_learning_rate', 0.001)
    precision_rate = base_precision_rate * energy_modulation
    error_sq = state.current.error ** 2
    state.model.precision += precision_rate * (1.0 / (error_sq + 1e-8) - state.model.precision)
    
    state.model.version += 1
    # Store ACTUAL weight change, not raw gradient (metabolic cost is on realized change)
    state.current.update_direction = weight_delta
    return state

def metabolize(state: UltronState, config: dict) -> UltronState:
    """
    Metabolize: pay costs and earn energy.
    
    KEY CHANGE: Energy extraction is now CONTINGENT on prediction quality
    relative to what random guessing would achieve.
    
    - In structured environments: error < baseline → extract energy
    - In chaotic environments: error ≈ baseline → extract nothing
    
    This makes structure "edible" and chaos "barren".
    
    BIRTH TRAITS APPLIED:
    - extraction_efficiency: multiplier on energy extraction
    - metabolic_rate: multiplier on base consumption
    """
    
    # === COSTS (always paid) ===
    # Base cost modified by metabolic rate trait
    base_cost = state.energy.consumption_rate
    cost = base_cost * state.traits.metabolic_rate
    
    # Update cost: bigger changes cost more
    update_cost_factor = config.get('update_cost_factor', 0.1)
    update_magnitude = np.linalg.norm(state.current.update_direction.flatten())
    cost += update_magnitude * update_cost_factor
    
    # === ENERGY EXTRACTION (contingent on competence) ===
    # 
    # Random baseline: expected error if predicting randomly
    # For normalized observations with unit variance per dim, this is √(obs_dim)
    obs_dim = config.get('observation_dim', 32)
    random_baseline = np.sqrt(obs_dim)
    
    # How much better than random are we doing?
    actual_error = state.current.error_magnitude
    
    # Exponential extraction efficiency
    base_extraction_efficiency = np.exp(-actual_error / random_baseline)
    
    # Apply birth trait multiplier
    extraction_efficiency = base_extraction_efficiency * state.traits.extraction_efficiency
    
    # Environmental energy available
    environmental_richness = config.get('environmental_richness', 1.0)
    
    # Energy extracted = richness * efficiency * extraction_factor
    extraction_factor = config.get('extraction_factor', 0.5)
    energy_extracted = environmental_richness * extraction_efficiency * extraction_factor
    
    # === APPLY METABOLISM ===
    state.energy.current -= cost
    state.energy.current += energy_extracted
    state.energy.current = np.clip(state.energy.current, 0, state.energy.capacity)
    
    # Track history
    state.energy.history.append(state.energy.current)
    if len(state.energy.history) > 1000:
        state.energy.history = state.energy.history[-1000:]
    
    # Near-death tracking
    low_threshold = config.get('near_death_threshold', 10.0)
    if state.energy.current < low_threshold:
        state.history.near_death_count += 1
    
    return state

def historify(state: UltronState, config: dict) -> UltronState:
    state.history.accumulated_error += state.current.error_magnitude
    state.history.peak_error = max(state.history.peak_error, state.current.error_magnitude)
    state.history.survival_ticks += 1
    state_summary = (
        f"{state.time.tick}:{state.current.error_magnitude:.6f}:"
        f"{state.energy.current:.6f}:{state.model.version}"
    ).encode()
    state.history.current_hash = hashlib.sha256(
        state.history.current_hash + state_summary
    ).digest()
    return state

def advance(state: UltronState, config: dict) -> UltronState:
    state.time.tick += 1
    state.time.current_time = time.time()
    return state

def die(state: UltronState, cause: str) -> UltronState:
    state.is_alive = False
    state.history.death_cause = cause
    state.history.death_tick = state.time.tick
    death_summary = f"DEATH:{cause}:{state.time.tick}".encode()
    state.history.current_hash = hashlib.sha256(
        state.history.current_hash + death_summary
    ).digest()
    return state

def feed_energy(state: UltronState, amount: float) -> UltronState:
    if not state.is_alive:
        return state
    state.energy.current = min(state.energy.capacity, state.energy.current + amount)
    state.energy.last_intake = amount
    return state
