# ============================================================
# operators/semantic.py
# ------------------------------------------------------------
# Semantic attractor field operators for RSVP.
#
# Treats discrete "tokens" (concepts, categories, labels) as
# point charges generating a Coulomb-like potential landscape.
# The RSVP vector field flows along this landscape, producing
# categorical basins.  CLIO damps inter-basin oscillation,
# implementing soft categorical commitment.
#
# Main API
# --------
#   SemanticField      — class encapsulating token set
#   semantic_potential — functional variant
#   basin_assignment   — Voronoi-style basin labelling
#   inter_basin_flux   — cross-basin information flow
#   observer_projection — line-of-sight projection
#   anisotropy_index   — scalar measure of field asymmetry
#
# Author: Flyxion
# ============================================================

import numpy as np
from scipy.ndimage import gaussian_filter
from operators.rsvp import gradient, curl, divergence, laplacian


# ============================================================
# Semantic potential (Coulomb-like)
# ============================================================

def semantic_potential(shape, positions, charges, epsilon=8.0):
    """
    Compute the regularised Coulomb potential

        V(x,y) = Σ_i q_i / (r_i + ε)

    Parameters
    ----------
    shape     : (H, W) — field grid dimensions
    positions : (N, 2) float array — token (x, y) coordinates
    charges   : (N,) float array  — signed token charges ±1
    epsilon   : float — regularisation radius (pixels)

    Returns
    -------
    V : (H, W) float array
    """
    H_, W_ = shape
    xs = np.arange(W_)[None, :]
    ys = np.arange(H_)[:, None]
    V  = np.zeros((H_, W_))
    for (px, py), q in zip(positions, charges):
        r  = np.sqrt((xs - px)**2 + (ys - py)**2)
        V += q / (r + epsilon)
    return V


def semantic_gradient_force(V, gamma_sem=0.25):
    """
    Return the (vx_force, vy_force) that the semantic
    potential exerts on the RSVP vector field.

        F = γ_sem · ∇V
    """
    gx, gy = gradient(V)
    return gamma_sem * gx, gamma_sem * gy


# ============================================================
# SemanticField class
# ============================================================

class SemanticField:
    """
    Encapsulates a set of named semantic attractors on a grid.

    Parameters
    ----------
    H, W    : int — grid dimensions
    n_tokens: int — number of attractors to place
    labels  : list[str] or None — token names; auto-generated if None
    seed    : int — RNG seed for random placement
    epsilon : float — Coulomb regularisation
    """

    def __init__(self, H, W, n_tokens=8, labels=None, seed=0, epsilon=8.0):
        self.H, self.W   = H, W
        self.n            = n_tokens
        self.epsilon      = epsilon
        rng               = np.random.default_rng(seed)
        self.positions    = rng.random((n_tokens, 2)) * np.array([W, H])
        self.charges      = rng.choice([-1.0, 1.0], size=n_tokens)
        if labels is None:
            self.labels   = [f"T{i}" for i in range(n_tokens)]
        else:
            self.labels   = list(labels)[:n_tokens]

        self.V            = semantic_potential(
            (H, W), self.positions, self.charges, epsilon
        )

    def potential(self):
        """Return the pre-computed potential array."""
        return self.V

    def force(self, gamma_sem=0.25):
        """Return (Fx, Fy) force arrays."""
        return semantic_gradient_force(self.V, gamma_sem)

    def basin_map(self):
        """
        Return an integer array assigning each cell to the
        index of the nearest token (Voronoi partition).
        """
        return basin_assignment(self.H, self.W, self.positions)

    def inter_basin_flux(self, phi):
        """
        Compute mean |∇Φ| along basin boundaries.
        High flux ↔ strong semantic tension at boundaries.
        """
        return inter_basin_flux(phi, self.basin_map())

    def attractor_entropy(self, phi):
        """
        For each basin, return the mean and variance of Φ
        within that basin.  High variance → weak commitment.
        """
        bmap   = self.basin_map()
        result = {}
        for i, lbl in enumerate(self.labels):
            mask        = bmap == i
            vals        = phi[mask]
            result[lbl] = {
                "mean": float(np.mean(vals)) if vals.size else 0.0,
                "var":  float(np.var(vals))  if vals.size else 0.0,
            }
        return result


# ============================================================
# Basin utilities
# ============================================================

def basin_assignment(H, W, positions):
    """
    Assign each pixel to the index of the nearest position.
    Returns an integer (H, W) array.
    """
    xs = np.arange(W)[None, :]
    ys = np.arange(H)[:, None]
    dists = np.stack([
        np.sqrt((xs - px)**2 + (ys - py)**2)
        for px, py in positions
    ], axis=0)
    return np.argmin(dists, axis=0)


def inter_basin_flux(phi, basin_map):
    """
    Mean gradient magnitude along basin boundaries.

    Basin boundaries are cells adjacent to a cell with a
    different basin label.
    """
    gx, gy    = gradient(phi)
    grad_mag  = np.sqrt(gx**2 + gy**2)

    # Boundary mask: any cell whose right or lower neighbour
    # is in a different basin
    right  = np.roll(basin_map, -1, axis=1)
    below  = np.roll(basin_map, -1, axis=0)
    boundary = (basin_map != right) | (basin_map != below)

    return float(np.mean(grad_mag[boundary])) if boundary.any() else 0.0


# ============================================================
# Observer projection
# ============================================================

def observer_projection(field, cx, cy, angle_deg, length=60):
    """
    Project field values along a ray from (cx, cy) at angle_deg.

    Parameters
    ----------
    field     : (H, W) array
    cx, cy    : float — ray origin (pixel coords)
    angle_deg : float — direction in degrees (0 = East)
    length    : int   — half-length of ray in pixels

    Returns
    -------
    ts      : 1-D array of arc positions (centred at 0)
    values  : 1-D array of projected field values
    """
    H_, W_ = field.shape
    theta  = np.radians(angle_deg)
    dx, dy = np.cos(theta), np.sin(theta)
    ts     = np.linspace(-length / 2, length / 2, length * 4)
    xs     = np.clip(cx + ts * dx, 0, W_ - 1).astype(int)
    ys     = np.clip(cy + ts * dy, 0, H_ - 1).astype(int)
    return ts, field[ys, xs]


def anisotropy_index(field, observers):
    """
    Compute σ/μ of mean projected entropy across observer set.

    Parameters
    ----------
    field     : (H, W) entropy field S
    observers : list of dicts with keys cx, cy, angle

    Returns
    -------
    float — anisotropy index (0 = isotropic)
    """
    means = []
    for obs in observers:
        _, vals = observer_projection(
            field, obs["cx"], obs["cy"], obs["angle"]
        )
        means.append(np.mean(vals))
    means = np.array(means)
    denom = np.mean(means) + 1e-9
    return float(np.std(means) / denom)


# ============================================================
# Semantic evolution step
# ============================================================

def evolve_semantic(phi, vx, vy, S, R,
                    sem_field,
                    dt=0.05,
                    gamma_sem=0.25,
                    beta=0.08, delta=0.03, eta=0.05,
                    alpha=0.12,
                    clio_fn=None):
    """
    RSVP evolution step with semantic attractor forcing.

    Identical to rsvp.evolve() except the vector field
    additionally responds to ∇V (the semantic potential).

    Parameters
    ----------
    sem_field : SemanticField instance or pre-computed V array
    gamma_sem : float — strength of semantic coupling
    """
    if isinstance(sem_field, SemanticField):
        Vgx, Vgy = sem_field.force(gamma_sem)
    else:
        Vgx, Vgy = semantic_gradient_force(sem_field, gamma_sem)

    from operators.rsvp import curl, divergence, laplacian, gradient

    gx, gy   = gradient(phi)
    gSx, gSy = gradient(S)

    vx = vx + dt * (Vgx - beta * gSx)
    vy = vy + dt * (Vgy - beta * gSy)

    torsion = curl(vx, vy)
    R       = R + dt * (delta * torsion - 0.01 * R)

    advect = vx * gx + vy * gy
    phi    = phi + dt * (alpha * laplacian(phi) - advect - 0.02 * S + 0.01 * R)

    div_v = divergence(vx, vy)
    S     = S + dt * (
        0.03 * np.abs(div_v) + 0.02 * torsion**2 - eta * S + 0.01 * laplacian(S)
    )

    if clio_fn is not None:
        phi, S = clio_fn(phi, S)

    return phi, vx, vy, S, R
