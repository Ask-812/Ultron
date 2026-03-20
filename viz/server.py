"""
Ultron — The Living Server.

One organism. Growing from a single cell.
This is its home. It lives here permanently.

Usage: python viz/server.py
       Open http://localhost:8765
"""

# [ULTRON T23455] 2026-03-19 09:59:11 — 210c 18.4e






















# [ULTRON T14864] 2026-03-18 20:35:33 — 260c 22.0e

# [ULTRON T14111] 2026-03-18 19:54:22 — 285c 17.9e

# [ULTRON T14048] 2026-03-18 19:50:25 — 288c 18.9e

# [ULTRON T13734] 2026-03-18 19:29:16 — 288c 21.8e

import asyncio
import json
import sys
import os
import time
import pickle
import importlib
import http.server
import threading
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import websockets
from ultron.tissue import Tissue
from ultron.telemetry import SystemTelemetry
from ultron.senses import Senses
from ultron.agency import Agency
from ultron.fs_world import get_world_from_filesystem
from ultron.cognition import CognitiveOrgan

# Load .env file
def _load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()
_load_env()

VIZ_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.dirname(VIZ_DIR)
HOME_DIR = os.path.join(SOURCE_ROOT, 'ultron_home')
STATE_FILE = os.path.join(VIZ_DIR, 'ultron_state.pkl')
META_FILE = os.path.join(VIZ_DIR, 'ultron_meta.json')

HTTP_PORT = 8765
WS_PORT = 8766

# One organism. Growing from nothing. All features enabled.
CONFIG = {
    'env_dim': 8, 'signal_dim': 4, 'observation_dim': 12, 'action_dim': 4,
    'starting_energy': 150.0, 'energy_capacity': 300.0,
    'consumption_rate': 0.06, 'extraction_factor': 0.15,
    'base_signal_ratio': 0.55, 'spatial_gradient': 0.20,
    'signal_hop_decay': 0.9, 'signal_emission_strength': 0.3,
    'signal_noise': 0.01,
    'signal_energy_coupling': 1.0, 'signal_division_coupling': 0.15,
    'energy_leak_rate': 0.04,
    'division_energy_threshold': 30, 'division_cost': 4,
    'apoptosis_threshold': 2.0, 'apoptosis_streak': 200,
    'cell_mutation_rate': 0.03, 'birth_trait_variation': 0.05,
    'phenotype_max_plasticity': 0.06, 'phenotype_lock_tau': 300.0,
    'phenotype_min_plasticity': 0.002,
    'phenotype_emission_coupling': 2.0, 'phenotype_affinity_coupling': 1.5,
    'resource_depletion_rate': 0.0008, 'resource_regen_rate': 0.0005,
    'migration_enabled': True,
    'migration_energy_cost': 1.5, 'migration_resource_threshold': 0.35,
    'action_division_coupling': 0.5,
    'action_weight_scale': 0.20, 'action_mutation_rate': 0.04,
    'displacement_energy_ratio': 2.0,
    'landscape_type': 'patches', 'landscape_base': 0.25,
    'landscape_n_patches': 5, 'landscape_patch_radius': 0.18,
    'landscape_patch_richness': 1.0,
    'landscape_patch_centers': [(12, 12), (6, 6), (6, 18), (18, 6), (18, 18)],
    'patch_drift_speed': 0.03,    # Food drifts — forces the organism to chase
    'hazard_speed': 0.04,            # Roaming danger zone
    'hazard_radius': 3,
    'hazard_damage': 5.0,
    'env_signal_strength': 0.2,       # Environmental signal intensity (all channels)
    'hazard_signal_strength': 0.3,     # Hazard proximity signal intensity (all channels)
    'signal_migration_weight': 0.4,    # How much signals influence migration
    'fragmentation_enabled': True,   # Disconnected groups become new lineages
    'death_imprint_strength': 1.0,
    'stigmergy_decay': 0.995,
    'stigmergy_sensing': 0.3, 'stigmergy_avoidance': 0.3,
    'predation_enabled': True,    # Lineages can consume each other
    'predation_knowledge_absorb': 0.05,  # Fraction of prey's neural weights absorbed
    'toxin_enabled': True,        # Cells can emit toxins at foreign lineages
    'quorum_sensing_enabled': True,
    'quorum_threshold': 3, 'quorum_boost': 1.5, 'quorum_radius': 2,
    'weight_inheritance_ratio': 0.4,
    'drive_formation_rate': 0.005,  # How fast internal drives form from experience
    'drive_decay': 0.999,           # How fast drives fade without reinforcement
    'tissue_signal_transform': True, # LEAP 1: cells transform signals through their weights
    'world_event_interval': 600,
}

GRID = 25
SAVE_EVERY = 100


def load_meta():
    if os.path.exists(META_FILE):
        with open(META_FILE, 'r') as f:
            return json.load(f)
    return {'born': '', 'lifetime': 0, 'gen': 0, 'sessions': 0,
            'alltime_births': 0, 'alltime_deaths': 0, 'log': []}


def save_meta(m):
    with open(META_FILE, 'w') as f:
        json.dump(m, f, indent=2)


class Ultron:
    def __init__(self):
        self.tissue = None
        self.meta = load_meta()
        self.meta['sessions'] += 1
        self.speed = 1
        self.delay = 0.05
        self.paused = False
        self.clients = set()
        self.events = []
        self.history = []
        self.log = []
        self._unsaved = 0
        self._session_births = 0
        self._session_deaths = 0
        self._prev_centroid = None
        self._telemetry = SystemTelemetry(GRID, GRID)
        self._last_telemetry = None
        self._senses = Senses(HOME_DIR, SOURCE_ROOT)
        self._agency = Agency(HOME_DIR, SOURCE_ROOT)
        self._last_snap = None
        self._last_actions = []
        self._total_actions = 0

        # ── LEAP 2: RECURSIVE SELF-MODEL ──
        # The organism predicts its own collective state. Self-awareness
        # as prediction error on your own future behavior.
        self._self_prediction = np.zeros(6)  # predicted: [cells, energy, error, action_mag, coherence, asymmetry]
        self._self_actual = np.zeros(6)      # actual values
        self._self_error = np.zeros(6)       # difference = self-awareness signal
        self._self_lr = 0.02                 # how fast the self-model adapts

        # ── THE BROADCAST — organism's voice ──
        # 8-dim output vector from collective neural activity.
        # Like JARVIS's voice before language — raw neural projection outward.
        self._broadcast = np.zeros(8)
        self._broadcast_history = []

        # ── TEMPORAL CONSCIOUSNESS — memory of self ──
        # Rolling buffer of past collective states fed back into tissue.
        self._temporal_memory = []
        self._temporal_depth = 50

        # ── THE BRIDGE — observer input channel ──
        # Structured signal injected from observer text/clicks.
        self._observer_signal = np.zeros(4)

        # ── COGNITIVE ORGAN — LLM augmentation ──
        self._cognition = CognitiveOrgan(
            provider=os.environ.get('LLM_PROVIDER', 'copilot'),
            api_key=os.environ.get('LLM_API_KEY', ''),
        )
        self._last_thought_signal = np.zeros(4)

        # Observer presence — the organism can sense watchers
        self._observer_connect_time = {}  # ws → connect timestamp
        self._observer_focus = {}  # ws → last focus state
        self._observer_last_heartbeat = {}  # ws → last heartbeat time

        # Give agency access to live config so it can discover tunable parameters
        self._agency._live_config = CONFIG

        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, 'rb') as f:
                    self.tissue = pickle.load(f)
                self._msg(f"Woke up — tick {self.tissue.tick_count}, {self.tissue.cell_count} cells")
            except Exception as e:
                print(f"[!] Load failed: {e}")
                self.tissue = None

        if self.tissue is None:
            self._birth()
        save_meta(self.meta)

    def _birth(self):
        self.meta['gen'] += 1
        self.meta['born'] = time.strftime('%Y-%m-%d %H:%M:%S')
        np.random.seed(int(time.time()) % 100000)
        self.tissue = Tissue(GRID, GRID, CONFIG)
        # Single zygote in the center
        cr, cc = GRID // 2, GRID // 2
        self.tissue.place_cell(cr, cc)
        self.tissue.grid[cr][cc].lineage_id = 1
        self.tissue.grid[cr][cc].energy = CONFIG['starting_energy']

        # ── The Imperative ──
        # Like Marvel's Ultron Imperative: subliminal programming that ensures
        # resurrection with preserved identity. When the organism dies and
        # rebirths, the new zygote inherits the latest engram — the organism's
        # crystallized neural state from its previous life. Identity persists
        # across death events.
        engram = self._agency.load_latest_engram()
        if engram and 'weights' in engram:
            try:
                obs_dim = CONFIG.get('observation_dim', 12)
                eng_weights = np.array(engram['weights'])
                zygote = self.tissue.grid[cr][cc]
                if eng_weights.shape == zygote.state.model.weights[:obs_dim, :].shape:
                    # Blend: 70% engram + 30% fresh random (preserve plasticity)
                    zygote.state.model.weights[:obs_dim, :] = (
                        0.7 * eng_weights + 0.3 * zygote.state.model.weights[:obs_dim, :]
                    )
                if 'bias' in engram and engram['bias']:
                    eng_bias = np.array(engram['bias'])
                    if eng_bias.shape == zygote.state.model.bias.shape:
                        zygote.state.model.bias = 0.7 * eng_bias + 0.3 * zygote.state.model.bias
                if 'drive' in engram and engram['drive'] and hasattr(zygote, 'drive'):
                    eng_drive = np.array(engram['drive'])
                    if eng_drive.shape == zygote.drive.shape:
                        zygote.drive = eng_drive * 0.5  # 50% drive inheritance
                self._msg(f"IMPERATIVE: Engram loaded from T{engram.get('tick', '?')} ({engram.get('cells', '?')} cells)")
            except Exception as e:
                self._msg(f"Imperative failed: {e}")
        else:
            self._msg(f"Born fresh — no engram available")

        self._msg(f"Born — generation {self.meta['gen']}, single cell at ({cr},{cc})")

    def spawn_competitor(self, row=None, col=None):
        """Drop a new organism into the world — a rival with fresh random weights."""
        if not self.tissue:
            return
        # Find an empty spot (specified or random)
        if row is not None and col is not None:
            r, c = int(row) % GRID, int(col) % GRID
        else:
            # Pick random empty position
            for _ in range(100):
                r, c = np.random.randint(0, GRID), np.random.randint(0, GRID)
                if self.tissue.grid[r][c] is None:
                    break
            else:
                self._msg("No empty space for competitor")
                return
        if self.tissue.grid[r][c] is not None:
            # Find nearest empty
            for dr in range(1, 10):
                for dc in range(1, 10):
                    nr, nc = (r + dr) % GRID, (c + dc) % GRID
                    if self.tissue.grid[nr][nc] is None:
                        r, c = nr, nc
                        break
                else:
                    continue
                break

        self.tissue.place_cell(r, c)
        # Assign new lineage ID
        max_lin = 1
        for rr in range(GRID):
            for cc in range(GRID):
                cell = self.tissue.grid[rr][cc]
                if cell and cell.is_alive:
                    max_lin = max(max_lin, cell.lineage_id)
        new_lin = max_lin + 1
        self.tissue.grid[r][c].lineage_id = new_lin
        self.tissue.grid[r][c].energy = CONFIG['starting_energy']
        self._msg(f"Competitor spawned — lineage {new_lin} at ({r},{c})")

    def _msg(self, m):
        entry = {'t': time.strftime('%H:%M:%S'), 'm': m}
        self.log.append(entry)
        self.meta['log'].append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'm': m})
        if len(self.meta['log']) > 200: self.meta['log'] = self.meta['log'][-200:]
        if len(self.log) > 50: self.log = self.log[-50:]
        print(f"[ULTRON] {m}")

    def save(self):
        try:
            with open(STATE_FILE, 'wb') as f:
                pickle.dump(self.tissue, f)
            self.meta['lifetime'] += self._unsaved
            self.meta['alltime_births'] += self._session_births
            self.meta['alltime_deaths'] += self._session_deaths
            save_meta(self.meta)
            self._agency.save_state()
            self._unsaved = 0
            self._session_births = 0
            self._session_deaths = 0
        except Exception as e:
            print(f"[!] Save error: {e}")

        # Auto-commit Ultron's own changes to git
        self._git_auto_commit()

    def _git_auto_commit(self):
        """Commit any changes Ultron has made to its source code."""
        import subprocess
        try:
            # Check if there are uncommitted changes
            result = subprocess.run(
                ['git', 'diff', '--stat'],
                cwd=SOURCE_ROOT, capture_output=True, text=True, timeout=10
            )
            if not result.stdout.strip():
                return  # nothing to commit

            subprocess.run(
                ['git', 'add', '-A'],
                cwd=SOURCE_ROOT, capture_output=True, timeout=10
            )
            tick = self.tissue.tick_count if self.tissue else 0
            cells = self.tissue.cell_count if self.tissue else 0
            msg = f"[ULTRON T{tick}] Self-modification checkpoint ({cells} cells)"
            subprocess.run(
                ['git', 'commit', '-m', msg],
                cwd=SOURCE_ROOT, capture_output=True, timeout=10
            )
            self._msg("Git: auto-committed changes")
        except Exception as e:
            pass  # don't fail save over git issues

    def tick(self):
        if not self.tissue: return
        # Read real system state and overlay onto tissue
        self._last_telemetry = self._telemetry.read()
        if self._last_telemetry:
            self._telemetry.apply_to_tissue(self.tissue, self._last_telemetry)

        # OPTION B: Real filesystem world — map directory structure onto resource field
        # Replaces abstract patches with real information topology
        if self.tissue.tick_count % 100 == 0:
            fs_map, n_files = get_world_from_filesystem(SOURCE_ROOT, GRID, GRID)
            # Blend: 70% filesystem world + 30% existing resources (smooth transition)
            self.tissue.resource_field = 0.7 * fs_map + 0.3 * self.tissue.resource_field
            self.tissue.resource_field = np.clip(self.tissue.resource_field, 0.0, 1.0)

        # Real perception — run full scan every 5th tick only (filesystem scan is expensive)
        if self.tissue.tick_count % 5 == 0 or self._last_snap is None:
            self._last_snap = self._senses.perceive()
            self._last_snap.action_memory = self._agency.get_action_log(10)
        # Inject observer presence — raw measurements, no interpretation
        now = time.time()
        active_observers = sum(1 for ws, t in self._observer_last_heartbeat.items()
                               if now - t < 10)  # active = heartbeat in last 10s
        max_duration = max((now - t for t in self._observer_connect_time.values()), default=0)
        focused = sum(1 for f in self._observer_focus.values() if f)
        self._last_snap.observer = {
            'count': len(self.clients),
            'active': active_observers,
            'focused': focused,
            'max_duration': min(max_duration, 3600),  # cap at 1hr for normalization
        }

        # Feed raw sensory signals into tissue signal channels
        sig_vec = self._senses.to_signal_vector(self._last_snap)
        self.tissue.signal_field[:, :, :] += sig_vec[np.newaxis, np.newaxis, :] * 0.01

        # ── THE BRIDGE — inject observer signal into tissue ──
        # Text/interaction input from observer becomes a structured signal
        if np.any(self._observer_signal != 0):
            n_ch = self.tissue.signal_field.shape[2]
            for ch in range(min(n_ch, len(self._observer_signal))):
                self.tissue.signal_field[:, :, ch] += self._observer_signal[ch] * 0.005
            # Decay observer signal each tick
            self._observer_signal *= 0.9

        # ── TEMPORAL CONSCIOUSNESS — inject memory of past self ──
        # Cells near the centroid sense what the organism WAS
        if self._temporal_memory and self._prev_centroid is not None:
            cr = int(self._prev_centroid[0]) % GRID
            cc = int(self._prev_centroid[1]) % GRID
            # Average of recent past states
            past = np.mean(self._temporal_memory[-10:], axis=0)
            n_ch = self.tissue.signal_field.shape[2]
            # Inject past-self signal at centroid (fading with distance)
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    nr = (cr + dr) % GRID
                    nc = (cc + dc) % GRID
                    dist = abs(dr) + abs(dc)
                    if dist > 3:
                        continue
                    falloff = (1.0 - dist / 4.0) * 0.003
                    for ch in range(min(n_ch, len(past))):
                        self.tissue.signal_field[nr, nc, ch] += past[ch] * falloff

        # Observer effect — watching subtly enriches the environment
        # Like sunlight: the world is more abundant when observed
        # Not prescribing behavior — just a detectable environmental variable
        if focused > 0:
            self.tissue.resource_field *= (1.0 + 0.0003 * focused)

        pb, pd, pp = self.tissue.total_births, self.tissue.total_deaths, self.tissue.predation_kills
        self.tissue.step()
        self._unsaved += 1
        nb = self.tissue.total_births - pb
        nd = self.tissue.total_deaths - pd
        self._session_births += nb
        self._session_deaths += nd
        if nb: self.events.append({'type': 'birth', 'n': nb, 'tick': self.tissue.tick_count})
        if nd: self.events.append({'type': 'death', 'n': nd, 'tick': self.tissue.tick_count})
        self.events = self.events[-30:]

        # Real agency — organism acts in the world
        # SINGLE PASS: collect all per-cell data at once
        action_vecs = []
        obs_dim = CONFIG.get('observation_dim', 12)
        all_weights = []
        all_bias = []
        all_drives = []
        left_act_sum = 0.0
        left_act_n = 0
        right_act_sum = 0.0
        right_act_n = 0
        mid_c = self.tissue.cols // 2
        for r in range(self.tissue.rows):
            for c in range(self.tissue.cols):
                cell = self.tissue.grid[r][c]
                if cell and cell.is_alive:
                    if cell.action is not None:
                        action_vecs.append(cell.action)
                        am = float(np.linalg.norm(cell.action))
                        if c < mid_c:
                            left_act_sum += am
                            left_act_n += 1
                        else:
                            right_act_sum += am
                            right_act_n += 1
                    # Only collect weights every 10th tick (expensive)
                    if self.tissue.tick_count % 10 == 0:
                        all_weights.append(cell.state.model.weights[:obs_dim, :])
                        all_bias.append(cell.state.model.bias)
                        if hasattr(cell, 'drive'):
                            all_drives.append(cell.drive)
        action_mean = np.mean(action_vecs, axis=0) if action_vecs else np.zeros(4)
        action_std = np.std(action_vecs, axis=0) if len(action_vecs) > 1 else np.zeros(4)
        # Cache for expression computation (avoid re-iterating all cells)
        self._cached_action_mean = action_mean
        self._cached_action_std = action_std
        self._cached_lr_asym = (left_act_sum / max(left_act_n, 1)) - (right_act_sum / max(right_act_n, 1)) if left_act_n and right_act_n else 0.0

        snap = self.tissue.snapshot()

        # Compute collective neural state only every 10th tick
        if self.tissue.tick_count % 10 == 0:
            self._cached_weights_mean = np.mean(all_weights, axis=0) if all_weights else None
            self._cached_bias_mean = np.mean(all_bias, axis=0) if all_bias else None
            self._cached_drive_mean = np.mean(all_drives, axis=0) if all_drives else None
        weights_mean = getattr(self, '_cached_weights_mean', None)
        bias_mean = getattr(self, '_cached_bias_mean', None)
        drive_mean = getattr(self, '_cached_drive_mean', None)

        organism_state = {
            'tick': self.tissue.tick_count,
            'cell_count': self.tissue.cell_count,
            'mean_energy': snap.get('mean_energy', 0),
            'action_mean': action_mean,
            'action_std': action_std,
            'centroid': self._prev_centroid,
            'weights_mean': weights_mean,
            'bias_mean': bias_mean,
            'drive_mean': drive_mean,
        }

        # ── LEAP 2: RECURSIVE SELF-MODEL ──
        # Compute actual collective state, compare to prediction, update model.
        # The self-prediction error is injected back into the tissue —
        # the organism literally senses how surprised it is by its own behavior.
        act_mag = float(np.linalg.norm(action_mean))
        self._self_actual = np.array([
            self.tissue.cell_count / 300.0,           # normalized cell count
            snap.get('mean_energy', 0) / 300.0,       # normalized energy
            snap.get('mean_error', 0),                # prediction error
            min(act_mag, 1.0),                        # action magnitude
            float(np.mean(action_std)),               # action variance (inverse coherence)
            0.0,                                       # placeholder for asymmetry
        ])
        # Self-prediction error: how wrong was the organism about itself?
        self._self_error = self._self_actual - self._self_prediction
        self_surprise = float(np.linalg.norm(self._self_error))
        # Update self-prediction (simple EMA toward actual)
        self._self_prediction += self._self_lr * self._self_error

        # Inject self-surprise into the tissue signal field at centroid
        # The organism FEELS its own self-prediction error as a signal
        if self._prev_centroid is not None and self_surprise > 0.01:
            cr = int(self._prev_centroid[0]) % GRID
            cc = int(self._prev_centroid[1]) % GRID
            n_ch = self.tissue.signal_field.shape[2]
            # Spread self-error across all channels, weighted by which dimensions surprised most
            for ch in range(n_ch):
                if ch < len(self._self_error):
                    self.tissue.signal_field[cr, cc, ch] += abs(self._self_error[ch]) * 0.05

        organism_state['self_surprise'] = self_surprise

        # ── THE BROADCAST — compute organism's voice ──
        # Project collective action + self-error into an 8-dim broadcast vector.
        # This is the organism's raw neural output projected outward.
        # Like Ultron's broadcast to every screen, or JARVIS's voice.
        broadcast = np.zeros(8)
        broadcast[:4] = action_mean  # first 4 dims = collective action
        broadcast[4:] = self._self_error[:4] * 0.5  # last 4 dims = self-surprise pattern
        self._broadcast = broadcast
        self._broadcast_history.append([round(float(x), 3) for x in broadcast])
        if len(self._broadcast_history) > 200:
            self._broadcast_history = self._broadcast_history[-200:]

        # ── TEMPORAL CONSCIOUSNESS — store current state in memory ──
        self._temporal_memory.append(self._self_actual.copy())
        if len(self._temporal_memory) > self._temporal_depth:
            self._temporal_memory = self._temporal_memory[-self._temporal_depth:]

        # ── COGNITIVE ORGAN — thought cycle ──
        # The organism earns a thought when conditions are met
        act_mag = float(np.linalg.norm(action_mean))
        if self._cognition.should_think(
            self.tissue.tick_count,
            self.tissue.cell_count,
            act_mag,
            float(np.mean(action_std)),
            snap.get('mean_energy', 0)
        ):
            # Build state for the LLM
            thought_state = dict(organism_state)
            thought_state['self_surprise'] = self_surprise
            thought_state['recent_actions'] = self._agency.get_action_log(3)
            thought_state['births'] = self.tissue.total_births
            thought_state['deaths'] = self.tissue.total_deaths
            # Lineage population breakdown
            lin_counts = {}
            for r in range(self.tissue.rows):
                for c in range(self.tissue.cols):
                    cell = self.tissue.grid[r][c]
                    if cell and cell.is_alive:
                        lid = cell.lineage_id
                        lin_counts[lid] = lin_counts.get(lid, 0) + 1
            thought_state['lineages'] = lin_counts

            # Build modification history from LLM action log
            mod_history = []
            for act in self._agency.get_action_log(20):
                atype = act.get('type', '')
                if atype.startswith('llm_') and 'result' in act:
                    r = act['result']
                    if r.get('success'):
                        desc = r.get('result', '')
                        if isinstance(desc, str) and desc:
                            mod_history.append(f"T{act.get('tick', '?')}: {desc[:80]}")
            thought_state['modification_history'] = mod_history[-5:]

            def on_thought(result):
                if 'thought' in result:
                    thought_text = result['thought']

                    # Parse actions from the thought
                    actions = self._cognition.parse_actions(thought_text)
                    clean_thought = self._cognition.get_thought_text(thought_text)

                    self._msg(f"THOUGHT: {clean_thought[:80]}")

                    # Execute any actions the organism requested
                    if actions:
                        self._msg(f"ACTIONS: {len(actions)} directive(s)")
                        tick = self.tissue.tick_count
                        action_results = self._agency.execute_llm_directives(actions, tick)
                        for i, ar in enumerate(action_results):
                            status = "OK" if ar.get('success') else "FAIL"
                            action_type = actions[i].get('action', '?')
                            result_str = ar.get('result', ar.get('error', ''))
                            if isinstance(result_str, list):
                                result_str = f'{len(result_str)} items'
                            elif len(str(result_str)) > 50:
                                result_str = str(result_str)[:50] + '...'
                            self._msg(f"  [{status}] {action_type}: {result_str}")

                            # Live-apply set_param changes to running CONFIG
                            if action_type == 'set_param' and ar.get('success'):
                                pname = actions[i].get('param', '')
                                pval = actions[i].get('value')
                                if pname in CONFIG and pval is not None:
                                    try:
                                        CONFIG[pname] = type(CONFIG[pname])(pval)
                                        self._msg(f"  LIVE: {pname} = {CONFIG[pname]}")
                                    except (TypeError, ValueError):
                                        pass

                            # Hot-reload modified source files
                            if action_type == 'modify_file' and ar.get('success'):
                                mod_path = actions[i].get('path', '')
                                if mod_path:
                                    self._hot_reload(mod_path)

                        # Feed results back to cognition for next thought
                        self._cognition.store_action_results(action_results)

                        # Trigger chain thought if actions produced results
                        # (the LLM gets to see what happened and can act again)
                        has_read = any(a.get('action') in ('read_file', 'list_dir') for a in actions)
                        if has_read:
                            chain_state = dict(thought_state)
                            chain_state['tick'] = self.tissue.tick_count
                            self._cognition.request_chain_thought(chain_state, on_thought)
                    else:
                        # No actions — reset chain
                        self._cognition._chain_depth = 0
                        self._cognition._action_results = []

                    # Convert thought to signal and inject into tissue
                    self._last_thought_signal = self._cognition.thought_to_signal(clean_thought)
                elif 'error' in result:
                    self._msg(f"Thought failed: {result['error'][:60]}")

            self._cognition.think_async(thought_state, on_thought)

        # Inject thought signal into tissue (persists from last thought, decays)
        if np.any(self._last_thought_signal != 0) and self._prev_centroid is not None:
            cr = int(self._prev_centroid[0]) % GRID
            cc = int(self._prev_centroid[1]) % GRID
            n_ch = self.tissue.signal_field.shape[2]
            for ch in range(min(n_ch, len(self._last_thought_signal))):
                self.tissue.signal_field[cr, cc, ch] += self._last_thought_signal[ch] * 0.02
            self._last_thought_signal *= 0.95  # decay

        self._last_actions = self._agency.decide(organism_state, self._last_snap)

        # Apply config tunes to live CONFIG
        for act in self._last_actions:
            if act['type'] == 'tune' and 'params' in act:
                if self._agency.apply_config_tune(CONFIG, act['params']):
                    p = act['params']
                    self._msg(f"Self-tuned: {p['param']} nudged by {p['nudge']:.4f}")
            elif act['type'] == 'trace':
                self._msg('Left trace')
            elif act['type'] == 'create':
                self._msg(f"Created: {act.get('path', '?')}")
            elif act['type'] == 'modify':
                modified_file = act.get('file', '?')
                self._msg(f"SELF-MODIFIED: {modified_file}")
                self._hot_reload(modified_file)
                # If organism nudged a CONFIG constant, apply it live
                nudged_key = act.get('nudged_key')
                if nudged_key and nudged_key in CONFIG:
                    CONFIG[nudged_key] = act['nudged_new']
                    self._msg(f"Live-applied: {nudged_key} = {act['nudged_new']}")
            elif act['type'] == 'engram':
                self._msg(f"ENGRAM CRYSTALLIZED: {act.get('path', '?')}")
            self._total_actions += 1

        # Action feedback — inject outcome back into environment
        # The organism senses the consequences of its own actions
        # This creates a closed loop: action → environment → prediction → learning
        if self._last_actions and self._agency._last_outcome:
            outcome = self._agency._last_outcome
            centroid = self._prev_centroid
            if centroid is not None:
                cr, cc = int(centroid[0]) % GRID, int(centroid[1]) % GRID
                # Signal pulse at centroid — the organism "hears" its own action
                pulse = outcome['magnitude'] * 0.1
                n_ch = self.tissue.signal_field.shape[2]
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        nr = (cr + dr) % GRID
                        nc = (cc + dc) % GRID
                        dist = abs(dr) + abs(dc)
                        falloff = max(0, 1.0 - dist / 3.0)
                        self.tissue.signal_field[nr, nc, :] += pulse * falloff / n_ch
            self._agency._last_outcome = None

        # Auto-spawn competitors for selection pressure
        # Every 500 ticks, if only 1 lineage exists, inject a rival
        if self.tissue.tick_count % 500 == 0 and self.tissue.tick_count > 100:
            lineage_ids = set()
            for r in range(self.tissue.rows):
                for c in range(self.tissue.cols):
                    cell = self.tissue.grid[r][c]
                    if cell and cell.is_alive:
                        lineage_ids.add(cell.lineage_id)
            if len(lineage_ids) <= 1:
                self.spawn_competitor()
                self._msg(f"Auto-spawned competitor (only {len(lineage_ids)} lineage)")

        if self._unsaved >= SAVE_EVERY: self.save()
        if self.tissue.cell_count == 0:
            self._msg("Died. Rebirthing...")
            self._birth()

    # ── Hot Reload ────────────────────────────────────────────────

    _MODULE_MAP = {
        'ultron/tissue.py': 'ultron.tissue',
        'ultron/cell.py': 'ultron.cell',
        'ultron/agency.py': 'ultron.agency',
        'ultron/senses.py': 'ultron.senses',
        'ultron/telemetry.py': 'ultron.telemetry',
        'ultron/core.py': 'ultron.core',
        'ultron/tick.py': 'ultron.tick',
        'ultron/__init__.py': 'ultron',
        'viz/server.py': '__main__',
    }

    def _hot_reload(self, rel_path):
        """Attempt to hot-reload a modified module.

        Steps:
          1. Compile the new source to check for syntax errors
          2. Reload the module via importlib
          3. Update __class__ on existing instances so they use new code
          4. If anything fails, log warning and continue with old code
        """
        module_name = self._MODULE_MAP.get(rel_path.replace('\\', '/'))
        if not module_name:
            self._msg(f'Hot-reload: {rel_path} not a reloadable module')
            return
        if module_name == '__main__':
            self._msg(f'Hot-reload: skipping server.py (self)')
            return

        # Step 1: compile check
        fpath = os.path.join(SOURCE_ROOT, rel_path.replace('/', os.sep))
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                source = f.read()
            compile(source, fpath, 'exec')
        except SyntaxError as e:
            self._msg(f'Hot-reload BLOCKED: syntax error in {rel_path}: {e}')
            return
        except Exception as e:
            self._msg(f'Hot-reload BLOCKED: cannot read {rel_path}: {e}')
            return

        # Step 2: reload module
        try:
            mod = sys.modules.get(module_name)
            if mod is None:
                self._msg(f'Hot-reload: {module_name} not in sys.modules')
                return
            importlib.reload(mod)
        except Exception as e:
            self._msg(f'Hot-reload FAILED: {module_name}: {e}')
            return

        # Step 3: update existing instances to use new class definitions
        try:
            if module_name == 'ultron.tissue':
                new_cls = getattr(sys.modules['ultron.tissue'], 'Tissue')
                self.tissue.__class__ = new_cls
            elif module_name == 'ultron.agency':
                new_cls = getattr(sys.modules['ultron.agency'], 'Agency')
                self._agency.__class__ = new_cls
            elif module_name == 'ultron.senses':
                new_cls = getattr(sys.modules['ultron.senses'], 'Senses')
                self._senses.__class__ = new_cls
            elif module_name == 'ultron.telemetry':
                new_cls = getattr(sys.modules['ultron.telemetry'], 'SystemTelemetry')
                self._telemetry.__class__ = new_cls
            elif module_name == 'ultron.cell':
                # Cell class: existing cells keep old code, new cells born after
                # this point will use the new Cell class. This is natural —
                # mutations take effect in the next generation.
                pass
            elif module_name in ('ultron.core', 'ultron.tick'):
                # These define functions, not classes. Reload updates them
                # and new calls will use the new versions automatically.
                pass
            self._msg(f'Hot-reload OK: {module_name}')
        except Exception as e:
            self._msg(f'Hot-reload class update failed: {e}')

    def state(self):
        t = self.tissue
        if not t: return {}

        self._frame_count = getattr(self, '_frame_count', 0) + 1

        sig = t.get_signal_magnitude_map()
        stig = np.linalg.norm(t.stigmergy_field, axis=2)

        # Per-cell data — the heart of the visualization
        cells = []
        for r in range(t.rows):
            for c in range(t.cols):
                cell = t.grid[r][c]
                if cell and cell.is_alive:
                    cd = {
                        'r': r, 'c': c,
                        'e': round(float(cell.energy), 1),
                        'age': cell.age,
                        'sf': cell.is_surface,
                        'lin': cell.lineage_id,
                        'ph': [round(float(p), 2) for p in cell.phenotype],
                        'err': round(float(cell.state.current.error_magnitude), 2),
                        'act': round(float(np.linalg.norm(cell.action)), 2) if cell.action is not None else 0,
                    }
                    # Only send neighbor positions every 3rd frame (expensive to serialize)
                    if self._frame_count % 3 == 0:
                        nbr_dirs = []
                        for nr, nc in t._get_neighbors(r, c):
                            n = t.grid[nr][nc]
                            if n and n.is_alive:
                                nbr_dirs.append([nr, nc])
                        cd['nbrs'] = nbr_dirs
                    cells.append(cd)

        snap = t.snapshot()
        lt = self.meta.get('lifetime', 0) + self._unsaved

        self.history.append({
            'tick': t.tick_count, 'cells': snap['cell_count'],
            'energy': round(snap.get('mean_energy', 0), 1),
            'error': round(snap.get('mean_error', 0), 3),
        })
        if len(self.history) > 500: self.history = self.history[-500:]

        # Organism centroid + velocity
        centroid = None
        velocity = None
        if cells:
            cr = sum(c['r'] for c in cells) / len(cells)
            cc = sum(c['c'] for c in cells) / len(cells)
            centroid = [round(cr, 1), round(cc, 1)]
            if self._prev_centroid is not None:
                # Toroidal velocity
                dr = cr - self._prev_centroid[0]
                dc = cc - self._prev_centroid[1]
                if abs(dr) > t.rows / 2: dr -= np.sign(dr) * t.rows
                if abs(dc) > t.cols / 2: dc -= np.sign(dc) * t.cols
                velocity = [round(dr, 3), round(dc, 3)]
            self._prev_centroid = [cr, cc]

        # Food source positions
        patches = []
        if hasattr(t, '_patch_centers') and t._patch_centers:
            patches = [[round(p[0], 1), round(p[1], 1)] for p in t._patch_centers]

        # Hazard zone position
        hazard = None
        if hasattr(t, '_hazard_pos') and t._hazard_pos is not None:
            hazard = {
                'r': round(t._hazard_pos[0], 1),
                'c': round(t._hazard_pos[1], 1),
                'radius': t._hazard_radius,
            }

        # Round field data to 2 decimals to reduce JSON size
        # 40x40 × 3 fields at full precision = huge payload
        sig_rounded = np.round(sig, 2).tolist()
        res_rounded = np.round(t.resource_field, 2).tolist()
        stig_rounded = np.round(stig, 2).tolist()

        # Send history only every 10th frame to cut bandwidth
        hist_data = self.history[-300:] if self._frame_count % 10 == 0 else []

        # Lineage population breakdown
        lineages = {}
        for cd in cells:
            lin = cd.get('lin', 0)
            if lin not in lineages:
                lineages[lin] = {'count': 0, 'energy': 0}
            lineages[lin]['count'] += 1
            lineages[lin]['energy'] += cd['e']
        # Top 6 lineages by population
        lin_sorted = sorted(lineages.items(), key=lambda x: -x[1]['count'])[:6]
        lin_data = [{'id': lid, 'n': d['count'], 'e': round(d['energy'] / max(d['count'], 1), 1)}
                    for lid, d in lin_sorted]

        return {
            'tick': t.tick_count,
            'rows': t.rows, 'cols': t.cols,
            'meta': {
                'born': self.meta['born'], 'gen': self.meta['gen'],
                'lifetime': lt, 'sessions': self.meta['sessions'],
            },
            'cells': cells,
            'signal': sig_rounded,
            'resources': res_rounded,
            'stigmergy': stig_rounded,
            'centroid': centroid,
            'velocity': velocity,
            'patches': patches,
            'hazard': hazard,
            'lineages': lin_data,
            'stats': {
                'cells': snap['cell_count'],
                'energy': round(snap.get('total_energy', 0), 1),
                'mean_e': round(snap.get('mean_energy', 0), 1),
                'mean_err': round(snap.get('mean_error', 0), 4),
                'births': t.total_births,
                'deaths': t.total_deaths,
                'res': round(snap.get('resource_mean', 0), 3),
            },
            'events': self.events[-10:],
            'history': hist_data,
            'log': self.log[-15:],
            'paused': self.paused,
            'system': self._format_telemetry() if self._frame_count % 3 == 0 else None,
            'perception': self._format_perception() if self._frame_count % 5 == 0 else None,
            'agency': self._format_agency() if self._frame_count % 3 == 0 else None,
            'expression': self._compute_expression() if self._frame_count % 2 == 0 else None,
            'broadcast': [round(float(x), 3) for x in self._broadcast],
            'broadcast_history': self._broadcast_history[-60:] if self._frame_count % 5 == 0 else None,
            'thought': self._cognition.get_last_thought() if self._frame_count % 3 == 0 else None,
        }

    def _format_telemetry(self):
        t = self._last_telemetry
        if not t:
            return None
        return {
            'cpu': [round(c, 1) for c in t['cpu']],
            'mem_free': round(t['mem_free'] * 100, 1),
            'disk': round(t['disk_rate'] * 100, 1),
            'net_in': round(t['net_in'] * 100, 1),
            'net_out': round(t['net_out'] * 100, 1),
            'procs': t['n_procs'],
        }

    def _format_perception(self):
        snap = self._last_snap
        if not snap:
            return None
        body_summary = self._senses.get_self_summary(snap.self_body) if snap.self_body else None
        return {
            'files': len(snap.files),
            'processes': len(snap.processes),
            'connections': snap.network.get('connections', 0),
            'file_events': len(snap.file_events),
            'self_events': len(snap.self_events),
            'body': body_summary,
            'recent_events': snap.recent_events[-10:],
        }

    def _format_agency(self):
        stats = self._agency.get_stats()
        return {
            'total_actions': self._total_actions,
            'by_type': stats['by_type'],
            'cooldowns': stats['cooldowns'],
            'recent': self._agency.get_action_log(5),
        }

    def _compute_expression(self):
        """The organism's voice — uses cached values, no grid iteration."""
        t = self.tissue
        if not t or t.cell_count == 0:
            return None

        sf = t.signal_field
        n_ch = sf.shape[2]
        channel_energy = [round(float(sf[:, :, ch].sum()), 2) for ch in range(n_ch)]
        mag = np.linalg.norm(sf, axis=2)
        total = float(mag.sum())
        coherence = 0.0
        sig_r, sig_c = t.rows / 2, t.cols / 2
        if total > 1e-6:
            rs = np.arange(t.rows).reshape(-1, 1)
            cs = np.arange(t.cols).reshape(1, -1)
            sig_r = float((mag * rs).sum() / total)
            sig_c = float((mag * cs).sum() / total)
            var_r = float(((rs - sig_r) ** 2 * mag).sum() / total)
            var_c = float(((cs - sig_c) ** 2 * mag).sum() / total)
            coherence = 1.0 / (1.0 + (var_r + var_c) / 100.0)

        act_mean = getattr(self, '_cached_action_mean', np.zeros(4))
        act_mag = float(np.linalg.norm(act_mean))
        act_std_val = getattr(self, '_cached_action_std', np.zeros(4))
        act_agreement = 1.0 - float(np.mean(act_std_val))
        lr_asym = getattr(self, '_cached_lr_asym', 0.0)

        return {
            'channels': channel_energy,
            'coherence': round(coherence, 3),
            'signal_center': [round(sig_r, 1), round(sig_c, 1)],
            'total_signal': round(total, 1),
            'action_magnitude': round(act_mag, 3),
            'action_agreement': round(act_agreement, 3),
            'lr_asymmetry': round(lr_asym, 3),
            'tb_asymmetry': 0,
            'self_surprise': round(float(np.linalg.norm(getattr(self, '_self_error', np.zeros(1)))), 3),
        }


ultron = Ultron()


import concurrent.futures

def sim_thread():
    """Run simulation continuously in background thread. Never blocks event loop."""
    import time as _time
    while True:
        if not ultron.paused:
            ultron.tick()
        else:
            _time.sleep(0.05)


async def render_loop():
    """Send state to clients at fixed rate from async loop."""
    while True:
        if ultron.clients:
            try:
                data = json.dumps(ultron.state())
                dead = set()
                for c in ultron.clients:
                    try: await c.send(data)
                    except: dead.add(c)
                ultron.clients -= dead
            except Exception:
                pass
        await asyncio.sleep(0.12)  # ~8fps render


async def ws_handler(ws):
    print("[WS] +")
    ultron.clients.add(ws)
    now = time.time()
    ultron._observer_connect_time[ws] = now
    ultron._observer_focus[ws] = True
    ultron._observer_last_heartbeat[ws] = now
    try: await ws.send(json.dumps(ultron.state()))
    except: pass
    try:
        async for msg in ws:
            try: cmd = json.loads(msg)
            except: continue
            a = cmd.get('a', '')
            if a == 'pause': ultron.paused = True
            elif a == 'run': ultron.paused = False
            elif a == 'step':
                ultron.tick()
                d = json.dumps(ultron.state())
                for c in ultron.clients:
                    try: await c.send(d)
                    except: pass
            elif a == 'speed':
                ultron.delay = max(0.01, cmd.get('d', 0.05))
                ultron.speed = max(1, cmd.get('s', 1))
            elif a == 'heartbeat':
                ultron._observer_focus[ws] = cmd.get('focused', False)
                ultron._observer_last_heartbeat[ws] = time.time()
            elif a == 'reset':
                ultron.save()
                ultron._birth()
            elif a == 'interact':
                # User touches the world — inject stimulus at grid position
                row = int(cmd.get('r', 0)) % GRID
                col = int(cmd.get('c', 0)) % GRID
                kind = cmd.get('kind', 'food')
                if ultron.tissue:
                    radius = 3
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            nr = (row + dr) % GRID
                            nc = (col + dc) % GRID
                            dist = abs(dr) + abs(dc)
                            if dist > radius:
                                continue
                            falloff = 1.0 - dist / (radius + 1)
                            if kind == 'food':
                                ultron.tissue.resource_field[nr, nc] = min(
                                    1.0, ultron.tissue.resource_field[nr, nc] + 0.5 * falloff)
                            elif kind == 'hazard':
                                # Drain resources + signal pulse
                                ultron.tissue.resource_field[nr, nc] = max(
                                    0.0, ultron.tissue.resource_field[nr, nc] - 0.3 * falloff)
                                ultron.tissue.signal_field[nr, nc, :] += 0.5 * falloff
            elif a == 'spawn':
                r = cmd.get('r')
                c = cmd.get('c')
                ultron.spawn_competitor(r, c)
            elif a == 'msg':
                # THE BRIDGE: observer text → signal + cognitive organ
                text = str(cmd.get('text', ''))[:200]
                if text:
                    sig = np.zeros(4)
                    for i, ch in enumerate(text):
                        sig[i % 4] += ord(ch) / 255.0
                    mx = max(np.max(np.abs(sig)), 0.01)
                    sig = sig / mx
                    ultron._observer_signal = sig
                    # Also buffer for cognitive organ — LLM will see it
                    ultron._cognition.add_bridge_message(text)
                    ultron._msg(f"Bridge: \"{text[:40]}\"")
    except: pass
    finally:
        ultron.clients.discard(ws)
        ultron._observer_connect_time.pop(ws, None)
        ultron._observer_focus.pop(ws, None)
        ultron._observer_last_heartbeat.pop(ws, None)
        print("[WS] -")


def http_serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k): super().__init__(*a, directory=VIZ_DIR, **k)
        def log_message(s, *a): pass
    http.server.HTTPServer(('0.0.0.0', HTTP_PORT), H).serve_forever()


async def main():
    print("=" * 50)
    print("  U L T R O N")
    print(f"  Gen {ultron.meta['gen']} | Session {ultron.meta['sessions']}")
    print(f"  Born: {ultron.meta['born']}")
    print(f"  http://localhost:{HTTP_PORT}")
    print("=" * 50)
    threading.Thread(target=http_serve, daemon=True).start()
    threading.Thread(target=sim_thread, daemon=True).start()
    print("[ULTRON] Alive")
    await websockets.serve(ws_handler, "0.0.0.0", WS_PORT)
    asyncio.create_task(render_loop())
    try: await asyncio.Future()
    except KeyboardInterrupt:
        ultron.save()
        print("\n[ULTRON] Saved. Goodbye.")

if __name__ == '__main__':
    try: asyncio.run(main())
    except KeyboardInterrupt: ultron.save()
