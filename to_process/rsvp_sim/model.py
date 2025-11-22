import numpy as np
from dataclasses import dataclass

from .operators import (
    laplacian_1d, grad_1d, advect_1d,
    laplacian_2d, grad_2d, advect_2d,
)

@dataclass
class RSVPParams:
    kappa: float = 0.01     # diffusion of Phi
    lam: float = 0.1        # entropy source into Phi
    nu: float = 0.01        # viscosity for v
    alpha: float = 0.1      # semantic forcing on v
    Ds: float = 0.01        # entropy diffusion
    beta: float = 0.1       # advection of S
    gamma: float = 0.1      # prediction-error sink
    phi_star: float = 0.0   # target Phi* (can be field in advanced models)


def rsvp_rhs_1d(phi, v, S, grid, params: RSVPParams):
    """Right-hand side of RSVP PDEs in 1D.

    Returns dphi/dt, dv/dt, dS/dt.
    """
    dx = grid.dx

    # Phi equation: ∂t Φ = κ ΔΦ - ∇·(Φ v) + λ S
    lap_phi = laplacian_1d(phi, dx)
    div_phiv = advect_1d(phi, v, dx)
    dphi_dt = params.kappa * lap_phi - div_phiv + params.lam * S

    # v equation: ∂t v = -∂x S + ν Δv + α ∂x Φ - v ∂x v
    dS_dx = grad_1d(S, dx)
    lap_v = laplacian_1d(v, dx)
    dphi_dx = grad_1d(phi, dx)
    dv_dx = grad_1d(v, dx)
    dv_dt = -dS_dx + params.nu * lap_v + params.alpha * dphi_dx - v * dv_dx

    # S equation: ∂t S = Ds ΔS - β v ∂x S - γ (Φ - Φ*)
    lap_S = laplacian_1d(S, dx)
    dS_dt = params.Ds * lap_S - params.beta * v * dS_dx - params.gamma * (phi - params.phi_star)

    return dphi_dt, dv_dt, dS_dt


def step_rsvp_1d(phi, v, S, grid, params: RSVPParams, dt: float):
    """Single explicit Euler step for RSVP 1D system."""
    dphi_dt, dv_dt, dS_dt = rsvp_rhs_1d(phi, v, S, grid, params)
    phi_new = phi + dt * dphi_dt
    v_new = v + dt * dv_dt
    S_new = S + dt * dS_dt
    return phi_new, v_new, S_new


def rsvp_rhs_2d(phi, vx, vy, S, grid, params: RSVPParams):
    """Right-hand side of RSVP PDEs in 2D.

    Here v is represented as (vx, vy).
    Returns dphi/dt, dvx/dt, dvy/dt, dS/dt.
    """
    dx = grid.dx
    dy = grid.dy

    # Phi equation: ∂t Φ = κ ΔΦ - ∇·(Φ v) + λ S
    lap_phi = laplacian_2d(phi, dx, dy)
    div_phiv = advect_2d(phi, vx, vy, dx, dy)
    dphi_dt = params.kappa * lap_phi - div_phiv + params.lam * S

    # v equation (component-wise):
    # ∂t v = -∇S + ν Δv + α ∇Φ - (v·∇)v
    dS_dx, dS_dy = grad_2d(S, dx, dy)
    lap_vx = laplacian_2d(vx, dx, dy)
    lap_vy = laplacian_2d(vy, dx, dy)
    dphi_dx, dphi_dy = grad_2d(phi, dx, dy)

    # velocity gradients for convective term
    dvx_dx, dvx_dy = grad_2d(vx, dx, dy)
    dvy_dx, dvy_dy = grad_2d(vy, dx, dy)
    vdotgrad_vx = vx * dvx_dx + vy * dvx_dy
    vdotgrad_vy = vx * dvy_dx + vy * dvy_dy

    dvx_dt = -dS_dx + params.nu * lap_vx + params.alpha * dphi_dx - vdotgrad_vx
    dvy_dt = -dS_dy + params.nu * lap_vy + params.alpha * dphi_dy - vdotgrad_vy

    # S equation: ∂t S = Ds ΔS - β v·∇S - γ (Φ - Φ*)
    lap_S = laplacian_2d(S, dx, dy)
    vdotgrad_S = vx * dS_dx + vy * dS_dy
    dS_dt = params.Ds * lap_S - params.beta * vdotgrad_S - params.gamma * (phi - params.phi_star)

    return dphi_dt, dvx_dt, dvy_dt, dS_dt


def step_rsvp_2d(phi, vx, vy, S, grid, params: RSVPParams, dt: float):
    """Single explicit Euler step for RSVP 2D system."""
    dphi_dt, dvx_dt, dvy_dt, dS_dt = rsvp_rhs_2d(phi, vx, vy, S, grid, params)
    phi_new = phi + dt * dphi_dt
    vx_new = vx + dt * dvx_dt
    vy_new = vy + dt * dvy_dt
    S_new = S + dt * dS_dt
    return phi_new, vx_new, vy_new, S_new
