# Simplified RSVPFields
import jax, jax.numpy as jnp
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class RSVPFields:
    size:int=256
    dx:float=1.0
    Phi:jnp.ndarray=jnp.zeros((256,256))
    vx:jnp.ndarray=jnp.zeros((256,256))
    vy:jnp.ndarray=jnp.zeros((256,256))
    S:jnp.ndarray=jnp.zeros((256,256))

    def replace(self, **kwargs):
        return replace(self, **kwargs)