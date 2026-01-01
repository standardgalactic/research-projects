#!/usr/bin/env python3
"""
PDE lattice simulation -> equilibrium score -> phase stream theta(t)

2D periodic grid, explicit time stepping (stable for small dt).
Fields: TA, TB, Phi, S, vx, vy

Dependencies: numpy (only).
"""

import numpy as np

# -----------------------------
# Utilities: periodic FD ops
# -----------------------------

def roll(a, shift, axis):
    return np.roll(a, shift=shift, axis=axis)

def grad_x(f, dx):
    return (roll(f, -1, 1) - roll(f, 1, 1)) / (2.0 * dx)

def grad_y(f, dy):
    return (roll(f, -1, 0) - roll(f, 1, 0)) / (2.0 * dy)

def laplacian(f, dx, dy):
    return (roll(f, -1, 1) - 2*f + roll(f, 1, 1)) / (dx*dx) + \
           (roll(f, -1, 0) - 2*f + roll(f, 1, 0)) / (dy*dy)

def div(Fx, Fy, dx, dy):
    return (roll(Fx, -1, 1) - roll(Fx, 1, 1)) / (2.0*dx) + \
           (roll(Fy, -1, 0) - roll(Fy, 1, 0)) / (2.0*dy)

def advect_upwind(f, vx, vy, dx, dy):
    """
    First-order upwind advection: -v·∇f
    Periodic BCs via roll.
    """
    fx_fwd = (roll(f, -1, 1) - f) / dx
    fx_bwd = (f - roll(f, 1, 1)) / dx
    fy_fwd = (roll(f, -1, 0) - f) / dy
    fy_bwd = (f - roll(f, 1, 0)) / dy

    df_dx = np.where(vx >= 0, fx_bwd, fx_fwd)
    df_dy = np.where(vy >= 0, fy_bwd, fy_fwd)
    return -(vx * df_dx + vy * df_dy)

def curl_z(vx, vy, dx, dy):
    # 2D scalar vorticity: ∂x vy - ∂y vx
    dvy_dx = grad_x(vy, dx)
    dvx_dy = grad_y(vx, dy)
    return dvy_dx - dvx_dy


# -----------------------------
# Model parameters
# -----------------------------

class P:
    # grid / time
    nx = 96
    ny = 96
    Lx = 1.0
    Ly = 1.0
    dt = 2e-4
    steps = 4000

    # environment
    T_env = 300.0

    # diffusion
    kT = 8e-4
    kPhi = 6e-4
    kS = 8e-4
    kv = 1e-3

    # relaxation / coupling
    alphaA = 0.6
    alphaB = 0.5
    lamAB = 1.2

    # Phi forcing
    gammaPhi = 0.8
    etaPhi = 0.35

    # entropy
    sigma0 = 0.01
    betaT = 0.02
    betav = 0.03
    mu = 0.6

    # flow
    cPhi = 1.0
    cS = 0.8
    nu = 1.2   # linear damping


# -----------------------------
# Initialization
# -----------------------------

def init_fields(p: P, seed=0):
    rng = np.random.default_rng(seed)
    nx, ny = p.nx, p.ny

    # base temperatures + small noise
    TA = p.T_env + 3.0 * rng.normal(size=(ny, nx))
    TB = p.T_env + 3.0 * rng.normal(size=(ny, nx))

    # Phi near 1 with smooth bump
    y = np.linspace(0, 1, ny, endpoint=False)
    x = np.linspace(0, 1, nx, endpoint=False)
    X, Y = np.meshgrid(x, y)
    bump = np.exp(-((X-0.55)**2 + (Y-0.45)**2) / (2*(0.08**2)))
    Phi = 1.0 + 0.08 * bump + 0.01 * rng.normal(size=(ny, nx))

    # entropy small positive
    S = 0.05 + 0.02 * rng.random(size=(ny, nx))

    # initial flow: small vortical perturbation
    vx = 0.2*(Y-0.5) + 0.01*rng.normal(size=(ny, nx))
    vy = -0.2*(X-0.5) + 0.01*rng.normal(size=(ny, nx))

    # clamps
    Phi = np.maximum(Phi, 1e-6)
    S = np.maximum(S, 0.0)

    return TA, TB, Phi, S, vx, vy


# -----------------------------
# One timestep
# -----------------------------

def step(TA, TB, Phi, S, vx, vy, p: P, dx, dy):
    # --- Temperatures ---
    advTA = advect_upwind(TA, vx, vy, dx, dy)
    advTB = advect_upwind(TB, vx, vy, dx, dy)

    dTA = advTA + p.kT*laplacian(TA, dx, dy) \
          - p.alphaA*(TA - p.T_env) + p.lamAB*(TB - TA)

    dTB = advTB + p.kT*laplacian(TB, dx, dy) \
          - p.alphaB*(TB - p.T_env) + p.lamAB*(TA - TB)

    # --- Phi ---
    # conservative-ish transport: ∂t Phi + div(Phi v) = ...
    advPhi = -div(Phi*vx, Phi*vy, dx, dy)
    dPhi = advPhi + p.kPhi*laplacian(Phi, dx, dy) \
           - p.gammaPhi*(Phi - 1.0) - p.etaPhi*S

    # --- Entropy ---
    advS = -div(S*vx, S*vy, dx, dy)
    dTdiff_dx = grad_x(TA - TB, dx)
    dTdiff_dy = grad_y(TA - TB, dy)
    gradT2 = dTdiff_dx**2 + dTdiff_dy**2
    vort = curl_z(vx, vy, dx, dy)

    dS = advS + p.kS*laplacian(S, dx, dy) \
         + p.sigma0 + p.betaT*gradT2 + p.betav*(vort**2) \
         - p.mu*Phi*S

    # --- Flow ---
    # v_t + (v·∇)v = -∇(cPhi Phi + cS S) - nu v + kv Δv
    pressure = p.cPhi*Phi + p.cS*S
    px = grad_x(pressure, dx)
    py = grad_y(pressure, dy)

    advvx = advect_upwind(vx, vx, vy, dx, dy)  # -v·∇vx
    advvy = advect_upwind(vy, vx, vy, dx, dy)

    dvx = advvx - px - p.nu*vx + p.kv*laplacian(vx, dx, dy)
    dvy = advvy - py - p.nu*vy + p.kv*laplacian(vy, dx, dy)

    # explicit Euler update
    TA2  = TA  + p.dt*dTA
    TB2  = TB  + p.dt*dTB
    Phi2 = Phi + p.dt*dPhi
    S2   = S   + p.dt*dS
    vx2  = vx  + p.dt*dvx
    vy2  = vy  + p.dt*dvy

    # clamps for physicality
    Phi2 = np.maximum(Phi2, 1e-6)
    S2   = np.maximum(S2, 0.0)

    return TA2, TB2, Phi2, S2, vx2, vy2


# -----------------------------
# Equilibrium score -> phase
# -----------------------------

def equilibrium_score_field(TA, TB, Phi):
    return (TA + TB) / (2.0 * Phi)

def theta_from_probe(Es_field):
    Es_bar = float(Es_field.mean())         # probe = spatial mean
    frac = Es_bar % 1.0
    return float(2.0*np.pi*frac), Es_bar


# -----------------------------
# Run simulation
# -----------------------------

def run(seed=0):
    p = P()
    dx = p.Lx / p.nx
    dy = p.Ly / p.ny

    TA, TB, Phi, S, vx, vy = init_fields(p, seed=seed)

    thetas = np.zeros(p.steps+1, dtype=float)
    Esbars = np.zeros(p.steps+1, dtype=float)

    # initial
    Es = equilibrium_score_field(TA, TB, Phi)
    thetas[0], Esbars[0] = theta_from_probe(Es)

    for n in range(1, p.steps+1):
        TA, TB, Phi, S, vx, vy = step(TA, TB, Phi, S, vx, vy, p, dx, dy)
        Es = equilibrium_score_field(TA, TB, Phi)
        thetas[n], Esbars[n] = theta_from_probe(Es)

    return thetas, Esbars, (TA, TB, Phi, S, vx, vy)


if __name__ == "__main__":
    thetas, Esbars, final_fields = run(seed=1)
    print("theta[0], theta[-1] =", thetas[0], thetas[-1])
    print("Esbar[0], Esbar[-1] =", Esbars[0], Esbars[-1])