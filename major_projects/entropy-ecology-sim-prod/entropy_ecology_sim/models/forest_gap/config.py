
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BCIModelConfig:
    grid_size: int = 500
    years: int = 200
    census_interval: int = 5
    tree_max_age: int = 800
    light_extinction: float = 0.04
    seed_rain_global: float = 12.0
    seed: int = 1990
