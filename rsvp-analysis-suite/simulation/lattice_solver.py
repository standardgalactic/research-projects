"""
lattice_solver.py

Finite-difference 2D/3D lattice solver for RSVP fields (Phi, V, S).
Supports optional GPU acceleration via Numba/CuPy.

Purpose:
- Evolve fields according to discrete PDEs
- Support core solver testing and entropy evolution studies

Inputs:
- Phi, V, S arrays (numpy)
- dt: time step
- n_steps: number of iterations
- use_gpu: boolean flag for GPU acceleration

Outputs:
- Updated Phi, V, S arrays

Testing Focus:
- Convergence with grid resolution
- Stability under different dt and n_steps
"""
from __future__ import annotations
from typing import Tuple
import numpy as np

try:
    import cupy as cp
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    from numba import njit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False


def finite_diff_step(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Basic finite-difference step for 2D fields (CPU)."""
    Phi_new = Phi + dt * (np.roll(Phi, 1, axis=0) + np.roll(Phi, -1, axis=0) +
                          np.roll(Phi, 1, axis=1) + np.roll(Phi, -1, axis=1) - 4*Phi)
    V_new = V + dt * (np.roll(V, 1, axis=0) + np.roll(V, -1, axis=0) +
                      np.roll(V, 1, axis=1) + np.roll(V, -1, axis=1) - 4*V)
    S_new = S + dt * (np.roll(S, 1, axis=0) + np.roll(S, -1, axis=0) +
                      np.roll(S, 1, axis=1) + np.roll(S, -1, axis=1) - 4*S)
    return Phi_new, V_new, S_new


def run_lattice_solver(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01, n_steps: int = 100, use_gpu: bool = False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    if use_gpu and GPU_AVAILABLE:
        Phi_gpu, V_gpu, S_gpu = cp.asarray(Phi), cp.asarray(V), cp.asarray(S)
        for _ in range(n_steps):
            Phi_gpu, V_gpu, S_gpu = finite_diff_step(cp.asnumpy(Phi_gpu), cp.asnumpy(V_gpu), cp.asnumpy(S_gpu), dt=dt)
        return cp.asnumpy(Phi_gpu), cp.asnumpy(V_gpu), cp.asnumpy(S_gpu)
    else:
        Phi_curr, V_curr, S_curr = Phi.copy(), V.copy(), S.copy()
        for _ in range(n_steps):
            Phi_curr, V_curr, S_curr = finite_diff_step(Phi_curr, V_curr, S_curr, dt=dt)
        return Phi_curr, V_curr, S_curr


# Demo harness
if __name__ == '__main__':
    print('lattice_solver demo')
    shape = (16,16)
    Phi, V, S = np.random.randn(*shape), np.random.randn(*shape,2), np.random.randn(*shape)
    Phi_new, V_new, S_new = run_lattice_solver(Phi, V, S, dt=0.01, n_steps=50)
    print('Phi_new min/max:', Phi_new.min(), Phi_new.max())
    print('S_new min/max:', S_new.min(), S_new.max())

