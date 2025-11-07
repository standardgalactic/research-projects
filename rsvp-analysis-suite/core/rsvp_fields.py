"""
rsvp_fields.py

Core field definitions and evolution utilities for the RSVP Analysis Suite (RAS).
This starter module provides:
- initialization of scalar (Phi), vector (v), and entropy (S) fields on a 2D grid
- simple finite-difference discretization (forward Euler) with periodic BCs
- diffusion + optional advection step for scalar and entropy fields
- utility I/O for experiments and a small self-test when executed as __main__

Designed as a clean, well-documented starting point you can extend.
"""

from __future__ import annotations
import numpy as np
from typing import Tuple, Dict
import os

Array = np.ndarray


def periodic_pad(arr: Array) -> Array:
    """Return a padded view for periodic boundary finite differences.
    This uses numpy's pad with wrap mode, returning an array with 1-cell padding.
    """
    return np.pad(arr, pad_width=1, mode="wrap")


def laplacian(u: Array, dx: float = 1.0) -> Array:
    """Compute discrete 2D Laplacian with second-order central differences.
    Assumes periodic boundaries via padding.
    """
    up = periodic_pad(u)
    lap = (up[2:, 1:-1] + up[0:-2, 1:-1] + up[1:-1, 2:] + up[1:-1, 0:-2] - 4 * up[1:-1, 1:-1])
    return lap / (dx * dx)


def advect_scalar(phi: Array, vx: Array, vy: Array, dx: float, dt: float) -> Array:
    """Simple upwind-ish advective update for scalar phi under velocity field (vx, vy).
    This is a first-order finite difference advection step (conservative form approx.).

    Notes:
      - For stability keep dt small (CFL condition): dt <= dx / max(|v|)
      - This is intentionally simple so you can replace with higher-order schemes later.
    """
    # central differences for gradient
    phi_p = periodic_pad(phi)
    dphi_dx = (phi_p[1:-1, 2:] - phi_p[1:-1, 0:-2]) / (2 * dx)
    dphi_dy = (phi_p[2:, 1:-1] - phi_p[0:-2, 1:-1]) / (2 * dx)

    return phi - dt * (vx * dphi_dx + vy * dphi_dy)


def init_fields(grid_size: int = 128, noise: float = 1e-3, seed: int | None = None) -> Tuple[Array, Array, Array]:
    """Initialize scalar (Phi), vector (v = (vx, vy)), and entropy (S) fields.

    Returns:
      Phi: (N, N) array
      v:  tuple of (vx, vy) each (N, N)
      S:  (N, N) array
    """
    rng = np.random.default_rng(seed)
    N = grid_size
    # Smooth random initial scalar field
    Phi = rng.normal(scale=noise, size=(N, N))
    # small scale structure
    kx = np.fft.fftfreq(N)
    ky = np.fft.fftfreq(N)
    KX, KY = np.meshgrid(kx, ky)
    radius = np.sqrt(KX ** 2 + KY ** 2)
    # low-pass filter in Fourier domain to produce smooth initial condition
    filt = np.exp(-(radius * N / 8.0) ** 2)
    Phi = np.real(np.fft.ifft2(np.fft.fft2(Phi) * filt))

    # divergence-free initial velocity via streamfunction
    psi = rng.normal(scale=noise * 0.5, size=(N, N))
    psi_hat = np.fft.fft2(psi)
    kx2 = (2 * np.pi * KX)
    ky2 = (2 * np.pi * KY)
    with np.errstate(divide='ignore', invalid='ignore'):
        vx_hat = 1j * ky2 * psi_hat
        vy_hat = -1j * kx2 * psi_hat
    vx = np.real(np.fft.ifft2(vx_hat))
    vy = np.real(np.fft.ifft2(vy_hat))

    # Entropy field positive-definite
    S = np.abs(Phi) * 0.0 + 0.1 + rng.uniform(-noise, noise, size=(N, N))
    S = np.clip(S, 1e-8, None)

    return Phi, (vx, vy), S


def compute_entropy(S: Array, base: float = 2.0) -> Array:
    """Compute Shannon-like pointwise entropy (per cell).
    S should be positive. We use -p * log_b(p) where p is normalized locally.
    For simplicity we normalize S over the whole grid to produce a probability mass.
    """
    p = S / np.sum(S)
    with np.errstate(divide='ignore', invalid='ignore'):
        ent = -p * np.log(p) / np.log(base)
    ent = np.nan_to_num(ent, nan=0.0, posinf=0.0, neginf=0.0)
    return ent


def evolve_field(Phi: Array,
                 v: Tuple[Array, Array],
                 S: Array,
                 dt: float = 0.01,
                 dx: float = 1.0,
                 diffusion_phi: float = 0.01,
                 diffusion_S: float = 0.005,
                 advect: bool = True,
                 steps: int = 1) -> Tuple[Array, Tuple[Array, Array], Array]:
    """Evolve the (Phi, v=(vx,vy), S) fields forward in time using simple operators.

    Operators used in this starter implementation:
      - Scalar diffusion: dPhi/dt = D_phi * laplacian(Phi)
      - Entropy diffusion: dS/dt = D_S * laplacian(S)
      - Advection of Phi and S by (vx, vy) using a low-order advective step
      - Velocity field is currently static; later modules can evolve it with momentum eqns

    Returns updated copies of (Phi, v, S).
    """
    vx, vy = v
    Phi_new = Phi.copy()
    S_new = S.copy()

    for _ in range(steps):
        # diffusion terms
        lap_phi = laplacian(Phi_new, dx=dx)
        lap_S = laplacian(S_new, dx=dx)

        Phi_new = Phi_new + dt * diffusion_phi * lap_phi
        S_new = S_new + dt * diffusion_S * lap_S

        if advect:
            Phi_new = advect_scalar(Phi_new, vx, vy, dx, dt)
            S_new = advect_scalar(S_new, vx, vy, dx, dt)

        # enforce positivity for entropy
        S_new = np.clip(S_new, 1e-12, None)

    return Phi_new, (vx, vy), S_new


def variational_step(Phi: Array, S: Array, params: Dict | None = None) -> Tuple[Array, Array]:
    """Placeholder for a variational/gradient step that would minimize an RSVP action.

    This starter routine returns the inputs unchanged. Replace with a symbolic
    derivative of your action functional (or a numerical gradient step).
    """
    # TODO: implement action functional derivatives here
    return Phi, S


def save_state(path: str, Phi: Array, v: Tuple[Array, Array], S: Array, metadata: Dict | None = None) -> None:
    """Save a simulation snapshot to a .npz file including metadata dict.
    Example: save_state('out/snap_000.npz', Phi, v, S, {'t': 0.1})
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    vx, vy = v
    if metadata is None:
        metadata = {}
    # np.savez supports saving arrays; we serialize metadata as a string
    np.savez(path, Phi=Phi, vx=vx, vy=vy, S=S, metadata=repr(metadata))


def load_state(path: str) -> Tuple[Array, Tuple[Array, Array], Array, Dict]:
    """Load a saved .npz state (saved with save_state).
    Returns (Phi, (vx,vy), S, metadata)
    """
    data = np.load(path, allow_pickle=True)
    Phi = data['Phi']
    vx = data['vx']
    vy = data['vy']
    S = data['S']
    meta = data.get('metadata', b'{}')
    try:
        metadata = eval(meta)
    except Exception:
        metadata = {}
    return Phi, (vx, vy), S, metadata


if __name__ == "__main__":
    # small self-check: run a short evolution and save a snapshot
    print("Running quick self-test of rsvp_fields module...")
    Phi, v, S = init_fields(grid_size=64, noise=0.01, seed=42)
    print("Initial sums: Phi.sum()=", Phi.sum(), "S.sum()=", S.sum())
    Phi, v, S = evolve_field(Phi, v, S, dt=0.02, dx=1.0, diffusion_phi=0.1, diffusion_S=0.05, advect=True, steps=10)
    ent = compute_entropy(S)
    print("Post-evolution sums: Phi.sum()=", Phi.sum(), "S.sum()=", S.sum(), "Entropy.sum()=", ent.sum())
    out = 'out/snap_test.npz'
    save_state(out, Phi, v, S, metadata={'test': True})
    print(f"Saved test snapshot to {out}")

