
from __future__ import annotations

from dataclasses import dataclass, replace
import jax
import jax.numpy as jnp


@dataclass(frozen=True)
class RSVPFields:
    """Container for the RSVP scalar (Phi), vector (vx, vy), and entropy (S) fields."
    """
    size: int
    dx: float
    Phi: jnp.ndarray
    vx: jnp.ndarray
    vy: jnp.ndarray
    S: jnp.ndarray

    @classmethod
    def random(cls, size: int = 256, dx: float = 1.0, seed: int = 0) -> "RSVPFields":
        """Initialize fields with mildly perturbed entropy and constraint patterns."
        """
        key = jax.random.PRNGKey(seed)
        key_phi, key_s = jax.random.split(key)

        Phi = jax.random.uniform(key_phi, (size, size), minval=0.4, maxval=0.6)
        S = jax.random.uniform(key_s, (size, size), minval=0.6, maxval=0.9)
        vx = jnp.zeros((size, size))
        vy = jnp.zeros((size, size))

        return cls(size=size, dx=dx, Phi=Phi, vx=vx, vy=vy, S=S)

    def replace(self, **kwargs) -> "RSVPFields":
        """Return a new RSVPFields with specified fields replaced (functional style)."
        """
        return replace(self, **kwargs)
