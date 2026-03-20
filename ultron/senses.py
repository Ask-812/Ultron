"""
Ultron Senses — Real System Perception.

The organism's eyes, ears, and touch. This module gives Ultron
actual awareness of the digital world it lives in:

  - File system: directories, files, sizes, ages, changes
  - Processes: what's running, how much they consume
  - Network: active connections, ports, traffic
  - Events: what changed since last tick

This is NOT hardcoded mapping. Raw sensory data is delivered
to the organism as signal vectors. The organism's neural weights
decide what matters — we don't tell it.

The file system IS the terrain. Processes ARE other entities.
Network connections ARE pathways. Changes ARE events.
"""

import os
import time
import numpy as np

try:
    import psutil
    PSUTIL = True
except ImportError:
    PSUTIL = False


class Senses:
    """Real system perception for the organism — including self-awareness."""

    def __init__(self, home_dir, source_root=None):
        """
        Args:
            home_dir: The organism's home territory on disk.
            source_root: Root of the organism's own source code.
                         If None, auto-detected from this file's location.
        """
        self.home = home_dir
        os.makedirs(home_dir, exist_ok=True)

        # The organism's own body — the source files that make it alive
        if source_root is None:
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_root = source_root
        self._source_dirs = ['ultron', 'viz']  # directories that ARE the organism

        # Perception state (remembered between ticks)
        self._prev_files = {}       # path → (size, mtime)
        self._prev_procs = set()    # set of pids
        self._prev_connections = 0
        self._prev_net_bytes = (0, 0)
        self._prev_self_files = {}  # own source: path → (size, mtime, hash)
        self._event_log = []        # recent events
        self._tick = 0

    def perceive(self):
        """One tick of perception. Returns a SensorySnapshot."""
        self._tick += 1
        snap = SensorySnapshot()

        # 1. File system perception — scan home directory
        snap.files = self._scan_files()
        snap.file_events = self._detect_file_changes(snap.files)

        # 2. Process perception — what else lives on this machine
        snap.processes = self._scan_processes()
        snap.process_events = self._detect_process_changes(snap.processes)

        # 3. Network perception — connections and traffic
        snap.network = self._scan_network()

        # 4. System vitals — raw numbers
        snap.vitals = self._read_vitals()

        # 5. Self-perception — the organism sees its own source code
        snap.self_body = self._scan_self()
        snap.self_events = self._detect_self_changes(snap.self_body)

        # 6. Compile event stream
        all_events = snap.file_events + snap.process_events + snap.self_events
        for e in all_events:
            self._event_log.append(e)
        if len(self._event_log) > 200:
            self._event_log = self._event_log[-200:]
        snap.recent_events = self._event_log[-20:]

        return snap

    # ── Self-perception ──────────────────────────────────────────

    def _scan_self(self):
        """The organism reads its own source files — its body."""
        body = {}
        for src_dir in self._source_dirs:
            dirpath = os.path.join(self.source_root, src_dir)
            if not os.path.isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
                if not fname.endswith(('.py', '.html', '.js', '.css')):
                    continue
                fpath = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(fpath)
                    rel = os.path.join(src_dir, fname)
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    body[rel] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'lines': content.count('\n') + 1,
                        'content': content,
                    }
                except (OSError, PermissionError):
                    pass
        return body

    def _detect_self_changes(self, current_body):
        """Detect changes to the organism's own source code."""
        events = []
        prev = self._prev_self_files

        for path, info in current_body.items():
            if path not in prev:
                events.append({'type': 'self_new', 'path': path,
                               'lines': info['lines'], 'tick': self._tick})
            elif info['mtime'] != prev[path][1]:
                events.append({'type': 'self_changed', 'path': path,
                               'lines': info['lines'], 'tick': self._tick})

        for path in prev:
            if path not in current_body:
                events.append({'type': 'self_lost', 'path': path,
                               'tick': self._tick})

        self._prev_self_files = {p: (i['size'], i['mtime'])
                                  for p, i in current_body.items()}
        return events

    def get_self_summary(self, body):
        """Summarize the organism's own body — what it's made of."""
        total_lines = sum(f['lines'] for f in body.values())
        total_bytes = sum(f['size'] for f in body.values())
        files_by_dir = {}
        for path, info in body.items():
            d = path.split(os.sep)[0] if os.sep in path else path.split('/')[0]
            files_by_dir.setdefault(d, []).append({
                'name': os.path.basename(path),
                'lines': info['lines'],
                'size': info['size'],
            })
        return {
            'total_files': len(body),
            'total_lines': total_lines,
            'total_bytes': total_bytes,
            'components': files_by_dir,
        }

    def _scan_files(self):
        """Walk home directory. Each file becomes a perceived entity."""
        files = {}
        try:
            for root, dirs, filenames in os.walk(self.home):
                # Limit depth to prevent massive scans
                depth = root.replace(self.home, '').count(os.sep)
                if depth > 3:
                    dirs.clear()
                    continue
                for fname in filenames:
                    fpath = os.path.join(root, fname)
                    try:
                        stat = os.stat(fpath)
                        rel = os.path.relpath(fpath, self.home)
                        files[rel] = {
                            'size': stat.st_size,
                            'mtime': stat.st_mtime,
                            'age': time.time() - stat.st_mtime,
                            'ext': os.path.splitext(fname)[1].lower(),
                        }
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass
        return files

    def _detect_file_changes(self, current_files):
        """Compare against previous scan — what's new, changed, gone?"""
        events = []
        prev = self._prev_files

        for path, info in current_files.items():
            if path not in prev:
                events.append({'type': 'file_new', 'path': path,
                               'size': info['size'], 'tick': self._tick})
            elif info['mtime'] != prev[path][1]:
                events.append({'type': 'file_changed', 'path': path,
                               'size': info['size'], 'tick': self._tick})

        for path in prev:
            if path not in current_files:
                events.append({'type': 'file_gone', 'path': path,
                               'tick': self._tick})

        # Update state
        self._prev_files = {p: (i['size'], i['mtime'])
                            for p, i in current_files.items()}
        return events

    def _scan_processes(self):
        """Perceive running processes as other entities."""
        if not PSUTIL:
            return []
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent',
                                          'memory_percent', 'status']):
                try:
                    info = p.info
                    procs.append({
                        'pid': info['pid'],
                        'name': info['name'] or 'unknown',
                        'cpu': info.get('cpu_percent', 0) or 0,
                        'mem': info.get('memory_percent', 0) or 0,
                        'status': info.get('status', 'unknown'),
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception:
            pass
        return procs

    def _detect_process_changes(self, current_procs):
        """Detect new and dead processes."""
        events = []
        current_pids = {p['pid'] for p in current_procs}

        new_pids = current_pids - self._prev_procs
        dead_pids = self._prev_procs - current_pids

        for p in current_procs:
            if p['pid'] in new_pids:
                events.append({'type': 'proc_born', 'name': p['name'],
                               'pid': p['pid'], 'tick': self._tick})

        for pid in dead_pids:
            events.append({'type': 'proc_died', 'pid': pid,
                           'tick': self._tick})

        self._prev_procs = current_pids
        return events

    def _scan_network(self):
        """Perceive network connections."""
        if not PSUTIL:
            return {'connections': 0, 'traffic_in': 0, 'traffic_out': 0}

        try:
            conns = psutil.net_connections(kind='inet')
            n_conns = len(conns)

            # Listening ports (organism's "openings")
            listening = [c for c in conns if c.status == 'LISTEN']
            established = [c for c in conns if c.status == 'ESTABLISHED']

            # Traffic delta
            net = psutil.net_io_counters()
            d_in = max(0, net.bytes_recv - self._prev_net_bytes[0])
            d_out = max(0, net.bytes_sent - self._prev_net_bytes[1])
            self._prev_net_bytes = (net.bytes_recv, net.bytes_sent)

            return {
                'connections': n_conns,
                'listening': len(listening),
                'established': len(established),
                'traffic_in': d_in,
                'traffic_out': d_out,
            }
        except Exception:
            return {'connections': 0, 'traffic_in': 0, 'traffic_out': 0}

    def _read_vitals(self):
        """Raw system vitals — unprocessed numbers."""
        if not PSUTIL:
            return {}
        try:
            cpu = psutil.cpu_percent(interval=0, percpu=True)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(self.home)
            return {
                'cpu_per_core': cpu,
                'cpu_avg': sum(cpu) / len(cpu) if cpu else 0,
                'ram_total': mem.total,
                'ram_used': mem.used,
                'ram_free_pct': mem.available / mem.total if mem.total else 0,
                'disk_total': disk.total,
                'disk_free': disk.free,
                'disk_free_pct': disk.free / disk.total if disk.total else 0,
            }
        except Exception:
            return {}

    def to_signal_vector(self, snap):
        """Convert raw perception into a fixed-size numerical vector.

        This is a TRANSDUCER — it normalizes raw system data into [0,1]
        range so the tissue signal channels can carry it. No interpretation.
        Each channel carries one raw measurement, normalized.
        The organism's neural weights learn what matters.

        Returns: numpy array of shape (signal_dim,) — normalized sensory data
        """
        v = np.zeros(4)

        vitals = snap.vitals
        if vitals:
            # Channel 0: CPU utilization (0-1)
            v[0] = min(vitals.get('cpu_avg', 0) / 100.0, 1.0)

            # Channel 1: RAM utilization (0-1)
            v[1] = 1.0 - vitals.get('ram_free_pct', 0.5)

            # Channel 2: Event count, normalized (0-1)
            n_events = len(snap.file_events) + len(snap.process_events) + len(snap.self_events)
            v[2] = min(n_events / 10.0, 1.0)

            # Channel 3: combined environmental activity
            # Network traffic + observer presence + recent events
            total_traffic = snap.network.get('traffic_in', 0) + \
                            snap.network.get('traffic_out', 0)
            net_component = min(total_traffic / 1e6, 1.0)

            # Observer presence contributes to channel 3
            obs_component = 0.0
            if hasattr(snap, 'observer') and snap.observer:
                obs = snap.observer
                obs_component = min(obs.get('active', 0) / 3.0, 1.0)  # normalize: 3 watchers = max
                obs_component += 0.2 * min(obs.get('focused', 0), 1.0)  # focused adds 0.2
                obs_component = min(obs_component, 1.0)

            v[3] = min(net_component + obs_component, 1.0)

        return v


class SensorySnapshot:
    """One moment of perception — everything the organism senses."""

    def __init__(self):
        self.files = {}           # path → {size, mtime, age, ext}
        self.file_events = []     # new, changed, gone
        self.processes = []       # running processes
        self.process_events = []  # born, died
        self.network = {}         # connections, traffic
        self.vitals = {}          # cpu, ram, disk
        self.self_body = {}       # own source files: path → {size, lines, content}
        self.self_events = []     # self_new, self_changed, self_lost
        self.recent_events = []   # last 20 events
        self.action_memory = []   # recent action outcomes — the organism senses its own actions
        self.observer = None       # observer presence data (set by server)
