"""
ULTRON AutoResearch — Automated experiment generation, execution, and analysis.

Includes both predefined campaign sweeps and a fully autonomous
hypothesis-driven research loop that generates, tests, and learns
from its own experiments.

Usage as library:
    from autoresearch import run_tissue, grid_sweep, TISSUE_BASE
    results = grid_sweep(
        run_tissue, TISSUE_BASE,
        {'extraction_factor': [0.3, 0.4, 0.5, 0.6]},
        n_seeds=3, ticks=5000, rows=12, cols=12,
    )

Usage as CLI:
    python -m autoresearch                          # list campaigns
    python -m autoresearch tissue_viability          # run a campaign
    python -m autoresearch tissue_viability --quick  # fast test run
    python -m autoresearch auto                     # autonomous research loop
    python -m autoresearch auto --cycles 5          # run 5 cycles
    python -m autoresearch journal                  # show research journal
"""

from .experiment import run_single, run_population, run_tissue
from .sweep import grid_sweep, adaptive_sweep
from .analysis import find_phase_boundary, results_table, suggest_next, pivot_results
from .report import generate_report, save_report, save_results
from .campaigns import (
    CAMPAIGNS, TISSUE_BASE, POPULATION_BASE, SINGLE_BASE,
    list_campaigns, run_campaign,
)
from .journal import load_journal, save_journal, journal_summary
from .brain import generate_hypothesis, interpret_results
from .loop import run_loop

__version__ = "2.0.0"
