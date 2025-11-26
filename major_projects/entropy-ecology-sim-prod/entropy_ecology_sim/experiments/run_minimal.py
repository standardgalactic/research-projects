
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Sequence, Optional

import jax
import jax.numpy as jnp
from jax import random
import matplotlib.pyplot as plt
from rich.console import Console
from rich.progress import Progress, TimeElapsedColumn, BarColumn, TaskProgressColumn

from entropy_ecology_sim.core.fields import RSVPFields
from entropy_ecology_sim.core.dynamics import (
    step_fields,
    DynamicsParams,
    PARAMS_FOREST,
)
from entropy_ecology_sim.core.agents import (
    Agent,
    AGENT_CLASSES,
    AutocatalyticNode,
    EntropyPump,
    ConstraintBuilder,
    InvasiveParasite,
)


console = Console()


@dataclass
class MinimalDemoConfig:
    grid_size: int = 256
    steps: int = 5000
    save_every: int = 200
    n_autocatalytic: int = 30
    n_entropy_pump: int = 4
    n_constraint_builder: int = 6
    n_parasite: int = 3
    seed: int = 11
    output_dir: str = "outputs/minimal_demo/"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def spawn_agents(cfg: MinimalDemoConfig, key: jax.random.PRNGKey) -> list[Agent]:
    size = cfg.grid_size
    agents: list[Agent] = []

    def rand_xy(k):
        x = random.randint(k, (), 0, size - 1)
        k, sub = random.split(k)
        y = random.randint(sub, (), 0, size - 1)
        return int(x), int(y)

    k = key

    for _ in range(cfg.n_autocatalytic):
        k, sub = random.split(k)
        x, y = rand_xy(sub)
        agents.append(AutocatalyticNode(x=x, y=y, strength=0.8))

    for _ in range(cfg.n_entropy_pump):
        k, sub = random.split(k)
        x, y = rand_xy(sub)
        agents.append(EntropyPump(x=x, y=y, strength=1.2))

    for _ in range(cfg.n_constraint_builder):
        k, sub = random.split(k)
        x, y = rand_xy(sub)
        agents.append(ConstraintBuilder(x=x, y=y, strength=1.1))

    for _ in range(cfg.n_parasite):
        k, sub = random.split(k)
        x, y = rand_xy(sub)
        agents.append(InvasiveParasite(x=x, y=y, strength=1.4))

    return agents


def apply_agents(
    fields: RSVPFields,
    agents: Sequence[Agent],
    key: Optional[jax.random.PRNGKey],
) -> RSVPFields:
    k = key
    for agent in agents:
        if k is not None:
            k, sub = random.split(k)
        else:
            sub = None
        fields = agent.act(fields, sub)
    return fields


def demo(cfg: MinimalDemoConfig = MinimalDemoConfig()) -> None:
    _ensure_dir(cfg.output_dir)

    console.rule("[bold cyan]Entropy Ecology Minimal Demo")

    master_key = random.PRNGKey(cfg.seed)
    key_fields, key_agents = random.split(master_key)

    console.print("[bold green]Initializing fields…[/]")
    fields = RSVPFields.random(size=cfg.grid_size, seed=cfg.seed)

    console.print("[bold green]Spawning agents…[/]")
    agents = spawn_agents(cfg, key_agents)

    params: DynamicsParams = PARAMS_FOREST

    console.print(
        f"[yellow]Running {cfg.steps} steps with {len(agents)} agents on a "
        f"{cfg.grid_size}×{cfg.grid_size} lattice…[/]"
    )

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Simulating", total=cfg.steps)

        key_loop = key_fields
        for t in range(cfg.steps):
            key_loop, step_key = random.split(key_loop)
            fields = step_fields(fields, params, key=step_key)
            fields = apply_agents(fields, agents, step_key)

            if t % cfg.save_every == 0:
                fname = os.path.join(cfg.output_dir, f"S_step_{t:05d}.png")
                plt.figure(figsize=(7, 7))
                plt.imshow(fields.S, cmap="magma", vmin=0.0, vmax=1.0)
                plt.title(f"S field – step {t}")
                plt.axis("off")
                plt.savefig(fname, dpi=120, bbox_inches="tight")
                plt.close()
                console.print(f"[dim]Saved {fname}[/]")

            progress.update(task, advance=1)

    fname = os.path.join(cfg.output_dir, "final_S.png")
    plt.figure(figsize=(7, 7))
    plt.imshow(fields.S, cmap="magma", vmin=0.0, vmax=1.0)
    plt.title("Final Entropy Field")
    plt.axis("off")
    plt.savefig(fname, dpi=160, bbox_inches="tight")
    plt.close()

    console.print(f"[bold green]Done! Final image saved to {fname}[/]")


if __name__ == "__main__":
    demo()
