"""
scaling_laws.py

Fits Phi–S–Σ̇ scaling relations for RSVP Analysis Suite (RAS).

Purpose:
- Perform regression analysis to find scaling exponents.
- Compute residuals and goodness-of-fit metrics.

Inputs:
- Phi, S arrays (numpy)
- optional Sigma_dot array (entropy production rate)
- fit_type: 'linear' (log-log) or 'polynomial'

Outputs:
- Scaling exponents
- Residuals
- Optional plots

Testing Focus:
- Regression correctness
- Reproducibility of scaling exponents
"""
from __future__ import annotations
from typing import Tuple, Optional
import numpy as np
from scipy import stats

from rsvp_analysis_suite.utils import data_viz


def fit_scaling(Phi: np.ndarray, S: np.ndarray, Sigma_dot: Optional[np.ndarray] = None, fit_type: str = 'linear') -> Tuple[float, float, np.ndarray]:
    """Fit scaling relation Phi ~ S^alpha (or log-log linear). Returns alpha, intercept, residuals."""
    x = S.ravel()
    y = Phi.ravel()
    if fit_type == 'linear':
        # log-log fit
        mask = (x>0) & (y>0)
        log_x = np.log(x[mask])
        log_y = np.log(y[mask])
        slope, intercept, r_value, p_value, std_err = stats.linregress(log_x, log_y)
        residuals = log_y - (slope*log_x + intercept)
        alpha = slope
        return alpha, intercept, residuals
    else:
        # polynomial fit
        p = np.polyfit(x, y, deg=2)
        residuals = y - np.polyval(p, x)
        alpha = p[0]
        intercept = p[-1]
        return alpha, intercept, residuals


def plot_scaling(Phi: np.ndarray, S: np.ndarray, alpha: float, intercept: float):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.scatter(S.ravel(), Phi.ravel(), label='Data', alpha=0.5)
    S_sorted = np.sort(S.ravel())
    plt.plot(S_sorted, np.exp(intercept)*S_sorted**alpha, color='red', label=f'Fit: alpha={alpha:.2f}')
    plt.xlabel('S')
    plt.ylabel('Phi')
    plt.legend()
    plt.title('Scaling Law Fit')
    plt.show()


# Demo harness
if __name__ == '__main__':
    print('scaling_laws demo')
    S = np.random.rand(100)**2 + 0.1
    Phi = S**1.5 * np.random.rand(100)*0.1 + S**1.5
    alpha, intercept, residuals = fit_scaling(Phi, S)
    print('Fitted alpha:', alpha)
    print('Residuals mean/std:', np.mean(residuals), np.std(residuals))
    plot_scaling(Phi, S, alpha, intercept)

