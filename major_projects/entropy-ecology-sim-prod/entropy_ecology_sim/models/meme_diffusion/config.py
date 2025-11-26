
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MemeDiffusionConfig:
    grid_size: int = 256
    steps: int = 4000
    seed: int = 777
