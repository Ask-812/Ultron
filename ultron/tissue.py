"""
Tissue — the spatial substrate for multicellular Ultron.

A Tissue is a 2D grid where each position either:
  - contains a living Cell
  - is empty (None)

Each global tick:
  1. Diffuse chemical signals across the grid
  2. Each cell senses environment + local signals
  3. Each cell runs its tick loop
  4. Passive energy leakage between neighbors
  5. Division: cells with surplus energy split into empty neighbors
  6. Apoptosis: cells with prolonged low energy die
  7. Record organism-level metrics

The environment provides spatially-varying input:
  - Center of the tissue gets cleaner signal
  - Edges get noisier signal
  This creates a natural gradient for differentiation.
"""

import numpy as np
from typing import Optional
from .cell import Cell, create_cell
from .environments import MixedEnvironment


class Tissue:
    """A 2D grid of Cells forming one multicellular organism."""

    def __init__(self, rows: int, cols: int, config: dict):
        self.rows = rows
        self.cols = cols
        self.config = config
        self.grid: list[list[Optional[Cell]]] = [[None] * cols for _ in range(rows)]

        # Signal field: multi-channel signals propagating across the grid.
        # Each cell broadcasts prediction error; signals decay per hop.
        # This creates information locality — the driver of centralization.
        signal_dim = config.get('signal_dim', 4)
        self.signal_field = np.zeros((rows, cols, signal_dim))

        self.tick_count = 0
        self.next_cell_id = 0
        self.total_births = 0
        self.total_deaths = 0
        self._env_cache = {}  # signal_ratio -> MixedEnvironment

        # Stigmergy field: chemical traces left by dying cells.
        # Death imprint: when a cell dies, its phenotype is deposited into
        # the stigmergy field at that position. Decays slowly.
        # Living cells sense this and can avoid death zones or exploit them.
        self.stigmergy_field = np.zeros((rows, cols, signal_dim))

        # Resource field: local energy availability [0, 1].
        # Surface cells deplete resources when extracting;
        # resources regenerate slowly. This creates genuine scarcity.
        self.resource_field = np.ones((rows, cols))

        # Optional heterogeneous landscape: resource patches
        self._init_landscape(config)

        # Dynamic patch tracking — food sources that drift
        self._patch_centers = []
        self._patch_radius = 0
        self._patch_richness = 1.0
        centers = config.get('landscape_patch_centers', None)
        if centers and config.get('landscape_type', 'uniform') == 'patches':
            self._patch_centers = [[float(r), float(c)] for r, c in centers]
            self._patch_radius = int(config.get('landscape_patch_radius', 0.2) * min(rows, cols))
            self._patch_richness = config.get('landscape_patch_richness', 1.0)
            # Give each patch a drift velocity (slow random direction)
            self._patch_velocities = []
            for _ in self._patch_centers:
                angle = np.random.uniform(0, 2 * np.pi)
                speed = config.get('patch_drift_speed', 0.0)
                self._patch_velocities.append([np.cos(angle) * speed,
                                                np.sin(angle) * speed])

        # Roaming hazard — a danger zone that moves and damages cells
        hazard_speed = config.get('hazard_speed', 0.0)
        if hazard_speed > 0:
            self._hazard_pos = [float(np.random.randint(0, rows)),
                                float(np.random.randint(0, cols))]
            self._hazard_radius = config.get('hazard_radius', 3)
            self._hazard_damage = config.get('hazard_damage', 5.0)
            angle = np.random.uniform(0, 2 * np.pi)
            self._hazard_vel = [np.cos(angle) * hazard_speed,
                                np.sin(angle) * hazard_speed]
        else:
            self._hazard_pos = None

        # Lineage tracking for ecosystem dynamics
        self.lineage_stats = {}  # lineage_id -> {count, energy, births, ...}
        self.predation_kills = 0  # total predation events this run
        self.toxin_damage_dealt = 0.0  # cumulative toxin damage this run
        self.toxin_events = 0  # total toxin emission events
    def _init_landscape(self, config: dict):
        """Initialize heterogeneous resource landscape.

        landscape_type controls the spatial pattern:
          'uniform' (default): all resources = 1.0
          'patches': circular oases of high resources in a low-resource desert
          'gradient': linear gradient from left (poor) to right (rich)
          'islands': several distinct high-resource islands
        """
        landscape = config.get('landscape_type', 'uniform')
        if landscape == 'uniform':
            return  # already initialized to 1.0

        base_level = config.get('landscape_base', 0.3)
        self.resource_field[:] = base_level

        if landscape == 'patches':
            n_patches = config.get('landscape_n_patches', 4)
            patch_radius = config.get('landscape_patch_radius', 0.2)  # fraction of grid
            patch_richness = config.get('landscape_patch_richness', 1.0)
            radius_cells = int(patch_radius * min(self.rows, self.cols))
            # Use explicit centers if provided, else generate randomly
            centers = config.get('landscape_patch_centers', None)
            if centers is None:
                rng = np.random.RandomState(config.get('landscape_seed', 42))
                centers = []
                for _ in range(n_patches):
                    pr = rng.randint(radius_cells, self.rows - radius_cells)
                    pc = rng.randint(radius_cells, self.cols - radius_cells)
                    centers.append((pr, pc))
            for pr, pc in centers:
                for r in range(self.rows):
                    for c in range(self.cols):
                        dist = np.sqrt((r - pr)**2 + (c - pc)**2)
                        if dist < radius_cells:
                            falloff = 1.0 - (dist / radius_cells)**2
                            self.resource_field[r, c] = max(
                                self.resource_field[r, c],
                                base_level + (patch_richness - base_level) * falloff
                            )

        elif landscape == 'gradient':
            for c in range(self.cols):
                self.resource_field[:, c] = base_level + (1.0 - base_level) * (c / max(1, self.cols - 1))

        elif landscape == 'islands':
            n_islands = config.get('landscape_n_patches', 3)
            rng = np.random.RandomState(config.get('landscape_seed', 42))
            island_r = int(0.15 * min(self.rows, self.cols))
            for _ in range(n_islands):
                ir = rng.randint(island_r + 1, self.rows - island_r - 1)
                ic = rng.randint(island_r + 1, self.cols - island_r - 1)
                for r in range(max(0, ir - island_r), min(self.rows, ir + island_r + 1)):
                    for c in range(max(0, ic - island_r), min(self.cols, ic + island_r + 1)):
                        dist = np.sqrt((r - ir)**2 + (c - ic)**2)
                        if dist <= island_r:
                            self.resource_field[r, c] = 1.0

        self.resource_field = np.clip(self.resource_field, 0.0, 1.0)
        # Store initial landscape for regeneration target
        self._landscape_capacity = self.resource_field.copy()

    @property
    def cell_count(self) -> int:
        return sum(1 for r in range(self.rows) for c in range(self.cols)
                   if self.grid[r][c] is not None and self.grid[r][c].is_alive)

    @property
    def total_energy(self) -> float:
        return sum(self.grid[r][c].energy
                   for r in range(self.rows) for c in range(self.cols)
                   if self.grid[r][c] is not None and self.grid[r][c].is_alive)

    def place_cell(self, row: int, col: int, cell: Optional[Cell] = None):
        """Place a cell at (row, col). Creates a new one if cell is None."""
        if cell is None:
            cell = create_cell(self.config, cell_id=self.next_cell_id)
            self.next_cell_id += 1
        self.grid[row][col] = cell

    def seed_center(self, n: int = 1):
        """Place n cells at the center of the grid (the 'zygote' pattern)."""
        cr, cc = self.rows // 2, self.cols // 2
        placed = 0
        for dr in range(-n, n + 1):
            for dc in range(-n, n + 1):
                r, c = cr + dr, cc + dc
                if 0 <= r < self.rows and 0 <= c < self.cols and placed < n:
                    self.place_cell(r, c)
                    placed += 1
                    if placed >= n:
                        return

    def seed_full(self):
        """Fill every grid position with a cell."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.place_cell(r, c)

    def get_env_observation(self, row: int, col: int, tick: int) -> np.ndarray:
        """
        Environment observation at a grid position.

        Spatial gradient: cells closer to center get higher signal_ratio.
        Seasonal modulation: base_signal_ratio oscillates with tick count
        when season_amplitude > 0 (summer = structured, winter = chaotic).
        """
        cr, cc = self.rows / 2.0, self.cols / 2.0
        max_dist = np.sqrt(cr ** 2 + cc ** 2)
        dist = np.sqrt((row - cr) ** 2 + (col - cc) ** 2)

        base_ratio = self.config.get('base_signal_ratio', 0.55)
        # Seasonal modulation: ratio oscillates over time
        amplitude = self.config.get('season_amplitude', 0.0)
        period = self.config.get('season_period', 1000.0)
        if amplitude > 0:
            base_ratio = base_ratio + amplitude * np.sin(2 * np.pi * tick / period)

        gradient_strength = self.config.get('spatial_gradient', 0.20)
        ratio = base_ratio + gradient_strength * (1.0 - dist / max_dist) - gradient_strength / 2.0
        # Resource depletion: depleted positions have lower signal quality
        ratio *= self.resource_field[row, col]
        ratio = np.clip(ratio, 0.0, 1.0)

        env_dim = self.config.get('env_dim', self.config.get('observation_dim', 8))
        # Cache environment objects to avoid re-allocation each tick
        key = round(ratio, 4)
        if key not in self._env_cache:
            self._env_cache[key] = MixedEnvironment(env_dim, signal_ratio=ratio)
        return self._env_cache[key].get_input(tick)

    def _get_neighbors(self, row: int, col: int):
        """Return list of (r, c) for von Neumann neighbors.

        Toroidal topology: edges wrap around. No walls.
        Every cell has exactly 4 neighbors.
        """
        nbrs = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr = (row + dr) % self.rows
            nc = (col + dc) % self.cols
            nbrs.append((nr, nc))
        return nbrs

    def _direction_index(self, r, c, nr, nc):
        """Get action direction (0=up,1=down,2=left,3=right) for toroidal neighbor."""
        dr = (nr - r + self.rows // 2) % self.rows - self.rows // 2
        dc = (nc - c + self.cols // 2) % self.cols - self.cols // 2
        if dr == -1: return 0
        if dr == 1: return 1
        if dc == -1: return 2
        return 3

    def _propagate_signals(self):
        """Hop-by-hop signal propagation with multiplicative decay.

        Each cell's signal field becomes the average of its neighbors' signals × decay.
        Information weakens with distance — creating locality.
        Cells must relay signals to extend their reach.
        """
        decay = self.config.get('signal_hop_decay', 0.9)

        # Toroidal wrapping: signals wrap around edges
        padded = np.pad(self.signal_field, ((1, 1), (1, 1), (0, 0)), mode='wrap')

        # Sum of von Neumann neighbors
        nbr_sum = (padded[:-2, 1:-1, :] + padded[2:, 1:-1, :] +
                   padded[1:-1, :-2, :] + padded[1:-1, 2:, :])

        # Every cell has exactly 4 neighbors (toroidal)
        self.signal_field = (nbr_sum / 4.0) * decay

    def _energy_sharing(self):
        """
        Signal-coupled energy diffusion with phenotype affinity.

        Base flow: gradient from high to low energy.
        Action coupling: local signal magnitude AMPLIFIES diffusion rate.
        Phenotype affinity: cells with similar phenotypes share more readily.

        Cells receiving strong signals become energy routers.
        Cells with different phenotypes create diffusion barriers.
        Together these produce tissue boundaries between cell types.
        """
        base_rate = self.config.get('energy_leak_rate', 0.01)
        if base_rate <= 0:
            return

        # Signal magnitude per cell (L2 norm across channels)
        sig_mag = np.linalg.norm(self.signal_field, axis=2)

        # Action coupling: diffusion_rate = base * (1 + coupling * signal)
        coupling = self.config.get('signal_energy_coupling', 1.0)
        rate_map = base_rate * (1.0 + coupling * sig_mag)

        # Phenotype affinity: build phenotype map for distance computation
        affinity_coupling = self.config.get('phenotype_affinity_coupling', 2.0)
        pheno_map = self.get_phenotype_map()  # (rows, cols, signal_dim)

        # Build energy array (0 for empty cells)
        energy = self.get_energy_map()
        alive = self.get_occupancy_map()
        deltas = np.zeros_like(energy)

        # For each direction, compute flow from higher to lower
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            # Shifted arrays
            nbr_energy = np.roll(energy, -dr, axis=0) if dr != 0 else np.roll(energy, -dc, axis=1)
            nbr_alive = np.roll(alive, -dr, axis=0) if dr != 0 else np.roll(alive, -dc, axis=1)
            nbr_rate = np.roll(rate_map, -dr, axis=0) if dr != 0 else np.roll(rate_map, -dc, axis=1)
            nbr_pheno = np.roll(pheno_map, -dr, axis=0) if dr != 0 else np.roll(pheno_map, -dc, axis=1)
            # Toroidal: np.roll already wraps — no boundary zeroing needed

            # Phenotype affinity: similar phenotypes share more readily
            pheno_dist = np.linalg.norm(pheno_map - nbr_pheno, axis=2)
            affinity = np.exp(-pheno_dist * affinity_coupling)

            # Flow where both cells alive and this cell has more energy
            # Rate is the MAX of the two cells' rates (hub pulls AND pushes)
            diff = energy - nbr_energy
            mask = (alive > 0) & (nbr_alive > 0) & (diff > 0)
            local_rate = np.maximum(rate_map, nbr_rate)
            flow = diff * local_rate * affinity * mask
            deltas -= flow  # lose from self
            # Add to neighbor (reverse shift)
            if dr != 0:
                deltas += np.roll(flow, dr, axis=0)
            else:
                deltas += np.roll(flow, dc, axis=1)

        # Apply deltas to living cells
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive and deltas[r, c] != 0:
                    cell.energy = cell.energy + deltas[r, c]

    def _handle_division(self):
        """Cells with enough energy divide into an empty neighbor."""
        # Collect candidates first to avoid modifying grid during iteration
        dividers = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive and cell.should_divide(self.config):
                    dividers.append((r, c))

        np.random.shuffle(dividers)

        for r, c in dividers:
            cell = self.grid[r][c]
            if not cell.should_divide(self.config):
                continue  # may have lost energy from a neighbor's division

            # Find empty neighbors
            empty = [(nr, nc) for nr, nc in self._get_neighbors(r, c)
                     if self.grid[nr][nc] is None or not self.grid[nr][nc].is_alive]

            # Competitive displacement: if no empty neighbors and cell has a lineage,
            # it can displace a foreign neighbor with much less energy.
            if not empty and hasattr(cell, 'lineage_id') and cell.lineage_id > 0:
                displacement_ratio = self.config.get('displacement_energy_ratio', 3.0)
                for nr, nc in self._get_neighbors(r, c):
                    nbr = self.grid[nr][nc]
                    if (nbr is not None and nbr.is_alive
                            and hasattr(nbr, 'lineage_id')
                            and nbr.lineage_id != cell.lineage_id
                            and cell.energy > nbr.energy * displacement_ratio):
                        # Displace the weaker foreign cell
                        nbr.state.is_alive = False
                        self.grid[nr][nc] = None
                        self.total_deaths += 1
                        empty = [(nr, nc)]
                        break

            if not empty:
                continue

            # Choose division target: action-directed or random
            action_coupling = self.config.get('action_division_coupling', 0.0)
            if (action_coupling > 0.0 and cell.action is not None
                    and len(cell.action) >= 4 and len(empty) > 1):
                # Score each neighbor using action vector magnitude as a general bias
                # Action outputs are not mapped to cardinal directions — instead
                # total action magnitude modulates resource-based preference
                act_mag = float(np.linalg.norm(cell.action))
                best_pos = None
                best_score = -np.inf
                for pos in empty:
                    nr, nc = pos
                    score = self.resource_field[nr, nc] + action_coupling * act_mag * self.resource_field[nr, nc]
                    if score > best_score:
                        best_score = score
                        best_pos = pos
                nr, nc = best_pos
            else:
                nr, nc = empty[np.random.randint(len(empty))]

            child = cell.divide(self.next_cell_id, self.config)
            self.next_cell_id += 1
            self.grid[nr][nc] = child
            self.total_births += 1

    def _handle_apoptosis(self):
        """Remove cells that have been starving too long or already dead.

        When a cell dies, it leaves a chemical imprint (stigmergy) at its
        position — its phenotype deposited into the stigmergy field. This
        creates a spatial death-memory that surviving cells can sense.

        Also cleans up cells killed by energy exhaustion in tick() —
        these have is_alive=False but remain in the grid.
        """
        death_imprint = self.config.get('death_imprint_strength', 1.0)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None:
                    continue
                # Already dead (energy exhaustion in tick) — clean up
                if not cell.is_alive:
                    if death_imprint > 0 and hasattr(cell, 'phenotype'):
                        self.stigmergy_field[r, c] += cell.phenotype * death_imprint
                    self.grid[r][c] = None
                    self.total_deaths += 1
                    continue
                # Alive but should die (apoptosis from prolonged starvation)
                if cell.should_die(self.config):
                    if death_imprint > 0 and hasattr(cell, 'phenotype'):
                        self.stigmergy_field[r, c] += cell.phenotype * death_imprint
                    cell.state.is_alive = False
                    self.grid[r][c] = None
                    self.total_deaths += 1

    def _handle_predation(self):
        """Inter-lineage predation with evolved attack/defense arms race.

        A cell can consume an adjacent cell if:
          1. They belong to different lineages
          2. The predator's energy exceeds prey's by effective_ratio
          3. The predator has not consumed recently (cooldown)
          4. The prey fails to evade

        v0.9.0 evolutionary arms race mechanics:

        ATTACK: Action magnitude amplifies predation power.
          effective_ratio = base_ratio / (1 + action_power * ||action||)
          Cells with larger evolved action weights need LESS energy dominance.
          This makes aggression an evolvable heritable trait.

        DEFENSE: Prey competence enables evasion.
          dodge_probability = evasion_scaling * phenotype[2]
          Cells with low prediction error (high competence) can dodge attacks.
          This makes prediction quality a survival trait, not just efficiency.

        ALARM: When a cell is consumed, nearby same-lineage cells receive
          a burst signal. This creates danger awareness and can trigger
          migration away from predation zones.
        """
        if not self.config.get('predation_enabled', False):
            return

        energy_ratio = self.config.get('predation_energy_ratio', 2.0)
        efficiency = self.config.get('predation_efficiency', 0.5)
        cooldown = self.config.get('predation_cooldown', 10)
        action_threshold = self.config.get('predation_action_threshold', 0.0)
        death_imprint = self.config.get('death_imprint_strength', 1.0)
        action_power = self.config.get('predation_action_power', 0.0)
        evasion_scaling = self.config.get('predation_evasion_scaling', 0.0)
        alarm_strength = self.config.get('predation_alarm_strength', 0.0)

        # Collect predation candidates
        predators = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None or not cell.is_alive:
                    continue
                # Cooldown: skip if recently consumed
                if hasattr(cell, '_predation_cooldown') and cell._predation_cooldown > 0:
                    cell._predation_cooldown -= 1
                    continue
                # Action threshold: only cells with strong actions attempt predation
                if action_threshold > 0 and cell.action is not None:
                    if np.linalg.norm(cell.action) < action_threshold:
                        continue
                predators.append((r, c))

        np.random.shuffle(predators)

        for r, c in predators:
            cell = self.grid[r][c]
            if cell is None or not cell.is_alive:
                continue

            # Action-coupled predation power: higher action magnitude = lower threshold
            action_mag = 0.0
            if cell.action is not None:
                action_mag = float(np.linalg.norm(cell.action))
            effective_ratio = energy_ratio / (1.0 + action_power * action_mag)

            # Find adjacent foreign cells (different lineage)
            prey_candidates = []
            for nr, nc in self._get_neighbors(r, c):
                nbr = self.grid[nr][nc]
                if (nbr is not None and nbr.is_alive
                        and hasattr(nbr, 'lineage_id')
                        and nbr.lineage_id != cell.lineage_id):
                    prey_candidates.append((nr, nc, nbr))

            if not prey_candidates:
                continue

            # Pick the weakest prey neighbor
            prey_candidates.sort(key=lambda x: x[2].energy)
            pr, pc, prey = prey_candidates[0]

            # Predation condition: energy dominance (action-modulated)
            if cell.energy < prey.energy * effective_ratio:
                continue

            # Phenotype-based evasion: prey's overall phenotype magnitude affects dodge chance
            # No specific channel is "competence" — the full phenotype contributes
            if evasion_scaling > 0 and hasattr(prey, 'phenotype'):
                pheno_mag = float(np.linalg.norm(prey.phenotype)) / len(prey.phenotype)
                dodge_prob = evasion_scaling * pheno_mag
                if np.random.random() < dodge_prob:
                    continue  # Prey escapes!

            # Consume: predator gains energy, prey dies
            gained = prey.energy * efficiency
            cell.energy = cell.energy + gained

            # ── Predatory Knowledge Absorption ──
            # The predator absorbs a fraction of the prey's neural weights.
            # Horizontal knowledge transfer through consumption — the predator
            # literally learns from what it eats. Inspired by Marvel Ultron
            # absorbing Adam Warlock's body to gain his capabilities.
            absorb_rate = self.config.get('predation_knowledge_absorb', 0.05)
            if absorb_rate > 0:
                obs_dim = self.config.get('observation_dim', 12)
                # Blend prediction weights (learned knowledge)
                pred_w = cell.state.model.weights[:obs_dim, :]
                prey_w = prey.state.model.weights[:obs_dim, :]
                cell.state.model.weights[:obs_dim, :] = (
                    (1 - absorb_rate) * pred_w + absorb_rate * prey_w
                )
                # Also absorb drive — consume the prey's motivations
                if hasattr(prey, 'drive') and hasattr(cell, 'drive'):
                    cell.drive += prey.drive * absorb_rate * 0.5

            # Death imprint for prey
            if death_imprint > 0 and hasattr(prey, 'phenotype'):
                self.stigmergy_field[pr, pc] += prey.phenotype * death_imprint

            # Alarm signal: alert same-lineage neighbors of the predation event
            if alarm_strength > 0:
                prey_lineage = prey.lineage_id
                for anr, anc in self._get_neighbors(pr, pc):
                    ally = self.grid[anr][anc]
                    if (ally is not None and ally.is_alive
                            and hasattr(ally, 'lineage_id')
                            and ally.lineage_id == prey_lineage):
                        # Burst signal: all channels get alarm_strength
                        self.signal_field[anr, anc] += alarm_strength

            prey.state.is_alive = False
            self.grid[pr][pc] = None
            self.total_deaths += 1
            self.predation_kills += 1

            # Set cooldown
            if not hasattr(cell, '_predation_cooldown'):
                cell._predation_cooldown = 0
            cell._predation_cooldown = cooldown

    def _apply_quorum_sensing(self):
        """Modulate cell actions based on local density of same-lineage allies.

        When many allies surround a cell, it boosts action magnitude (coordinated
        aggression / pack behavior). When isolated, it reduces actions (conserve
        energy, stealth mode). This creates emergent group coordination without
        any explicit communication — purely from local density sensing.
        """
        if not self.config.get('quorum_sensing_enabled', False):
            return

        quorum_threshold = self.config.get('quorum_threshold', 4)
        quorum_boost = self.config.get('quorum_boost', 0.3)
        quorum_radius = self.config.get('quorum_radius', 2)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None or not cell.is_alive or cell.action is None:
                    continue

                # Count same-lineage allies within quorum_radius (Manhattan)
                ally_count = 0
                for dr in range(-quorum_radius, quorum_radius + 1):
                    for dc in range(-quorum_radius, quorum_radius + 1):
                        if dr == 0 and dc == 0:
                            continue
                        if abs(dr) + abs(dc) > quorum_radius:
                            continue
                        nr, nc = r + dr, c + dc
                        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                            continue
                        n = self.grid[nr][nc]
                        if (n is not None and n.is_alive
                                and n.lineage_id == cell.lineage_id):
                            ally_count += 1

                # Scale actions: boost when above threshold, dampen when below
                if ally_count >= quorum_threshold:
                    scale = 1.0 + quorum_boost * (ally_count - quorum_threshold + 1)
                else:
                    scale = 0.5 + 0.5 * (ally_count / max(quorum_threshold, 1))
                cell.action = cell.action * scale

    def _handle_toxins(self):
        """Chemical warfare: cells emit toxins that damage nearby foreign cells.

        Toxin output is proportional to action magnitude — an evolved trait.
        Organisms with larger action weights produce more toxin, but pay an
        energy cost. Toxin damages foreign-lineage cells within toxin_range
        (Manhattan distance), with damage falling off with distance.
        Same-lineage cells are immune (self-recognition).

        This creates genuine chemical arms races:
        - High action magnitude = strong toxin BUT high metabolic cost
        - Selection favors just enough toxin to deter neighbors
        - Organisms on resource-poor patches can't afford high toxin output
        - Dense organisms produce more total toxin, creating area denial
        """
        if not self.config.get('toxin_enabled', False):
            return

        toxin_rate = self.config.get('toxin_emission_rate', 0.1)
        toxin_damage = self.config.get('toxin_damage_rate', 0.5)
        toxin_range = self.config.get('toxin_range', 3)
        toxin_cost = self.config.get('toxin_cost_rate', 0.1)
        toxin_resistance = self.config.get('toxin_resistance_scaling', 0.0)

        # Collect all living cells
        cells_list = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    cells_list.append((r, c, cell))

        # Each cell emits toxin proportional to action magnitude
        for r, c, cell in cells_list:
            if cell.action is None:
                continue
            toxin_output = float(np.linalg.norm(cell.action)) * toxin_rate
            if toxin_output < 0.001:
                continue

            # Pay metabolic cost for toxin production
            cost = toxin_output * toxin_cost
            cell.energy = max(0, cell.energy - cost)

            # Damage foreign cells within Manhattan distance
            emitter_lineage = cell.lineage_id
            for dr in range(-toxin_range, toxin_range + 1):
                for dc in range(-toxin_range, toxin_range + 1):
                    dist = abs(dr) + abs(dc)
                    if dist == 0 or dist > toxin_range:
                        continue
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                        continue
                    target = self.grid[nr][nc]
                    if target is None or not target.is_alive:
                        continue
                    if target.lineage_id == emitter_lineage:
                        continue  # self-immunity
                    # Damage falls off inversely with distance
                    dmg = toxin_output * toxin_damage / dist
                    # Phenotype-based resistance: overall phenotype magnitude resists toxins
                    # No specific channel is "competence" — full phenotype contributes
                    if toxin_resistance > 0 and hasattr(target, 'phenotype'):
                        pheno_mag = float(np.linalg.norm(target.phenotype)) / len(target.phenotype)
                        resist = toxin_resistance * pheno_mag
                        dmg *= max(0.0, 1.0 - resist)
                    target.energy = max(0, target.energy - dmg)
                    self.toxin_damage_dealt += dmg

            self.toxin_events += 1

    def _emit_environmental_signals(self):
        """Inject environmental stimuli into signal field — channel-agnostic.

        Living cells transduce local resource levels and hazard proximity
        into ALL signal channels equally. No channel has a prescribed
        meaning — channel specialization emerges from the cells' own
        phenotype-modulated emission in _emit_signals().
        """
        env_signal_strength = self.config.get('env_signal_strength', 0.2)
        n_channels = self.signal_field.shape[2]
        per_channel = env_signal_strength / n_channels

        # Resource stimulus: proportional to local resource richness
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    res = self.resource_field[r, c]
                    self.signal_field[r, c, :] += res * per_channel

        # Hazard stimulus: proximity creates signal intensity, spread across all channels
        if hasattr(self, '_hazard_pos') and self._hazard_pos is not None:
            hr, hc = self._hazard_pos[0], self._hazard_pos[1]
            sense_range = self._hazard_radius * 2.5
            hazard_strength = self.config.get('hazard_signal_strength', 0.3)
            per_ch_hazard = hazard_strength / n_channels
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    if cell is not None and cell.is_alive:
                        dr = min(abs(r - hr), self.rows - abs(r - hr))
                        dc = min(abs(c - hc), self.cols - abs(c - hc))
                        dist = np.sqrt(dr**2 + dc**2)
                        if dist < sense_range:
                            intensity = 1.0 - dist / sense_range
                            self.signal_field[r, c, :] += intensity * per_ch_hazard

    def _handle_migration(self):
        """Surface cells migrate toward fresh resources and signal gradients.

        Migration is driven by three forces:
          1. Resource gradient — move toward richer soil
          2. Signal gradient — move toward food signals (ch0),
             away from danger signals (ch1)
          3. Stigmergy avoidance — avoid death traces
          4. Action bias — cell's evolved directional preference

        This creates coordinated organism-level movement:
        edge sensors detect food/danger → signals propagate inward →
        cells on the far side migrate in response → the whole body moves.
        """
        migration_cost = self.config.get('migration_energy_cost', 2.0)
        resource_threshold = self.config.get('migration_resource_threshold', 0.5)
        signal_migration_weight = self.config.get('signal_migration_weight', 0.4)

        # Collect candidates: surface cells at depleted positions with enough energy
        migrants = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if (cell is not None and cell.is_alive and cell.is_surface
                        and self.resource_field[r, c] < resource_threshold
                        and cell.energy > migration_cost * 3):
                    migrants.append((r, c))

        np.random.shuffle(migrants)

        for r, c in migrants:
            cell = self.grid[r][c]
            if cell is None or not cell.is_alive:
                continue

            # Find empty neighbor with the highest combined score
            action_coupling = self.config.get('action_division_coupling', 0.0)
            best_pos = None
            best_score = self.resource_field[r, c]
            stigmergy_avoidance = self.config.get('stigmergy_avoidance', 0.0)

            # Current signal magnitude for gradient computation (channel-agnostic)
            my_sig_mag = float(np.linalg.norm(self.signal_field[r, c, :]))

            for nr, nc in self._get_neighbors(r, c):
                if (self.grid[nr][nc] is None or not self.grid[nr][nc].is_alive):
                    score = self.resource_field[nr, nc]
                    # Avoid positions where many cells have died
                    if stigmergy_avoidance > 0:
                        stig_mag = float(np.linalg.norm(self.stigmergy_field[nr, nc]))
                        score -= stig_mag * stigmergy_avoidance
                    if (action_coupling > 0.0 and cell.action is not None
                            and len(cell.action) >= 4):
                        direction = self._direction_index(r, c, nr, nc)
                        score += action_coupling * cell.action[direction]
                    # Signal gradient: move toward higher total signal magnitude
                    # No channel has prescribed meaning — cells follow aggregate gradient
                    if signal_migration_weight > 0:
                        nbr_sig_mag = float(np.linalg.norm(self.signal_field[nr, nc, :]))
                        sig_gradient = nbr_sig_mag - my_sig_mag
                        score += signal_migration_weight * sig_gradient
                    if score > best_score:
                        best_score = score
                        best_pos = (nr, nc)

            if best_pos is not None:
                nr, nc = best_pos
                self.grid[nr][nc] = cell
                self.grid[r][c] = None
                cell.energy -= migration_cost

    def step(self):
        """One global tissue tick."""
        # 1. Propagate signals (hop-by-hop with decay)
        self._propagate_signals()

        # 2. Inject cell emissions into signal field
        emission_strength = self.config.get('signal_emission_strength', 0.3)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    self.signal_field[r, c] += cell.emitted_signal * emission_strength

        # 2b. Environmental chemotaxis: inject food/hazard signals
        self._emit_environmental_signals()

        # 3. Surface status, signal delivery, and BATCHED cell step
        #
        # First pass: set surface status and deliver signals (lightweight)
        signal_transform = self.config.get('tissue_signal_transform', True)
        do_transform = signal_transform and (self.tick_count % 2 == 1)
        stigmergy_coupling = self.config.get('stigmergy_sensing', 0.0)

        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None or not cell.is_alive:
                    continue
                nbrs = self._get_neighbors(r, c)
                cell.is_surface = any(
                    self.grid[nr][nc] is None or not self.grid[nr][nc].is_alive
                    for nr, nc in nbrs
                )
                raw_signal = self.signal_field[r, c].copy()
                if stigmergy_coupling > 0:
                    raw_signal += self.stigmergy_field[r, c] * stigmergy_coupling
                if do_transform and hasattr(cell.state, 'model'):
                    sig_dim = len(raw_signal)
                    w_block = cell.state.model.weights[:sig_dim, :sig_dim]
                    transformed = np.tanh(w_block @ raw_signal) * 0.5 + raw_signal * 0.5
                    cell.received_signal = transformed
                else:
                    cell.received_signal = raw_signal

        # Second pass: BATCHED tick — all cells processed simultaneously via numpy
        from .batch_engine import batch_step
        batch_step(self.grid, self.rows, self.cols,
                   self.signal_field, self.resource_field,
                   self.config, self.tick_count)

        # 4. Quorum sensing: every 3rd tick only (expensive)
        if self.tick_count % 3 == 0:
            self._apply_quorum_sensing()

        # 5. Toxin warfare: every 2nd tick
        if self.tick_count % 2 == 0:
            self._handle_toxins()

        # 6. Predation
        self._handle_predation()

        # 7. Energy sharing: every 2nd tick (expensive numpy ops)
        if self.tick_count % 2 == 0:
            self._energy_sharing()

        # 8. Division
        self._handle_division()

        # 9. Apoptosis
        self._handle_apoptosis()

        # 10. Migration: every 2nd tick
        if self.tick_count % 2 == 0:
            self._handle_migration()

        # 11. Resource depletion and regeneration
        depletion = self.config.get('resource_depletion_rate', 0.0)
        regen = self.config.get('resource_regen_rate', 0.0)
        if depletion > 0:
            for r in range(self.rows):
                for c in range(self.cols):
                    cell = self.grid[r][c]
                    if cell is not None and cell.is_alive and cell.is_surface:
                        self.resource_field[r, c] = max(0.0, self.resource_field[r, c] - depletion)
        if regen > 0:
            # Regenerate toward landscape capacity (not always 1.0)
            if hasattr(self, '_landscape_capacity'):
                self.resource_field = np.clip(
                    self.resource_field + regen * self._landscape_capacity,
                    0.0, self._landscape_capacity
                )
            else:
                self.resource_field = np.clip(self.resource_field + regen, 0.0, 1.0)

        # 12. Detect fragmentation: disconnected cell groups get new lineage IDs
        frag_enabled = self.config.get('fragmentation_enabled', False)
        if frag_enabled and self.tick_count % self.config.get('fragmentation_interval', 50) == 0:
            self._detect_fragments()

        # 13. Stigmergy decay: death traces fade over time
        stigmergy_decay = self.config.get('stigmergy_decay', 0.995)
        self.stigmergy_field *= stigmergy_decay

        # 14. Dynamic landscape: random world events
        self._dynamic_landscape()

        # 15. Drift resource patches — food sources slowly move
        self._drift_patches()

        # 16. Move roaming hazard zone — damages cells it touches
        self._move_hazard()

        self.tick_count += 1

    def _dynamic_landscape(self):
        """Random world events that reshape the environment.

        Every event_interval ticks, one of these can happen:
          - Resource bloom: a new rich patch appears somewhere
          - Drought: a random patch loses resources
          - Seasonal shift: base resource level oscillates
          - Meteor: destroys resources in a small area

        This prevents stagnation and rewards exploration/adaptation.
        """
        interval = self.config.get('world_event_interval', 500)
        if interval <= 0 or self.tick_count % interval != 0:
            return
        if self.tick_count == 0:
            return

        event_type = np.random.choice(['bloom', 'drought', 'season', 'meteor'],
                                       p=[0.4, 0.2, 0.25, 0.15])

        if event_type == 'bloom':
            # New resource patch appears at random location
            cr = np.random.randint(0, self.rows)
            cc = np.random.randint(0, self.cols)
            radius = np.random.randint(2, max(3, self.rows // 8))
            for r in range(self.rows):
                for c in range(self.cols):
                    # Toroidal distance
                    dr = min(abs(r - cr), self.rows - abs(r - cr))
                    dc = min(abs(c - cc), self.cols - abs(c - cc))
                    dist = np.sqrt(dr**2 + dc**2)
                    if dist < radius:
                        boost = (1.0 - dist / radius) * 0.8
                        self.resource_field[r, c] = min(1.0, self.resource_field[r, c] + boost)
                        if hasattr(self, '_landscape_capacity'):
                            self._landscape_capacity[r, c] = max(
                                self._landscape_capacity[r, c],
                                self.resource_field[r, c])

        elif event_type == 'drought':
            # Random area loses resources
            cr = np.random.randint(0, self.rows)
            cc = np.random.randint(0, self.cols)
            radius = np.random.randint(2, max(3, self.rows // 6))
            for r in range(self.rows):
                for c in range(self.cols):
                    dr = min(abs(r - cr), self.rows - abs(r - cr))
                    dc = min(abs(c - cc), self.cols - abs(c - cc))
                    dist = np.sqrt(dr**2 + dc**2)
                    if dist < radius:
                        loss = (1.0 - dist / radius) * 0.6
                        self.resource_field[r, c] = max(0.05, self.resource_field[r, c] - loss)
                        if hasattr(self, '_landscape_capacity'):
                            self._landscape_capacity[r, c] = max(
                                0.05, self._landscape_capacity[r, c] - loss * 0.5)

        elif event_type == 'season':
            # Global resource shift — everything gets slightly richer or poorer
            shift = np.random.uniform(-0.08, 0.12)  # Biased positive — world slowly enriches
            self.resource_field = np.clip(self.resource_field + shift, 0.05, 1.0)
            if hasattr(self, '_landscape_capacity'):
                self._landscape_capacity = np.clip(self._landscape_capacity + shift * 0.5, 0.05, 1.0)

        elif event_type == 'meteor':
            # Small area devastated — resources wiped, cells killed
            cr = np.random.randint(0, self.rows)
            cc = np.random.randint(0, self.cols)
            radius = np.random.randint(1, max(2, self.rows // 12))
            for r in range(self.rows):
                for c in range(self.cols):
                    dr = min(abs(r - cr), self.rows - abs(r - cr))
                    dc = min(abs(c - cc), self.cols - abs(c - cc))
                    dist = np.sqrt(dr**2 + dc**2)
                    if dist < radius:
                        self.resource_field[r, c] = 0.02
                        if hasattr(self, '_landscape_capacity'):
                            self._landscape_capacity[r, c] = 0.05
                        cell = self.grid[r][c]
                        if cell is not None and cell.is_alive:
                            cell.energy = max(1.0, cell.energy * 0.3)

    def _drift_patches(self):
        """Move resource patch centers slowly across the grid.

        Each patch drifts according to its velocity, wrapping toroidally.
        The resource field and landscape capacity are rebuilt from the
        drifting centers. This forces the organism to track and chase
        its food — the first whole-organism behavior.

        Patches also wobble randomly to prevent perfect predictability.
        """
        if not self._patch_centers or not hasattr(self, '_patch_velocities'):
            return

        drift_speed = self.config.get('patch_drift_speed', 0.0)
        if drift_speed <= 0:
            return

        base_level = self.config.get('landscape_base', 0.25)

        # Update patch centers
        for i, (center, vel) in enumerate(zip(self._patch_centers, self._patch_velocities)):
            # Drift
            center[0] = (center[0] + vel[0]) % self.rows
            center[1] = (center[1] + vel[1]) % self.cols

            # Slight random wobble
            center[0] = (center[0] + np.random.uniform(-0.1, 0.1)) % self.rows
            center[1] = (center[1] + np.random.uniform(-0.1, 0.1)) % self.cols

            # Occasionally change drift direction (every ~200 ticks on avg)
            if np.random.random() < 0.005:
                angle = np.random.uniform(0, 2 * np.pi)
                vel[0] = np.cos(angle) * drift_speed
                vel[1] = np.sin(angle) * drift_speed

        # Rebuild resource field from drifting patch positions
        self.resource_field[:] = base_level
        radius = self._patch_radius
        richness = self._patch_richness

        for cr, cc in self._patch_centers:
            icr, icc = int(cr), int(cc)
            for r in range(self.rows):
                for c in range(self.cols):
                    # Toroidal distance
                    dr = min(abs(r - icr), self.rows - abs(r - icr))
                    dc = min(abs(c - icc), self.cols - abs(c - icc))
                    dist = np.sqrt(dr**2 + dc**2)
                    if dist < radius:
                        falloff = 1.0 - (dist / radius)**2
                        val = base_level + (richness - base_level) * falloff
                        self.resource_field[r, c] = max(self.resource_field[r, c], val)

        self.resource_field = np.clip(self.resource_field, 0.0, 1.0)
        self._landscape_capacity = self.resource_field.copy()

    def _move_hazard(self):
        """Move the roaming hazard zone and damage cells it touches.

        The hazard is an environmental threat — like a predator or
        toxic plume — that roams the grid independently. Any cells
        within its radius take energy damage each tick. Cells that
        die near the hazard leave stigmergy traces, which other cells
        can sense and avoid — creating pressure for threat avoidance.

        The hazard occasionally changes direction, making it
        unpredictable. The organism must develop awareness.
        """
        if not hasattr(self, '_hazard_pos') or self._hazard_pos is None:
            return

        # Move
        self._hazard_pos[0] = (self._hazard_pos[0] + self._hazard_vel[0]) % self.rows
        self._hazard_pos[1] = (self._hazard_pos[1] + self._hazard_vel[1]) % self.cols

        # Occasionally change direction
        if np.random.random() < 0.008:
            speed = np.sqrt(self._hazard_vel[0]**2 + self._hazard_vel[1]**2)
            angle = np.random.uniform(0, 2 * np.pi)
            self._hazard_vel = [np.cos(angle) * speed, np.sin(angle) * speed]

        # Damage cells within radius
        hr, hc = int(self._hazard_pos[0]), int(self._hazard_pos[1])
        radius = self._hazard_radius
        damage = self._hazard_damage

        for r in range(self.rows):
            for c in range(self.cols):
                dr = min(abs(r - hr), self.rows - abs(r - hr))
                dc = min(abs(c - hc), self.cols - abs(c - hc))
                dist = np.sqrt(dr**2 + dc**2)
                if dist < radius:
                    cell = self.grid[r][c]
                    if cell is not None and cell.is_alive:
                        falloff = 1.0 - dist / radius
                        cell.energy -= damage * falloff

    def get_energy_map(self) -> np.ndarray:
        """Return a 2D array of cell energies (0 for empty)."""
        m = np.zeros((self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    m[r, c] = cell.energy
        return m

    def get_error_map(self) -> np.ndarray:
        """Return a 2D array of cell prediction errors (0 for empty)."""
        m = np.zeros((self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    m[r, c] = cell.state.current.error_magnitude
        return m

    def get_occupancy_map(self) -> np.ndarray:
        """Return a 2D binary array (1 = alive cell, 0 = empty)."""
        m = np.zeros((self.rows, self.cols))
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    m[r, c] = 1
        return m

    def snapshot(self) -> dict:
        """Organism-level summary metrics."""
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    cells.append(cell)

        if not cells:
            return {
                'tick': self.tick_count,
                'cell_count': 0,
                'total_energy': 0.0,
                'mean_error': 0.0,
                'births': self.total_births,
                'deaths': self.total_deaths,
                'phenotype_diversity': 0.0,
                'phenotype_mean_mag': 0.0,
                'resource_mean': float(np.mean(self.resource_field)),
                'resource_min': float(np.min(self.resource_field)),
            }

        energies = [c.energy for c in cells]
        errors = [c.state.current.error_magnitude for c in cells]
        ages = [c.age for c in cells]
        ext = [c.state.traits.extraction_efficiency for c in cells]
        met = [c.state.traits.metabolic_rate for c in cells]

        return {
            'tick': self.tick_count,
            'cell_count': len(cells),
            'total_energy': sum(energies),
            'mean_energy': float(np.mean(energies)),
            'std_energy': float(np.std(energies)),
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'mean_age': float(np.mean(ages)),
            'max_age': max(ages),
            'mean_extraction': float(np.mean(ext)),
            'mean_metabolic': float(np.mean(met)),
            'births': self.total_births,
            'deaths': self.total_deaths,
            'signal_max': float(np.linalg.norm(self.signal_field, axis=2).max()),
            'signal_mean': float(np.linalg.norm(self.signal_field, axis=2).mean()),
            'phenotype_diversity': float(np.std([np.linalg.norm(c.phenotype) for c in cells])),
            'phenotype_mean_mag': float(np.mean([np.linalg.norm(c.phenotype) for c in cells])),
            'resource_mean': float(np.mean(self.resource_field)),
            'resource_min': float(np.min(self.resource_field)),
            'action_mean_mag': float(np.mean([np.linalg.norm(c.action) for c in cells
                                               if c.action is not None])) if any(c.action is not None for c in cells) else 0.0,
        }

    def get_signal_magnitude_map(self) -> np.ndarray:
        """Return a 2D array of signal magnitude (L2 norm across channels)."""
        return np.linalg.norm(self.signal_field, axis=2)

    def get_phenotype_map(self) -> np.ndarray:
        """Return a (rows, cols, signal_dim) array of cell phenotypes (zeros for empty)."""
        signal_dim = self.config.get('signal_dim', 4)
        m = np.zeros((self.rows, self.cols, signal_dim))
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    m[r, c] = cell.phenotype
        return m

    def _detect_fragments(self):
        """Detect disconnected cell groups and assign new lineage IDs.

        Uses flood-fill to find connected components within each lineage.
        If a lineage has >1 component, the smaller ones get new IDs.
        This implements organism-level reproduction via fragmentation.
        """
        # Build occupancy map with lineage info
        visited = [[False] * self.cols for _ in range(self.rows)]

        # Group cells by lineage
        lineage_cells = {}
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    lid = cell.lineage_id
                    if lid not in lineage_cells:
                        lineage_cells[lid] = []
                    lineage_cells[lid].append((r, c))

        next_lineage = max(lineage_cells.keys(), default=0) + 1

        for lid, positions in lineage_cells.items():
            if len(positions) < 2:
                continue

            # Flood-fill to find connected components within this lineage
            pos_set = set(positions)
            components = []
            visited_local = set()

            for start in positions:
                if start in visited_local:
                    continue
                # BFS
                component = []
                queue = [start]
                while queue:
                    r, c = queue.pop()
                    if (r, c) in visited_local:
                        continue
                    visited_local.add((r, c))
                    component.append((r, c))
                    for nr, nc in self._get_neighbors(r, c):
                        if (nr, nc) in pos_set and (nr, nc) not in visited_local:
                            queue.append((nr, nc))
                if component:
                    components.append(component)

            if len(components) <= 1:
                continue

            # Keep the largest component with the original lineage ID.
            # Assign new IDs to fragments above minimum viable size.
            # Tiny fragments (1-2 cells) stay with parent lineage — they're
            # just stray cells, not viable organisms.
            min_fragment = self.config.get('fragmentation_min_size', 5)
            components.sort(key=len, reverse=True)
            for fragment in components[1:]:
                if len(fragment) >= min_fragment:
                    new_lid = next_lineage
                    next_lineage += 1
                    for r, c in fragment:
                        self.grid[r][c].lineage_id = new_lid

    def get_lineage_map(self) -> np.ndarray:
        """Return a 2D array of lineage IDs (-1 for empty)."""
        m = np.full((self.rows, self.cols), -1)
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    m[r, c] = cell.lineage_id
        return m

    def ecosystem_snapshot(self) -> dict:
        """Per-lineage metrics for ecosystem tracking."""
        lineages = {}
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is not None and cell.is_alive:
                    lid = cell.lineage_id
                    if lid not in lineages:
                        lineages[lid] = {
                            'cells': [], 'energies': [], 'errors': [],
                            'ages': [], 'phenotypes': [], 'positions': [],
                            'extraction': [], 'metabolic': [],
                        }
                    d = lineages[lid]
                    d['cells'].append(cell)
                    d['energies'].append(cell.energy)
                    d['errors'].append(cell.state.current.error_magnitude)
                    d['ages'].append(cell.age)
                    d['phenotypes'].append(cell.phenotype.copy())
                    d['positions'].append((r, c))
                    d['extraction'].append(cell.state.traits.extraction_efficiency)
                    d['metabolic'].append(cell.state.traits.metabolic_rate)

        result = {'tick': self.tick_count, 'lineages': {}}
        for lid, d in lineages.items():
            positions = np.array(d['positions'])
            phenotypes = np.array(d['phenotypes'])
            result['lineages'][lid] = {
                'cell_count': len(d['cells']),
                'total_energy': sum(d['energies']),
                'mean_energy': float(np.mean(d['energies'])),
                'mean_error': float(np.mean(d['errors'])),
                'mean_age': float(np.mean(d['ages'])),
                'centroid': (float(positions[:, 0].mean()), float(positions[:, 1].mean())),
                'extent': float(positions.max(0).sum() - positions.min(0).sum()),
                'mean_extraction': float(np.mean(d['extraction'])),
                'mean_metabolic': float(np.mean(d['metabolic'])),
                'phenotype_mean': phenotypes.mean(0).tolist(),
                'phenotype_std': float(phenotypes.std()),
            }
        result['n_lineages'] = len(lineages)
        result['total_cells'] = sum(v['cell_count'] for v in result['lineages'].values())
        return result
