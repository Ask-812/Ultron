"""
Report generation — markdown + JSON output.

Reports are saved under  history/reports/
"""

import os
import json
from datetime import datetime
from .analysis import results_table, find_all_boundaries, suggest_next, pivot_results

REPORT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'history', 'reports'
)


def generate_report(name, results, config_used, elapsed_seconds=0):
    """Build a markdown report string from sweep results."""
    boundaries = find_all_boundaries(results)
    suggestions = suggest_next(results, boundaries)
    table = results_table(results)

    lines = [
        f'# AutoResearch Report: {name}',
        '',
        f'**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  ',
        f'**Duration:** {elapsed_seconds:.1f}s ({elapsed_seconds / 60:.1f}m)  ',
        f'**Configurations tested:** {len(results)}  ',
        f'**Total runs:** {sum(r.get("n_seeds", 1) for r in results)}',
        '',
    ]

    # Swept parameters
    if results:
        lines.append('## Parameters Swept')
        for k in results[0]['params']:
            vals = sorted(set(r['params'][k] for r in results))
            lines.append(f'- **{k}**: {vals}')
        lines.append('')

    # Base config
    param_keys = set(results[0]['params'].keys()) if results else set()
    lines.append('## Base Configuration')
    lines.append('```')
    for k, v in sorted(config_used.items()):
        if k not in param_keys:
            lines.append(f'  {k}: {v}')
    lines.append('```')
    lines.append('')

    # Results table
    lines.append('## Results')
    lines.append('```')
    lines.append(table)
    lines.append('```')
    lines.append('')

    # 2-param heatmap (text version) if exactly 2 params swept
    if results and len(results[0]['params']) == 2:
        params = list(results[0]['params'].keys())
        piv = pivot_results(results, params[0], params[1], 'survival_rate')
        lines.append(f'## Survival Heatmap  ({params[0]} × {params[1]})')
        lines.append('```')
        # Header
        header = f'{"":>10} | ' + ' | '.join(f'{c:>7.3f}' for c in piv['col_values'])
        lines.append(header)
        lines.append('-' * len(header))
        for i, rv in enumerate(piv['row_values']):
            row_cells = []
            for j in range(len(piv['col_values'])):
                val = piv['matrix'][i][j]
                if val is None or (isinstance(val, float) and val != val):  # NaN
                    row_cells.append(f'{"---":>7}')
                else:
                    row_cells.append(f'{val:>7.0%}')
            lines.append(f'{rv:>10.4f} | ' + ' | '.join(row_cells))
        lines.append('```')
        lines.append('')

    # Phase transitions
    if boundaries:
        lines.append('## Phase Transitions Detected')
        for b in boundaries:
            lines.append(
                f'- **{b["param"]}**: boundary ≈ {b["boundary"]:.4f} '
                f'(between {b["low"]:.4f} and {b["high"]:.4f})'
            )
        lines.append('')

    # Suggestions
    lines.append('## Suggested Next Experiments')
    for i, s in enumerate(suggestions, 1):
        lines.append(f'{i}. {s}')
    lines.append('')

    return '\n'.join(lines)


def save_report(report_text, name):
    """Save markdown report to history/reports/."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{name}_{ts}.md'
    path = os.path.join(REPORT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(f'Report saved → {path}')
    return path


def save_results(results, name):
    """Save raw (snapshot-stripped) results as JSON."""
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{name}_{ts}.json'
    path = os.path.join(REPORT_DIR, filename)

    # Strip heavy data (snapshots, individual runs) to keep file small
    compact = []
    for r in results:
        c = {k: v for k, v in r.items() if k not in ('runs',)}
        compact.append(c)

    with open(path, 'w') as f:
        json.dump(compact, f, indent=2, default=str)
    print(f'Results saved → {path}')
    return path
