"""
Ultron Telemetry — Real System as Environment.

Maps real computer metrics onto the tissue grid so the organism
experiences the actual machine as its world:

  CPU cores    → heat zones (high CPU = resource drain)
  Free memory  → global resource regeneration rate
  Disk I/O     → seismic activity (resource field disturbance)
  Network I/O  → signal injection on channels 2-3
  Process count → environmental pressure

The organism doesn't know it's reading system stats.
It just experiences a world that shifts and pulses with the
real rhythms of the computer it lives on.
"""

import numpy as np
import time

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class SystemTelemetry:
    """Reads system metrics and maps them onto tissue-sized arrays."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self._prev_net = None
        self._prev_disk = None
        self._cpu_zones = self._build_cpu_zones()

    def _build_cpu_zones(self):
        """Assign each CPU core to a region of the grid.

        Cores are distributed in a roughly even spatial layout so
        high CPU usage on core N creates a localized hot zone.
        """
        if not PSUTIL_AVAILABLE:
            return []

        n_cores = psutil.cpu_count() or 4
        zones = []
        # Arrange cores in a grid pattern
        side = int(np.ceil(np.sqrt(n_cores)))
        zone_h = self.rows / side
        zone_w = self.cols / side

        for i in range(n_cores):
            row_idx = i // side
            col_idx = i % side
            center_r = zone_h * (row_idx + 0.5)
            center_c = zone_w * (col_idx + 0.5)
            radius = min(zone_h, zone_w) * 0.6
            zones.append({
                'center': (center_r, center_c),
                'radius': radius,
                'core': i,
            })
        return zones

    def read(self):
        """Read current system state. Returns a telemetry dict."""
        if not PSUTIL_AVAILABLE:
            return None

        # CPU per core (0-100)
        cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)

        # Memory
        mem = psutil.virtual_memory()
        mem_free_pct = (mem.available / mem.total) if mem.total > 0 else 0.5

        # Disk I/O delta
        disk_rate = 0.0
        try:
            disk = psutil.disk_io_counters()
            if disk and self._prev_disk is not None:
                delta = (disk.read_bytes + disk.write_bytes) - self._prev_disk
                disk_rate = min(delta / 1e8, 1.0)  # normalize to 0-1
            if disk:
                self._prev_disk = disk.read_bytes + disk.write_bytes
        except Exception:
            pass

        # Network I/O delta
        net_rate_in = 0.0
        net_rate_out = 0.0
        try:
            net = psutil.net_io_counters()
            if net and self._prev_net is not None:
                d_in = net.bytes_recv - self._prev_net[0]
                d_out = net.bytes_sent - self._prev_net[1]
                net_rate_in = min(d_in / 1e6, 1.0)
                net_rate_out = min(d_out / 1e6, 1.0)
            if net:
                self._prev_net = (net.bytes_recv, net.bytes_sent)
        except Exception:
            pass

        # Process count
        try:
            n_procs = len(psutil.pids())
        except Exception:
            n_procs = 100

        return {
            'cpu': cpu_per_core,
            'mem_free': mem_free_pct,
            'disk_rate': disk_rate,
            'net_in': net_rate_in,
            'net_out': net_rate_out,
            'n_procs': n_procs,
        }

    def apply_to_tissue(self, tissue, telemetry):
        """Overlay real system metrics onto the tissue's environment.

        This is where the digital world becomes the organism's reality.
        """
        if telemetry is None:
            return

        cpu = telemetry['cpu']
        mem_free = telemetry['mem_free']
        disk_rate = telemetry['disk_rate']
        net_in = telemetry['net_in']
        net_out = telemetry['net_out']

        # 1. CPU heat zones: high CPU usage drains resources in that region
        #    The organism experiences CPU load as "scorched earth"
        for zone in self._cpu_zones:
            if zone['core'] >= len(cpu):
                continue
            load = cpu[zone['core']] / 100.0  # 0-1
            if load < 0.1:
                continue
            cr, cc = zone['center']
            radius = zone['radius']
            drain = load * 0.003  # resource drain proportional to CPU load

            r_lo = max(0, int(cr - radius))
            r_hi = min(self.rows, int(cr + radius) + 1)
            c_lo = max(0, int(cc - radius))
            c_hi = min(self.cols, int(cc + radius) + 1)

            for r in range(r_lo, r_hi):
                for c in range(c_lo, c_hi):
                    dr = min(abs(r - cr), self.rows - abs(r - cr))
                    dc = min(abs(c - cc), self.cols - abs(c - cc))
                    dist = np.sqrt(dr**2 + dc**2)
                    if dist < radius:
                        falloff = 1.0 - dist / radius
                        tissue.resource_field[r, c] -= drain * falloff

        # 2. Memory pressure: low free memory = slower resource regeneration
        #    High free memory = the world is abundant
        #    This modulates the base resource regen globally
        tissue.resource_field *= (0.998 + 0.002 * mem_free)

        # 3. Disk I/O: seismic tremors — random resource perturbation
        #    Heavy disk usage creates "earthquakes" in the resource field
        if disk_rate > 0.05:
            noise = np.random.randn(self.rows, self.cols) * disk_rate * 0.01
            tissue.resource_field += noise

        # 4. Network traffic: inject as signal pulses spread across ALL channels
        #    No channel has prescribed meaning — the organism evolves its own interpretation
        n_channels = tissue.signal_field.shape[2]
        if net_in > 0.01:
            nr, nc = np.random.randint(0, self.rows), np.random.randint(0, self.cols)
            tissue.signal_field[nr, nc, :] += net_in * 0.5 / n_channels
        if net_out > 0.01:
            nr, nc = np.random.randint(0, self.rows), np.random.randint(0, self.cols)
            tissue.signal_field[nr, nc, :] += net_out * 0.5 / n_channels

        # Clamp
        tissue.resource_field = np.clip(tissue.resource_field, 0.0, 1.0)

    # ── LEAP 3: DIGITAL METABOLISM ──
    # The organism feeds on real information structure.
    # High-entropy positions (structured data nearby) = rich food.
    # Low-entropy positions = barren desert.
    # Called periodically from the server tick loop.

    def apply_digital_metabolism(self, tissue, home_dir):
        """Map real filesystem information density onto the resource field.

        The organism doesn't eat abstract numbers — it metabolizes the
        predictability of the real digital environment. Structured files
        (code, JSON, text) create rich zones. Empty areas stay barren.
        """
        import os
        import math

        try:
            # Scan the home directory for files
            file_entries = []
            for root, dirs, files in os.walk(home_dir):
                for f in files:
                    fpath = os.path.join(root, f)
                    try:
                        stat = os.stat(fpath)
                        file_entries.append({
                            'size': stat.st_size,
                            'mtime': stat.st_mtime,
                            'age': max(0, time.time() - stat.st_mtime),
                        })
                    except OSError:
                        continue

            if not file_entries:
                return

            # Compute information metrics
            total_size = sum(f['size'] for f in file_entries)
            n_files = len(file_entries)
            recent_files = sum(1 for f in file_entries if f['age'] < 300)  # files changed in last 5 min
            freshness = recent_files / max(n_files, 1)

            # Map onto resource field as a gradient boost
            # More files + more recent activity = richer world
            info_richness = min(math.log1p(total_size) / 20.0, 0.5)  # 0 to 0.5
            activity_boost = freshness * 0.1  # recent file changes boost resources

            # Apply as a subtle global boost to resource regeneration
            tissue.resource_field += (info_richness + activity_boost) * 0.001

            # Process count creates information texture — map process diversity
            # onto specific grid regions for spatial variation
            if PSUTIL_AVAILABLE:
                try:
                    pids = psutil.pids()
                    n_procs = len(pids)
                    # More processes = more information = richer world
                    proc_richness = min(n_procs / 500.0, 1.0) * 0.002
                    tissue.resource_field += proc_richness
                except Exception:
                    pass

            tissue.resource_field = np.clip(tissue.resource_field, 0.0, 1.0)
        except Exception:
            pass
