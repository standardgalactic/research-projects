"""
stats_utils.py

Provides statistical utilities for RSVP analysis: Lyapunov proxies, Wasserstein distances, entropy gradients.

Purpose:
- Compute metrics for field stability, divergence, and distribution comparisons.

Inputs:
- Arrays or field snapshots

Outputs:
- Scalars or matrices depending on metric

Testing Focus:
- Correctness of correlation and distance calculations
"""
from __future__ import annotations
import numpy as np
from scipy.stats import wasserstein_distance


def lyapunov_proxy(field1: np.ndarray, field2: np.ndarray, dt: float = 0.01) -> float:
    # Measures exponential divergence: ln(||delta||)/dt
    delta = np.linalg.norm(field2 - field1)
    if delta <= 0:
        return 0.0
    return np.log(delta)/dt


def compute_entropy_gradient(S: np.ndarray) -> np.ndarray:
    grad_x, grad_y = np.gradient(S)
    return np.sqrt(grad_x**2 + grad_y**2)


def wasserstein_distance_fields(field1: np.ndarray, field2: np.ndarray) -> float:
    return wasserstein_distance(field1.ravel(), field2.ravel())


# Demo harness
if __name__ == '__main__':
    print('stats_utils demo')
    f1, f2 = np.random.randn(16,16), np.random.randn(16,16)
    print('Lyapunov proxy:', lyapunov_proxy(f1,f2))
    print('Entropy gradient norm:', np.mean(compute_entropy_gradient(f1)))
    print('Wasserstein distance:', wasserstein_distance_fields(f1,f2))

