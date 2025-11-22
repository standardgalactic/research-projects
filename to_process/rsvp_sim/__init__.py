"""RSVP simulation suite: PDE core, grids, integrators, and diagnostics.

This package implements a minimal but extensible numerical backend for
the RSVP PDE system described in Appendix A:

    ∂t Φ = κ ΔΦ - ∇·(Φ v) + λ S
    ∂t v = -∇S + ν Δv + α ∇Φ - (v·∇)v
    ∂t S = D_S ΔS - β v·∇S - γ (Φ - Φ*)

The implementation is intentionally simple and pedagogical, not optimised.
"""

from .grids import Grid1D, Grid2D
from .operators import laplacian_1d, grad_1d, advect_1d, laplacian_2d, grad_2d, advect_2d
from .model import RSVPParams, rsvp_rhs_1d, rsvp_rhs_2d, step_rsvp_1d, step_rsvp_2d
from .diagnostics import energy_1d, energy_2d, entropy_1d, entropy_2d
