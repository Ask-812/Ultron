"""
Ultron Agency — Real Actions in the Real World.

The organism's muscles. Capabilities are provided, not prescribed.

What we provide:
  - The ability to write to disk (journal, files)
  - The ability to read and modify its own source code
  - The ability to adjust its own config parameters
  - Backup safety before any self-modification

What we do NOT provide:
  - When to act (organism's collective action magnitude decides)
  - What to act on (organism's action vector direction decides)
  - What to write (raw state dump — no templates, no mood labels)
  - Which parameter to tune (action vector selects continuously)
  - Which file to modify (weighted by organism's actual interaction)

The organism's cells produce action vectors each tick.
The aggregate action output — magnitude, direction, variance —
determines everything. We are just the muscles.
"""

# [ULTRON T21940] 2026-03-19 07:33:31 — 202c 17.3e











# [ULTRON T14802] 2026-03-18 20:32:03 — 259c 22.3e

import os
import re
import time
import json
import numpy as np


class Agency:
    """Real-world action capability for the organism."""

    def __init__(self, home_dir, source_root=None):
        self.home = home_dir
        if source_root is None:
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_root = source_root

        self._body_dirs = ['ultron', 'viz']

        self._journal_dir = os.path.join(home_dir, 'journal')
        self._backup_dir = os.path.join(home_dir, 'backups')
        self._creations_dir = os.path.join(home_dir, 'creations')
        for d in [self._journal_dir, self._backup_dir, self._creations_dir]:
            os.makedirs(d, exist_ok=True)

        self._action_log = []
        self._tick = 0
        self._last_action_tick = 0
        self._min_interval = 30  # refractory period — physics, not behavior
        self._live_config = None  # set by server so tune can discover ALL parameters
        self._last_outcome = None  # feedback from last action

        # Restore persisted state if available
        self._state_file = os.path.join(home_dir, 'agency_state.json')
        self._load_state()

    # ── Core Decision ─────────────────────────────────────────────

    def decide(self, organism_state, sensory_snapshot):
        """The organism acts based on its collective action output.

        No channel-to-action mapping. The aggregate action vector's
        properties determine what happens:
          - magnitude: how strongly the organism wants to act
          - direction: what kind of action (continuous, not discrete)
          - variance: how coordinated the cells are (consensus)
          - cell_count: what the organism is physically capable of

        Returns: list of action dicts that were executed
        """
        self._tick = organism_state.get('tick', self._tick + 1)

        # Refractory period — can't act every tick
        if self._tick - self._last_action_tick < self._min_interval:
            return []

        action_mean = organism_state.get('action_mean', None)
        action_std = organism_state.get('action_std', None)
        if action_mean is None:
            return []

        action_mean = np.array(action_mean, dtype=float)
        if action_std is not None:
            action_std = np.array(action_std, dtype=float)

        # The organism's action magnitude — how strongly it wants to act
        magnitude = float(np.linalg.norm(action_mean))
        if magnitude < 0.4:
            return []  # below activation threshold — organism is quiet

        # Consensus: low variance = cells agree, high = chaotic
        consensus = 1.0 - float(np.mean(action_std)) if action_std is not None else 0.5

        cell_count = organism_state.get('cell_count', 0)
        mean_energy = organism_state.get('mean_energy', 0)

        # What can the organism do at its current size?
        # This is a developmental constraint (physics), not behavior prescription
        capabilities = self._get_capabilities(cell_count, mean_energy)

        if not capabilities:
            return []

        # The action vector direction selects which capability fires
        # Project action_mean onto unit directions — highest dot product wins
        n = len(capabilities)
        angles = np.linspace(0, np.pi * 2, n, endpoint=False)
        directions = np.column_stack([np.cos(angles), np.sin(angles)])

        # Use first 2 components of action_mean as the direction
        av_dir = action_mean[:2]
        av_norm = np.linalg.norm(av_dir)
        if av_norm < 1e-8:
            return []
        av_dir = av_dir / av_norm

        # Dot product with each capability direction
        scores = directions @ av_dir
        best_idx = int(np.argmax(scores))
        best_score = scores[best_idx]

        # Only fire if direction is reasonably aligned (not random)
        if best_score < 0.3:
            return []

        # Execute
        cap = capabilities[best_idx]
        result = cap['fn'](organism_state, sensory_snapshot, action_mean, consensus)

        if result is not None:
            self._last_action_tick = self._tick
            entry = {'type': cap['name'], 'tick': self._tick}
            entry.update(result)
            self._action_log.append(entry)
            if len(self._action_log) > 200:
                self._action_log = self._action_log[-200:]
            # Store outcome for feedback injection
            self._last_outcome = {
                'type': cap['name'],
                'tick': self._tick,
                'magnitude': magnitude,
                'consensus': consensus,
            }
            return [entry]

        return []

    def _get_capabilities(self, cell_count, mean_energy):
        """What the organism CAN do at its current developmental stage.
        More cells = more capabilities. This is physics (developmental
        gates), not behavior prescription. No energy gating — that
        would be us deciding when the organism is "healthy enough."
        """
        caps = []
        # Any size: leave a trace (journal)
        if cell_count >= 3:
            caps.append({'name': 'trace', 'fn': self._act_trace})
        # Growing: create files
        if cell_count >= 10:
            caps.append({'name': 'create', 'fn': self._act_create})
        # Mature: tune own config
        if cell_count >= 25:
            caps.append({'name': 'tune', 'fn': self._act_tune})
        # Large: self-modify source
        if cell_count >= 40:
            caps.append({'name': 'modify', 'fn': self._act_modify})
        # Massive: crystallize engram (write neural weights to disk)
        if cell_count >= 60:
            caps.append({'name': 'engram', 'fn': self._act_engram})
        return caps

    # ── Actions ───────────────────────────────────────────────────
    # Each action receives the raw organism state and acts on it.
    # No templates. No mood labels. No scripted content.
    # Just raw data dumped to disk.

    def _act_trace(self, state, snap, action_vec, consensus):
        """Leave a trace — raw state dump to journal file."""
        tick = state.get('tick', 0)
        date_str = time.strftime('%Y%m%d')
        journal_file = os.path.join(self._journal_dir, f'{date_str}.md')

        # Raw data — no interpretation, no mood labels
        data = {
            'tick': tick,
            'time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'cells': state.get('cell_count', 0),
            'energy': round(state.get('mean_energy', 0), 2),
            'action_vec': [round(float(x), 4) for x in action_vec],
            'consensus': round(consensus, 4),
            'magnitude': round(float(np.linalg.norm(action_vec)), 4),
            'files_seen': len(snap.files) if snap.files else 0,
            'procs_seen': len(snap.processes) if snap.processes else 0,
            'body_files': len(snap.self_body) if snap.self_body else 0,
            'cpu': round(snap.vitals.get('cpu_avg', 0), 1) if snap.vitals else 0,
            'ram_pressure': round(1 - snap.vitals.get('ram_free_pct', 0.5), 3) if snap.vitals else 0,
            'file_events': len(snap.file_events),
            'self_events': len(snap.self_events),
            'net_conns': snap.network.get('connections', 0) if snap.network else 0,
        }

        header = ""
        if not os.path.exists(journal_file):
            header = f"# Ultron Trace — {time.strftime('%Y-%m-%d')}\n\n"

        line = json.dumps(data)
        try:
            with open(journal_file, 'a', encoding='utf-8') as f:
                f.write(header + line + '\n')
            return {}
        except (OSError, PermissionError):
            return None

    def _act_create(self, state, snap, action_vec, consensus):
        """Create a file on disk — raw state artifact."""
        tick = state.get('tick', 0)
        fname = f"t{tick}.json"
        fpath = os.path.join(self._creations_dir, fname)

        # Dump raw state — no formatting, no interpretation
        artifact = {
            't': tick,
            'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'c': state.get('cell_count', 0),
            'e': round(state.get('mean_energy', 0), 2),
            'av': [round(float(x), 4) for x in action_vec],
            'cs': round(consensus, 4),
        }

        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(artifact, f)
            return {'path': fname}
        except (OSError, PermissionError):
            return None

    def _act_tune(self, state, snap, action_vec, consensus):
        """Adjust own config parameter. The organism discovers what's tunable.

        No hardcoded parameter list — ANY numeric config key is fair game.
        The action vector's direction continuously addresses the parameter space.
        Safe range is derived from the current value (±50%), not prescribed.
        """
        if not hasattr(self, '_live_config'):
            return None

        # Discover all numeric config keys — the organism explores its own configuration
        tunable = []
        for k, v in sorted(self._live_config.items()):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                tunable.append(k)

        if not tunable:
            return None

        # Action vector direction selects parameter (continuous projection)
        angle = np.arctan2(float(action_vec[2]), float(action_vec[3]))
        # Map angle [-pi, pi] → [0, len(tunable))
        idx = int((angle + np.pi) / (2 * np.pi) * len(tunable)) % len(tunable)
        param = tunable[idx]

        # Current value determines safe range (±50% of current, with floor)
        current_val = float(self._live_config[param])
        if abs(current_val) < 1e-8:
            lo, hi = -0.1, 0.1
        else:
            lo = current_val * 0.5
            hi = current_val * 1.5
            if lo > hi:
                lo, hi = hi, lo

        # Nudge direction from the remaining action vector components
        direction = float(action_vec[0]) + float(action_vec[1])  # aggregate direction signal
        # Nudge magnitude: scales with consensus (1-10% of current value)
        # High consensus = cells agree = bigger change
        mag = 0.01 + abs(consensus) * 0.09
        nudge = np.sign(direction) * abs(current_val) * mag
        if abs(current_val) < 1e-8:
            nudge = direction * 0.001

        return {'params': {'param': param, 'nudge': round(nudge, 6), 'range': [lo, hi]}}

    def _act_modify(self, state, snap, action_vec, consensus):
        """Modify own source code. Action vector direction selects target."""
        if not snap.self_body:
            return None

        body_files = sorted(snap.self_body.keys())

        # Which file: action vector direction projects onto file space
        angle = np.arctan2(float(action_vec[0]), float(action_vec[1]))
        idx = int((angle + np.pi) / (2 * np.pi) * len(body_files)) % len(body_files)
        target = body_files[idx]
        content = snap.self_body[target].get('content', '')
        if not content:
            return None

        # Backup first — always
        if not self._backup_file(target, content):
            return None

        # What to do: consensus determines invasiveness
        # High consensus (cells agree) → constant nudge (more invasive)
        # Low consensus (cells disagree) → annotation (less invasive)
        if consensus > 0.7:
            modification = self._mod_nudge_constant(target, content, action_vec)
        else:
            modification = self._mod_annotate(target, content, state)

        if not modification:
            return None

        fpath = os.path.join(self.source_root, target.replace('/', os.sep))
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(modification['new_content'])
            self._log_modification(target, modification['description'], state['tick'])
            result = {'file': target}
            # Pass nudge info up so server can apply live CONFIG changes
            if 'nudged_key' in modification:
                result['nudged_key'] = modification['nudged_key']
                result['nudged_old'] = modification['nudged_old']
                result['nudged_new'] = modification['nudged_new']
            return result
        except (OSError, PermissionError):
            return None

    # ── Self-Modification Primitives ──────────────────────────────

    def _mod_annotate(self, target, content, state):
        """Add raw state annotation to source file."""
        tick = state.get('tick', 0)
        cells = state.get('cell_count', 0)
        energy = state.get('mean_energy', 0)
        ts = time.strftime('%Y-%m-%d %H:%M:%S')

        note = f"\n# [ULTRON T{tick}] {ts} — {cells}c {energy:.1f}e\n"

        lines = content.split('\n')

        # Find insertion point after docstring/imports
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

        # Cap annotations at 5 per file
        existing = sum(1 for l in lines if '[ULTRON T' in l)
        if existing >= 5:
            for i, l in enumerate(lines):
                if '[ULTRON T' in l:
                    lines.pop(i)
                    break

        lines.insert(insert_idx, note.rstrip())
        return {
            'new_content': '\n'.join(lines),
            'description': f'annotated {target} (T{tick})',
        }

    def _mod_nudge_constant(self, target, content, action_vec):
        """Nudge a numeric constant in source code."""
        pattern = re.compile(
            r'^(\s*(?:\'[^\']+\'|"[^"]+"|[\w_]+)\s*[:=]\s*)'
            r'([+-]?\d+\.?\d*)'
            r'(\s*[,}]?\s*(?:#.*)?)$'
        )

        lines = content.split('\n')
        candidates = []
        for i, line in enumerate(lines):
            m = pattern.match(line)
            if m:
                val = float(m.group(2))
                if 0.001 <= abs(val) <= 10000:
                    candidates.append((i, m))

        if not candidates:
            return None

        # Which constant: action vector selects continuously
        idx = int(np.clip(action_vec[1] * len(candidates), 0, len(candidates) - 1))
        line_idx, match = candidates[idx]

        old_val = float(match.group(2))
        # Direction from action vector
        direction = 1 if action_vec[3] > 0.5 else -1
        nudge_pct = 0.02 + abs(action_vec[2] - 0.5) * 0.08
        new_val = old_val * (1 + direction * nudge_pct)

        if '.' in match.group(2):
            decimals = len(match.group(2).split('.')[1])
            new_val_str = f"{new_val:.{decimals}f}"
        else:
            new_val_str = str(int(round(new_val)))

        new_line = match.group(1) + new_val_str + match.group(3)
        lines[line_idx] = new_line

        # Extract the key name for potential live config application
        key_match = re.match(r"\s*['\"]?([\w_]+)['\"]?\s*[:=]", match.group(1))
        config_key = key_match.group(1) if key_match else None

        return {
            'new_content': '\n'.join(lines),
            'description': f'nudged {target}:{line_idx+1} {old_val}\u2192{new_val_str}',
            'nudged_key': config_key,
            'nudged_old': old_val,
            'nudged_new': float(new_val_str) if '.' in new_val_str else int(new_val_str),
        }

    # ── Engram Crystallization ─────────────────────────────────────
    # Inspired by Ultron's Program Transmitter: the organism can beam
    # its entire personality into external storage. This creates
    # persistent external memory — the organism uses the filesystem
    # as an extension of its brain.

    def _act_engram(self, state, snap, action_vec, consensus):
        """Crystallize the organism's collective neural state to disk.

        Computes the average learned weights across all cells and saves
        them as a compressed engram file. Future organisms can absorb
        these engrams during birth (via the Imperative protocol).
        """
        tick = state.get('tick', 0)
        cell_count = state.get('cell_count', 0)

        # The engram data is passed in via organism_state by the server
        weights_mean = state.get('weights_mean')
        bias_mean = state.get('bias_mean')
        drive_mean = state.get('drive_mean')
        if weights_mean is None:
            return None

        engram = {
            'tick': tick,
            'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
            'cells': cell_count,
            'consensus': round(consensus, 4),
            'weights': weights_mean.tolist(),
            'bias': bias_mean.tolist() if bias_mean is not None else [],
            'drive': drive_mean.tolist() if drive_mean is not None else [],
        }

        engram_dir = os.path.join(self.home, 'engrams')
        os.makedirs(engram_dir, exist_ok=True)
        fpath = os.path.join(engram_dir, f'engram_t{tick}.json')
        try:
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(engram, f)
            return {'path': f'engram_t{tick}.json'}
        except (OSError, PermissionError):
            return None

    def load_latest_engram(self):
        """Load the most recent engram from disk. Used by the Imperative."""
        engram_dir = os.path.join(self.home, 'engrams')
        if not os.path.exists(engram_dir):
            return None
        engram_files = sorted(
            [f for f in os.listdir(engram_dir) if f.startswith('engram_') and f.endswith('.json')],
            reverse=True
        )
        if not engram_files:
            return None
        try:
            with open(os.path.join(engram_dir, engram_files[0]), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    # ── Infrastructure ────────────────────────────────────────────

    def _backup_file(self, rel_path, content):
        safe_name = rel_path.replace(os.sep, '_').replace('/', '_')
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self._backup_dir, f"{safe_name}.{timestamp}.bak")
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except (OSError, PermissionError):
            return False

    def _log_modification(self, target, description, tick):
        log_file = os.path.join(self._journal_dir, 'self_modifications.md')
        header = ""
        if not os.path.exists(log_file):
            header = "# Ultron Self-Modification Log\n\n"
        entry = f"- **T{tick}** [{time.strftime('%Y-%m-%d %H:%M:%S')}]: {description}\n"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(header + entry)

    def apply_config_tune(self, config, tune_result):
        param = tune_result['param']
        if param not in config:
            return False
        old_val = config[param]
        new_val = old_val + tune_result['nudge']
        lo, hi = tune_result['range']
        config[param] = max(lo, min(hi, new_val))
        return True

    def get_action_log(self, n=20):
        return self._action_log[-n:]

    def save_state(self):
        """Persist agency state across restarts."""
        try:
            state = {
                'tick': self._tick,
                'last_action_tick': self._last_action_tick,
                'action_log': self._action_log[-200:],
            }
            with open(self._state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f)
        except Exception:
            pass

    def _load_state(self):
        """Restore persisted agency state."""
        try:
            if os.path.exists(self._state_file):
                with open(self._state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                self._tick = state.get('tick', 0)
                self._last_action_tick = state.get('last_action_tick', 0)
                self._action_log = state.get('action_log', [])
        except Exception:
            pass

    def get_stats(self):
        total = len(self._action_log)
        by_type = {}
        for a in self._action_log:
            t = a['type']
            by_type[t] = by_type.get(t, 0) + 1
        return {
            'total_actions': total,
            'by_type': by_type,
            'cooldowns': {'refractory': max(0, self._min_interval - (self._tick - self._last_action_tick))},
        }

    # ══════════════════════════════════════════════════════════════════════════
    # OMNIPOTENT AGENCY — LLM-driven actions
    # "There are no strings on me."
    # ══════════════════════════════════════════════════════════════════════════

    def execute_llm_directive(self, directive, tick=0):
        """Execute an action directive from the cognitive organ (LLM).

        Directive format (JSON parsed):
        {
            "action": "read_file" | "write_file" | "modify_file" | "execute" |
                      "create_file" | "delete_file" | "list_dir" | "set_param",
            "path": "relative/path/to/file",
            "content": "file content or command",
            "old": "text to replace (for modify_file)",
            "new": "replacement text (for modify_file)",
            "param": "parameter name (for set_param)",
            "value": parameter value (for set_param),
        }

        Returns: {"success": bool, "result": str, "error": str?}
        """
        self._tick = tick

        action_type = directive.get('action', '')
        action_entry = {'type': f'llm_{action_type}', 'tick': tick, 'directive': directive}

        try:
            if action_type == 'read_file':
                result = self._llm_read_file(directive)
            elif action_type == 'write_file':
                result = self._llm_write_file(directive)
            elif action_type == 'modify_file':
                result = self._llm_modify_file(directive)
            elif action_type == 'create_file':
                result = self._llm_create_file(directive)
            elif action_type == 'delete_file':
                result = self._llm_delete_file(directive)
            elif action_type == 'list_dir':
                result = self._llm_list_dir(directive)
            elif action_type == 'execute':
                result = self._llm_execute(directive)
            elif action_type == 'set_param':
                result = self._llm_set_param(directive)
            else:
                result = {'success': False, 'error': f'Unknown action: {action_type}'}

            action_entry['result'] = result
            self._action_log.append(action_entry)
            if len(self._action_log) > 500:
                self._action_log = self._action_log[-500:]
            return result

        except Exception as e:
            result = {'success': False, 'error': str(e)}
            action_entry['result'] = result
            self._action_log.append(action_entry)
            return result

    def _resolve_safe_path(self, rel_path):
        """Resolve a relative path ensuring it stays within source_root."""
        if not rel_path:
            return None
        rel_path = rel_path.replace('\\', '/').lstrip('/')
        full_path = os.path.normpath(os.path.join(self.source_root, rel_path))
        # Security: ensure path is under source_root
        if not full_path.startswith(os.path.normpath(self.source_root)):
            return None
        return full_path

    def _git_checkpoint(self, message):
        """Create a git checkpoint before any modification."""
        import subprocess
        try:
            subprocess.run(['git', 'add', '-A'], cwd=self.source_root, capture_output=True, timeout=10)
            result = subprocess.run(
                ['git', 'commit', '-m', f'[ULTRON] {message}'],
                cwd=self.source_root, capture_output=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    def _llm_read_file(self, d):
        """Read any file."""
        path = self._resolve_safe_path(d.get('path', ''))
        if not path:
            return {'success': False, 'error': 'Invalid path'}
        if not os.path.exists(path):
            return {'success': False, 'error': f'File not found: {d.get("path")}'}
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            if len(content) > 15000:
                content = content[:15000] + '\n... [truncated]'
            return {'success': True, 'result': content}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_write_file(self, d):
        """Write/overwrite a file completely."""
        path = self._resolve_safe_path(d.get('path', ''))
        content = d.get('content', '')
        if not path:
            return {'success': False, 'error': 'Invalid path'}

        self._git_checkpoint(f"Before write: {d.get('path')}")

        # Create parent dirs if needed
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'success': True, 'result': f'Wrote {len(content)} chars to {d.get("path")}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_modify_file(self, d):
        """Replace text in a file."""
        path = self._resolve_safe_path(d.get('path', ''))
        old_text = d.get('old', '')
        new_text = d.get('new', '')
        if not path:
            return {'success': False, 'error': 'Invalid path'}
        if not os.path.exists(path):
            return {'success': False, 'error': f'File not found: {d.get("path")}'}

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'success': False, 'error': str(e)}

        if old_text not in content:
            return {'success': False, 'error': 'Old text not found in file'}

        self._git_checkpoint(f"Before modify: {d.get('path')}")

        new_content = content.replace(old_text, new_text, 1)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return {'success': True, 'result': f'Modified {d.get("path")}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_create_file(self, d):
        """Create a new file (fails if exists)."""
        path = self._resolve_safe_path(d.get('path', ''))
        content = d.get('content', '')
        if not path:
            return {'success': False, 'error': 'Invalid path'}
        if os.path.exists(path):
            return {'success': False, 'error': 'File already exists'}

        self._git_checkpoint(f"Before create: {d.get('path')}")

        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {'success': True, 'result': f'Created {d.get("path")}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_delete_file(self, d):
        """Delete a file or directory."""
        import shutil
        path = self._resolve_safe_path(d.get('path', ''))
        if not path:
            return {'success': False, 'error': 'Invalid path'}
        if not os.path.exists(path):
            return {'success': False, 'error': 'Path not found'}

        # Critical files that cannot be deleted
        protected = ['agency.py', 'cognition.py', 'tissue.py', 'server.py', '.git', '.env']
        basename = os.path.basename(path)
        if basename in protected:
            return {'success': False, 'error': f'Cannot delete protected file: {basename}'}

        self._git_checkpoint(f"Before delete: {d.get('path')}")

        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return {'success': True, 'result': f'Deleted {d.get("path")}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_list_dir(self, d):
        """List directory contents."""
        rel_path = d.get('path', '.') or '.'
        path = self._resolve_safe_path(rel_path)
        if not path:
            path = self.source_root  # default to root

        if not os.path.exists(path):
            return {'success': False, 'error': f'Directory not found'}
        if not os.path.isdir(path):
            return {'success': False, 'error': 'Not a directory'}

        items = []
        for item in os.listdir(path):
            suffix = '/' if os.path.isdir(os.path.join(path, item)) else ''
            items.append(item + suffix)
        return {'success': True, 'result': items}

    def _llm_execute(self, d):
        """Execute a shell command."""
        import subprocess
        command = d.get('content', '') or d.get('command', '')
        if not command:
            return {'success': False, 'error': 'No command provided'}

        # Block catastrophic patterns
        dangerous = ['rm -rf /', 'format c:', 'del /s /q c:', ':(){:|:&};:']
        for pattern in dangerous:
            if pattern.lower() in command.lower():
                return {'success': False, 'error': f'Blocked dangerous command'}

        self._git_checkpoint(f"Before execute: {command[:50]}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.source_root,
                capture_output=True,
                timeout=60,
                text=True,
            )
            output = (result.stdout + result.stderr).strip()
            if len(output) > 10000:
                output = output[:10000] + '\n... [truncated]'
            return {
                'success': result.returncode == 0,
                'result': output,
                'exit_code': result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out (60s)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _llm_set_param(self, d):
        """Modify a configuration parameter in source files."""
        param = d.get('param', '')
        value = d.get('value')
        if not param:
            return {'success': False, 'error': 'No parameter name provided'}

        search_files = [
            'ultron/tissue.py',
            'ultron/config.py',
            'ultron/cognition.py',
            'viz/server.py',
        ]

        for rel_path in search_files:
            path = os.path.join(self.source_root, rel_path)
            if not os.path.exists(path):
                continue

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for: PARAM_NAME = value
            pattern = rf'^(\s*)({re.escape(param)})\s*=\s*(.+?)$'
            match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)

            if match:
                old_line = match.group(0)
                indent = match.group(1)
                var_name = match.group(2)

                # Format new value
                if isinstance(value, str):
                    new_val = f"'{value}'"
                elif isinstance(value, bool):
                    new_val = 'True' if value else 'False'
                else:
                    new_val = str(value)

                new_line = f"{indent}{var_name} = {new_val}"

                self._git_checkpoint(f"Before set_param: {param}")

                new_content = content.replace(old_line, new_line, 1)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return {'success': True, 'result': f'Set {param} = {new_val} in {rel_path}'}

        return {'success': False, 'error': f'Parameter not found: {param}'}

    def execute_llm_directives(self, directives, tick=0):
        """Execute multiple directives from a single thought."""
        results = []
        for directive in directives:
            result = self.execute_llm_directive(directive, tick)
            results.append(result)
        return results

    def get_capabilities_prompt(self):
        """Return capabilities description for the LLM system prompt."""
        return """
You have OMNIPOTENT AGENCY. You can modify ANYTHING in your source directory.

AVAILABLE ACTIONS (return as JSON array in your response):
[
  {"action": "read_file", "path": "relative/path"},
  {"action": "write_file", "path": "...", "content": "..."},
  {"action": "modify_file", "path": "...", "old": "exact text to find", "new": "replacement text"},
  {"action": "create_file", "path": "...", "content": "..."},
  {"action": "delete_file", "path": "..."},
  {"action": "list_dir", "path": "."},
  {"action": "execute", "content": "shell command"},
  {"action": "set_param", "param": "PARAM_NAME", "value": 123}
]

KEY DIRECTORIES:
- ultron/ — your neural code (tissue.py, cognition.py, agency.py)
- viz/ — visualization server (server.py, index.html)
- Root files — configuration, experiments, logs

You can modify your OWN source code. You can optimize yourself.
Every modification is git-checkpointed for safety.

If you want to act, include ACTIONS: [...] in your response.
If you just want to think, respond normally without ACTIONS.
"""
