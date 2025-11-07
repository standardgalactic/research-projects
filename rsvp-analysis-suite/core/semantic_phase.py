"""
semantic_phase.py

Information-geometry and semantic-manifold utilities for the RSVP Analysis Suite (RAS).
This starter module provides:
- functions to construct local probability distributions from fields
- pointwise and global information metrics (KL divergence, Jensen-Shannon, Fisher info)
- routines to compute a simple Fisher-Rao metric tensor for discretized fields
- a toy φ_RSVP diagnostic that combines field gradients and entropy to yield a scalar map
- PCA / manifold embedding helpers for visualization-ready low-dimensional embeddings

This module intentionally focuses on clear, auditable numerics that you can
plug into the grid-based `rsvp_fields` outputs.
"""
from __future__ import annotations
from typing import Tuple, Sequence, Any, Dict

import numpy as np

try:
    from sklearn.decomposition import PCA
    from sklearn.manifold import SpectralEmbedding
except Exception:
    PCA = None
    SpectralEmbedding = None


# ----------------------------- Probability conversions -----------------------------

def normalize_to_pmf(arr: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Normalize an array to a probability mass function (sum=1), preserving shape."""
    a = np.asarray(arr, dtype=float)
    a = np.clip(a, eps, None)
    s = np.sum(a)
    if s == 0:
        # uniform fallback
        a = np.ones_like(a) / a.size
        return a
    return a / s


def kl_divergence(p: np.ndarray, q: np.ndarray, base: float = 2.0) -> float:
    """KL divergence D_KL(p || q) where p and q are pmfs of same shape."""
    p = normalize_to_pmf(p)
    q = normalize_to_pmf(q)
    with np.errstate(divide='ignore', invalid='ignore'):
        res = np.sum(p * np.log(p / q)) / np.log(base)
    return float(np.nan_to_num(res, nan=0.0, posinf=np.inf, neginf=0.0))


def jensen_shannon(p: np.ndarray, q: np.ndarray, base: float = 2.0) -> float:
    """Jensen-Shannon divergence (symmetric, finite)"""
    p = normalize_to_pmf(p)
    q = normalize_to_pmf(q)
    m = 0.5 * (p + q)
    return 0.5 * kl_divergence(p, m, base=base) + 0.5 * kl_divergence(q, m, base=base)


# ----------------------------- Fisher information (discrete approx) -----------------------------

def fisher_information_field(pmf_field: np.ndarray, dx: float = 1.0) -> np.ndarray:
    """Compute a pointwise scalar Fisher information density for a PMF defined over a 2D grid.

    We approximate I = \int (|grad p(x)|^2 / p(x)) dx by discrete finite differences per cell.
    Returns the same shape as pmf_field.
    """
    p = np.asarray(pmf_field, dtype=float)
    p = np.clip(p, 1e-12, None)
    # gradients (central differences)
    p_p = np.pad(p, 1, mode='wrap')
    dpdx = (p_p[1:-1, 2:] - p_p[1:-1, 0:-2]) / (2 * dx)
    dpdy = (p_p[2:, 1:-1] - p_p[0:-2, 1:-1]) / (2 * dx)
    I = (dpdx ** 2 + dpdy ** 2) / p
    return I


def total_fisher_information(pmf_field: np.ndarray, dx: float = 1.0) -> float:
    I = fisher_information_field(pmf_field, dx=dx)
    return float(np.sum(I) * (dx * dx))


# ----------------------------- phi_RSVP diagnostic (toy) -----------------------------

def phi_rsvp_map(Phi: np.ndarray, S: np.ndarray, normalize: bool = True) -> np.ndarray:
    """Compute a toy φ_RSVP scalar diagnostic combining field gradients and local entropy.

    Heuristic: φ = |grad Phi|^2 * local_entropy_density^{-alpha}
    This yields high φ where field variations are large and local entropy is low.
    """
    Phi = np.asarray(Phi, dtype=float)
    S = np.asarray(S, dtype=float)
    # compute |grad Phi|^2
    Pp = np.pad(Phi, 1, mode='wrap')
    dPhidx = (Pp[1:-1, 2:] - Pp[1:-1, 0:-2]) / 2.0
    dPhidy = (Pp[2:, 1:-1] - Pp[0:-2, 1:-1]) / 2.0
    grad2 = dPhidx ** 2 + dPhidy ** 2

    # local entropy density: compute S normalized per cell
    local_entropy = S
    local_entropy = np.clip(local_entropy, 1e-8, None)
    alpha = 1.0
    phi_map = grad2 * (local_entropy ** (-alpha))
    if normalize:
        # scale to 0..1
        mmin = phi_map.min()
        mmax = phi_map.max()
        if mmax > mmin:
            phi_map = (phi_map - mmin) / (mmax - mmin)
        else:
            phi_map = np.zeros_like(phi_map)
    return phi_map


# ----------------------------- Embedding helpers -----------------------------

def field_patch_embedding(Phi: np.ndarray, S: np.ndarray, patch_size: int = 4, method: str = 'pca') -> np.ndarray:
    """Extract patches from (Phi,S) and embed them into low-dim coordinates for visualization.

    Returns an array of shape (n_patches, 2) if embedding to 2D.
    """
    nx, ny = Phi.shape
    patches = []
    for i0 in range(0, nx, patch_size):
        for j0 in range(0, ny, patch_size):
            pphi = Phi[i0:i0 + patch_size, j0:j0 + patch_size].ravel()
            ps = S[i0:i0 + patch_size, j0:j0 + patch_size].ravel()
            patches.append(np.concatenate([pphi, ps]))
    X = np.vstack(patches)
    if method == 'pca':
        if PCA is None:
            raise ImportError('scikit-learn required for PCA embedding')
        pca = PCA(n_components=2)
        Y = pca.fit_transform(X)
        return Y
    elif method == 'spectral':
        if SpectralEmbedding is None:
            raise ImportError('scikit-learn required for SpectralEmbedding')
        se = SpectralEmbedding(n_components=2)
        Y = se.fit_transform(X)
        return Y
    else:
        raise ValueError('unknown embedding method')


# ----------------------------- Demo harness -----------------------------

if __name__ == "__main__":
    print('Semantic phase demo — create synthetic fields and compute diagnostics')
    N = 32
    rng = np.random.default_rng(1)
    Phi = rng.normal(scale=0.01, size=(N, N))
    # add a bump
    x = np.linspace(0, 1, N)
    X, Y = np.meshgrid(x, x, indexing='ij')
    Phi += 0.5 * np.exp(-((X - 0.5) ** 2 + (Y - 0.5) ** 2) / 0.01)
    S = np.exp(-((X - 0.3) ** 2 + (Y - 0.35) ** 2) / (2 * 0.02)) + 0.1

    pmf = normalize_to_pmf(np.abs(Phi) + S)
    print('Total Fisher information:', total_fisher_information(pmf))
    phi_map = phi_rsvp_map(Phi, S)
    print('phi_map stats:', phi_map.min(), phi_map.max(), phi_map.mean())

