
from __future__ import annotations

import os
from typing import Sequence

import matplotlib.pyplot as plt
import jax.numpy as jnp


def save_entropy_frames(history: Sequence[jnp.ndarray], outdir: str, prefix: str = "S") -> None:
    os.makedirs(outdir, exist_ok=True)
    for i, S in enumerate(history):
        fname = os.path.join(outdir, f"{prefix}_{i:04d}.png")
        plt.figure(figsize=(6, 6))
        plt.imshow(S, cmap="magma", vmin=0.0, vmax=1.0)
        plt.axis("off")
        plt.savefig(fname, dpi=120, bbox_inches="tight")
        plt.close()
