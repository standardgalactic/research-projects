# ============================================================
# operators/cosmology.py
# ------------------------------------------------------------
# Cosmological extension operators for RSVP.
#
# Models the RSVP field on an expanding background by
# introducing a scale factor a(t) and Hubble drag.  Also
# includes a two-manifold coupling module and extractive
# economic field dynamics.
#
# Modules
# -------
#   hubble_expand          — update scale factor a(t)
#   evolve_cosmological    — full RSVP step with expansion
#   CosmologicalHistory    — records a(t) and structure metrics
#   evolve_coupled         — two-manifold synchrony step
#   EconomicField          — capital / labour / precarity system
#   double_well_force      — soliton-supporting potential
#
# Author: Flyxion
# ============================================================

import numpy as np
from scipy.ndimage import gaussian_filter
from operators.rsvp import (
    gradient, divergence, laplacian, curl,
    ALPHA, BETA, GAMMA, DELTA, ETA
)
from operators.topology import gini, synchrony


# ============================================================
# Hubble expansion
# ============================================================

def hubble_expand(a, H0=0.003, dt=0.05):
    """
    Advance the scale factor by one time step.

        da/dt = H0 · a   →   a(t+dt) ≈ a + dt · H0 · a

    For de Sitter expansion H0 > 0.  Set H0 = 0 for a
    static (Minkowski) background.

    Parameters
    ----------
    a  : float — current scale factor (a₀ = 1)
    H0 : float — Hubble-like constant (simulation units)
    dt : float — time step

    Returns
    -------
    float — updated scale factor
    """
    return a + dt * H0 * a


def evolve_cosmological(phi, vx, vy, S, R, a,
                        dt=0.05, H0=0.003,
                        alpha=ALPHA, beta=BETA, gamma=GAMMA,
                        delta=DELTA, eta=ETA,
                        clio_fn=None):
    """
    RSVP evolution step on an expanding background.

    Physical gradients are rescaled by 1/a, implementing the
    standard comoving → physical coordinate transformation.
    The vector field acquires a Hubble drag term −H0 · v.

    Equations
    ---------
    ∂ₜvx = γ (∂ₓΦ)/a − H0 vx − β (∂ₓS)/a
    ∂ₜvy = γ (∂yΦ)/a − H0 vy − β (∂yS)/a
    ∂ₜΦ  = α/a² · ∇²Φ − v·∇Φ/a − 0.02 S + 0.01 R
    ∂ₜS  = (entropy production terms)

    Parameters
    ----------
    a      : float — current scale factor
    H0     : float — Hubble constant

    Returns
    -------
    phi, vx, vy, S, R, a_new
    """
    a_new = hubble_expand(a, H0=H0, dt=dt)
    inv_a = 1.0 / a

    gx, gy   = gradient(phi)
    gSx, gSy = gradient(S)

    gx  *= inv_a;  gy  *= inv_a
    gSx *= inv_a;  gSy *= inv_a

    # Hubble drag
    vx = vx + dt * (gamma * gx - H0 * vx - beta * gSx)
    vy = vy + dt * (gamma * gy - H0 * vy - beta * gSy)

    torsion = curl(vx, vy)
    R       = R + dt * (delta * torsion - 0.01 * R)

    advect = vx * gx + vy * gy
    phi    = phi + dt * (
        alpha * inv_a**2 * laplacian(phi)
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

    return phi, vx, vy, S, R, a_new


# ============================================================
# Cosmological history recorder
# ============================================================

class CosmologicalHistory:
    """
    Records the evolution of the scale factor and key field
    statistics during a cosmological RSVP simulation.

    Usage
    -----
    hist = CosmologicalHistory()
    for step in range(N):
        phi, vx, vy, S, R, a = evolve_cosmological(...)
        if step % 10 == 0:
            hist.record(a, phi, S)

    Then call hist.summary() or plot hist.scale_factors etc.
    """

    def __init__(self):
        self.scale_factors  = []
        self.phi_std        = []
        self.entropy_mean   = []
        self.log_a          = []

    def record(self, a, phi, S):
        self.scale_factors.append(float(a))
        self.phi_std.append(float(np.std(phi)))
        self.entropy_mean.append(float(np.mean(S)))
        self.log_a.append(float(np.log(a)))

    def horizon_crossing_frame(self, threshold=2.0):
        """
        Return the first frame at which a(t) exceeds threshold.
        Returns None if never crossed.
        """
        for i, a in enumerate(self.scale_factors):
            if a >= threshold:
                return i
        return None

    def summary(self):
        n = len(self.scale_factors)
        print(f"Frames recorded : {n}")
        if n:
            print(f"Scale factor    : {self.scale_factors[0]:.3f} → {self.scale_factors[-1]:.3f}")
            print(f"σ(Φ) change     : {self.phi_std[0]:.4f} → {self.phi_std[-1]:.4f}")
            hf = self.horizon_crossing_frame()
            print(f"Horizon crossing: frame {hf}" if hf else "Horizon crossing: not reached")


# ============================================================
# Coupled manifold evolution
# ============================================================

def evolve_coupled(phi1, vx1, vy1, S1, R1,
                   phi2, vx2, vy2, S2, R2,
                   dt=0.05, eps=0.04,
                   clio_fn=None):
    """
    Advance two RSVP manifolds M₁ and M₂ with weak
    inter-manifold coupling ε(Φ_other − Φ_self).

    The coupling injects an additional force into each
    manifold's scalar field proportional to the difference,
    driving synchronisation when ε > 0.

    Parameters
    ----------
    phi1…R1  : fields of manifold 1
    phi2…R2  : fields of manifold 2
    eps      : float — coupling strength (0 = independent)

    Returns
    -------
    (phi1, vx1, vy1, S1, R1), (phi2, vx2, vy2, S2, R2), C
    where C is the instantaneous Pearson synchrony.
    """
    from operators.rsvp import evolve

    coupling1 = eps * (phi2 - phi1)
    coupling2 = eps * (phi1 - phi2)

    phi1, vx1, vy1, S1, R1 = evolve(
        phi1 + dt * coupling1, vx1, vy1, S1, R1,
        dt=dt, clio_fn=clio_fn
    )
    phi2, vx2, vy2, S2, R2 = evolve(
        phi2 + dt * coupling2, vx2, vy2, S2, R2,
        dt=dt, clio_fn=clio_fn
    )

    C = synchrony(phi1, phi2)
    return (phi1, vx1, vy1, S1, R1), (phi2, vx2, vy2, S2, R2), C


# ============================================================
# Extractive economic field
# ============================================================

class EconomicField:
    """
    Two-class extractive economy modelled as coupled fields:

        K(x,t) — capital  (self-concentrating)
        L(x,t) — labour   (depleted by extraction)
        P(x,t) — precarity (analogous to entropy S)

    Parameters
    ----------
    H, W        : int — grid dimensions
    extract     : float — extraction rate  K ← L
    accum       : float — self-reinforcing accumulation
    precarity   : float — precarity generation from extraction
    reg         : float — regulatory repair pressure (CLIO strength)
    seed        : int   — RNG seed
    """

    def __init__(self, H, W,
                 extract=0.08, accum=0.12,
                 precarity=0.06, reg=0.03,
                 seed=7):
        rng       = np.random.default_rng(seed)
        self.H, self.W = H, W
        self.K    = gaussian_filter(rng.random((H, W)) * 0.3 + 0.1, sigma=8)
        self.L    = np.clip(1.0 - self.K + rng.random((H, W)) * 0.05, 0, None)
        self.P    = gaussian_filter(rng.random((H, W)) * 0.1, sigma=3)

        self.extract   = extract
        self.accum     = accum
        self.precarity = precarity
        self.reg       = reg

        self.gini_history   = []
        self.labour_history = []

    def step(self, dt=0.05):
        """Advance the economic system by one time step."""
        K, L, P = self.K, self.L, self.P

        gx_K, gy_K = gradient(K)

        # Capital accumulation + extraction
        K = K + dt * (
            self.accum * laplacian(K)
            + 0.05 * K * (gx_K**2 + gy_K**2)
            - self.extract * L * K
        )

        # Labour depletion + logistic replenishment
        L = L + dt * (
            0.04 * laplacian(L)
            - self.extract * K * L
            + 0.02 * (1.0 - L)
        )

        # Precarity dynamics
        P = P + dt * (
            self.precarity * K * (1.0 - L)
            - 0.05 * P
            + 0.01 * laplacian(P)
        )

        # Regulatory CLIO on K
        tension_K    = np.abs(gx_K) + np.abs(gy_K)
        reg_mask     = tension_K > np.percentile(tension_K, 80)
        smoothed_K   = gaussian_filter(K, sigma=1.5)
        K[reg_mask]  = (
            (1.0 - self.reg) * K[reg_mask]
            + self.reg        * smoothed_K[reg_mask]
        )

        self.K = np.clip(K, 0, None)
        self.L = np.clip(L, 0, None)
        self.P = P

    def record(self):
        """Append current Gini(K) and mean(L) to history."""
        self.gini_history.append(gini(self.K))
        self.labour_history.append(float(np.mean(self.L)))

    def run(self, steps=600, record_every=20, dt=0.05):
        """
        Run the simulation for `steps` steps, recording
        statistics every `record_every` steps.

        Returns
        -------
        list of K snapshots at recording times.
        """
        snapshots = []
        for step in range(steps):
            self.step(dt=dt)
            if step % record_every == 0:
                self.record()
                snapshots.append(self.K.copy())
        return snapshots

    def summary(self):
        if self.gini_history:
            print(f"Gini K : {self.gini_history[0]:.4f} → {self.gini_history[-1]:.4f}")
            print(f"⟨L⟩    : {self.labour_history[0]:.4f} → {self.labour_history[-1]:.4f}")


# ============================================================
# Soliton potential
# ============================================================

def double_well_force(phi, mu=0.18):
    """
    Restoring force from the double-well potential
        V(Φ) = μ (Φ² − 1)²

    dV/dΦ = 4μ Φ (Φ² − 1)

    The equation of motion includes −dV/dΦ, so the force
    returned here is  +4μ Φ (Φ² − 1)  with a sign flip
    for use as ∂ₜΦ ⊃ −dV/dΦ = −4μ Φ (Φ² − 1).

    The function returns the force term with the correct sign
    (negative), ready to be added to ∂ₜΦ.
    """
    return -4.0 * mu * phi * (phi**2 - 1.0)
