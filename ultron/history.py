"""
Experiment History System for Ultron.

Stores all experiments, learnings, and evolutionary progress
in persistent storage. Every run contributes to the collective
knowledge of what works and what doesn't.

"Those who cannot remember the past are condemned to repeat it."
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Default history directory
HISTORY_DIR = Path(__file__).parent.parent / "history"


def ensure_history_dir():
    """Ensure the history directory exists."""
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    (HISTORY_DIR / "experiments").mkdir(exist_ok=True)
    (HISTORY_DIR / "learnings").mkdir(exist_ok=True)
    (HISTORY_DIR / "lineages").mkdir(exist_ok=True)


def get_experiment_id() -> str:
    """Generate unique experiment ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def save_experiment(
    experiment_id: str,
    config: dict,
    summary: dict,
    birth_tests: dict,
    metadata: Optional[dict] = None
) -> str:
    """Save a complete experiment record.
    
    Args:
        experiment_id: Unique identifier for this experiment
        config: Configuration used
        summary: Observer summary (survival, energy, error stats)
        birth_tests: Results of birth tests
        metadata: Optional additional metadata
    
    Returns:
        Path to the saved experiment file
    """
    ensure_history_dir()
    
    record = {
        "experiment_id": experiment_id,
        "timestamp": datetime.now().isoformat(),
        "config": config,
        "summary": summary,
        "birth_tests": birth_tests,
        "metadata": metadata or {},
    }
    
    filepath = HISTORY_DIR / "experiments" / f"{experiment_id}.json"
    with open(filepath, "w") as f:
        json.dump(record, f, indent=2, default=str)
    
    # Also update the master index
    _update_experiment_index(experiment_id, record)
    
    return str(filepath)


def _update_experiment_index(experiment_id: str, record: dict):
    """Update the master experiment index."""
    index_path = HISTORY_DIR / "experiment_index.json"
    
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {"experiments": [], "stats": {}}
    
    # Add summary entry
    index["experiments"].append({
        "id": experiment_id,
        "timestamp": record["timestamp"],
        "survived": record["summary"].get("is_alive", False),
        "ticks": record["summary"].get("total_ticks", 0),
        "config_type": record["metadata"].get("config_type", "unknown"),
        "environment": record["metadata"].get("environment", "unknown"),
    })
    
    # Update aggregate stats
    stats = index["stats"]
    stats["total_experiments"] = len(index["experiments"])
    stats["total_ticks"] = sum(e["ticks"] for e in index["experiments"])
    stats["survival_rate"] = sum(1 for e in index["experiments"] if e["survived"]) / len(index["experiments"])
    stats["last_updated"] = datetime.now().isoformat()
    
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def record_learning(
    category: str,
    title: str,
    description: str,
    evidence: dict,
    experiment_ids: Optional[List[str]] = None
) -> str:
    """Record a learning or insight from experiments.
    
    Args:
        category: Type of learning (e.g., "energy", "prediction", "survival")
        title: Short title for the learning
        description: Detailed description
        evidence: Supporting data
        experiment_ids: Related experiment IDs
    
    Returns:
        Path to the saved learning file
    """
    ensure_history_dir()
    
    learning_id = get_experiment_id()
    
    record = {
        "learning_id": learning_id,
        "timestamp": datetime.now().isoformat(),
        "category": category,
        "title": title,
        "description": description,
        "evidence": evidence,
        "experiment_ids": experiment_ids or [],
    }
    
    filepath = HISTORY_DIR / "learnings" / f"{learning_id}.json"
    with open(filepath, "w") as f:
        json.dump(record, f, indent=2, default=str)
    
    # Update learnings index
    _update_learnings_index(learning_id, record)
    
    return str(filepath)


def _update_learnings_index(learning_id: str, record: dict):
    """Update the learnings index."""
    index_path = HISTORY_DIR / "learnings_index.json"
    
    if index_path.exists():
        with open(index_path, "r") as f:
            index = json.load(f)
    else:
        index = {"learnings": [], "by_category": {}}
    
    index["learnings"].append({
        "id": learning_id,
        "timestamp": record["timestamp"],
        "category": record["category"],
        "title": record["title"],
    })
    
    # Update category index
    category = record["category"]
    if category not in index["by_category"]:
        index["by_category"][category] = []
    index["by_category"][category].append(learning_id)
    
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)


def save_lineage(
    lineage_id: str,
    parent_id: Optional[str],
    config: dict,
    birth_hash: str,
    summary: dict
):
    """Track evolutionary lineage of Ultron instances.
    
    Args:
        lineage_id: Unique ID for this instance
        parent_id: ID of parent instance (if evolved from another)
        config: Configuration used
        birth_hash: Birth hash of this instance
        summary: Life summary
    """
    ensure_history_dir()
    
    record = {
        "lineage_id": lineage_id,
        "parent_id": parent_id,
        "timestamp": datetime.now().isoformat(),
        "birth_hash": birth_hash,
        "config": config,
        "summary": summary,
        "generation": _get_generation(parent_id),
    }
    
    filepath = HISTORY_DIR / "lineages" / f"{lineage_id}.json"
    with open(filepath, "w") as f:
        json.dump(record, f, indent=2, default=str)
    
    _update_lineage_tree(lineage_id, record)


def _get_generation(parent_id: Optional[str]) -> int:
    """Get generation number based on parent."""
    if parent_id is None:
        return 0
    
    parent_file = HISTORY_DIR / "lineages" / f"{parent_id}.json"
    if parent_file.exists():
        with open(parent_file, "r") as f:
            parent = json.load(f)
            return parent.get("generation", 0) + 1
    return 0


def _update_lineage_tree(lineage_id: str, record: dict):
    """Update the lineage tree."""
    tree_path = HISTORY_DIR / "lineage_tree.json"
    
    if tree_path.exists():
        with open(tree_path, "r") as f:
            tree = json.load(f)
    else:
        tree = {"roots": [], "nodes": {}, "stats": {}}
    
    tree["nodes"][lineage_id] = {
        "parent": record["parent_id"],
        "generation": record["generation"],
        "timestamp": record["timestamp"],
        "survived": record["summary"].get("is_alive", False),
        "ticks": record["summary"].get("total_ticks", 0),
    }
    
    if record["parent_id"] is None:
        tree["roots"].append(lineage_id)
    
    # Update stats
    tree["stats"]["total_instances"] = len(tree["nodes"])
    tree["stats"]["max_generation"] = max(n["generation"] for n in tree["nodes"].values())
    tree["stats"]["last_updated"] = datetime.now().isoformat()
    
    with open(tree_path, "w") as f:
        json.dump(tree, f, indent=2)


def load_experiment(experiment_id: str) -> Optional[dict]:
    """Load a specific experiment record."""
    filepath = HISTORY_DIR / "experiments" / f"{experiment_id}.json"
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return None


def load_experiment_index() -> dict:
    """Load the experiment index."""
    index_path = HISTORY_DIR / "experiment_index.json"
    if index_path.exists():
        with open(index_path, "r") as f:
            return json.load(f)
    return {"experiments": [], "stats": {}}


def load_learnings_index() -> dict:
    """Load the learnings index."""
    index_path = HISTORY_DIR / "learnings_index.json"
    if index_path.exists():
        with open(index_path, "r") as f:
            return json.load(f)
    return {"learnings": [], "by_category": {}}


def load_lineage_tree() -> dict:
    """Load the lineage tree."""
    tree_path = HISTORY_DIR / "lineage_tree.json"
    if tree_path.exists():
        with open(tree_path, "r") as f:
            return json.load(f)
    return {"roots": [], "nodes": {}, "stats": {}}


def get_best_experiments(n: int = 10, metric: str = "ticks") -> List[dict]:
    """Get the best experiments by a given metric.
    
    Args:
        n: Number of experiments to return
        metric: Metric to rank by ("ticks", "survival", etc.)
    
    Returns:
        List of experiment summaries
    """
    index = load_experiment_index()
    experiments = index.get("experiments", [])
    
    if metric == "ticks":
        experiments.sort(key=lambda x: x.get("ticks", 0), reverse=True)
    elif metric == "survival":
        experiments.sort(key=lambda x: (x.get("survived", False), x.get("ticks", 0)), reverse=True)
    
    return experiments[:n]


def get_history_summary() -> dict:
    """Get a summary of all history."""
    exp_index = load_experiment_index()
    learn_index = load_learnings_index()
    lineage_tree = load_lineage_tree()
    
    return {
        "experiments": exp_index.get("stats", {}),
        "learnings": {
            "total": len(learn_index.get("learnings", [])),
            "categories": list(learn_index.get("by_category", {}).keys()),
        },
        "lineage": lineage_tree.get("stats", {}),
    }


def analyze_experiments() -> dict:
    """Analyze all experiments to extract patterns.
    
    Returns insights about what configurations work best.
    """
    index = load_experiment_index()
    experiments = index.get("experiments", [])
    
    if not experiments:
        return {"status": "no_experiments"}
    
    # Group by config type
    by_config = {}
    for exp in experiments:
        config_type = exp.get("config_type", "unknown")
        if config_type not in by_config:
            by_config[config_type] = {"experiments": [], "survivals": 0, "total_ticks": 0}
        by_config[config_type]["experiments"].append(exp)
        by_config[config_type]["total_ticks"] += exp.get("ticks", 0)
        if exp.get("survived", False):
            by_config[config_type]["survivals"] += 1
    
    # Calculate stats per config
    config_stats = {}
    for config_type, data in by_config.items():
        n = len(data["experiments"])
        config_stats[config_type] = {
            "count": n,
            "survival_rate": data["survivals"] / n if n > 0 else 0,
            "avg_ticks": data["total_ticks"] / n if n > 0 else 0,
        }
    
    # Group by environment
    by_env = {}
    for exp in experiments:
        env = exp.get("environment", "unknown")
        if env not in by_env:
            by_env[env] = {"experiments": [], "survivals": 0, "total_ticks": 0}
        by_env[env]["experiments"].append(exp)
        by_env[env]["total_ticks"] += exp.get("ticks", 0)
        if exp.get("survived", False):
            by_env[env]["survivals"] += 1
    
    env_stats = {}
    for env, data in by_env.items():
        n = len(data["experiments"])
        env_stats[env] = {
            "count": n,
            "survival_rate": data["survivals"] / n if n > 0 else 0,
            "avg_ticks": data["total_ticks"] / n if n > 0 else 0,
        }
    
    return {
        "total_experiments": len(experiments),
        "by_config": config_stats,
        "by_environment": env_stats,
        "best_config": max(config_stats.items(), key=lambda x: x[1]["survival_rate"])[0] if config_stats else None,
        "best_environment": max(env_stats.items(), key=lambda x: x[1]["survival_rate"])[0] if env_stats else None,
    }
