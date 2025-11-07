"""
stochastic_dynamics.py

Implements Langevin/MCMC relaxation and noise-driven evolution of RSVP fields (Phi, V, S).

Purpose:
- Introduce stochasticity to test entropic smoothing and field stability.
- Supports Monte Carlo sampling and Langevin dynamics.

Inputs:
- Phi, V, S arrays
- dt: timestep
- n_steps: number of iterations
- noise_strength: standard deviation of Gaussian noise

Outputs:
- Evolved Phi, V, S arrays

Testing Focus:
- Statistical consistency with expected noise properties
- Stability under different noise amplitudes
"""
from __future__ import annotations
from typing import Tuple
import numpy as np


def langevin_step(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01, noise_strength: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    noise_Phi = np.random.randn(*Phi.shape) * noise_strength * np.sqrt(dt)
    noise_V = np.random.randn(*V.shape) * noise_strength * np.sqrt(dt)
    noise_S = np.random.randn(*S.shape) * noise_strength * np.sqrt(dt)

    # Simple diffusion + noise step (toy placeholder)
    Phi_new = Phi + dt * (np.roll(Phi,1,axis=0)+np.roll(Phi,-1,axis=0)+np.roll(Phi,1,axis=1)+np.roll(Phi,-1,axis=1)-4*Phi) + noise_Phi
    V_new = V + dt * (np.roll(V,1,axis=0)+np.roll(V,-1,axis=0)+np.roll(V,1,axis=1)+np.roll(V,-1,axis=1)-4*V) + noise_V
    S_new = S + dt * (np.roll(S,1,axis=0)+np.roll(S,-1,axis=0)+np.roll(S,1,axis=1)+np.roll(S,-1,axis=1)-4*S) + noise_S

    return Phi_new, V_new, S_new


def run_stochastic_dynamics(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01, n_steps: int = 100, noise_strength: float = 0.05) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    Phi_curr, V_curr, S_curr = Phi.copy(), V.copy(), S.copy()
    for _ in range(n_steps):
        Phi_curr, V_curr, S_curr = langevin_step(Phi_curr, V_curr, S_curr, dt=dt, noise_strength=noise_strength)
    return Phi_curr, V_curr, S_curr


# Demo harness
if __name__ == '__main__':
    print('stochastic_dynamics demo')
    shape = (16,16)
    Phi, V, S = np.random.randn(*shape), np.random.randn(*shape,2), np.random.randn(*shape)
    Phi_new, V_new, S_new = run_stochastic_dynamics(Phi, V, S, dt=0.01, n_steps=50, noise_strength=0.1)
    print('Phi_new min/max:', Phi_new.min(), Phi_new.max())
    print('S_new min/max:', S_new.min(), S_new.max())

