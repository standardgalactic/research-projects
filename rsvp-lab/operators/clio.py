# ============================================================
# operators/clio.py
# ------------------------------------------------------------
# CLIO — Constraint-Local Integrity Operator
#
# CLIO is the repair layer of the RSVP framework.  It acts
# on high-tension regions of the scalar field Φ and the
# entropy field S to restore local compatibility.
#
# Variants included
# -----------------
#   clio_standard    — gradient-tension-based smoothing
#   clio_regulatory  — anisotropic repair biased toward
#                      low-entropy seed regions
#   clio_sheaf       — patch-gluing obstruction repair
#   clio_identity    — identity-gap restoring force
#   clio_economic    — extractive-economy regulator
#
# All variants share the same call signature:
#     phi_new, S_new = clio_*(phi, S, **kwargs)
#
# Author: Flyxion
# ============================================================

import numpy as np
from scipy.ndimage import gaussian_filter

from operators.rsvp import gradient, laplacian


# ============================================================
# Standard CLIO
# ============================================================

def clio_standard(phi, S,
                  lambda_repair=0.15,
                  smooth_sigma=1.2,
                  tension_pct=85,
                  entropy_damping=0.97):
    """
    Identify high-gradient (high-tension) cells and blend them
    toward a locally smoothed version of Φ.  Entropy in the
    same cells is slightly damped, reflecting the cost of
    constraint enforcement.

    Parameters
    ----------
    lambda_repair   : float — interpolation weight toward smooth
    smooth_sigma    : float — Gaussian blur radius for target
    tension_pct     : float — percentile threshold for repair mask
    entropy_damping : float — multiplicative entropy reduction
                              in repaired cells (< 1)
    """
    gx, gy      = gradient(phi)
    tension     = np.abs(gx) + np.abs(gy)
    repair_mask = tension > np.percentile(tension, tension_pct)

    repaired         = gaussian_filter(phi, sigma=smooth_sigma)
    phi[repair_mask] = (
        (1.0 - lambda_repair) * phi[repair_mask]
        + lambda_repair        * repaired[repair_mask]
    )
    S[repair_mask] *= entropy_damping
    return phi, S


# ============================================================
# Regulatory CLIO  (anisotropic, seed-biased)
# ============================================================

def clio_regulatory(phi, S,
                    lambda_repair=0.20,
                    smooth_sigma=2.0,
                    tension_pct=80,
                    seed_entropy_pct=30):
    """
    A stricter variant that repairs toward a seed region
    defined by the lowest-entropy cells.  Mimics a regulatory
    process that restores high-tension zones to a reference
    "low-precarity" baseline rather than just blurring.

    seed_entropy_pct : float — percentile below which S is
                                considered a seed / baseline
    """
    gx, gy      = gradient(phi)
    tension     = np.abs(gx) + np.abs(gy)
    repair_mask = tension > np.percentile(tension, tension_pct)
    seed_mask   = S < np.percentile(S, seed_entropy_pct)

    # Target: mean of seed cells (scalar reference)
    seed_target = np.mean(phi[seed_mask]) if seed_mask.any() else 0.0

    smoothed         = gaussian_filter(phi, sigma=smooth_sigma)
    # Blend toward seed_target-weighted smoothed field
    target           = 0.5 * smoothed + 0.5 * seed_target
    phi[repair_mask] = (
        (1.0 - lambda_repair) * phi[repair_mask]
        + lambda_repair        * target if np.isscalar(target)
        else (1.0 - lambda_repair) * phi[repair_mask]
             + lambda_repair        * target[repair_mask]
    )
    S[repair_mask] *= 0.95
    return phi, S


# ============================================================
# Sheaf CLIO  (patch-gluing repair)
# ============================================================

def clio_sheaf(phi, S,
               patch=32, overlap=8,
               lambda_repair=0.10):
    """
    Compute the gluing obstruction cocycle across overlapping
    patches and apply a repair proportional to the local
    mismatch.  This drives the field toward a globally
    consistent section of the sheaf of local data.

    The repair term is:
        Δφ(x,y) = −λ · (φ(x,y) − mean_of_overlapping_neighbours)

    Only cells whose local gluing error exceeds the 75th
    percentile receive the correction.
    """
    H_, W_ = phi.shape
    stride = patch - overlap
    error_field = np.zeros_like(phi)
    count_field = np.zeros_like(phi)

    for y in range(0, H_ - patch + 1, stride):
        for x in range(0, W_ - patch + 1, stride):
            tile = phi[y:y+patch, x:x+patch]

            # Right neighbour
            xr = x + stride
            if xr + patch <= W_:
                nb = phi[y:y+patch, xr:xr+patch]
                diff = tile[:, -overlap:] - nb[:, :overlap]
                error_field[y:y+patch, x+patch-overlap:x+patch] += np.abs(diff)
                count_field[y:y+patch, x+patch-overlap:x+patch] += 1

            # Bottom neighbour
            yb = y + stride
            if yb + patch <= H_:
                nb = phi[yb:yb+patch, x:x+patch]
                diff = tile[-overlap:, :] - nb[:overlap, :]
                error_field[y+patch-overlap:y+patch, x:x+patch] += np.abs(diff)
                count_field[y+patch-overlap:y+patch, x:x+patch] += 1

    # Normalise
    count_field = np.where(count_field > 0, count_field, 1)
    error_field /= count_field

    repair_mask = error_field > np.percentile(error_field, 75)
    smoothed    = gaussian_filter(phi, sigma=1.5)
    phi[repair_mask] = (
        (1.0 - lambda_repair) * phi[repair_mask]
        + lambda_repair        * smoothed[repair_mask]
    )
    # Entropy cost proportional to gluing error
    S[repair_mask] += 0.01 * error_field[repair_mask]
    S = np.clip(S, 0, None)
    return phi, S


# ============================================================
# Identity CLIO  (self-consistency constraint)
# ============================================================

def clio_identity(phi, S,
                  lambda_id=0.06,
                  tile_size=16):
    """
    Penalise deviation from the coarse-grained identity
    surface  {Φ : Φ = F(Φ)}  where F is the tile-mean map.

    Implements:
        ∂ₜΦ ⊃ −λ_id · (Φ − F(Φ))

    Applied as a one-step Euler correction inside CLIO so it
    can be composed with any evolution scheme.
    """
    # Import here to avoid circular dependency
    from operators.rsvp import coarse_grain
    F_phi = coarse_grain(phi, tile_size=tile_size)
    gap   = phi - F_phi
    phi   = phi - lambda_id * gap
    # Identity violation slightly raises entropy
    S     = S + 0.005 * np.abs(gap)
    return phi, S


# ============================================================
# Economic CLIO  (capital-field regulator)
# ============================================================

def clio_economic(K, S_econ,
                  reg_strength=0.03,
                  smooth_sigma=1.5,
                  tension_pct=80):
    """
    Regulatory repair for the extractive-economy field K.

    High spatial-gradient regions of K (capital concentration
    fronts) are smoothed toward their neighbourhood average,
    mimicking redistribution or antitrust intervention.
    The precarity field S_econ is slightly reduced in repaired
    cells as a consequence of regulatory stabilisation.

    Note: uses the same call signature (field, entropy) as
    other CLIO variants so it can slot into generic loops.
    """
    gx, gy      = gradient(K)
    tension     = np.abs(gx) + np.abs(gy)
    repair_mask = tension > np.percentile(tension, tension_pct)

    smoothed        = gaussian_filter(K, sigma=smooth_sigma)
    K[repair_mask]  = (
        (1.0 - reg_strength) * K[repair_mask]
        + reg_strength        * smoothed[repair_mask]
    )
    S_econ[repair_mask] *= 0.96
    K = np.clip(K, 0, None)
    return K, S_econ


# ============================================================
# Factory / selector
# ============================================================

CLIO_VARIANTS = {
    "standard":   clio_standard,
    "regulatory": clio_regulatory,
    "sheaf":      clio_sheaf,
    "identity":   clio_identity,
    "economic":   clio_economic,
}


def get_clio(name="standard", **kwargs):
    """
    Return a CLIO callable with kwargs pre-bound via closure.

    Usage
    -----
    clio_fn = get_clio("sheaf", patch=32, overlap=8, lambda_repair=0.12)
    phi, S  = clio_fn(phi, S)
    """
    if name not in CLIO_VARIANTS:
        raise ValueError(
            f"Unknown CLIO variant '{name}'. "
            f"Choose from: {list(CLIO_VARIANTS)}"
        )
    base = CLIO_VARIANTS[name]

    def _clio(phi, S):
        return base(phi, S, **kwargs)

    _clio.__name__ = f"clio_{name}"
    return _clio
