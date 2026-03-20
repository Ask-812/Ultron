"""Quick test of tissue experiment."""
from autoresearch.experiment import run_tissue
from autoresearch.brain import TISSUE_BASE

config = TISSUE_BASE.copy()
config['extraction_factor'] = 0.50
config['base_signal_ratio'] = 0.40

r = run_tissue(config, ticks=3000, seed=42, rows=12, cols=12)
print(f'survived={r["survived"]}, cells={r["final_cells"]}, peak={r["peak_cells"]}')
print(f'energy={r["mean_energy"]:.1f}, births={r["births"]}, deaths={r["deaths"]}')
