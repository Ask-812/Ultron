"""
Filesystem World — Maps real directory structure onto the tissue grid.

Instead of abstract food patches, the organism's world IS the computer's
filesystem. Directories become regions, files become resources, modification
times become freshness, file entropy becomes richness.

The organism literally lives inside your filesystem.
"""

import os
import math
import numpy as np


def scan_filesystem(root_dir, max_files=500):
    """Scan a directory tree and return file metadata."""
    entries = []
    try:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for fname in filenames[:50]:  # cap per directory
                fpath = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(fpath)
                    rel = os.path.relpath(fpath, root_dir)
                    depth = rel.count(os.sep)
                    entries.append({
                        'path': rel,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'depth': depth,
                        'ext': os.path.splitext(fname)[1].lower(),
                    })
                except (OSError, PermissionError):
                    continue
                if len(entries) >= max_files:
                    break
            if len(entries) >= max_files:
                break
    except (OSError, PermissionError):
        pass
    return entries


def map_to_grid(entries, rows, cols):
    """Map filesystem entries onto a 2D grid as resource values.

    Uses a space-filling approach: entries are sorted by path and
    distributed across the grid. Richer files (larger, more recently
    modified) create higher resource values at their grid position.

    Returns: (rows, cols) numpy array of resource values [0, 1]
    """
    resource_map = np.full((rows, cols), 0.15)  # base resource level

    if not entries:
        return resource_map

    import time as _time
    now = _time.time()

    # Sort by path for spatial locality
    entries.sort(key=lambda e: e['path'])

    # Distribute entries across grid positions
    n = len(entries)
    for i, entry in enumerate(entries):
        # Map index to grid position (space-filling curve approximation)
        pos = i / max(n - 1, 1)
        # Zigzag pattern for spatial coherence
        row_f = pos * rows
        r = int(row_f) % rows
        col_phase = row_f - int(row_f)
        if int(row_f) % 2 == 1:
            col_phase = 1.0 - col_phase  # zigzag
        c = int(col_phase * cols) % cols

        # Resource value based on file properties
        size_value = min(math.log1p(entry['size']) / 15.0, 1.0)  # log-scaled size
        age = max(0, now - entry['mtime'])
        freshness = 1.0 / (1.0 + age / 86400.0)  # decays over days
        # Code files are richer (more structured = more predictable = more "edible")
        code_bonus = 1.5 if entry['ext'] in ('.py', '.js', '.ts', '.json', '.md', '.html', '.css') else 1.0

        richness = (size_value * 0.4 + freshness * 0.6) * code_bonus
        richness = min(richness, 1.0)

        # Spread across nearby cells for spatial smoothness
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr = (r + dr) % rows
                nc = (c + dc) % cols
                dist = abs(dr) + abs(dc)
                falloff = 1.0 - dist / 3.0
                resource_map[nr, nc] = max(resource_map[nr, nc], richness * falloff)

    return np.clip(resource_map, 0.0, 1.0)


def get_world_from_filesystem(scan_root, rows, cols, cache={}):
    """Get or update the filesystem-based world map.

    Caches the scan and only refreshes every 30 seconds.
    """
    import time as _time
    now = _time.time()
    last_scan = cache.get('last_scan', 0)

    if now - last_scan > 30 or 'map' not in cache:
        entries = scan_filesystem(scan_root)
        cache['map'] = map_to_grid(entries, rows, cols)
        cache['last_scan'] = now
        cache['n_files'] = len(entries)

    return cache['map'], cache.get('n_files', 0)
