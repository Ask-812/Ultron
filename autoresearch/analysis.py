"""
Analysis utilities for autoresearch sweep results.

  find_phase_boundary  – locate where survival flips along a parameter
  find_all_boundaries  – scan all swept params for transitions
  results_table        – format results as aligned text table
  pivot_results        – reshape 2-param sweep into a matrix (for heatmaps)
  suggest_next         – generate follow-up experiment suggestions
"""

import numpy as np


def find_phase_boundary(results, param_name,
                        metric='survival_rate', threshold=0.5):
    """
    Find where `metric` crosses `threshold` along `param_name`.

    Returns dict with 'low', 'high', 'boundary' (interpolated), or None.
    """
    sorted_r = sorted(results, key=lambda r: r['params'][param_name])
    vals = [r['params'][param_name] for r in sorted_r]
    mvals = [r.get(metric, 0) for r in sorted_r]

    for i in range(len(sorted_r) - 1):
        m1, m2 = mvals[i], mvals[i + 1]
        v1, v2 = vals[i], vals[i + 1]
        if (m1 < threshold <= m2) or (m1 >= threshold > m2):
            frac = (threshold - m1) / (m2 - m1) if m2 != m1 else 0.5
            bdry = v1 + frac * (v2 - v1)
            return {
                'param': param_name,
                'low': v1,
                'high': v2,
                'boundary': bdry,
                'metric': metric,
                'threshold': threshold,
            }
    return None


def find_all_boundaries(results, metric='survival_rate', threshold=0.5):
    """Find phase boundaries along every swept parameter."""
    if not results:
        return []
    param_names = list(results[0]['params'].keys())
    boundaries = []
    for p in param_names:
        b = find_phase_boundary(results, p, metric, threshold)
        if b:
            boundaries.append(b)
    return boundaries


def results_table(results):
    """
    Produce a compact aligned text table from aggregated sweep results.
    Auto-detects which metrics are available.
    """
    if not results:
        return 'No results.'

    # Columns: all param names, then available standard metrics
    param_names = list(results[0]['params'].keys())
    available_metrics = [
        m for m in [
            'survival_rate', 'mean_energy', 'mean_error',
            'mean_cells', 'mean_peak_cells', 'mean_fitness',
            'mean_births', 'mean_deaths',
        ]
        if m in results[0]
    ]
    cols = param_names + available_metrics
    widths = [max(12, len(c) + 2) for c in cols]

    def fmt(val, w):
        if isinstance(val, float):
            return f'{val:{w}.4f}'
        return f'{val!s:>{w}}'

    header = '|'.join(f'{c:^{w}}' for c, w in zip(cols, widths))
    sep = '+'.join('-' * w for w in widths)
    rows = [header, sep]

    for r in results:
        cells = []
        for p in param_names:
            cells.append(fmt(r['params'].get(p, ''), widths[len(cells)]))
        for m in available_metrics:
            cells.append(fmt(r.get(m, 0), widths[len(cells)]))
        rows.append('|'.join(cells))

    return '\n'.join(rows)


def pivot_results(results, row_param, col_param, metric='survival_rate'):
    """
    Reshape a 2-parameter sweep into a matrix.

    Returns dict with 'matrix' (2D list), 'row_values', 'col_values',
    and the param/metric names.  Useful for heatmap plotting.
    """
    row_vals = sorted(set(r['params'][row_param] for r in results))
    col_vals = sorted(set(r['params'][col_param] for r in results))
    matrix = np.full((len(row_vals), len(col_vals)), np.nan)
    for r in results:
        i = row_vals.index(r['params'][row_param])
        j = col_vals.index(r['params'][col_param])
        matrix[i, j] = r.get(metric, 0)
    return {
        'matrix': matrix.tolist(),
        'row_values': row_vals,
        'col_values': col_vals,
        'row_param': row_param,
        'col_param': col_param,
        'metric': metric,
    }


def suggest_next(results, boundaries):
    """Generate follow-up experiment suggestions from sweep results."""
    suggestions = []

    for b in boundaries:
        suggestions.append(
            f"Refine {b['param']} boundary: sweep [{b['low']:.4f}, {b['high']:.4f}] "
            f"with finer resolution (estimated boundary ≈ {b['boundary']:.4f})"
        )

    if results and all(r['survival_rate'] == 1.0 for r in results):
        suggestions.append(
            'All configs survived — consider harder conditions '
            '(lower extraction, higher noise, smaller grid).'
        )
    elif results and all(r['survival_rate'] == 0.0 for r in results):
        suggestions.append(
            'All configs died — consider easier conditions '
            '(higher extraction, more signal, larger starting energy).'
        )

    if not suggestions:
        suggestions.append(
            'Results look clean — consider expanding parameter range '
            'or adding new sweep dimensions.'
        )

    return suggestions
