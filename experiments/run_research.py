"""Run the autonomous research loop with proper encoding."""
import sys

# Fix Windows console encoding - replace unencodable chars
sys.stdout.reconfigure(errors='replace')
sys.stderr.reconfigure(errors='replace')

from autoresearch.loop import run_loop

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--cycles', type=int, default=None)
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    if args.reset:
        from autoresearch.journal import JOURNAL_PATH
        if JOURNAL_PATH.exists():
            JOURNAL_PATH.unlink()
            print('[Reset] Deleted research journal.')

    run_loop(max_cycles=args.cycles)
