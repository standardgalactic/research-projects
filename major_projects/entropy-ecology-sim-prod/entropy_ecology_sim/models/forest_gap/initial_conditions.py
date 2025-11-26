
from __future__ import annotations

import jax
from jax import random

from entropy_ecology_sim.core.fields import RSVPFields
from .config import BCIModelConfig


def load_bci_initial_conditions(cfg: BCIModelConfig) -> RSVPFields:
    """Placeholder initial conditions for the Barro Colorado Island model.

    In a full implementation, this is where the real Smithsonian census
    data would be parsed and mapped onto Phi and S. For now, we use a
    structured random seed to generate a canopy-like pattern.
    """
    key = random.PRNGKey(cfg.seed)
    base_fields = RSVPFields.random(size=cfg.grid_size, seed=cfg.seed)

    # Simple "canopy" modulation: large-scale Perlin-like noise via smoothing
    Phi = base_fields.Phi
    for _ in range(3):
        Phi = 0.25 * (
            jax.numpy.roll(Phi, 1, 0) + jax.numpy.roll(Phi, -1, 0) +
            jax.numpy.roll(Phi, 1, 1) + jax.numpy.roll(Phi, -1, 1)
        )

    return base_fields.replace(Phi=Phi)
