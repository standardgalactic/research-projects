"""
spectral_solver.py

Fourier-domain solver for RSVP fields (Phi, V, S).

Purpose:
- Integrate fields in spectral domain to analyze dispersion and stability.
- Support comparison with finite-difference and stochastic solvers.

Inputs:
- Phi, V, S arrays
- dt: timestep
- n_steps: number of iterations

Outputs:
- Evolved Phi, V, S arrays in real space

Testing Focus:
- Correct FFT/IFFT operations
- Energy conservation / dispersion properties
"""
from __future__ import annotations
from typing import Tuple
import numpy as np


def spectral_step(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # FFT
    Phi_k = np.fft.fft2(Phi)
    V_k = np.fft.fft2(V, axes=(0,1))
    S_k = np.fft.fft2(S)

    # Wave numbers
    kx = np.fft.fftfreq(Phi.shape[0]).reshape(-1,1)
    ky = np.fft.fftfreq(Phi.shape[1]).reshape(1,-1)
    k2 = (kx**2 + ky**2)

    # Avoid division by zero
    k2[0,0] = 1.0

    # Simple spectral diffusion (toy placeholder)
    Phi_k_new = Phi_k * np.exp(-k2*dt)
    V_k_new = V_k * np.exp(-k2[...,np.newaxis]*dt)
    S_k_new = S_k * np.exp(-k2*dt)

    # IFFT
    Phi_new = np.fft.ifft2(Phi_k_new).real
    V_new = np.fft.ifft2(V_k_new, axes=(0,1)).real
    S_new = np.fft.ifft2(S_k_new).real

    return Phi_new, V_new, S_new


def run_spectral_solver(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01, n_steps: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    Phi_curr, V_curr, S_curr = Phi.copy(), V.copy(), S.copy()
    for _ in range(n_steps):
        Phi_curr, V_curr, S_curr = spectral_step(Phi_curr, V_curr, S_curr, dt=dt)
    return Phi_curr, V_curr, S_curr


# Demo harness
if __name__ == '__main__':
    print('spectral_solver demo')
    shape = (16,16)
    Phi, V, S = np.random.randn(*shape), np.random.randn(*shape,2), np.random.randn(*shape)
    Phi_new, V_new, S_new = run_spectral_solver(Phi, V, S, dt=0.01, n_steps=50)
    print('Phi_new min/max:', Phi_new.min(), Phi_new.max())
    print('S_new min/max:', S_new.min(), S_new.max())

