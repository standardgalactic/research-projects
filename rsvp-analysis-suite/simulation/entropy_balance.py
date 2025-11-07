"""
entropy_balance.py

Tracks entropy evolution: ∂_t S, divergence of (Phi*V), and entropy production rate Σ̇.

Purpose:
- Monitor entropy conservation or production in RSVP simulations.
- Provide metrics for stability and phase transitions.

Inputs:
- Phi, V, S arrays
- dt: timestep
- n_steps: number of iterations

Outputs:
- Sigma_dot time series
- Updated S array

Testing Focus:
- Correct computation of divergence
- Consistency of integrated Σ̇
"""
from __future__ import annotations
from typing import Tuple
import numpy as np


def divergence(Phi: np.ndarray, V: np.ndarray) -> np.ndarray:
    # 2D central difference
    dVx_dx = (np.roll(V[...,0], -1, axis=0) - np.roll(V[...,0], 1, axis=0))/2
    dVy_dy = (np.roll(V[...,1], -1, axis=1) - np.roll(V[...,1], 1, axis=1))/2
    return dVx_dx + dVy_dy


def run_entropy_balance(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, dt: float = 0.01, n_steps: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    Sigma_dot_history = []
    S_curr = S.copy()
    for _ in range(n_steps):
        div_PhiV = divergence(Phi, V)
        Sigma_dot = np.sum(div_PhiV)  # total entropy production rate
        Sigma_dot_history.append(Sigma_dot)
        # simple update for S (toy placeholder)
        S_curr += dt * div_PhiV
    return np.array(Sigma_dot_history), S_curr


# Demo harness
if __name__ == '__main__':
    print('entropy_balance demo')
    shape = (16,16)
    Phi, V, S = np.random.randn(*shape), np.random.randn(*shape,2), np.random.randn(*shape)
    Sigma_dot_history, S_final = run_entropy_balance(Phi, V, S, dt=0.01, n_steps=50)
    print('Sigma_dot_history min/max:', Sigma_dot_history.min(), Sigma_dot_history.max())
    print('S_final min/max:', S_final.min(), S_final.max())

