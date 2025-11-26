
from __future__ import annotations

import os
import matplotlib.pyplot as plt
import jax
from jax import random
import jax.numpy as jnp

from entropy_ecology_sim.core.fields import RSVPFields
from entropy_ecology_sim.core.dynamics import step_fields, PARAMS_MEME
from entropy_ecology_sim.core.agents import InvasiveParasite
from .config import MemeDiffusionConfig


def main(seed: int = 777, config: MemeDiffusionConfig | None = None) -> None:
    if config is None:
        config = MemeDiffusionConfig(seed=seed)

    outdir = "outputs/meme_diffusion/"
    os.makedirs(outdir, exist_ok=True)

    key = random.PRNGKey(config.seed)
    fields = RSVPFields.random(size=config.grid_size, seed=config.seed)

    parasites = [
        InvasiveParasite(x=config.grid_size // 2, y=config.grid_size // 2, strength=1.8)
    ]

    for t in range(config.steps):
        key, step_key = random.split(key)
        fields = step_fields(fields, PARAMS_MEME, key=step_key)

        for p in parasites:
            fields = p.act(fields, step_key)

        # Occasionally inject global "meme storms"
        if t % 500 == 0 and t > 0:
            fields = fields.replace(S=jnp.clip(fields.S + 0.15, 0.0, 1.0))

        if t in (0, config.steps // 2, config.steps - 1):
            fname = os.path.join(outdir, f"S_step_{t:05d}.png")
            plt.figure(figsize=(7, 7))
            plt.imshow(fields.S, cmap="magma", vmin=0.0, vmax=1.0)
            plt.title(f"Meme entropy – step {t}")
            plt.axis("off")
            plt.savefig(fname, dpi=140, bbox_inches="tight")
            plt.close()


if __name__ == "__main__":
    main()
