#!/usr/bin/env python3
"""
rsvp_equilibrium_chi.py
-----------------------
History-coupled equilibrium score: Es = ((TA+TB)/(2*Phi)) * g(chi)
Designed as a drop-in replacement for equilibrium_score_field().
"""

import numpy as np

def g_chi_multiplicative(chi, k=0.25):
    """
    Bounded monotone factor in (0, 1]:
        g(chi) = 1 / (1 + k*chi)
    Large chi -> smaller effective Es (history dampens equilibrium phase).
    """
    return 1.0 / (1.0 + k * chi)

def equilibrium_score_field_chi(TA, TB, Phi, chi, eps=1e-12, k=0.25):
    """
    Es(x,t) = ((TA+TB)/(2*Phi)) * g(chi)
    """
    Phi_safe = np.maximum(Phi, eps)
    base = (TA + TB) / (2.0 * Phi_safe)
    return base * g_chi_multiplicative(chi, k=k)

def equilibrium_score_field_chi_denominator(TA, TB, Phi, chi, eps=1e-12, k=0.25):
    """
    Alternative coupling:
        Es = (TA+TB) / (2 * Phi * (1 + k*chi))
    Similar effect but pushes coupling into the "scale" structure.
    """
    Phi_safe = np.maximum(Phi, eps)
    return (TA + TB) / (2.0 * Phi_safe * (1.0 + k * chi))

def theta_from_probe(Es_field):
    """
    Mean-probe -> theta in [0,2pi).
    """
    Es_bar = float(Es_field.mean())
    frac = Es_bar % 1.0
    theta = float(2.0 * np.pi * frac)
    return theta, Es_bar