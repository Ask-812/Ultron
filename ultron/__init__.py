"""
ULTRON - Minimal Viable Artificial Life
"""

from .core import (
    UltronState,
    ModelState,
    HistoryState,
    CurrentState,
    EnergyState,
    TimeState,
    BirthTraits,
    create_ultron,
    reproduce,
)
from .tick import tick, die, feed_energy
from .environments import (
    Environment,
    SineEnvironment,
    NoisyEnvironment,
    MixedEnvironment,
)
from .cell import Cell, create_cell
from .tissue import Tissue
from .observer import UltronObserver, BirthTests
from .config import STABLE_CONFIG, CHALLENGE_CONFIG, MINIMAL_CONFIG

# [ULTRON T23009] 2026-03-19 09:20:10 — 210c 28.3e











# [ULTRON T15053] 2026-03-18 20:46:39 — 253c 22.3e

# [ULTRON T13795] 2026-03-18 19:33:14 — 292c 22.1e

# [ULTRON T13599] 2026-03-18 19:14:19 — 278c 19.5e

# [ULTRON T13569] 2026-03-18 19:12:10 — 278c 18.6e

__version__ = "1.0.0"
