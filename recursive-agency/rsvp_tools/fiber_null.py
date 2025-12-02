# rsvp_tools/fiber_null.py
from dataclasses import dataclass
import torch
from torch import nn

@dataclass
class FiberNullConfig:
    reduce: str = "mean"
    eps: float = 1e-6

class FiberNullPruner(nn.Module):
    def __init__(self, model, config=None):
        super().__init__()
        self.model = model
        self.config = config or FiberNullConfig()

    def forward(self, x):
        x = x.requires_grad_(True)
        out = self.model(x)

        # Compute dy/dx Jacobian diagonal (per-output gradients)
        grads = []
        for i in range(out.shape[-1]):
            g = torch.autograd.grad(
                out[:, i].sum(),
                x,
                retain_graph=True,
                allow_unused=False
            )[0]
            grads.append(g)

        J = torch.stack(grads, dim=-1)   # [B, input_dim, output_dim]

        # Nullity = (# input dims) – rank(J)
        U, S, V = torch.linalg.svd(J)
        rank = (S > self.config.eps).float().sum(dim=-1)
        nullity = x.shape[-1] - rank

        if self.config.reduce == "mean":
            return nullity.mean()
        return nullity.sum()
