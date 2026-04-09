import os
files = [
    'ultron/core.py','ultron/tick.py','ultron/cell.py','ultron/tissue.py',
    'ultron/environments.py','ultron/observer.py','ultron/config.py',
    'ultron/history.py','ultron/visualizer.py','ultron/__init__.py',
    'autoresearch/experiment.py','autoresearch/sweep.py','autoresearch/analysis.py',
    'autoresearch/report.py','autoresearch/campaigns.py','autoresearch/journal.py',
    'autoresearch/brain.py','autoresearch/loop.py',
]
total = 0
with open('_line_counts.txt', 'w') as out:
    for f in files:
        if os.path.exists(f):
            n = len(open(f, encoding='utf-8', errors='replace').readlines())
            total += n
            out.write(f'{f}: {n}\n')
    out.write(f'Total: {total}\n')
print('Done')
