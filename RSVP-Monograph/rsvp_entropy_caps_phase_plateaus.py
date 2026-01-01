#!/usr/bin/env python3
"""
rsvp_entropy_caps_phase_plateaus.py
-----------------------------------
Entropy caps and plateau-inducing modifications.
Provides hard clamp and soft-cap sink terms.
"""

import numpy as np

def hard_cap(S, S_max):
    """
    Hard clamp: S := min(S, S_max)
    """
    return np.minimum(S, S_max)

def soft_cap_sink(S, S_max, k_cap=1.0, power=1.0, eps=1e-12):
    """
    Returns an additional sink term to be SUBTRACTED in dS:
        sink = k_cap * S * (S/S_max)^power
    For power=1: sink ~ k_cap * S^2 / S_max
    """
    Smax = max(float(S_max), eps)
    ratio = np.maximum(S, 0.0) / Smax
    return k_cap * np.maximum(S, 0.0) * (ratio ** power)

def plateau_phase_filter(theta_series, strength=0.2):
    """
    Optional post-processing: low-pass filter theta(t) to emphasize plateaus.
    Not required for the dynamics; useful for visualizing 'aging' behavior.
    """
    out = np.empty_like(theta_series)
    out[0] = theta_series[0]
    for i in range(1, len(theta_series)):
        out[i] = (1.0 - strength) * out[i-1] + strength * theta_series[i]
    return out