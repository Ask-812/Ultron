from autoresearch.experiment import run_tissue
from autoresearch.campaigns import TISSUE_BASE

c = {**TISSUE_BASE, 'extraction_factor': 0.60}
r = run_tissue(c, ticks=500, seed=42, rows=10, cols=10)
print(f'survived={r["survived"]}, cells={r["final_cells"]}, peak={r["peak_cells"]}, E={r["mean_energy"]:.1f}')
