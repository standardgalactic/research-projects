
from __future__ import annotations

import os
import matplotlib.pyplot as plt
import jax
import jax.numpy as jnp

from entropy_ecology_sim.core.dynamics import run_n_steps, PARAMS_FOREST
from .config import BCIModelConfig
from .initial_conditions import load_bci_initial_conditions


def main(seed: int = 42, config: BCIModelConfig | None = None) -> None:
    if config is None:
        config = BCIModelConfig(seed=seed)

    fields = load_bci_initial_conditions(config)
    years = config.years

    steps_per_year = 50
    total_steps = years * steps_per_year

    outdir = "outputs/forest_gap/"
    os.makedirs(outdir, exist_ok=True)

    key = jax.random.PRNGKey(seed)

    for year in range(years):
        fields = run_n_steps(fields, steps_per_year, PARAMS_FOREST, agent_act_fn=None, key=key)
        if year % config.census_interval == 0:
            fname = os.path.join(outdir, f"S_year_{year:03d}.png")
            plt.figure(figsize=(7, 7))
            plt.imshow(fields.S, cmap="magma", vmin=0.0, vmax=1.0)
            plt.title(f"Forest entropy – year {year}")
            plt.axis("off")
            plt.savefig(fname, dpi=140, bbox_inches="tight")
            plt.close()


if __name__ == "__main__":
    main()
