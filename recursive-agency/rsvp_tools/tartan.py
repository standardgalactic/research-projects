from dataclasses import dataclass
import torch
from torch import nn

@dataclass
class TARTANConfig:
    latent_dim: int = 8
    trajectory_smoothing: float = 0.1
    reduce: str = "mean"

class TARTANLayer(nn.Module):
    def __init__(self, dim, config=None):
        super().__init__()
        self.dim = dim
        self.config = config or TARTANConfig()

        self.proj = nn.Linear(dim, dim)
        self.memory = nn.Parameter(torch.zeros(self.config.latent_dim))

    def forward(self, x):
        # simple TARTAN-like recurrence
        mem = self.memory
        mem = mem + self.config.trajectory_smoothing * mem.tanh()
        self.memory.data.copy_(mem.detach())

        return self.proj(x) + mem[:self.dim]
