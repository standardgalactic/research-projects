# Full dynamics implementation (truncated)
from __future__ import annotations
import jax, jax.numpy as jnp
from jax import jit
from dataclasses import dataclass
from .fields import RSVPFields

@dataclass(frozen=True)
class DynamicsParams:
    dt:float=0.025; D_Phi:float=0.08; D_S:float=0.18; gamma:float=0.92
    beta:float=0.0; kappa:float=0.06; chi:float=0.12; S_max:float=1.0
    S_floor:float=1e-6; Phi_decay:float=0.0008

@jit
def step_fields(fields:RSVPFields, params:DynamicsParams, key=None):
    return fields

PARAMS_FOREST = DynamicsParams()