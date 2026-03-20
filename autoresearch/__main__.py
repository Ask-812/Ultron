"""
CLI entry point for Ultron AutoResearch.

Usage:
    python -m autoresearch                           # list campaigns
    python -m autoresearch tissue_viability           # run campaign
    python -m autoresearch tissue_viability --quick   # fast test run
    python -m autoresearch tissue_viability --seeds 5
    python -m autoresearch tissue_viability --ticks 10000

    python -m autoresearch auto                      # autonomous research loop
    python -m autoresearch auto --cycles 5           # run 5 research cycles
    python -m autoresearch auto --reset              # wipe journal and start fresh

    python -m autoresearch journal                   # show journal summary
"""

import argparse
import sys
from .campaigns import CAMPAIGNS, list_campaigns, run_campaign


def main():
    parser = argparse.ArgumentParser(
        prog='autoresearch',
        description='Ultron AutoResearch — automated experiment sweeps & autonomous research',
    )
    parser.add_argument(
        'campaign', nargs='?', default=None,
        help=(
            'Campaign name, "auto" for autonomous loop, '
            'or "journal" to show research journal'
        ),
    )
    parser.add_argument(
        '--seeds', type=int, default=None,
        help='Override number of random seeds per config',
    )
    parser.add_argument(
        '--ticks', type=int, default=None,
        help='Override tick count per experiment',
    )
    parser.add_argument(
        '--quick', action='store_true',
        help='Quick test: 1 seed, reduced ticks',
    )
    parser.add_argument(
        '--cycles', type=int, default=None,
        help='(auto mode) Number of research cycles to run (default: unlimited)',
    )
    parser.add_argument(
        '--reset', action='store_true',
        help='(auto mode) Wipe journal and start fresh',
    )

    args = parser.parse_args()

    if args.campaign is None:
        list_campaigns()
        print()
        print('  Autonomous modes:')
        print('    auto       — run the autonomous hypothesis-driven research loop')
        print('    journal    — show current research journal summary')
        return

    # ── Autonomous research loop ───────────────────────────────
    if args.campaign == 'auto':
        if args.reset:
            from .journal import JOURNAL_PATH
            if JOURNAL_PATH.exists():
                JOURNAL_PATH.unlink()
                print('[Reset] Deleted research journal. Starting fresh.')

        from .loop import run_loop
        run_loop(max_cycles=args.cycles)
        return

    # ── Journal summary ────────────────────────────────────────
    if args.campaign == 'journal':
        from .journal import load_journal, journal_summary
        journal = load_journal()
        print(journal_summary(journal))
        print()

        findings = sorted(
            journal['findings'],
            key=lambda f: f.get('confidence', 0),
            reverse=True,
        )
        if findings:
            print('Key findings:')
            for f in findings[:10]:
                conf = f.get('confidence', 0)
                print(f'  [{conf:.1f}] {f["statement"]}')
            print()

        open_q = [q for q in journal['open_questions'] if not q.get('resolved')]
        if open_q:
            print(f'Open questions ({len(open_q)}):')
            for q in open_q[:10]:
                print(f'  ? {q["question"]}')
            print()

        explored = journal.get('knowledge', {}).get('explored_params', [])
        if explored:
            print(f'Parameters explored: {", ".join(explored)}')
        return

    # ── Campaign sweeps ────────────────────────────────────────
    seeds = args.seeds
    ticks = args.ticks

    if args.quick:
        seeds = seeds or 1
        if ticks is None:
            camp = CAMPAIGNS.get(args.campaign, {})
            default_ticks = camp.get('run_kwargs', {}).get('ticks', 5000)
            ticks = max(500, default_ticks // 5)
        print(f'[QUICK MODE] seeds={seeds}, ticks={ticks}')
        print()

    result = run_campaign(
        args.campaign,
        override_seeds=seeds,
        override_ticks=ticks,
    )

    if result is None:
        sys.exit(1)


if __name__ == '__main__':
    main()
