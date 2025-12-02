from dataclasses import dataclass
import torch
from torch import nn

@dataclass
class LamFlowConfig:
    lam_weight: float = 1e-3
    hessian_weight: float = 1.0
    gradient_weight: float = 1.0
    use_hessian: bool = True
    reduce: str = "mean"


class LamFlowWrapper(nn.Module):
    def __init__(self, model, criterion, config=None):
        super().__init__()
        self.model = model
        self.criterion = criterion
        self.config = config or LamFlowConfig()

    def forward(self, x, y):
        x = x.requires_grad_(True)
        ypred = self.model(x)
        base = self.criterion(ypred, y)
        lam = self._lam_energy(x, ypred)
        return base + self.config.lam_weight * lam

    def _lam_energy(self, x, y):
        grad = torch.autograd.grad(
            y,
            x,
            torch.ones_like(y),
            retain_graph=True,
            create_graph=self.config.use_hessian
        )[0]

        # Fix: detach unless Hessian is needed
        if not self.config.use_hessian:
            grad = grad.detach()

        gterm = (grad ** 2).sum(dim=list(range(1, grad.ndim)))
        if self.config.reduce == "mean":
            return gterm.mean()
        return gterm.sum()
