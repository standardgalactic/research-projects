import numpy as np

def energy_1d(phi, v, S, dx):
    """Simple quadratic energy functional in 1D."""
    density = 0.5 * (phi ** 2 + v ** 2 + S ** 2)
    return dx * np.sum(density)

def entropy_1d(S, dx):
    """Total entropy-like quantity (L1 norm)."""
    return dx * np.sum(np.abs(S))


def energy_2d(phi, vx, vy, S, dx, dy):
    """Simple quadratic energy functional in 2D."""
    density = 0.5 * (phi ** 2 + vx ** 2 + vy ** 2 + S ** 2)
    return dx * dy * np.sum(density)

def entropy_2d(S, dx, dy):
    """Total entropy-like quantity (L1 norm) in 2D."""
    return dx * dy * np.sum(np.abs(S))
