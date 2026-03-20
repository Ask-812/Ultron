"""
ULTRON Visualization System
===========================

Real-time visualization of Ultron's existence.
Watch it breathe, learn, and persist.

Non-intervening: We observe but never modify.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import time

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


@dataclass
class VisualizationData:
    """Accumulated data for visualization."""
    ticks: List[int] = field(default_factory=list)
    energies: List[float] = field(default_factory=list)
    errors: List[float] = field(default_factory=list)
    accumulated_errors: List[float] = field(default_factory=list)
    near_death_ticks: List[int] = field(default_factory=list)
    feed_ticks: List[int] = field(default_factory=list)
    hash_changes: List[str] = field(default_factory=list)  # First 8 chars of hash
    model_versions: List[int] = field(default_factory=list)
    predictions: List[np.ndarray] = field(default_factory=list)
    observations: List[np.ndarray] = field(default_factory=list)
    
    # For tracking changes
    last_hash: Optional[bytes] = None
    last_near_death_count: int = 0


class UltronVisualizer:
    """
    Real-time visualization of Ultron's life.
    
    Four panels:
    1. Energy over time (survival pressure visible)
    2. Error over time (learning visible)
    3. Prediction vs Observation (first 3 dims)
    4. Hash/State info panel
    """
    
    def __init__(self, config: dict, max_points: int = 500):
        """
        Initialize visualizer.
        
        Args:
            config: Ultron configuration
            max_points: Maximum points to display (older ones scroll off)
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib required for visualization")
        
        self.config = config
        self.max_points = max_points
        self.data = VisualizationData()
        
        # Setup figure
        plt.ion()  # Interactive mode
        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 10))
        self.fig.suptitle('ULTRON: Artificial Life Monitor', fontsize=14, fontweight='bold')
        
        # Subplot references
        self.ax_energy = self.axes[0, 0]
        self.ax_error = self.axes[0, 1]
        self.ax_pred = self.axes[1, 0]
        self.ax_info = self.axes[1, 1]
        
        # Initialize plots
        self._setup_energy_plot()
        self._setup_error_plot()
        self._setup_prediction_plot()
        self._setup_info_panel()
        
        # Line objects for updating
        self.energy_line, = self.ax_energy.plot([], [], 'g-', linewidth=1.5, label='Energy')
        self.energy_capacity_line = self.ax_energy.axhline(
            y=config.get('initial_energy', 100), 
            color='gray', linestyle='--', alpha=0.5, label='Capacity'
        )
        self.energy_death_line = self.ax_energy.axhline(
            y=0, color='red', linestyle='-', alpha=0.3, label='Death'
        )
        
        self.error_line, = self.ax_error.plot([], [], 'b-', linewidth=1.5, label='Error')
        self.error_ma_line, = self.ax_error.plot([], [], 'r-', linewidth=2, alpha=0.7, label='MA(50)')
        
        self.pred_lines = []
        self.obs_lines = []
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        for i, c in enumerate(colors):
            pred_line, = self.ax_pred.plot([], [], color=c, linestyle='-', 
                                            linewidth=1.5, label=f'Pred dim {i}')
            obs_line, = self.ax_pred.plot([], [], color=c, linestyle=':', 
                                           linewidth=1, alpha=0.7)
            self.pred_lines.append(pred_line)
            self.obs_lines.append(obs_line)
        
        # Scatter for near-death events
        self.near_death_scatter = self.ax_energy.scatter([], [], c='red', s=50, 
                                                          marker='x', zorder=5, label='Near-death')
        self.feed_scatter = self.ax_energy.scatter([], [], c='blue', s=30,
                                                    marker='^', zorder=5, alpha=0.5, label='Feed')
        
        # Info text
        self.info_text = self.ax_info.text(0.05, 0.95, '', transform=self.ax_info.transAxes,
                                            fontfamily='monospace', fontsize=10,
                                            verticalalignment='top')
        
        # Legends
        self.ax_energy.legend(loc='upper right', fontsize=8)
        self.ax_error.legend(loc='upper right', fontsize=8)
        self.ax_pred.legend(loc='upper right', fontsize=8)
        
        plt.tight_layout()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        self._last_update = time.time()
        self._update_interval = 0.05  # 50ms minimum between updates
    
    def _setup_energy_plot(self):
        """Setup energy subplot."""
        self.ax_energy.set_title('Energy (Survival Pressure)')
        self.ax_energy.set_xlabel('Tick')
        self.ax_energy.set_ylabel('Energy')
        self.ax_energy.set_ylim(-10, self.config.get('initial_energy', 100) * 1.5)
        self.ax_energy.grid(True, alpha=0.3)
        self.ax_energy.axhspan(-10, 0, alpha=0.1, color='red')  # Death zone
    
    def _setup_error_plot(self):
        """Setup error subplot."""
        self.ax_error.set_title('Prediction Error (Learning)')
        self.ax_error.set_xlabel('Tick')
        self.ax_error.set_ylabel('Error Magnitude')
        self.ax_error.set_ylim(0, 10)
        self.ax_error.grid(True, alpha=0.3)
    
    def _setup_prediction_plot(self):
        """Setup prediction vs observation subplot."""
        self.ax_pred.set_title('Prediction vs Observation (First 3 Dims)')
        self.ax_pred.set_xlabel('Tick')
        self.ax_pred.set_ylabel('Value')
        self.ax_pred.set_ylim(-2, 2)
        self.ax_pred.grid(True, alpha=0.3)
    
    def _setup_info_panel(self):
        """Setup info panel."""
        self.ax_info.set_title('State Information')
        self.ax_info.axis('off')
    
    def record(self, state, fed_this_tick: bool = False):
        """
        Record a state snapshot for visualization.
        
        Args:
            state: UltronState
            fed_this_tick: Whether energy was fed this tick
        """
        tick = state.time.tick
        
        self.data.ticks.append(tick)
        self.data.energies.append(state.energy.current)
        self.data.errors.append(state.current.error_magnitude)
        self.data.accumulated_errors.append(state.history.accumulated_error)
        self.data.model_versions.append(state.model.version)
        
        # Track hash changes
        hash_hex = state.history.current_hash.hex()[:8]
        self.data.hash_changes.append(hash_hex)
        
        # Track near-death events
        if state.history.near_death_count > self.data.last_near_death_count:
            self.data.near_death_ticks.append(tick)
            self.data.last_near_death_count = state.history.near_death_count
        
        # Track feeding
        if fed_this_tick:
            self.data.feed_ticks.append(tick)
        
        # Store predictions and observations (just first few dims)
        self.data.predictions.append(state.current.prediction[:3].copy())
        self.data.observations.append(state.current.observation[:3].copy())
        
        # Trim old data
        if len(self.data.ticks) > self.max_points:
            self.data.ticks = self.data.ticks[-self.max_points:]
            self.data.energies = self.data.energies[-self.max_points:]
            self.data.errors = self.data.errors[-self.max_points:]
            self.data.accumulated_errors = self.data.accumulated_errors[-self.max_points:]
            self.data.hash_changes = self.data.hash_changes[-self.max_points:]
            self.data.model_versions = self.data.model_versions[-self.max_points:]
            self.data.predictions = self.data.predictions[-self.max_points:]
            self.data.observations = self.data.observations[-self.max_points:]
            
            # Filter near-death and feed ticks
            min_tick = self.data.ticks[0]
            self.data.near_death_ticks = [t for t in self.data.near_death_ticks if t >= min_tick]
            self.data.feed_ticks = [t for t in self.data.feed_ticks if t >= min_tick]
    
    def update(self, state, force: bool = False):
        """
        Update the visualization.
        
        Args:
            state: Current UltronState
            force: Force update regardless of interval
        """
        # Rate limiting
        now = time.time()
        if not force and (now - self._last_update) < self._update_interval:
            return
        self._last_update = now
        
        if len(self.data.ticks) < 2:
            return
        
        ticks = np.array(self.data.ticks)
        energies = np.array(self.data.energies)
        errors = np.array(self.data.errors)
        
        # Update energy plot
        self.energy_line.set_data(ticks, energies)
        self.ax_energy.set_xlim(ticks[0], ticks[-1] + 10)
        
        # Update near-death scatter
        if self.data.near_death_ticks:
            nd_ticks = np.array(self.data.near_death_ticks)
            # Get corresponding energies
            nd_energies = []
            for nd_t in nd_ticks:
                idx = np.searchsorted(ticks, nd_t)
                if idx < len(energies):
                    nd_energies.append(energies[idx])
                else:
                    nd_energies.append(0)
            self.near_death_scatter.set_offsets(np.c_[nd_ticks, nd_energies])
        
        # Update feed scatter
        if self.data.feed_ticks:
            fd_ticks = np.array(self.data.feed_ticks)
            fd_energies = []
            for fd_t in fd_ticks:
                idx = np.searchsorted(ticks, fd_t)
                if idx < len(energies):
                    fd_energies.append(energies[idx])
                else:
                    fd_energies.append(50)
            self.feed_scatter.set_offsets(np.c_[fd_ticks, fd_energies])
        
        # Update error plot
        self.error_line.set_data(ticks, errors)
        self.ax_error.set_xlim(ticks[0], ticks[-1] + 10)
        
        # Moving average
        if len(errors) >= 50:
            ma = np.convolve(errors, np.ones(50)/50, mode='valid')
            ma_ticks = ticks[49:]
            self.error_ma_line.set_data(ma_ticks, ma)
        
        # Auto-scale error y-axis
        max_error = max(errors) * 1.2
        self.ax_error.set_ylim(0, max(max_error, 1))
        
        # Update prediction vs observation plot
        predictions = np.array(self.data.predictions)
        observations = np.array(self.data.observations)
        
        for i in range(3):
            if predictions.shape[1] > i:
                self.pred_lines[i].set_data(ticks, predictions[:, i])
                self.obs_lines[i].set_data(ticks, observations[:, i])
        
        self.ax_pred.set_xlim(ticks[0], ticks[-1] + 10)
        
        # Update info panel
        info_text = self._build_info_text(state)
        self.info_text.set_text(info_text)
        
        # Refresh
        try:
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except:
            pass  # Handle closed window gracefully
    
    def _build_info_text(self, state) -> str:
        """Build info panel text."""
        alive_str = "[+] ALIVE" if state.is_alive else "[X] DEAD"
        
        # Calculate error trend
        if len(self.data.errors) >= 100:
            recent = np.mean(self.data.errors[-50:])
            older = np.mean(self.data.errors[-100:-50])
            trend = "↓ improving" if recent < older else "↑ worsening"
        else:
            trend = "..."
        
        # Calculate survival probability (simple heuristic)
        energy = state.energy.current
        capacity = self.config.get('initial_energy', 100)
        survival_pct = min(100, max(0, (energy / capacity) * 100))
        
        # Hash info
        birth_hash = state.history.birth_hash.hex()[:16]
        current_hash = state.history.current_hash.hex()[:16]
        
        text = f"""
╔══════════════════════════════════════╗
║  {alive_str:^34}  ║
╠══════════════════════════════════════╣
║  Tick:           {state.time.tick:>18,}  ║
║  Energy:         {state.energy.current:>18.2f}  ║
║  Survival:       {survival_pct:>17.1f}%  ║
║  Error (now):    {state.current.error_magnitude:>18.4f}  ║
║  Error (trend):  {trend:>18}  ║
╠══════════════════════════════════════╣
║  Model Version:  {state.model.version:>18,}  ║
║  Near-deaths:    {state.history.near_death_count:>18}  ║
║  Accum. Error:   {state.history.accumulated_error:>18.2f}  ║
╠══════════════════════════════════════╣
║  Birth Hash:     {birth_hash:>18}  ║
║  Current Hash:   {current_hash:>18}  ║
╚══════════════════════════════════════╝
"""
        return text
    
    def show_death(self, state):
        """Show death screen."""
        self.fig.suptitle(f'ULTRON: DEAD at tick {state.time.tick}', 
                         fontsize=14, fontweight='bold', color='red')
        
        # Add death cause text
        cause = state.history.death_cause or "unknown"
        self.ax_info.text(0.5, 0.3, f"DEATH\n{cause}", 
                         transform=self.ax_info.transAxes,
                         fontsize=24, color='red',
                         ha='center', va='center',
                         fontweight='bold')
        
        self.update(state, force=True)
        plt.ioff()
    
    def finalize(self, state):
        """
        Finalize visualization after experiment ends.
        
        Args:
            state: Final UltronState
        """
        self.update(state, force=True)
        
        if not state.is_alive:
            self.show_death(state)
        else:
            self.fig.suptitle(f'ULTRON: Survived {state.time.tick} ticks', 
                             fontsize=14, fontweight='bold', color='green')
        
        plt.ioff()
        print("\n[Visualization] Close the window to continue...")
        plt.show()
    
    def close(self):
        """Close the visualization window."""
        plt.close(self.fig)


class PostHocVisualizer:
    """
    Visualize completed experiments from history.
    """
    
    @staticmethod
    def plot_experiment(observations: List[dict], config: dict):
        """
        Plot a completed experiment from observation history.
        
        Args:
            observations: List of observer snapshots
            config: Experiment configuration
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib required for visualization")
            return
        
        if not observations:
            print("No observations to plot")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        ticks = [o['tick'] for o in observations]
        energies = [o['energy'] for o in observations]
        errors = [o['error'] for o in observations]
        near_deaths = [o['near_death_count'] for o in observations]
        
        # Energy plot
        axes[0, 0].plot(ticks, energies, 'g-', linewidth=1)
        axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('Energy Over Time')
        axes[0, 0].set_xlabel('Tick')
        axes[0, 0].set_ylabel('Energy')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Mark near-death events
        nd_ticks = []
        nd_energies = []
        last_nd = 0
        for i, (t, e, nd) in enumerate(zip(ticks, energies, near_deaths)):
            if nd > last_nd:
                nd_ticks.append(t)
                nd_energies.append(e)
                last_nd = nd
        if nd_ticks:
            axes[0, 0].scatter(nd_ticks, nd_energies, c='red', s=50, marker='x', 
                              label=f'Near-death ({len(nd_ticks)})')
            axes[0, 0].legend()
        
        # Error plot
        axes[0, 1].plot(ticks, errors, 'b-', linewidth=0.5, alpha=0.5, label='Error')
        # Moving average
        if len(errors) >= 50:
            ma = np.convolve(errors, np.ones(50)/50, mode='valid')
            axes[0, 1].plot(ticks[49:], ma, 'r-', linewidth=2, label='MA(50)')
        axes[0, 1].set_title('Prediction Error')
        axes[0, 1].set_xlabel('Tick')
        axes[0, 1].set_ylabel('Error')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Accumulated error
        acc_errors = [o['accumulated_error'] for o in observations]
        axes[1, 0].plot(ticks, acc_errors, 'purple', linewidth=1.5)
        axes[1, 0].set_title('Accumulated Error')
        axes[1, 0].set_xlabel('Tick')
        axes[1, 0].set_ylabel('Total Error')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Summary stats
        axes[1, 1].axis('off')
        final = observations[-1]
        
        summary = f"""
EXPERIMENT SUMMARY
==================

Duration:         {final['tick']:,} ticks
Final Status:     {'ALIVE' if final['is_alive'] else 'DEAD'}
Final Energy:     {final['energy']:.2f}
Final Error:      {final['error']:.4f}
Near-death Count: {final['near_death_count']}
Accumulated Error:{final['accumulated_error']:.2f}
Model Version:    {final['model_version']}

Config:           {config.get('type', 'unknown')}
Environment:      {config.get('environment', 'unknown')}

Energy Stats:
  Mean:           {np.mean(energies):.2f}
  Min:            {np.min(energies):.2f}
  Max:            {np.max(energies):.2f}

Error Stats:
  Mean:           {np.mean(errors):.4f}
  Min:            {np.min(errors):.4f}
  Max:            {np.max(errors):.4f}
"""
        axes[1, 1].text(0.1, 0.9, summary, transform=axes[1, 1].transAxes,
                       fontfamily='monospace', fontsize=10,
                       verticalalignment='top')
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def compare_experiments(experiments: List[dict]):
        """
        Compare multiple experiments side by side.
        
        Args:
            experiments: List of experiment records from history
        """
        if not MATPLOTLIB_AVAILABLE:
            print("matplotlib required for visualization")
            return
        
        if len(experiments) < 2:
            print("Need at least 2 experiments to compare")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Experiment Comparison', fontsize=14, fontweight='bold')
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(experiments)))
        
        for i, exp in enumerate(experiments):
            label = f"{exp['metadata'].get('config_type', '?')}-{exp['experiment_id'][:8]}"
            ticks = exp['summary']['total_ticks']
            
            # Bar: ticks survived
            axes[0, 0].barh(i, ticks, color=colors[i], label=label)
            
            # Bar: mean error
            axes[0, 1].barh(i, exp['summary']['mean_error'], color=colors[i])
            
            # Bar: final energy
            axes[1, 0].barh(i, exp['summary']['final_energy'], color=colors[i])
        
        labels = [f"{exp['metadata'].get('config_type', '?')}" for exp in experiments]
        
        axes[0, 0].set_yticks(range(len(experiments)))
        axes[0, 0].set_yticklabels(labels)
        axes[0, 0].set_xlabel('Ticks Survived')
        axes[0, 0].set_title('Survival Duration')
        
        axes[0, 1].set_yticks(range(len(experiments)))
        axes[0, 1].set_yticklabels(labels)
        axes[0, 1].set_xlabel('Mean Error')
        axes[0, 1].set_title('Prediction Accuracy')
        
        axes[1, 0].set_yticks(range(len(experiments)))
        axes[1, 0].set_yticklabels(labels)
        axes[1, 0].set_xlabel('Final Energy')
        axes[1, 0].set_title('Energy at End')
        
        # Summary table
        axes[1, 1].axis('off')
        table_data = []
        for exp in experiments:
            table_data.append([
                exp['experiment_id'][:8],
                exp['metadata'].get('config_type', '?'),
                str(exp['summary']['total_ticks']),
                'Yes' if exp['summary']['is_alive'] else 'No',
                f"{exp['summary']['mean_error']:.3f}"
            ])
        
        table = axes[1, 1].table(
            cellText=table_data,
            colLabels=['ID', 'Config', 'Ticks', 'Survived', 'Mean Err'],
            loc='center',
            cellLoc='center'
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        plt.tight_layout()
        plt.show()


def check_matplotlib():
    """Check if matplotlib is available."""
    return MATPLOTLIB_AVAILABLE
