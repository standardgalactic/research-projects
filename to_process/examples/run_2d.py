"""Minimal 2D RSVP simulation demo.

Usage:
    python run_2d.py

This will simulate a small 2D system and show the final Phi field.
"""

import numpy as np
import matplotlib.pyplot as plt

from rsvp_sim import Grid2D, RSVPParams, step_rsvp_2d, energy_2d, entropy_2d

def main():
    grid = Grid2D(nx=128, ny=128, lx=1.0, ly=1.0)
    params = RSVPParams()

    rng = np.random.default_rng(0)
    phi = 0.1 * rng.standard_normal((grid.nx, grid.ny))
    vx = np.zeros((grid.nx, grid.ny))
    vy = np.zeros((grid.nx, grid.ny))
    S = 0.1 * rng.standard_normal((grid.nx, grid.ny))

    dt = 5e-4
    n_steps = 1000

    energies = []
    entropies = []

    for step in range(n_steps):
        phi, vx, vy, S = step_rsvp_2d(phi, vx, vy, S, grid, params, dt)
        if step % 10 == 0:
            E = energy_2d(phi, vx, vy, S, grid.dx, grid.dy)
            H = entropy_2d(S, grid.dx, grid.dy)
            energies.append(E)
            entropies.append(H)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    ax = axes[0]
    im = ax.imshow(phi.T, origin="lower", extent=(0, grid.lx, 0, grid.ly))
    ax.set_title("Final Phi")
    plt.colorbar(im, ax=ax)

    ax2 = axes[1]
    ax2.plot(energies, label="Energy")
    ax2.plot(entropies, label="Entropy-like")
    ax2.set_xlabel("sample index (every 10 steps)")
    ax2.legend()
    ax2.set_title("Diagnostics")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
