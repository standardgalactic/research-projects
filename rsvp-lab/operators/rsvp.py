# ============================================================
# operators/rsvp.py
# ------------------------------------------------------------
# Core RSVP field dynamics:
#   Φ  — scalar plenum field
#   v  — vector field (vx, vy)
#   S  — entropy field
#   R  — torsion-memory residue field
#
# All operators are purely functional: they accept field
# arrays and return updated arrays.  No global state.
#
# Author: Flyxion
# ============================================================

import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.fft import fft2, ifft2, fftfreq


# ── Coupling constants (can be overridden by callers) ──────
ALPHA       = 0.12   # scalar diffusion
BETA        = 0.08   # entropy ↔ vector coupling
GAMMA       = 0.10   # vector alignment with ∇Φ
DELTA       = 0.03   # torsion memory accumulation
ETA         = 0.05   # entropy decay rate


# ============================================================
# Differential operators  (periodic boundary via np.roll)
# ============================================================

def gradient(field):
    """Central-difference gradient → (gx, gy)."""
    gx = (np.roll(field, -1, axis=1) - np.roll(field, 1, axis=1)) * 0.5
    gy = (np.roll(field, -1, axis=0) - np.roll(field, 1, axis=0)) * 0.5
    return gx, gy


def divergence(vx, vy):
    """Central-difference divergence of a 2-D vector field."""
    dx = (np.roll(vx, -1, axis=1) - np.roll(vx, 1, axis=1)) * 0.5
    dy = (np.roll(vy, -1, axis=0) - np.roll(vy, 1, axis=0)) * 0.5
    return dx + dy


def laplacian(field):
    """5-point stencil Laplacian with periodic BCs."""
    return (
        np.roll(field,  1, axis=0) + np.roll(field, -1, axis=0)
      + np.roll(field,  1, axis=1) + np.roll(field, -1, axis=1)
      - 4.0 * field
    )


def curl(vx, vy):
    """Scalar curl  ω = ∂vy/∂x − ∂vx/∂y  (vorticity / torsion)."""
    dvy_dx = (np.roll(vy, -1, axis=1) - np.roll(vy, 1, axis=1)) * 0.5
    dvx_dy = (np.roll(vx, -1, axis=0) - np.roll(vx, 1, axis=0)) * 0.5
    return dvy_dx - dvx_dy


def fractional_laplacian(field, alpha_frac=0.75):
    """
    Spectral fractional Laplacian  (−∇²)^alpha_frac.

    alpha_frac = 1.0  → ordinary Laplacian (up to sign convention)
    alpha_frac < 1.0  → sub-diffusive / Lévy long-range
    alpha_frac > 1.0  → hyper-diffusive, fine-structure suppression
    """
    H_, W_   = field.shape
    F        = fft2(field)
    kx       = fftfreq(W_, d=1.0 / (2 * np.pi))
    ky       = fftfreq(H_, d=1.0 / (2 * np.pi))
    KX, KY   = np.meshgrid(kx, ky)
    K2       = KX**2 + KY**2
    K2[0, 0] = 1.0          # regularise zero mode
    F_frac   = F * (K2 ** alpha_frac)
    F_frac[0, 0] = 0.0
    return np.real(ifft2(F_frac))


# ============================================================
# Field initialisation helpers
# ============================================================

def init_fields(H, W, seed=42):
    """
    Return a clean set of initial RSVP fields:
        phi, vx, vy, S, R
    Seeded for reproducibility.
    """
    rng = np.random.default_rng(seed)
    phi = gaussian_filter(rng.random((H, W)), sigma=6)
    S   = gaussian_filter(rng.random((H, W)), sigma=3)
    vx  = rng.standard_normal((H, W)) * 0.02
    vy  = rng.standard_normal((H, W)) * 0.02
    R   = np.zeros((H, W))
    return phi, vx, vy, S, R


def inject_kink(field, cx, cy, sign=1, width=5):
    """
    Inject a tanh kink soliton centred at (cx, cy).

    Parameters
    ----------
    field : 2-D array  — scalar field to modify in-place
    cx, cy : float     — centre coordinates (pixel units)
    sign   : ±1        — polarity of the kink
    width  : float     — characteristic width (pixels)

    Returns
    -------
    Modified field (also mutated in place).
    """
    H_, W_ = field.shape
    xs = np.arange(W_) - cx
    ys = np.arange(H_)[:, None] - cy
    r  = np.sqrt(xs**2 + ys**2)
    field += sign * np.tanh(r / width)
    return field


# ============================================================
# Core evolution step
# ============================================================

def evolve(phi, vx, vy, S, R,
           dt=0.05,
           alpha=ALPHA, beta=BETA, gamma=GAMMA,
           delta=DELTA, eta=ETA,
           clio_fn=None,
           extra_phi_force=None):
    """
    Advance the RSVP fields by one time step dt.

    Equations
    ---------
    ∂ₜvx = γ ∂ₓΦ − β ∂ₓS
    ∂ₜvy = γ ∂yΦ − β ∂yS
    ∂ₜR  = δ ω − 0.01 R
    ∂ₜΦ  = α ∇²Φ − v·∇Φ − 0.02 S + 0.01 R  [+ extra_phi_force]
    ∂ₜS  = 0.03|∇·v| + 0.02 ω² − η S + 0.01 ∇²S

    Parameters
    ----------
    clio_fn : callable or None
        If provided, called as  phi, S = clio_fn(phi, S)
        after the standard update.  Allows plugging in any
        CLIO variant (standard, economic, regulatory…).

    extra_phi_force : 2-D array or None
        Additional term added to ∂ₜΦ, e.g. double-well
        potential, semantic restoring force, or identity gap.

    Returns
    -------
    phi, vx, vy, S, R  — updated field arrays
    """
    gx, gy   = gradient(phi)
    gSx, gSy = gradient(S)

    vx = vx + dt * (gamma * gx - beta * gSx)
    vy = vy + dt * (gamma * gy - beta * gSy)

    torsion = curl(vx, vy)
    R       = R + dt * (delta * torsion - 0.01 * R)

    advect = vx * gx + vy * gy
    dphi   = alpha * laplacian(phi) - advect - 0.02 * S + 0.01 * R
    if extra_phi_force is not None:
        dphi = dphi + extra_phi_force
    phi = phi + dt * dphi

    div_v = divergence(vx, vy)
    S     = S + dt * (
        0.03 * np.abs(div_v)
        + 0.02 * torsion**2
        - eta * S
        + 0.01 * laplacian(S)
    )

    if clio_fn is not None:
        phi, S = clio_fn(phi, S)

    return phi, vx, vy, S, R


def evolve_fractional(phi, vx, vy, S, R,
                      dt=0.05, alpha_frac=0.75,
                      alpha=ALPHA, beta=BETA, gamma=GAMMA,
                      delta=DELTA, eta=ETA,
                      clio_fn=None):
    """
    Like evolve() but replaces the standard Laplacian with
    the fractional operator (−∇²)^alpha_frac, enabling
    Lévy-type (alpha_frac < 1) or hyper-diffusive
    (alpha_frac > 1) regimes.
    """
    gx, gy   = gradient(phi)
    gSx, gSy = gradient(S)

    vx = vx + dt * (gamma * gx - beta * gSx)
    vy = vy + dt * (gamma * gy - beta * gSy)

    torsion = curl(vx, vy)
    R       = R + dt * (delta * torsion - 0.01 * R)

    advect = vx * gx + vy * gy
    phi    = phi + dt * (
        -alpha * fractional_laplacian(phi, alpha_frac)
        - advect - 0.02 * S + 0.01 * R
    )

    div_v = divergence(vx, vy)
    S     = S + dt * (
        0.03 * np.abs(div_v)
        + 0.02 * torsion**2
        - eta * S
        + 0.01 * laplacian(S)
    )

    if clio_fn is not None:
        phi, S = clio_fn(phi, S)

    return phi, vx, vy, S, R


# ============================================================
# Admissibility
# ============================================================

def admissibility(phi, S, threshold=0.25, entropy_pct=70):
    """
    Return a float mask in [0,1]: 1 where the field satisfies
    RSVP admissibility:

        |∇Φ| < threshold   AND   S < percentile(S, entropy_pct)

    Admissible regions support well-defined trajectory closure.
    """
    gx, gy  = gradient(phi)
    tension = np.abs(gx) + np.abs(gy)
    mask    = (tension < threshold) & (S < np.percentile(S, entropy_pct))
    return mask.astype(float)


# ============================================================
# Phase metrics
# ============================================================

def field_metrics(phi, S, vx, vy):
    """Return a dict of scalar summary statistics for one frame."""
    torsion = curl(vx, vy)
    return {
        "phi_energy":      float(np.mean(phi**2)),
        "phi_std":         float(np.std(phi)),
        "entropy_mean":    float(np.mean(S)),
        "torsion_mean":    float(np.mean(np.abs(torsion))),
        "divergence":      float(np.mean(np.abs(divergence(vx, vy)))),
        "admissible_frac": float(np.mean(admissibility(phi, S))),
    }


# ============================================================
# Coarse-graining (used by identity-constraint experiment)
# ============================================================

def coarse_grain(field, tile_size=16):
    """
    Replace each (tile_size × tile_size) block with its mean.
    Returns a new array of the same shape.
    """
    out = field.copy()
    H_, W_ = field.shape
    for y in range(0, H_, tile_size):
        for x in range(0, W_, tile_size):
            tile = field[y:y+tile_size, x:x+tile_size]
            out[y:y+tile_size, x:x+tile_size] = np.mean(tile)
    return out
