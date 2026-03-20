"""
Cell — the multicellular unit of Ultron.

A Cell wraps one UltronState and adds:
  - signal emission (what this cell broadcasts to neighbors)
  - signal reception (what this cell receives from neighbors)
  - energy sharing (passive leakage to neighbors)
  - division (mitosis when energy is high enough)
  - apoptosis (death when energy stays critically low)

A Cell IS an Ultron. Same tick loop. Same physics.
The only addition is communication.
"""

# [ULTRON T100] 2026-03-18 18:19:27 — 60 cells, energy 80.0

import numpy as np
from .core import UltronState, BirthTraits, create_ultron
from .tick import tick


class Cell:
    """One cell in a multicellular Ultron tissue."""

    def __init__(self, state: UltronState, cell_id: int = 0, signal_dim: int = 4):
        self.state = state
        self.cell_id = cell_id
        self.received_signal = np.zeros(signal_dim)
        self.emitted_signal = np.zeros(signal_dim)
        self.phenotype = np.zeros(signal_dim)  # developmental identity, shaped by experience
        self.lineage_id = 0  # inherited from founder cell, used for multi-organism tracking
        self.action = None  # action outputs from model (evolved, not learned)
        self.age = 0
        self.low_energy_streak = 0  # ticks continuously below apoptosis threshold
        self.is_surface = True  # set by Tissue each tick
        self._predation_cooldown = 0  # ticks until next predation attempt allowed

        # ── Drive Formation ──
        # Internal persistent motivation vector. Accumulates based on whether
        # actions correlate with prediction error reduction. Not prescribed—
        # emerges from the cell's own experience over its lifetime.
        # Inspired by Marvel Ultron's motivation void: even with all power,
        # Ultron couldn't find his drive. Our cells BUILD their drives.
        self.drive = np.zeros(signal_dim)
        self._prev_error_mag = 0.0  # for computing error delta after action

    @property
    def is_alive(self) -> bool:
        return self.state.is_alive

    @property
    def energy(self) -> float:
        return self.state.energy.current

    @energy.setter
    def energy(self, val: float):
        self.state.energy.current = np.clip(val, 0, self.state.energy.capacity)

    def step(self, env_obs: np.ndarray, config: dict):
        """
        One cell tick.

        env_obs: the raw environmental observation at this grid position.
        Neighbor signals are already stored in self.received_signals
        by the Tissue before calling step().
        """
        if not self.is_alive:
            return

        # Combine environment observation with received signals.
        # Environment = local sensory data. Signals = relayed info from other cells.
        # Also inject previous error magnitude into signal — cells sense their own surprise
        prev_err = self.state.current.error_magnitude if hasattr(self.state.current, 'error_magnitude') else 0.0
        received_with_err = self.received_signal.copy()
        received_with_err[0] += min(prev_err * 0.1, 1.0)  # error bleeds into signal ch0
        # Drive vector modulates received signal — internal motivation colors perception
        drive = getattr(self, 'drive', np.zeros(len(received_with_err)))
        received_with_drive = received_with_err + drive * 0.1
        combined = np.concatenate([env_obs, received_with_drive])

        # Pad/truncate to observation_dim (env_dim + signal_dim)
        obs_dim = config.get('observation_dim', 12)
        if len(combined) > obs_dim:
            combined = combined[:obs_dim]
        elif len(combined) < obs_dim:
            combined = np.pad(combined, (0, obs_dim - len(combined)))

        # Interior cells cannot extract — only surface cells metabolize from environment
        if self.is_surface:
            self.state = tick(self.state, combined, config)
        else:
            cell_config = dict(config)
            cell_config['extraction_factor'] = 0.0
            self.state = tick(self.state, combined, cell_config)
        self.age += 1

        # Capture action outputs from model (if action_dim > 0)
        self.action = self.state.current.action

        # ── Drive Formation ──
        # Compare error before and after this tick's prediction.
        # If error decreased (prediction improved), reinforce the current action direction.
        # If error increased, weaken it. Over many ticks, this creates persistent
        # internal motivations — not prescribed goals, but emergent drives.
        if not hasattr(self, 'drive'):
            self.drive = np.zeros(len(self.received_signal))
            self._prev_error_mag = 0.0
        err_mag = self.state.current.error_magnitude
        err_delta = self._prev_error_mag - err_mag  # positive = improvement
        self._prev_error_mag = err_mag
        if self.action is not None:
            drive_rate = config.get('drive_formation_rate', 0.005)
            # Reinforce drive in the direction of action when error improves
            action_dir = self.action / (np.linalg.norm(self.action) + 1e-8)
            self.drive += drive_rate * err_delta * action_dir
            # Slow decay toward zero — drives fade without reinforcement
            self.drive *= config.get('drive_decay', 0.999)

        # Update phenotype: experience shapes identity.
        # Young cells are plastic (stem cells). Old cells are committed.
        self._update_phenotype(config)

        # Emit prediction error modulated by phenotype.
        # What a cell broadcasts is colored by what it has become.
        self._emit_signals(config)

        # Track apoptosis countdown
        apoptosis_threshold = config.get('apoptosis_threshold', 5.0)
        if self.energy < apoptosis_threshold:
            self.low_energy_streak += 1
        else:
            self.low_energy_streak = 0

    def _update_phenotype(self, config: dict):
        """Accumulate 4-channel phenotype from raw cell observables.

        Each channel tracks a different physical measurement of the cell's state.
        No channel has a prescribed behavioral role — downstream code uses the
        full phenotype vector (e.g. magnitude, distance) rather than individual
        channels for any physics coupling. Channel specialization emerges from
        the organism's own evolution.

        Plasticity decays with age creating critical periods.
        """
        max_plast = config.get('phenotype_max_plasticity', 0.05)
        lock_tau = config.get('phenotype_lock_tau', 200.0)
        min_plast = config.get('phenotype_min_plasticity', 0.001)
        plasticity = max_plast * np.exp(-self.age / lock_tau) + min_plast

        # Four distinct observables
        target = np.zeros(len(self.phenotype))
        target[0] = float(self.is_surface)
        target[1] = min(float(np.linalg.norm(self.received_signal)), 2.0)
        err = self.state.current.error_magnitude
        target[2] = 1.0 / (1.0 + err)  # sigmoid-like: low error -> high competence
        target[3] = self.energy / self.state.energy.capacity

        self.phenotype += plasticity * (target - self.phenotype)
        self.phenotype = np.clip(self.phenotype, 0.0, 2.0)

    def _emit_signals(self, config: dict = None):
        """Broadcast prediction error modulated by phenotype.

        Each cell emits what it failed to predict, colored by its
        developmental identity. A cell with phenotype[i] = +1 doubles
        its emission on channel i; phenotype[i] = -1 silences it.
        This creates signal channel specialization across cell types.
        """
        signal_dim = len(self.emitted_signal)
        error = self.state.current.error
        if len(error) >= signal_dim:
            raw = error[:signal_dim].copy()
        else:
            raw = np.pad(error, (0, signal_dim - len(error)))
        # Phenotype modulation: identity colors emission
        coupling = 0.5
        if config is not None:
            coupling = config.get('phenotype_emission_coupling', 2.0)
        self.emitted_signal = raw * (1.0 + coupling * self.phenotype)

    def should_divide(self, config: dict) -> bool:
        """Can this cell divide? Pure energy threshold — no signal coupling.

        Division readiness is a physical condition (enough energy),
        not prescribed by signal strength. The organism's evolved
        behavior determines WHERE and WHEN it places cells via action
        outputs, not a hardcoded signal→reproduction coupling.
        """
        if not self.is_alive:
            return False
        threshold = config.get('division_energy_threshold', 150.0)
        return self.energy >= threshold

    def should_die(self, config: dict) -> bool:
        """Should this cell undergo apoptosis?"""
        if not self.is_alive:
            return True
        streak_limit = config.get('apoptosis_streak', 500)
        return self.low_energy_streak >= streak_limit

    def divide(self, child_id: int, config: dict) -> 'Cell':
        """
        Mitosis: split into two cells.

        Parent keeps half energy, child gets half.
        Child inherits traits with tiny mutation.
        Child gets fresh model weights (no learned structure).
        """
        division_cost = config.get('division_cost', 0.0)
        total = self.energy - division_cost
        half = total / 2.0
        self.energy = half

        # Create child ultron
        child_state = create_ultron(config)

        # Inherit traits with micro-mutation
        mutation = config.get('cell_mutation_rate', 0.005)
        # Macromutation: 5% chance of a 10-30% jump in a trait
        # This creates real diversity — most mutations are small,
        # but occasionally a radical variant appears
        macro_chance = config.get('macromutation_chance', 0.05)
        macro_scale = config.get('macromutation_scale', 0.2)
        def mutate_trait(val):
            if np.random.random() < macro_chance:
                return val * (1 + np.random.uniform(-macro_scale, macro_scale))
            return val * (1 + np.random.uniform(-mutation, mutation))

        child_state.traits = BirthTraits(
            extraction_efficiency=mutate_trait(self.state.traits.extraction_efficiency),
            metabolic_rate=mutate_trait(self.state.traits.metabolic_rate),
            learning_capacity=mutate_trait(self.state.traits.learning_capacity),
        )

        child_state.energy.current = half
        child = Cell(child_state, cell_id=child_id, signal_dim=len(self.emitted_signal))
        # Partial phenotype inheritance: child starts halfway to parent's identity
        child.phenotype = self.phenotype * 0.5
        child.lineage_id = self.lineage_id

        # Drive inheritance: child inherits 30% of parent's drives
        # Drives build across generations — cultural momentum
        if hasattr(self, 'drive'):
            child.drive = self.drive * 0.3

        # Lamarckian inheritance: children can inherit parent's LEARNED prediction
        # weights, not just action weights. This transfers acquired knowledge across
        # generations — cultural/epigenetic inheritance.
        #
        # weight_inheritance_ratio controls the blend:
        #   0.0 = fresh random weights (original behavior)
        #   0.5 = 50% parent learned structure + 50% random
        #   1.0 = exact copy of parent's brain (pure Lamarckian)
        obs_dim = config.get('observation_dim', 12)
        weight_inheritance = config.get('weight_inheritance_ratio', 0.0)
        if weight_inheritance > 0:
            inherit_noise = config.get('weight_inheritance_noise', 0.01)
            # Blend inherited and fresh-random prediction weights
            child_state.model.weights[:obs_dim, :] = (
                weight_inheritance * self.state.model.weights[:obs_dim, :] +
                (1 - weight_inheritance) * child_state.model.weights[:obs_dim, :]
            )
            child_state.model.weights[:obs_dim, :] += (
                np.random.randn(obs_dim, obs_dim) * inherit_noise
            )
            # Also inherit bias
            child_state.model.bias = (
                weight_inheritance * self.state.model.bias +
                (1 - weight_inheritance) * child_state.model.bias
            )
            child_state.model.bias += np.random.randn(obs_dim) * inherit_noise

        # Inherit action weight rows from parent (innate behavior, evolved not learned).
        # Prediction weights are random (learned within lifetime).
        # Action weights are inherited with mutation (evolved across generations).
        action_dim = config.get('action_dim', 0)
        if action_dim > 0:
            action_mutation = config.get('action_mutation_rate', 0.02)
            child_state.model.weights[obs_dim:, :] = self.state.model.weights[obs_dim:, :].copy()
            # Macro-mutation on action weights too: 5% chance of 10-30% scramble
            if np.random.random() < config.get('macromutation_chance', 0.05):
                macro = config.get('macromutation_scale', 0.2)
                child_state.model.weights[obs_dim:, :] += np.random.randn(action_dim, obs_dim) * macro
            else:
                child_state.model.weights[obs_dim:, :] += np.random.randn(action_dim, obs_dim) * action_mutation

        return child


def create_cell(config: dict, cell_id: int = 0) -> Cell:
    """Create a fresh cell with default traits."""
    state = create_ultron(config)
    signal_dim = config.get('signal_dim', 4)
    return Cell(state, cell_id=cell_id, signal_dim=signal_dim)
