"""
cosmo_tests.py

Cosmological testing module for RSVP Analysis Suite (RAS).
Provides:
- toy simulations of cosmological scalar/vector fields
- analysis of entropy tilings over cosmic patches
- horizon-scale diagnostics (CMB analogs, mean field values)
- simple comparisons with standard cosmological metrics (toy ΛCDM vs RSVP)
"""
from __future__ import annotations
from typing import Optional

import numpy as np

from rsvp_analysis_suite.core import rsvp_fields, tiling_entropy
from rsvp_analysis_suite.utils import data_viz


def simulate_cosmo_field(shape: Tuple[int,int]=(64,64), seed: Optional[int]=42) -> np.ndarray:
    """Generate a toy cosmological Phi field."""
    rng = np.random.default_rng(seed)
    Phi = rng.standard_normal(shape)
    return Phi


def compute_horizon_entropy(Phi: np.ndarray, patch_size: int = 8) -> np.ndarray:
    """Compute patchwise mean entropy over the field."""
    nx, ny = Phi.shape
    entropies = np.zeros((nx//patch_size, ny//patch_size))
    for i in range(0, nx, patch_size):
        for j in range(0, ny, patch_size):
            patch = Phi[i:i+patch_size, j:j+patch_size]
            entropies[i//patch_size, j//patch_size] = tiling_entropy.compute_entropy(patch)
    return entropies


def plot_cosmo_diagnostics(Phi: np.ndarray, patch_entropy: np.ndarray):
    data_viz.plot_scalar_field(Phi, title='Cosmological Phi Field')
    data_viz.plot_scalar_field(patch_entropy, title='Patchwise Entropy')


if __name__ == "__main__":
    print('cosmo_tests demo')
    Phi = simulate_cosmo_field()
    patch_entropy = compute_horizon_entropy(Phi)
    print('Patchwise entropy shape:', patch_entropy.shape)
    plot_cosmo_diagnostics(Phi, patch_entropy)

