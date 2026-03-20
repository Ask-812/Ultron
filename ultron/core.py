from dataclasses import dataclass, field
from typing import Optional
import numpy as np
import hashlib
import time

@dataclass
class ModelState:
    weights: np.ndarray
    bias: np.ndarray
    priors: np.ndarray
    precision: np.ndarray
    version: int = 0

@dataclass
class HistoryState:
    birth_hash: bytes
    current_hash: bytes
    accumulated_error: float = 0.0
    peak_error: float = 0.0
    survival_ticks: int = 0
    near_death_count: int = 0
    death_cause: Optional[str] = None
    death_tick: Optional[int] = None

@dataclass
class CurrentState:
    observation: np.ndarray
    prediction: np.ndarray
    error: np.ndarray
    error_magnitude: float
    update_direction: np.ndarray
    prev_observation: np.ndarray = None  # Previous tick's observation for temporal prediction
    action: np.ndarray = None  # Action outputs from model (evolved, not learned)

@dataclass
class BirthTraits:
    """Permanent traits set at birth. Cannot change."""
    extraction_efficiency: float = 1.0  # Multiplier on extraction_factor
    metabolic_rate: float = 1.0  # Multiplier on consumption_rate
    learning_capacity: float = 1.0  # Multiplier on learning_rate

@dataclass
class EnergyState:
    current: float
    capacity: float
    consumption_rate: float
    last_intake: float = 0.0
    history: list = field(default_factory=list)

@dataclass
class TimeState:
    tick: int = 0
    birth_time: float = field(default_factory=time.time)
    current_time: float = field(default_factory=time.time)

@dataclass
class UltronState:
    model: ModelState
    history: HistoryState
    current: CurrentState
    energy: EnergyState
    time: TimeState
    traits: BirthTraits = field(default_factory=BirthTraits)
    is_alive: bool = True

def create_ultron(config: dict) -> UltronState:
    obs_dim = config.get('observation_dim', 32)
    action_dim = config.get('action_dim', 0)
    model_rows = obs_dim + action_dim
    
    seed = np.random.bytes(32)
    birth_time = time.time()
    birth_hash = hashlib.sha256(
        b"ULTRON_BIRTH" + seed + str(birth_time).encode()
    ).digest()
    
    model = ModelState(
        weights=np.random.randn(model_rows, obs_dim) * 0.01,
        bias=np.zeros(obs_dim),
        priors=np.ones(obs_dim) / obs_dim,
        precision=np.ones(obs_dim),
        version=0
    )
    
    # Action weight rows get larger initialization for stronger innate signals
    if action_dim > 0:
        action_weight_scale = config.get('action_weight_scale', 0.1)
        model.weights[obs_dim:, :] = np.random.randn(action_dim, obs_dim) * action_weight_scale
    
    history = HistoryState(
        birth_hash=birth_hash,
        current_hash=birth_hash
    )
    
    current = CurrentState(
        observation=np.zeros(obs_dim),
        prediction=np.zeros(obs_dim),
        error=np.zeros(obs_dim),
        error_magnitude=0.0,
        update_direction=np.zeros_like(model.weights),
        prev_observation=None  # No previous observation at birth
    )
    
    energy = EnergyState(
        current=config.get('starting_energy', 100.0),
        capacity=config.get('energy_capacity', 200.0),
        consumption_rate=config.get('consumption_rate', 1.0)
    )
    
    time_state = TimeState(
        tick=0,
        birth_time=birth_time,
        current_time=birth_time
    )
    
    # Birth traits: permanent variation set at birth
    # Default: ±2% variation in each trait
    trait_variation = config.get('birth_trait_variation', 0.02)
    
    traits = BirthTraits(
        extraction_efficiency=1.0 + np.random.uniform(-trait_variation, trait_variation),
        metabolic_rate=1.0 + np.random.uniform(-trait_variation, trait_variation),
        learning_capacity=1.0 + np.random.uniform(-trait_variation, trait_variation),
    )
    
    return UltronState(
        model=model,
        history=history,
        current=current,
        energy=energy,
        time=time_state,
        traits=traits,
        is_alive=True
    )


def reproduce(parent: UltronState, config: dict) -> tuple:
    """
    Asexual reproduction with trait inheritance and mutation.
    
    - Parent pays energy cost
    - Child inherits traits with small mutation
    - Child starts with fresh model (no learned weights)
    - Returns (parent, child) or (parent, None) if insufficient energy
    
    This is NOT sexual reproduction. This is fission-like division.
    """
    reproduction_cost = config.get('reproduction_cost', 50.0)
    mutation_rate = config.get('mutation_rate', 0.01)
    
    # Check if parent can afford reproduction
    if parent.energy.current < reproduction_cost:
        return (parent, None)
    
    # Pay the cost
    parent.energy.current -= reproduction_cost
    
    # Create child with inherited traits
    obs_dim = config.get('observation_dim', 32)
    
    seed = np.random.bytes(32)
    birth_time = time.time()
    birth_hash = hashlib.sha256(
        b"ULTRON_BIRTH" + seed + str(birth_time).encode() + parent.history.birth_hash
    ).digest()
    
    # Fresh model (no inherited learning)
    model = ModelState(
        weights=np.random.randn(obs_dim, obs_dim) * 0.01,
        bias=np.zeros(obs_dim),
        priors=np.ones(obs_dim) / obs_dim,
        precision=np.ones(obs_dim),
        version=0
    )
    
    history = HistoryState(
        birth_hash=birth_hash,
        current_hash=birth_hash
    )
    
    current = CurrentState(
        observation=np.zeros(obs_dim),
        prediction=np.zeros(obs_dim),
        error=np.zeros(obs_dim),
        error_magnitude=0.0,
        update_direction=np.zeros_like(model.weights),
        prev_observation=None
    )
    
    # Child starts with partial energy (split from parent)
    child_energy = reproduction_cost * 0.8  # 80% of cost goes to child
    energy = EnergyState(
        current=child_energy,
        capacity=config.get('energy_capacity', 200.0),
        consumption_rate=config.get('consumption_rate', 1.0)
    )
    
    time_state = TimeState(
        tick=0,
        birth_time=birth_time,
        current_time=birth_time
    )
    
    # Inherit traits with mutation
    traits = BirthTraits(
        extraction_efficiency=parent.traits.extraction_efficiency * (1 + np.random.uniform(-mutation_rate, mutation_rate)),
        metabolic_rate=parent.traits.metabolic_rate * (1 + np.random.uniform(-mutation_rate, mutation_rate)),
        learning_capacity=parent.traits.learning_capacity * (1 + np.random.uniform(-mutation_rate, mutation_rate)),
    )
    
    child = UltronState(
        model=model,
        history=history,
        current=current,
        energy=energy,
        time=time_state,
        traits=traits,
        is_alive=True
    )
    
    return (parent, child)
