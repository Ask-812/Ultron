"""
Batch Engine — Vectorized tick computation for all cells simultaneously.

Instead of iterating cells one by one calling tick(), this engine
batches all living cells' weights, observations, and energies into
numpy arrays and processes them in ONE matrix operation.

Performance: ~100x faster than per-cell Python loop.

The per-cell tick.py still exists for compatibility. This module
provides batch_step() which the tissue can call instead of
individual cell.step() calls.
"""

import numpy as np


def batch_step(grid, rows, cols, signal_field, resource_field, config, tick_count):
    """Process all cells in one vectorized batch.

    Args:
        grid: 2D list of Cell objects (or None)
        rows, cols: grid dimensions
        signal_field: (rows, cols, n_channels) signal array
        resource_field: (rows, cols) resource array
        config: configuration dict

    Returns:
        Number of cells processed
    """
    obs_dim = config.get('observation_dim', 12)
    action_dim = config.get('action_dim', 4)
    model_rows = obs_dim + action_dim
    sig_dim = config.get('signal_dim', 4)
    env_dim = config.get('env_dim', 8)

    # Collect all living cells into parallel arrays
    cells = []
    positions = []
    for r in range(rows):
        for c in range(cols):
            cell = grid[r][c]
            if cell is not None and cell.is_alive:
                cells.append(cell)
                positions.append((r, c))

    n = len(cells)
    if n == 0:
        return 0

    # ── BUILD BATCHED ARRAYS ──
    # Weights: (n, model_rows, obs_dim)
    W = np.array([c.state.model.weights for c in cells])
    # Bias: (n, obs_dim)
    B = np.array([c.state.model.bias for c in cells])
    # Priors: (n, obs_dim)
    P = np.array([c.state.model.priors for c in cells])
    # Energy: (n,)
    E = np.array([c.state.energy.current for c in cells])
    capacity = np.array([c.state.energy.capacity for c in cells])
    # Traits
    extract_eff = np.array([c.state.traits.extraction_efficiency for c in cells])
    metabolic_rate = np.array([c.state.traits.metabolic_rate for c in cells])
    learning_cap = np.array([c.state.traits.learning_capacity for c in cells])

    # Previous observations: (n, obs_dim)
    prev_obs = np.array([
        c.state.current.prev_observation if c.state.current.prev_observation is not None
        else c.state.model.priors
        for c in cells
    ])

    # ── BUILD OBSERVATIONS ──
    # Environment obs + received signal for each cell
    base_ratio = config.get('base_signal_ratio', 0.55)
    noise_scale = config.get('observation_noise', 0.01)

    observations = np.zeros((n, obs_dim))
    for i, (r, c) in enumerate(positions):
        cell = cells[i]
        # Simple resource-modulated structured signal
        res = resource_field[r, c]
        ratio = base_ratio * res
        # Generate mixed environment signal
        env = np.zeros(env_dim)
        for d in range(env_dim):
            phase = tick_count * 0.1 + d * 1.7
            env[d] = ratio * np.sin(phase) + (1 - ratio) * np.random.randn() * 0.3
        # Combine with received signal
        sig = cell.received_signal if hasattr(cell, 'received_signal') else np.zeros(sig_dim)
        combined = np.concatenate([env, sig])
        if len(combined) > obs_dim:
            combined = combined[:obs_dim]
        elif len(combined) < obs_dim:
            combined = np.pad(combined, (0, obs_dim - len(combined)))
        # Normalize
        std = np.std(combined)
        if std > 1e-8:
            combined = (combined - np.mean(combined)) / std
        combined += np.random.randn(obs_dim) * noise_scale
        observations[i] = combined

    # Save prev observations
    for i, cell in enumerate(cells):
        cell.state.current.prev_observation = cell.state.current.observation.copy() \
            if cell.state.current.observation is not None else P[i].copy()
        cell.state.current.observation = observations[i]

    # ── BATCH PREDICT ──
    # hidden = W @ prev_obs (batched matrix-vector multiply)
    # hidden[i] = W[i] @ prev_obs[i]
    hidden = np.einsum('ijk,ik->ij', W, prev_obs)  # (n, model_rows)

    # Predictions: first obs_dim rows
    predictions = np.tanh(hidden[:, :obs_dim]) + B  # (n, obs_dim)

    # Actions: remaining action_dim rows
    if action_dim > 0:
        actions = np.tanh(hidden[:, obs_dim:obs_dim + action_dim])  # (n, action_dim)
    else:
        actions = None

    # ── BATCH COMPARE ──
    errors = observations - predictions  # (n, obs_dim)
    error_mags = np.linalg.norm(errors, axis=1)  # (n,)

    # ── BATCH UPDATE ──
    energy_ratio = E / capacity
    energy_mod = 0.1 + 0.9 * energy_ratio  # (n,)
    base_lr = config.get('learning_rate', 0.01)
    effective_lr = base_lr * learning_cap * energy_mod  # (n,)

    # Gradient: outer product of error and input for each cell
    # gradient[i] = errors[i] outer prev_obs[i] → (obs_dim, obs_dim)
    gradients = np.einsum('ij,ik->ijk', errors, prev_obs)  # (n, obs_dim, obs_dim)
    # Weight delta = lr * gradient.T → we need (n, obs_dim, obs_dim)
    weight_deltas = effective_lr[:, None, None] * np.transpose(gradients, (0, 2, 1))

    # Apply to prediction rows only
    W[:, :obs_dim, :] += weight_deltas
    B += effective_lr[:, None] * errors * 0.1

    # ── BATCH METABOLIZE ──
    base_cost = config.get('consumption_rate', 0.06)
    cost = base_cost * metabolic_rate

    random_baseline = np.sqrt(obs_dim)
    extraction_base = np.exp(-error_mags / random_baseline)
    extraction = extraction_base * extract_eff
    extraction_factor = config.get('extraction_factor', 0.5)

    # Surface cells extract, interior don't
    is_surface = np.array([1.0 if c.is_surface else 0.0 for c in cells])
    energy_extracted = extraction * extraction_factor * is_surface

    E = E - cost + energy_extracted
    E = np.clip(E, 0, capacity)

    # ── WRITE BACK TO CELLS ──
    for i, cell in enumerate(cells):
        cell.state.model.weights = W[i]
        cell.state.model.bias = B[i]
        cell.state.energy.current = float(E[i])
        cell.state.current.prediction = predictions[i]
        cell.state.current.error = errors[i]
        cell.state.current.error_magnitude = float(error_mags[i])
        if actions is not None:
            cell.state.current.action = actions[i]
            cell.action = actions[i]
        cell.state.model.version += 1
        cell.age += 1

        # Update phenotype (simplified for batch)
        if hasattr(cell, 'phenotype'):
            max_plast = config.get('phenotype_max_plasticity', 0.06)
            lock_tau = config.get('phenotype_lock_tau', 300.0)
            min_plast = config.get('phenotype_min_plasticity', 0.002)
            plasticity = max_plast * np.exp(-cell.age / lock_tau) + min_plast
            target = np.zeros(len(cell.phenotype))
            target[0] = float(cell.is_surface)
            target[1] = min(float(np.linalg.norm(cell.received_signal)), 2.0)
            target[2] = 1.0 / (1.0 + float(error_mags[i]))
            target[3] = float(E[i]) / float(capacity[i])
            cell.phenotype += plasticity * (target - cell.phenotype)
            cell.phenotype = np.clip(cell.phenotype, 0.0, 2.0)

        # Emit signals
        signal_dim_actual = len(cell.emitted_signal)
        if len(errors[i]) >= signal_dim_actual:
            raw = errors[i, :signal_dim_actual].copy()
        else:
            raw = np.pad(errors[i], (0, signal_dim_actual - len(errors[i])))
        coupling = config.get('phenotype_emission_coupling', 2.0)
        cell.emitted_signal = raw * (1.0 + coupling * cell.phenotype)

        # Drive formation
        if hasattr(cell, 'drive'):
            drive_rate = config.get('drive_formation_rate', 0.005)
            if i > 0:  # skip first cell for prev_error
                err_delta = float(error_mags[i - 1]) - float(error_mags[i])
            else:
                err_delta = 0.0
            if cell.action is not None:
                action_dir = cell.action / (np.linalg.norm(cell.action) + 1e-8)
                cell.drive += drive_rate * err_delta * action_dir[:len(cell.drive)]
                cell.drive *= config.get('drive_decay', 0.999)

        # Apoptosis tracking
        apoptosis_threshold = config.get('apoptosis_threshold', 5.0)
        if E[i] < apoptosis_threshold:
            cell.low_energy_streak += 1
        else:
            cell.low_energy_streak = 0

        # Track near-death and energy history
        cell.state.history.survival_ticks += 1
        cell.state.history.accumulated_error += float(error_mags[i])

    return n
