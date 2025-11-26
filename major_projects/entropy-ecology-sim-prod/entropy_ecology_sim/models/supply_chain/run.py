
from __future__ import annotations

import os
import matplotlib.pyplot as plt
import jax
from jax import random

from entropy_ecology_sim.core.fields import RSVPFields
from entropy_ecology_sim.core.dynamics import step_fields, PARAMS_SUPPLYCHAIN
from entropy_ecology_sim.core.agents import EntropyPump, ConstraintBuilder
from .config import SupplyChainConfig


def main(seed: int = 123, config: SupplyChainConfig | None = None) -> None:
    if config is None:
        config = SupplyChainConfig(seed=seed)

    outdir = "outputs/supply_chain/"
    os.makedirs(outdir, exist_ok=True)

    key = random.PRNGKey(config.seed)
    fields = RSVPFields.random(size=config.grid_size, seed=config.seed)

    pumps = [
        EntropyPump(x=config.grid_size // 4, y=config.grid_size // 2, strength=1.5),
        EntropyPump(x=3 * config.grid_size // 4, y=config.grid_size // 2, strength=1.5),
    ]
    builders = [
        ConstraintBuilder(x=config.grid_size // 2, y=config.grid_size // 2, strength=1.2)
    ]
    agents = pumps + builders

    for t in range(config.steps):
        key, step_key = random.split(key)
        fields = step_fields(fields, PARAMS_SUPPLYCHAIN, key=step_key)
        for a in agents:
            fields = a.act(fields, step_key)

        if t in (0, config.steps // 2, config.steps - 1):
            fname = os.path.join(outdir, f"S_step_{t:05d}.png")
            plt.figure(figsize=(7, 7))
            plt.imshow(fields.S, cmap="magma", vmin=0.0, vmax=1.0)
            plt.title(f"Supply-chain entropy – step {t}")
            plt.axis("off")
            plt.savefig(fname, dpi=140, bbox_inches="tight")
            plt.close()


if __name__ == "__main__":
    main()
