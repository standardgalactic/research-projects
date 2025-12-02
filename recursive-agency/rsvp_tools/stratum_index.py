from dataclasses import dataclass
import torch
from torch import nn

@dataclass
class StratumIndexConfig:
    num_samples: int = 32
    batch_size: int = 32
    jacobian_mode: str = "full"        # "full" or "per-output"
    reduce: str = "mean"


class StratumIndexEstimator(nn.Module):
    def __init__(self, model, config=None):
        super().__init__()
        self.model = model
        self.config = config or StratumIndexConfig()

    def forward(self, x):
        """
        Estimate a 'stratum index' via approximate Jacobian rank.

        Input:
            x — input tensor [B, input_dim]
        Output:
            scalar tensor (rank estimate)
        """
        # Ensure gradients flow to x
        x = x.requires_grad_(True)

        # Forward pass the model
        y = self.model(x)               # [B, output_dim]

        if y.ndim != 2:
            raise ValueError("Expected model(x) to have shape [B, output_dim].")

        B, out_dim = y.shape
        _, in_dim  = x.shape

        jac_list = []

        # Loop over output dimensions
        for i in range(out_dim):
            grad_i = torch.autograd.grad(
                y[:, i].sum(),
                x,
                retain_graph=True,
                create_graph=False,
                allow_unused=False
            )[0]                        # shape [B, in_dim]

            jac_list.append(grad_i)

        # Stack across outputs → [B, in_dim, out_dim]
        J = torch.stack(jac_list, dim=-1)

        # Reshape to 2D for rank computation: [B*in_dim, out_dim]
        J_flat = J.reshape(-1, out_dim)

        # SVD for rank estimation (safe on CPU/GPU)
        try:
            _, S, _ = torch.linalg.svd(J_flat, full_matrices=False)
        except RuntimeError:
            # numerical fallback: add tiny noise
            J_flat = J_flat + 1e-6 * torch.randn_like(J_flat)
            _, S, _ = torch.linalg.svd(J_flat, full_matrices=False)

        # Rank threshold
        rank_est = (S > 1e-4).float().sum()

        return rank_est
