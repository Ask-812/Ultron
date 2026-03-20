import numpy as np
from abc import ABC, abstractmethod

class Environment(ABC):
    @abstractmethod
    def get_input(self, tick: int) -> np.ndarray:
        raise NotImplementedError

class SineEnvironment(Environment):
    def __init__(self, dim: int, frequencies: list = None):
        self.dim = dim
        self.frequencies = frequencies or [0.1 * (i + 1) for i in range(dim)]
        if len(self.frequencies) < dim:
            self.frequencies = self.frequencies + [0.1 * (i + 1) for i in range(len(self.frequencies), dim)]
        self.frequencies = self.frequencies[:dim]
    
    def __post_init(self):
        self._freq_array = np.array(self.frequencies)

    def get_input(self, tick: int) -> np.ndarray:
        if not hasattr(self, '_freq_array'):
            self._freq_array = np.array(self.frequencies)
        return np.sin(tick * self._freq_array)

class NoisyEnvironment(Environment):
    def __init__(self, dim: int, scale: float = 1.0):
        self.dim = dim
        self.scale = scale
    
    def get_input(self, tick: int) -> np.ndarray:
        return np.random.randn(self.dim) * self.scale

class MixedEnvironment(Environment):
    def __init__(self, dim: int, signal_ratio: float = 0.5):
        self.dim = dim
        self.signal_ratio = signal_ratio
        self.sine = SineEnvironment(dim)
        self.noise = NoisyEnvironment(dim)
    
    def get_input(self, tick: int) -> np.ndarray:
        signal = self.sine.get_input(tick)
        noise = self.noise.get_input(tick)
        return self.signal_ratio * signal + (1 - self.signal_ratio) * noise
