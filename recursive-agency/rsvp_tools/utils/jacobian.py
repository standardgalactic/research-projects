# skeleton
import torch
from torch import nn

def jacobian_vp(model, inputs, params=None, create_graph=False):
    num_params = sum(p.numel() for p in model.parameters())
    batch_size = inputs.shape[0]
    return torch.zeros(batch_size, num_params, device=inputs.device)

def approximate_rank(jac_repr, tol=1e-4, method="svd", max_rank=None):
    u,s,v = torch.linalg.svd(jac_repr, full_matrices=False)
    if max_rank: s = s[:max_rank]
    return int((s>tol).sum().item())
