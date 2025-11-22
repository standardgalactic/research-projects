"""Minimal 1D RSVP simulation demo.

Usage:
    python run_1d.py

This will simulate a small 1D system and print energy diagnostics.
"""

import numpy as np
import matplotlib.pyplot as plt

from rsvp_sim import Grid1D, RSVPParams, step_rsvp_1d, energy_1d, entropy_1d

def main():
    grid = Grid1D(nx=256, length=1.0)
    params = RSVPParams()

    # Initial conditions: small random perturbation in Phi, zero v, small S
    rng = np.random.default_rng(0)
    phi = 0.1 * rng.standard_normal(grid.nx)
    v = np.zeros(grid.nx)
    S = 0.1 * rng.standard_normal(grid.nx)

    dt = 1e-3
    n_steps = 2000

    energies = []
    entropies = []

    for step in range(n_steps):
        phi, v, S = step_rsvp_1d(phi, v, S, grid, params, dt)
        if step % 10 == 0:
            E = energy_1d(phi, v, S, grid.dx)
            H = entropy_1d(S, grid.dx)
            energies.append(E)
            entropies.append(H)

    # Plot final Phi, v, S and energy history
    fig, axes = plt.subplots(2, 1, figsize=(8, 6))

    ax = axes[0]
    ax.plot(grid.x, phi, label="Phi")
    ax.plot(grid.x, v, label="v")
    ax.plot(grid.x, S, label="S")
    ax.set_xlabel("x")
    ax.legend()
    ax.set_title("Final fields")

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
