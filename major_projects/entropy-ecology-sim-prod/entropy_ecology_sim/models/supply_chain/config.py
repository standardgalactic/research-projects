
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SupplyChainConfig:
    grid_size: int = 256
    steps: int = 3000
    seed: int = 123
