"""
phase_coherence.py

Computes spatiotemporal coherence of RSVP fields (Phi, V, S).

Purpose:
- Measure correlations like <Phi Phi'>, <S Phi> across lattice or time.
- Useful for detecting coherent patterns or phase transitions.

Inputs:
- Phi, S arrays
- time_series: optional 3D arrays (t,x,y) for temporal coherence

Outputs:
- Coherence matrices
- Optional scalar summary metrics

Testing Focus:
- Correct computation of spatial/temporal correlations
- Sensitivity to structured vs random fields
"""
from __future__ import annotations
from typing import Optional
import numpy as np


def spatial_coherence(Phi: np.ndarray, S: np.ndarray) -> float:
    """Compute simple spatial correlation between Phi and S."""
    Phi_flat = Phi.ravel()
    S_flat = S.ravel()
    return np.corrcoef(Phi_flat, S_flat)[0,1]


def temporal_coherence(time_series_Phi: Optional[np.ndarray] = None, time_series_S: Optional[np.ndarray] = None) -> np.ndarray:
    """Compute temporal correlation matrix over time for Phi and S."""
    if time_series_Phi is None or time_series_S is None:
        raise ValueError('Time series data required for temporal coherence.')
    t_steps = time_series_Phi.shape[0]
    corr_matrix = np.zeros((t_steps, t_steps))
    for i in range(t_steps):
        for j in range(t_steps):
            corr_matrix[i,j] = np.corrcoef(time_series_Phi[i].ravel(), time_series_S[j].ravel())[0,1]
    return corr_matrix


# Demo harness
if __name__ == '__main__':
    print('phase_coherence demo')
    shape = (16,16)
    Phi, S = np.random.randn(*shape), np.random.randn(*shape)
    spatial_corr = spatial_coherence(Phi, S)
    print('Spatial coherence Phi-S:', spatial_corr)

    # Temporal demo
    t_steps = 10
    time_series_Phi = np.random.randn(t_steps, *shape)
    time_series_S = np.random.randn(t_steps, *shape)
    temp_corr_matrix = temporal_coherence(time_series_Phi, time_series_S)
    print('Temporal coherence matrix shape:', temp_corr_matrix.shape)

