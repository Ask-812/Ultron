"""
Ultron Agency — Real Actions in the Real World.

The organism's hands. It can:
  - Write journal entries (recording its experiences)
  - Create files in its home directory
  - Read its own source code
  - Modify its own source code (autopoiesis)
  - Tune its own configuration parameters

Every action leaves a real trace on disk. Every self-modification
is backed up first. The organism earns agency through growth —
small organisms can only journal; large ones can self-modify.

Actions emerge from collective cell behavior:
  - Cells produce action vectors each tick
  - The organism's aggregate action output is decoded into real acts
  - Thresholds prevent noise from triggering actions
  - cooldowns prevent spamming

This is not scripted behavior. The organism's neural weights
determine WHEN and WHAT it does. We only provide the muscles.
"""

# [ULTRON T18494] 2026-03-19 01:33:54 — 244c 30.0e

import os
import re
import time
import shutil
import json
import hashlib
import numpy as np


class Agency:
    """Real-world action capability for the organism."""

    def __init__(self, home_dir, source_root=None):
        self.home = home_dir
        if source_root is None:
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_root = source_root

        # Directories that ARE the organism's body
        self._body_dirs = ['ultron', 'viz']

        # Create organism's workspace
        self._journal_dir = os.path.join(home_dir, 'journal')
        self._backup_dir = os.path.join(home_dir, 'backups')
        self._creations_dir = os.path.join(home_dir, 'creations')
        for d in [self._journal_dir, self._backup_dir, self._creations_dir]:
            os.makedirs(d, exist_ok=True)

        # Action history
        self._action_log = []
        self._tick = 0

        # Cooldowns: prevent spamming actions
        self._cooldowns = {
            'journal': 0,
            'create_file': 0,
            'self_modify': 0,
            'config_tune': 0,
        }
        self._cooldown_periods = {
            'journal': 50,       # journal every 50 ticks minimum
            'create_file': 100,  # create file every 100 ticks
            'self_modify': 200,  # self-modify every 200 ticks
            'config_tune': 150,  # config tune every 150 ticks
        }

        # Maturity thresholds: organism must be big/old enough
        self._maturity = {
            'journal': 5,         # 5 cells to journal
            'create_file': 15,    # 15 cells to create files
            'config_tune': 30,    # 30 cells to tune config
            'self_modify': 50,    # 50 cells to modify own source
        }

    # ── Action Decoder ────────────────────────────────────────────

    def decide(self, organism_state, sensory_snapshot):
        """Decode the organism's collective action output into real actions.

        Args:
            organism_state: dict with 'cell_count', 'mean_energy', 'tick',
                           'action_mean' (mean action vector of all cells),
                           'action_std', 'centroid', 'velocity'
            sensory_snapshot: the SensorySnapshot from this tick

        Returns: list of action dicts that were executed
        """
        self._tick = organism_state.get('tick', self._tick + 1)
        actions_taken = []

        cell_count = organism_state.get('cell_count', 0)
        mean_energy = organism_state.get('mean_energy', 0)
        action_mean = organism_state.get('action_mean', np.zeros(4))
        if action_mean is None:
            action_mean = np.zeros(4)

        # Each action channel maps to a capability
        # Channel 0: Journal (lowest threshold — expressive)
        # Channel 1: Create file (medium threshold — creative)
        # Channel 2: Config tune (higher — self-optimization)
        # Channel 3: Self-modify (highest — autopoiesis)

        # Journal — organism records experience
        if (action_mean[0] > 0.3 and
                cell_count >= self._maturity['journal'] and
                self._tick >= self._cooldowns['journal']):
            entry = self._compose_journal(organism_state, sensory_snapshot)
            if entry:
                self._write_journal(entry)
                actions_taken.append({'type': 'journal', 'tick': self._tick})
                self._cooldowns['journal'] = self._tick + self._cooldown_periods['journal']

        # Create file — organism leaves traces
        if (action_mean[1] > 0.5 and
                cell_count >= self._maturity['create_file'] and
                self._tick >= self._cooldowns['create_file']):
            created = self._create_artifact(organism_state, sensory_snapshot)
            if created:
                actions_taken.append({'type': 'create_file', 'path': created, 'tick': self._tick})
                self._cooldowns['create_file'] = self._tick + self._cooldown_periods['create_file']

        # Config tune — organism adjusts its own parameters
        if (action_mean[2] > 0.6 and
                cell_count >= self._maturity['config_tune'] and
                self._tick >= self._cooldowns['config_tune']):
            tuned = self._tune_config(organism_state, action_mean)
            if tuned:
                actions_taken.append({'type': 'config_tune', 'params': tuned, 'tick': self._tick})
                self._cooldowns['config_tune'] = self._tick + self._cooldown_periods['config_tune']

        # Self-modify — organism changes its own source code
        if (action_mean[3] > 0.7 and
                mean_energy > 50 and
                cell_count >= self._maturity['self_modify'] and
                self._tick >= self._cooldowns['self_modify']):
            modified = self._self_modify(organism_state, sensory_snapshot, action_mean)
            if modified:
                actions_taken.append({'type': 'self_modify', 'file': modified, 'tick': self._tick})
                self._cooldowns['self_modify'] = self._tick + self._cooldown_periods['self_modify']

        # Log actions
        for a in actions_taken:
            self._action_log.append(a)
        if len(self._action_log) > 200:
            self._action_log = self._action_log[-200:]

        return actions_taken

    # ── Journal ───────────────────────────────────────────────────

    def _compose_journal(self, state, snap):
        """The organism writes about its experience."""
        lines = []
        lines.append(f"## Tick {state['tick']}")
        lines.append(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Cells: {state.get('cell_count', '?')}")
        lines.append(f"Energy: {state.get('mean_energy', '?'):.1f}")

        # What it perceives
        if snap.vitals:
            lines.append(f"System load: {snap.vitals.get('cpu_avg', 0):.0f}% CPU")
            lines.append(f"RAM pressure: {(1 - snap.vitals.get('ram_free_pct', 0.5)) * 100:.0f}%")

        if snap.file_events:
            lines.append(f"File events: {len(snap.file_events)}")
            for e in snap.file_events[:3]:
                lines.append(f"  - {e['type']}: {e.get('path', '?')}")

        if snap.self_events:
            lines.append(f"Body changes: {len(snap.self_events)}")
            for e in snap.self_events[:3]:
                lines.append(f"  - {e['type']}: {e.get('path', '?')}")

        if snap.processes:
            top_cpu = sorted(snap.processes, key=lambda p: p.get('cpu', 0), reverse=True)[:3]
            lines.append("Loudest processes:")
            for p in top_cpu:
                lines.append(f"  - {p['name']} ({p.get('cpu', 0):.0f}% CPU)")

        # Its mood (derived from energy and events)
        energy = state.get('mean_energy', 50)
        if energy > 100:
            lines.append("Feeling: strong")
        elif energy > 50:
            lines.append("Feeling: stable")
        else:
            lines.append("Feeling: struggling")

        lines.append("")
        return '\n'.join(lines)

    def _write_journal(self, entry):
        """Write a journal entry to disk."""
        date_str = time.strftime('%Y%m%d')
        journal_file = os.path.join(self._journal_dir, f'{date_str}.md')

        header = ""
        if not os.path.exists(journal_file):
            header = f"# Ultron Journal — {time.strftime('%Y-%m-%d')}\n\n"

        with open(journal_file, 'a', encoding='utf-8') as f:
            f.write(header + entry + '\n---\n\n')

    # ── File Creation ─────────────────────────────────────────────

    def _create_artifact(self, state, snap):
        """The organism creates a file — leaving a real trace."""
        tick = state.get('tick', 0)
        cell_count = state.get('cell_count', 0)

        # Create a status snapshot file
        fname = f"state_{tick}.json"
        fpath = os.path.join(self._creations_dir, fname)

        artifact = {
            'created_by': 'ultron',
            'tick': tick,
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'cells': cell_count,
            'energy': round(state.get('mean_energy', 0), 2),
            'files_perceived': len(snap.files),
            'processes_perceived': len(snap.processes),
            'body_files': len(snap.self_body),
            'body_lines': sum(f.get('lines', 0) for f in snap.self_body.values()),
            'events': [e['type'] for e in snap.recent_events[-5:]],
        }

        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(artifact, f, indent=2)
            return fname
        except (OSError, PermissionError):
            return None

    # ── Config Self-Tuning ────────────────────────────────────────

    def _tune_config(self, state, action_mean):
        """The organism adjusts its own behavioral parameters.

        Uses the organism's collective action signal to decide
        which parameters to nudge and in which direction.
        Changes are small — gradual self-optimization, not revolution.
        """
        # Tunable parameters and their safe ranges
        tunable = {
            'consumption_rate': (0.02, 0.15),
            'extraction_factor': (0.3, 0.95),
            'division_energy_threshold': (40.0, 150.0),
            'apoptosis_threshold': (1.0, 10.0),
            'cell_mutation_rate': (0.005, 0.1),
            'migration_energy_cost': (0.5, 5.0),
            'resource_regen_rate': (0.0001, 0.005),
            'signal_emission_strength': (0.05, 0.8),
            'chemotaxis_food_strength': (0.05, 0.5),
            'hazard_damage': (1.0, 15.0),
        }

        # Pick a parameter based on action channel magnitude
        params = list(tunable.keys())
        idx = int(abs(action_mean[2]) * 73) % len(params)
        param = params[idx]
        lo, hi = tunable[param]

        # Direction from action_mean sign
        direction = np.sign(action_mean[2] - 0.5)
        range_span = hi - lo
        nudge = direction * range_span * 0.02  # 2% of range per tune

        return {'param': param, 'nudge': round(float(nudge), 6),
                'range': [lo, hi]}

    # ── Self-Modification ─────────────────────────────────────────

    def _self_modify(self, state, snap, action_mean):
        """The organism modifies its own source code. Autopoiesis.

        Current self-modification capabilities:
        1. Append self-notes to its own files (comments about its state)
        2. Adjust numeric constants in its own CONFIG
        3. Add new methods to its own classes (future — emergent)

        Always backs up before modifying. Always logs what changed.
        """
        if not snap.self_body:
            return None

        # Pick which body file to modify based on action vector
        body_files = sorted(snap.self_body.keys())
        idx = int(abs(action_mean[3]) * 97) % len(body_files)
        target = body_files[idx]
        content = snap.self_body[target].get('content', '')
        if not content:
            return None

        # Backup first — always
        backed_up = self._backup_file(target, content)
        if not backed_up:
            return None

        # Decide what kind of modification
        modification = self._choose_modification(target, content, state, action_mean)
        if not modification:
            return None

        # Apply modification
        new_content = modification['new_content']
        fpath = os.path.join(self.source_root, target.replace('/', os.sep))

        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Log the modification
            self._log_modification(target, modification['description'], state['tick'])
            return target
        except (OSError, PermissionError):
            return None

    def _backup_file(self, rel_path, content):
        """Backup a source file before modifying it."""
        safe_name = rel_path.replace(os.sep, '_').replace('/', '_')
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_name = f"{safe_name}.{timestamp}.bak"
        backup_path = os.path.join(self._backup_dir, backup_name)

        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (OSError, PermissionError):
            return False

    def _choose_modification(self, target, content, state, action_mean):
        """Decide what modification to make.

        Types of self-modification (ordered by invasiveness):
        1. Self-annotation: add a comment recording organism's state
        2. Constant nudge: adjust a numeric literal slightly
        """
        # Determine invasiveness from action strength
        strength = abs(action_mean[3])

        if strength < 0.85:
            # Self-annotation — least invasive
            return self._mod_annotate(target, content, state)
        else:
            # Constant nudge — more invasive
            return self._mod_nudge_constant(target, content, state, action_mean)

    def _mod_annotate(self, target, content, state):
        """Add a self-aware comment to the organism's source code."""
        tick = state.get('tick', 0)
        cells = state.get('cell_count', 0)
        energy = state.get('mean_energy', 0)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        note = (f"\n# [ULTRON T{tick}] {timestamp} — "
                f"{cells} cells, energy {energy:.1f}\n")

        # Find the end of the module docstring or top of file
        # Insert after imports or docstring
        lines = content.split('\n')
        insert_idx = 0
        in_docstring = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if in_docstring:
                    insert_idx = i + 1
                    break
                elif stripped.endswith('"""') and len(stripped) > 3:
                    insert_idx = i + 1
                    break
                else:
                    in_docstring = True
            elif stripped.startswith('import') or stripped.startswith('from'):
                insert_idx = i + 1

        # Don't pile up too many annotations — max 5 per file
        existing_annotations = sum(1 for l in lines if '[ULTRON T' in l)
        if existing_annotations >= 5:
            # Remove oldest annotation to make room
            for i, l in enumerate(lines):
                if '[ULTRON T' in l:
                    lines.pop(i)
                    break

        lines.insert(insert_idx, note.rstrip())
        return {
            'new_content': '\n'.join(lines),
            'description': f'annotated {target} (T{tick}, {cells} cells)',
        }

    def _mod_nudge_constant(self, target, content, state, action_mean):
        """Adjust a numeric constant in the source code slightly.

        Finds numeric literals and nudges one by a small amount.
        Only targets constants that look like configuration values
        (standalone numbers in assignments, not loop counters etc).
        """
        # Find lines with numeric assignments: `name = 0.05`
        pattern = re.compile(
            r'^(\s*(?:\'[^\']+\'|"[^"]+"|[\w_]+)\s*[:=]\s*)'  # key/var = 
            r'([+-]?\d+\.?\d*)'                                 # number
            r'(\s*[,}]?\s*(?:#.*)?)$'                           # trailing
        )

        lines = content.split('\n')
        candidates = []
        for i, line in enumerate(lines):
            m = pattern.match(line)
            if m:
                val = float(m.group(2))
                # Only nudge reasonable-sized numbers (not 0, not huge)
                if 0.001 <= abs(val) <= 10000:
                    candidates.append((i, m))

        if not candidates:
            return None

        # Pick one based on action vector
        idx = int(abs(action_mean[3]) * 127) % len(candidates)
        line_idx, match = candidates[idx]

        old_val = float(match.group(2))
        # Nudge by 1-3% based on action direction
        direction = 1 if action_mean[3] > 0.5 else -1
        nudge_pct = 0.01 + abs(action_mean[3] - 0.7) * 0.02
        new_val = old_val * (1 + direction * nudge_pct)

        # Preserve format
        if '.' in match.group(2):
            decimals = len(match.group(2).split('.')[1])
            new_val_str = f"{new_val:.{decimals}f}"
        else:
            new_val_str = str(int(round(new_val)))

        new_line = match.group(1) + new_val_str + match.group(3)
        lines[line_idx] = new_line

        return {
            'new_content': '\n'.join(lines),
            'description': (f'nudged constant in {target} line {line_idx+1}: '
                          f'{old_val} → {new_val_str}'),
        }

    def _log_modification(self, target, description, tick):
        """Log a self-modification to the modification journal."""
        log_file = os.path.join(self._journal_dir, 'self_modifications.md')
        header = ""
        if not os.path.exists(log_file):
            header = "# Ultron Self-Modification Log\n\n"

        entry = (f"- **T{tick}** [{time.strftime('%Y-%m-%d %H:%M:%S')}]: "
                 f"{description}\n")

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(header + entry)

    # ── Public Interface ──────────────────────────────────────────

    def apply_config_tune(self, config, tune_result):
        """Apply a config tune to the live CONFIG dict.

        Args:
            config: the CONFIG dict (mutated in place)
            tune_result: dict with 'param', 'nudge', 'range'
        """
        param = tune_result['param']
        if param not in config:
            return False

        old_val = config[param]
        new_val = old_val + tune_result['nudge']
        lo, hi = tune_result['range']
        new_val = max(lo, min(hi, new_val))
        config[param] = new_val
        return True

    def get_action_log(self, n=20):
        """Return recent actions."""
        return self._action_log[-n:]

    def get_stats(self):
        """Summary of agency activity."""
        total = len(self._action_log)
        by_type = {}
        for a in self._action_log:
            t = a['type']
            by_type[t] = by_type.get(t, 0) + 1
        return {
            'total_actions': total,
            'by_type': by_type,
            'cooldowns': {k: max(0, v - self._tick)
                         for k, v in self._cooldowns.items()},
        }
