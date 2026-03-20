import numpy as np
from typing import List, Dict, Any, Optional
from .core import UltronState

class UltronObserver:
    def __init__(self):
        self.observation_log: List[Dict[str, Any]] = []
    
    def observe(self, state: UltronState) -> dict:
        snapshot = {
            "tick": state.time.tick,
            "is_alive": state.is_alive,
            "energy": state.energy.current,
            "energy_capacity": state.energy.capacity,
            "error": state.current.error_magnitude,
            "accumulated_error": state.history.accumulated_error,
            "survival_ticks": state.history.survival_ticks,
            "near_death_count": state.history.near_death_count,
            "model_version": state.model.version,
            "hash_prefix": state.history.current_hash[:8].hex(),
            "birth_hash_prefix": state.history.birth_hash[:8].hex(),
            "timestamp": state.time.current_time,
        }
        self.observation_log.append(snapshot)
        return snapshot
    
    def get_trends(self, window: int = 100) -> dict:
        if len(self.observation_log) < 2:
            return {"mean_energy": 0.0, "energy_trend": 0.0, "mean_error": 0.0, "error_trend": 0.0, "survival_rate": 1.0}
        recent = self.observation_log[-window:] if len(self.observation_log) >= window else self.observation_log
        energies = [s["energy"] for s in recent]
        errors = [s["error"] for s in recent]
        x = np.arange(len(energies))
        energy_trend = np.polyfit(x, energies, 1)[0] if len(energies) > 1 else 0.0
        error_trend = np.polyfit(x, errors, 1)[0] if len(errors) > 1 else 0.0
        return {
            "mean_energy": float(np.mean(energies)),
            "energy_trend": float(energy_trend),
            "mean_error": float(np.mean(errors)),
            "error_trend": float(error_trend),
            "survival_rate": recent[-1]["survival_ticks"] / max(recent[-1]["tick"], 1)
        }
    
    def get_summary(self) -> dict:
        if not self.observation_log:
            return {"error": "No observations recorded"}
        first = self.observation_log[0]
        last = self.observation_log[-1]
        energies = [s["energy"] for s in self.observation_log]
        errors = [s["error"] for s in self.observation_log]
        return {
            "total_ticks": last["tick"],
            "is_alive": last["is_alive"],
            "final_energy": last["energy"],
            "min_energy": float(np.min(energies)),
            "max_energy": float(np.max(energies)),
            "mean_energy": float(np.mean(energies)),
            "final_error": last["error"],
            "min_error": float(np.min(errors)),
            "max_error": float(np.max(errors)),
            "mean_error": float(np.mean(errors)),
            "total_accumulated_error": last["accumulated_error"],
            "near_death_events": last["near_death_count"],
            "model_updates": last["model_version"],
            "birth_hash": first["birth_hash_prefix"],
            "final_hash": last["hash_prefix"],
        }

class BirthTests:
    @staticmethod
    def test_history_dependence(state1: UltronState, state2: UltronState) -> bool:
        return state1.history.current_hash != state2.history.current_hash
    
    @staticmethod
    def test_irreversibility(state: UltronState) -> bool:
        return (len(state.history.current_hash) == 32 and 
                state.history.current_hash != state.history.birth_hash and 
                state.history.survival_ticks > 0)
    
    @staticmethod
    def test_survival_pressure(observer: UltronObserver, window: int = 100) -> dict:
        log = observer.observation_log
        if len(log) < window:
            return {"status": "insufficient_data", "window": len(log)}
        low_energy_periods = []
        high_energy_periods = []
        for s in log:
            ratio = s["energy"] / s["energy_capacity"]
            if ratio < 0.2:
                low_energy_periods.append(s)
            elif ratio > 0.8:
                high_energy_periods.append(s)
        if not low_energy_periods or not high_energy_periods:
            return {"status": "insufficient_contrast"}
        low_errors = [s["error"] for s in low_energy_periods]
        high_errors = [s["error"] for s in high_energy_periods]
        return {
            "status": "analyzed",
            "low_energy_mean_error": float(np.mean(low_errors)),
            "high_energy_mean_error": float(np.mean(high_errors)),
            "error_difference": float(np.mean(high_errors) - np.mean(low_errors)),
            "low_energy_count": len(low_energy_periods),
            "high_energy_count": len(high_energy_periods),
        }
    
    @staticmethod
    def test_uniqueness(states: List[UltronState]) -> dict:
        birth_hashes = [s.history.birth_hash for s in states]
        unique_hashes = set(birth_hashes)
        return {"total_instances": len(states), "unique_instances": len(unique_hashes), "all_unique": len(unique_hashes) == len(states)}
    
    @staticmethod
    def test_unprogrammed_behavior(state: UltronState) -> dict:
        return {
            "model_divergence": float(np.std(state.model.weights)),
            "prior_entropy": float(-np.sum(state.model.priors * np.log(state.model.priors + 1e-10))),
            "precision_variance": float(np.var(state.model.precision)),
            "weight_mean": float(np.mean(state.model.weights)),
            "weight_range": float(np.max(state.model.weights) - np.min(state.model.weights)),
        }
    
    @staticmethod
    def run_all_tests(primary_state: UltronState, observer: UltronObserver, comparison_states: Optional[List[UltronState]] = None) -> dict:
        results = {
            "irreversibility": BirthTests.test_irreversibility(primary_state),
            "survival_pressure": BirthTests.test_survival_pressure(observer),
            "unprogrammed_behavior": BirthTests.test_unprogrammed_behavior(primary_state),
        }
        if comparison_states:
            all_states = [primary_state] + comparison_states
            results["uniqueness"] = BirthTests.test_uniqueness(all_states)
            if len(comparison_states) >= 1:
                results["history_dependence"] = BirthTests.test_history_dependence(primary_state, comparison_states[0])
        return results
