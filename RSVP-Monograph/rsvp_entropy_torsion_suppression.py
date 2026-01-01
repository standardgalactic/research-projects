#!/usr/bin/env python3
"""
Torsion-suppressed entropy production (stabilized).

Key changes:
- gradient and vorticity clipping BEFORE squaring
- NaN / inf protection
- stronger high-torsion suppression (physical + stable)
"""

import numpy as np

def roll(a, s, ax):
    return np.roll(a, s, axis=ax)

def grad_x(f, dx):
    return (roll(f, -1, 1) - roll(f, 1, 1)) / (2.0 * dx)

def grad_y(f, dy):
    return (roll(f, -1, 0) - roll(f, 1, 0)) / (2.0 * dy)

def curl_z(vx, vy, dx, dy):
    return grad_x(vy, dx) - grad_y(vx, dy)

def torsion_suppression_factor(vx, vy, dx, dy, alpha=1.0, omega_max=20.0):
    """
    Suppression factor Gamma = 1 / (1 + alpha * omega^2)

    omega is clipped BEFORE squaring to prevent overflow.
    """
    omega = curl_z(vx, vy, dx, dy)

    # numerical safety
    omega = np.nan_to_num(omega, nan=0.0, posinf=omega_max, neginf=-omega_max)
    omega = np.clip(omega, -omega_max, omega_max)

    Gamma = 1.0 / (1.0 + alpha * omega * omega)
    return Gamma, omega

def suppressed_entropy_production(
    TA, TB, vx, vy, dx, dy,
    sigma0=0.01,
    beta_gradT=0.02,
    alpha_omega=1.0,
    gradT_max=50.0
):
    """
    Entropy production:
        σ = (σ0 + β |∇(TA − TB)|²) · Γ(ω)

    with torsion-based suppression Γ.

    gradT is clipped BEFORE squaring.
    """

    # temperature difference
    dT = TA - TB
    dT = np.nan_to_num(dT, nan=0.0, posinf=0.0, neginf=0.0)

    dTx = grad_x(dT, dx)
    dTy = grad_y(dT, dy)

    # clip gradients BEFORE squaring
    dTx = np.clip(dTx, -gradT_max, gradT_max)
    dTy = np.clip(dTy, -gradT_max, gradT_max)

    gradT2 = dTx*dTx + dTy*dTy

    # torsion suppression
    Gamma, omega = torsion_suppression_factor(
        vx, vy, dx, dy,
        alpha=alpha_omega
    )

    production = (sigma0 + beta_gradT * gradT2) * Gamma

    # final numerical cleanup
    production = np.nan_to_num(
        production,
        nan=0.0,
        posinf=sigma0 + beta_gradT * gradT_max**2,
        neginf=0.0
    )

    return production, Gamma, omega
