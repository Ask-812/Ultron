STABLE_CONFIG = {
    'observation_dim': 32,
    'model_dim': 64,
    'starting_energy': 50,
    'energy_capacity': 50,
    'consumption_rate': 0.05,
    'learning_rate': 0.15,
    'prior_learning_rate': 0.001,
    'precision_learning_rate': 0.001,
    'update_cost_factor': 0.05,
    'prediction_reward_factor': 0.5,
    'observation_noise': 0.01,
    'low_energy_threshold': 20.0,
}

CHALLENGE_CONFIG = {
    'observation_dim': 64,
    'model_dim': 128,
    'starting_energy': 50.0,
    'energy_capacity': 100.0,
    'consumption_rate': 1.0,
    'learning_rate': 0.005,
    'prior_learning_rate': 0.0005,
    'precision_learning_rate': 0.0005,
    'update_cost_factor': 0.1,
    'prediction_reward_factor': 0.2,
    'observation_noise': 0.05,
    'low_energy_threshold': 10.0,
}

MINIMAL_CONFIG = {
    'observation_dim': 8,
    'model_dim': 16,
    'starting_energy': 100.0,
    'energy_capacity': 100.0,
    'consumption_rate': 0.1,
    'learning_rate': 0.1,
    'prior_learning_rate': 0.01,
    'precision_learning_rate': 0.01,
    'update_cost_factor': 0.01,
    'prediction_reward_factor': 1.0,
    'observation_noise': 0.001,
    'low_energy_threshold': 5.0,
}

DEFAULT_CONFIG = {
    'observation_dim': 32,
    'model_dim': 64,
    'starting_energy': 100.0,
    'energy_capacity': 200.0,
    'consumption_rate': 0.5,
    'learning_rate': 0.01,
    'prior_learning_rate': 0.001,
    'precision_learning_rate': 0.001,
    'update_cost_factor': 0.05,
    'prediction_reward_factor': 0.3,
    'observation_noise': 0.01,
    'low_energy_threshold': 10.0,
}

def get_config(name: str = "default") -> dict:
    configs = {"stable": STABLE_CONFIG, "challenge": CHALLENGE_CONFIG, "minimal": MINIMAL_CONFIG, "default": DEFAULT_CONFIG}
    return configs.get(name.lower(), DEFAULT_CONFIG).copy()

def merge_config(base: dict, overrides: dict) -> dict:
    result = base.copy()
    result.update(overrides)
    return result
