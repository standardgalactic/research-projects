#!/usr/bin/env python3
"""
rsvp_full_runner.py
-------------------
Full RSVP dynamical runner using ONLY imported modules.

Uses:
- torsion-driven flow
- irreversible history field chi
- chi-coupled equilibrium score
- torsion-suppressed entropy production
- entropy caps -> phase plateaus
- scalar -> RZ, vector -> RX/RY quantum mapping
"""

import numpy as np

# --- core PDE helpers (copied locally to avoid modifying other files) ---

def roll(a, s, ax): return np.roll(a, s, axis=ax)

def grad_x(f, dx): return (roll(f,-1,1) - roll(f,1,1)) / (2*dx)
def grad_y(f, dy): return (roll(f,-1,0) - roll(f,1,0)) / (2*dy)

def laplacian(f, dx, dy):
    return ((roll(f,-1,1)-2*f+roll(f,1,1))/(dx*dx)
          + (roll(f,-1,0)-2*f+roll(f,1,0))/(dy*dy))

def advect(f, vx, vy, dx, dy):
    fx = np.where(vx>=0, (f-roll(f,1,1))/dx,
                          (roll(f,-1,1)-f)/dx)
    fy = np.where(vy>=0, (f-roll(f,1,0))/dy,
                          (roll(f,-1,0)-f)/dy)
    return -(vx*fx + vy*fy)

# --- local imports ---

from rsvp_torsion_flow import step_flow
from rsvp_history_field import step_chi
from rsvp_equilibrium_chi import equilibrium_score_field_chi, theta_from_probe
from rsvp_entropy_torsion_suppression import suppressed_entropy_production
from rsvp_entropy_caps_phase_plateaus import soft_cap_sink, hard_cap
from rsvp_quantum_vector_gates import (
    normalize_v,
    angles_from_v_linear,
    build_hybrid_circuit
)

# --- simulation parameters ---

class P:
    nx = 96
    ny = 96
    Lx = 1.0
    Ly = 1.0
    dt = 2e-4
    steps = 3000

    T_env = 300.0

    # diffusion
    kT = 8e-4
    kPhi = 6e-4
    kS = 8e-4

    # relaxation
    alphaA = 0.6
    alphaB = 0.5
    lamAB = 1.2

    # Phi
    gammaPhi = 0.8
    etaPhi = 0.35

    # entropy
    mu = 0.6
    S_max = 0.6

    # chi
    chi_a = 0.8
    chi_b = 0.01
    chi_k = 2e-4

    # torsion flow params
    flow = dict(
        lambda=1.0,
        gamma=0.6,
        nu=1.2,
        kv=1e-3,
        dt=dt,
    )

# --- initialization ---

def init_fields(p: P, seed=0):
    rng = np.random.default_rng(seed)
    ny, nx = p.ny, p.nx

    TA = p.T_env + 3.0 * rng.normal(size=(ny, nx))
    TB = p.T_env + 3.0 * rng.normal(size=(ny, nx))

    Phi = 1.0 + 0.05 * rng.normal(size=(ny, nx))
    S = 0.05 + 0.02 * rng.random(size=(ny, nx))
    chi = np.zeros((ny, nx))

    y = np.linspace(0,1,ny,endpoint=False)
    x = np.linspace(0,1,nx,endpoint=False)
    X,Y = np.meshgrid(x,y)

    vx = 0.2*(Y-0.5)
    vy = -0.2*(X-0.5)

    return TA, TB, Phi, S, chi, vx, vy

# --- main loop ---

def run(seed=0, snapshot_stride=200):
    p = P()
    dx = p.Lx / p.nx
    dy = p.Ly / p.ny

    TA, TB, Phi, S, chi, vx, vy = init_fields(p, seed)

    theta_series = []
    Es_series = []
    circuits = []

    for n in range(p.steps):

        # --- flow update (torsion-driven) ---
        vx, vy = step_flow(vx, vy, Phi, S, dx, dy, p.flow)

        # --- temperature ---
        TA += p.dt * (
            advect(TA, vx, vy, dx, dy)
            + p.kT * laplacian(TA, dx, dy)
            - p.alphaA*(TA-p.T_env)
            + p.lamAB*(TB-TA)
        )

        TB += p.dt * (
            advect(TB, vx, vy, dx, dy)
            + p.kT * laplacian(TB, dx, dy)
            - p.alphaB*(TB-p.T_env)
            + p.lamAB*(TA-TB)
        )

        # --- entropy production (torsion suppressed) ---
        prod, Gamma, omega = suppressed_entropy_production(
            TA, TB, vx, vy, dx, dy,
            sigma0=0.01,
            beta_gradT=0.02,
            alpha_omega=2.0
        )

        dS = (
            advect(S, vx, vy, dx, dy)
            + p.kS * laplacian(S, dx, dy)
            + prod
            - p.mu * Phi * S
            - soft_cap_sink(S, p.S_max, k_cap=3.0)
        )

        S += p.dt * dS
        S = hard_cap(S, p.S_max)

        # --- history field ---
        chi = step_chi(
            chi, S, vx, vy, dx, dy,
            dict(a=p.chi_a, b=p.chi_b, kchi=p.chi_k, dt=p.dt)
        )

        # --- Phi ---
        Phi += p.dt * (
            -div := (grad_x(Phi*vx, dx) + grad_y(Phi*vy, dy))
        )  # conservative transport
        Phi += p.dt * (
            p.kPhi * laplacian(Phi, dx, dy)
            - p.gammaPhi * (Phi-1.0) / (1.0 + chi)
            - p.etaPhi * S
        )
        Phi = np.maximum(Phi, 1e-6)

        # --- equilibrium score + phase ---
        Es = equilibrium_score_field_chi(TA, TB, Phi, chi, k=0.15)
        theta, Esbar = theta_from_probe(Es)

        theta_series.append(theta)
        Es_series.append(Esbar)

        # --- quantum snapshot ---
        if n % snapshot_stride == 0:
            vx_bar = float(vx.mean())
            vy_bar = float(vy.mean())

            vx_n, vy_n = normalize_v(vx_bar, vy_bar, v_scale=0.5)
            thx, thy = angles_from_v_linear(vx_n, vy_n)

            try:
                qc = build_hybrid_circuit(theta, thx, thy)
                circuits.append((n, qc))
            except RuntimeError:
                pass

    return np.array(theta_series), np.array(Es_series), circuits

# --- execution ---

if __name__ == "__main__":
    theta, Es, circuits = run(seed=1)
    print("Final theta:", theta[-1])
    print("Theta std (plateau indicator):", theta.std())
    print("Circuit snapshots:", len(circuits))