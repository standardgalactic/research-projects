import numpy as np

def laplacian_1d(u, dx):
    """Periodic 1D Laplacian using second-order finite differences."""
    return (np.roll(u, -1) - 2.0 * u + np.roll(u, 1)) / (dx * dx)

def grad_1d(u, dx):
    """Periodic 1D gradient using central differences."""
    return (np.roll(u, -1) - np.roll(u, 1)) / (2.0 * dx)

def advect_1d(phi, v, dx):
    """Compute divergence of phi * v in 1D: d/dx (phi v)."""
    flux = phi * v
    return (np.roll(flux, -1) - np.roll(flux, 1)) / (2.0 * dx)


def laplacian_2d(u, dx, dy):
    """Periodic 2D Laplacian using second-order finite differences."""
    return (
        (np.roll(u, -1, axis=0) - 2.0 * u + np.roll(u, 1, axis=0)) / (dx * dx)
        + (np.roll(u, -1, axis=1) - 2.0 * u + np.roll(u, 1, axis=1)) / (dy * dy)
    )

def grad_2d(u, dx, dy):
    """Periodic 2D gradient: returns (ux, uy)."""
    ux = (np.roll(u, -1, axis=0) - np.roll(u, 1, axis=0)) / (2.0 * dx)
    uy = (np.roll(u, -1, axis=1) - np.roll(u, 1, axis=1)) / (2.0 * dy)
    return ux, uy

def advect_2d(phi, vx, vy, dx, dy):
    """Compute divergence of phi * v in 2D: ∇·(phi v)."""
    fx = phi * vx
    fy = phi * vy
    dfx_dx = (np.roll(fx, -1, axis=0) - np.roll(fx, 1, axis=0)) / (2.0 * dx)
    dfy_dy = (np.roll(fy, -1, axis=1) - np.roll(fy, 1, axis=1)) / (2.0 * dy)
    return dfx_dx + dfy_dy
