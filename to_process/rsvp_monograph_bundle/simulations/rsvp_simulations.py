"""
RSVP Simulation Suite
---------------------

This module implements a minimal but complete simulation suite
for the RSVP PDE/ODE toy models:

1. ODE reduction and phase portraits in (Phi, S) space.
2. 1-parameter bifurcation scan over the error-damping gamma parameter.
3. 1D PDE solver and animation for collapse to a semantic galaxy.
4. Optional 2D Phi+S toy evolution demo.

Requirements:
    - numpy
    - matplotlib
    - scipy (for solve_ivp)

You can run this module as a script to generate basic figures,
or import individual functions in a Jupyter notebook.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from dataclasses import dataclass
from typing import Tuple, Callable

try:
    from scipy.integrate import solve_ivp
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


# ------------------------------------------------------------
# Common parameter container
# ------------------------------------------------------------

@dataclass
class RSVPParams:
    # ODE parameters
    k_phi: float = 0.1         # semantic decay
    lam_S: float = 0.5         # entropy-to-phi source
    alpha_phi: float = 0.3     # semantic forcing on v
    nu_v: float = 0.2          # viscosity / damping of v
    beta_vS: float = 0.3       # coupling v*S in dS/dt
    gamma_err: float = 0.8     # error-damping term
    dS_lin: float = 0.1        # linear decay in S
    phi_star: float = 1.0      # target semantic field

    # PDE parameters
    kappa: float = 0.02
    nu: float = 0.02
    D_S: float = 0.02
    lambda_S: float = 0.3
    alpha: float = 0.3
    beta: float = 0.3
    gamma: float = 0.8


# ------------------------------------------------------------
# 1. Reduced ODE model
# ------------------------------------------------------------

def rsvp_ode_rhs(t: float, y: np.ndarray, p: RSVPParams) -> np.ndarray:
    """
    ODE right-hand side for spatially homogeneous RSVP model.

    y = [Phi, V, S].
    """
    Phi, V, S = y

    dPhi = -p.k_phi * Phi - V * Phi + p.lam_S * S
    dV   = -S + p.alpha_phi * Phi - p.nu_v * V - V * V
    dS   = -p.beta_vS * V * S - p.gamma_err * (Phi - p.phi_star) - p.dS_lin * S

    return np.array([dPhi, dV, dS], dtype=float)


def integrate_ode(
    y0: np.ndarray,
    t_span: Tuple[float, float],
    params: RSVPParams,
    t_eval: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Integrate the ODE model from y0 over t_span using solve_ivp
    (if SciPy is available) or a simple explicit Euler fallback.
    """
    if SCIPY_AVAILABLE:
        sol = solve_ivp(
            lambda t, y: rsvp_ode_rhs(t, y, params),
            t_span,
            y0,
            t_eval=t_eval,
            rtol=1e-6,
            atol=1e-9,
        )
        if not sol.success:
            raise RuntimeError("ODE integration failed: " + sol.message)
        return sol.t, sol.y.T

    # Fallback: explicit Euler
    if t_eval is None:
        n_steps = 2000
        t_eval = np.linspace(t_span[0], t_span[1], n_steps)
    dt = t_eval[1] - t_eval[0]
    y = np.array(y0, dtype=float)
    traj = np.zeros((len(t_eval), len(y0)), dtype=float)
    traj[0] = y
    for i in range(1, len(t_eval)):
        dy = rsvp_ode_rhs(t_eval[i-1], y, params)
        y = y + dt * dy
        traj[i] = y
    return t_eval, traj


def plot_phase_portraits(params: RSVPParams, n_grid: int = 6) -> None:
    """
    Plot phase portraits in the (Phi, S) plane using the reduced ODE.

    The velocity V is initialized to 0 for simplicity.
    """
    fig, ax = plt.subplots(figsize=(6, 5))

    Phi_vals = np.linspace(-1.0, 2.0, n_grid)
    S_vals = np.linspace(-1.0, 2.0, n_grid)

    for Phi0 in Phi_vals:
        for S0 in S_vals:
            y0 = np.array([Phi0, 0.0, S0], dtype=float)
            t_eval = np.linspace(0.0, 40.0, 800)
            t, traj = integrate_ode(y0, (t_eval[0], t_eval[-1]), params, t_eval=t_eval)
            ax.plot(traj[:, 0], traj[:, 2], linewidth=0.6)

    ax.set_xlabel(r"$\Phi$")
    ax.set_ylabel(r"$S$")
    ax.set_title("RSVP ODE Phase Portraits in $(\Phi, S)$")
    ax.axvline(params.phi_star, linestyle="--", linewidth=0.8)
    ax.grid(True)
    plt.tight_layout()


def bifurcation_scan(
    params: RSVPParams,
    gamma_values: np.ndarray | None = None,
    t_final: float = 80.0,
) -> None:
    """
    Simple 1-parameter bifurcation diagram:
    vary gamma_err and track final Phi value for a fixed initial condition.
    """
    if gamma_values is None:
        gamma_values = np.linspace(0.1, 2.5, 50)

    final_Phi = []

    for gE in gamma_values:
        local_params = RSVPParams(**{**params.__dict__, "gamma_err": float(gE)})
        y0 = np.array([0.5, 0.0, 1.0], dtype=float)
        t_eval = np.linspace(0.0, t_final, 2000)
        t, traj = integrate_ode(y0, (0.0, t_final), local_params, t_eval=t_eval)
        final_Phi.append(traj[-1, 0])

    final_Phi = np.array(final_Phi)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(gamma_values, final_Phi, marker="o", linestyle="none", markersize=3)
    ax.axhline(params.phi_star, linestyle="--", linewidth=0.8)
    ax.set_xlabel(r"$\gamma_{\text{err}}$")
    ax.set_ylabel(r"Final $\Phi$")
    ax.set_title("Bifurcation in Final $\Phi$ vs. Error Damping $\gamma_{\text{err}}$")
    ax.grid(True)
    plt.tight_layout()


# ------------------------------------------------------------
# 2. 1D PDE model
# ------------------------------------------------------------

def laplacian_1d(f: np.ndarray, dx: float) -> np.ndarray:
    """Second-order central-difference Laplacian with periodic BC."""
    return (np.roll(f, -1) - 2.0 * f + np.roll(f, 1)) / (dx * dx)


def gradient_1d(f: np.ndarray, dx: float) -> np.ndarray:
    """Central-difference gradient with periodic BC."""
    return (np.roll(f, -1) - np.roll(f, 1)) / (2.0 * dx)


def advect_1d(f: np.ndarray, v: np.ndarray, dx: float) -> np.ndarray:
    """Semi-discrete advection using flux form with central differences."""
    flux = f * v
    return -(np.roll(flux, -1) - np.roll(flux, 1)) / (2.0 * dx)


def step_rsvp_1d(
    phi: np.ndarray,
    v: np.ndarray,
    S: np.ndarray,
    dx: float,
    dt: float,
    params: RSVPParams,
    phi_star: float | np.ndarray = 1.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Single explicit-Euler timestep for 1D RSVP PDE system with periodic BC.
    """
    lap_phi = laplacian_1d(phi, dx)
    lap_v = laplacian_1d(v, dx)
    lap_S = laplacian_1d(S, dx)

    grad_phi = gradient_1d(phi, dx)
    grad_S = gradient_1d(S, dx)

    adv_phi = advect_1d(phi, v, dx)
    adv_S = v * grad_S

    dPhi = params.kappa * lap_phi + adv_phi + params.lambda_S * S
    dV   = -grad_S + params.nu * lap_v + params.alpha * grad_phi - v * grad_phi
    dS   = params.D_S * lap_S - params.beta * adv_S - params.gamma * (phi - phi_star)

    phi_new = phi + dt * dPhi
    v_new = v + dt * dV
    S_new = S + dt * dS

    return phi_new, v_new, S_new


def run_rsvp_1d_simulation(
    L: float = 10.0,
    nx: int = 256,
    t_final: float = 50.0,
    dt: float = 1e-3,
    seed: int | None = 0,
    params: RSVPParams | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Run a 1D RSVP PDE simulation with periodic boundary conditions.

    Returns:
        x: spatial grid
        phi_hist: array of shape (n_snapshots, nx)
        v_hist: array of shape (n_snapshots, nx)
        S_hist: array of shape (n_snapshots, nx)
    """
    if params is None:
        params = RSVPParams()

    if seed is not None:
        rng = np.random.default_rng(seed)
    else:
        rng = np.random.default_rng()

    x = np.linspace(0.0, L, nx, endpoint=False)
    dx = x[1] - x[0]

    phi = 0.1 * rng.standard_normal(nx)
    v = 0.1 * rng.standard_normal(nx)
    S = 0.1 * rng.standard_normal(nx)

    n_steps = int(t_final / dt)
    snapshot_every = max(1, n_steps // 200)
    n_snapshots = n_steps // snapshot_every + 1

    phi_hist = np.zeros((n_snapshots, nx))
    v_hist = np.zeros((n_snapshots, nx))
    S_hist = np.zeros((n_snapshots, nx))

    snapshot_idx = 0
    phi_hist[snapshot_idx] = phi
    v_hist[snapshot_idx] = v
    S_hist[snapshot_idx] = S

    phi_star = params.phi_star

    for step in range(1, n_steps + 1):
        phi, v, S = step_rsvp_1d(phi, v, S, dx, dt, params, phi_star)
        if step % snapshot_every == 0:
            snapshot_idx += 1
            phi_hist[snapshot_idx] = phi
            v_hist[snapshot_idx] = v
            S_hist[snapshot_idx] = S

    t_arr = np.linspace(0.0, t_final, n_snapshots)
    return x, t_arr, phi_hist, v_hist, S_hist


def animate_rsvp_1d(
    L: float = 10.0,
    nx: int = 256,
    t_final: float = 50.0,
    dt: float = 1e-3,
    params: RSVPParams | None = None,
) -> FuncAnimation:
    """
    Create a matplotlib.animation.FuncAnimation object
    showing the evolution of Phi, v, and S in 1D.
    """
    if params is None:
        params = RSVPParams()

    if scipy_available := SCIPY_AVAILABLE:
        pass  # just to avoid unused variable warnings if we later expand

    # Run a shorter internal sim for animation
    x, t_arr, phi_hist, v_hist, S_hist = run_rsvp_1d_simulation(
        L=L, nx=nx, t_final=t_final, dt=dt, params=params
    )

    fig, axes = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
    ax_phi, ax_v, ax_S = axes

    line_phi, = ax_phi.plot(x, phi_hist[0])
    ax_phi.set_ylabel(r"$\Phi$")
    ax_phi.grid(True)

    line_v, = ax_v.plot(x, v_hist[0])
    ax_v.set_ylabel(r"$v$")
    ax_v.grid(True)

    line_S, = ax_S.plot(x, S_hist[0])
    ax_S.set_ylabel(r"$S$")
    ax_S.set_xlabel(r"$x$")
    ax_S.grid(True)

    fig.suptitle("1D RSVP Evolution")

    def update(frame: int) -> list:
        line_phi.set_ydata(phi_hist[frame])
        line_v.set_ydata(v_hist[frame])
        line_S.set_ydata(S_hist[frame])
        return [line_phi, line_v, line_S]

    anim = FuncAnimation(
        fig,
        update,
        frames=len(t_arr),
        interval=50,
        blit=True,
    )

    plt.tight_layout()
    return anim


# ------------------------------------------------------------
# 3. 2D Phi+S toy evolution (optional)
# ------------------------------------------------------------

def laplacian_2d(f: np.ndarray, dx: float, dy: float) -> np.ndarray:
    """
    2D Laplacian with periodic boundary conditions using central differences.
    """
    f_ip = np.roll(f, -1, axis=1)
    f_im = np.roll(f, 1, axis=1)
    f_jp = np.roll(f, -1, axis=0)
    f_jm = np.roll(f, 1, axis=0)

    return (f_ip + f_im - 2.0 * f) / (dx * dx) + (f_jp + f_jm - 2.0 * f) / (dy * dy)


def rsvp_phi_2d_step(
    phi: np.ndarray,
    S: np.ndarray,
    dx: float,
    dy: float,
    dt: float,
    kappa: float,
    lambda_S: float,
) -> np.ndarray:
    """
    Simplified 2D evolution for Phi with fixed S:
    dPhi/dt = kappa * Laplacian(Phi) + lambda_S * S
    """
    lap_phi = laplacian_2d(phi, dx, dy)
    dPhi = kappa * lap_phi + lambda_S * S
    phi_new = phi + dt * dPhi
    return phi_new


def demo_phi_2d_gaussian(
    nx: int = 128,
    ny: int = 128,
    Lx: float = 10.0,
    Ly: float = 10.0,
    dt: float = 1e-3,
    n_steps: int = 2000,
    kappa: float = 0.02,
    lambda_S: float = 0.3,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Simple 2D demo where S is a Gaussian bump and Phi evolves toward it.
    Returns X, Y, Phi_final for visualization (e.g. with imshow or contourf).
    """
    x = np.linspace(-Lx/2.0, Lx/2.0, nx, endpoint=False)
    y = np.linspace(-Ly/2.0, Ly/2.0, ny, endpoint=False)
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    X, Y = np.meshgrid(x, y)

    rng = np.random.default_rng(0)
    phi = 0.1 * rng.standard_normal((ny, nx))

    # Gaussian entropy potential
    sigma2 = 1.0
    S = np.exp(-(X**2 + Y**2) / (2.0 * sigma2))

    for _ in range(n_steps):
        phi = rsvp_phi_2d_step(phi, S, dx, dy, dt, kappa, lambda_S)

    return X, Y, phi


# ------------------------------------------------------------
# 4. Command-line entry points (optional)
# ------------------------------------------------------------

def main():
    """
    If run as a script, generate a few basic figures.
    """
    params = RSVPParams()

    # Phase portraits
    plot_phase_portraits(params)
    plt.savefig("phase_portraits_phi_S.png", dpi=150)

    # Bifurcation scan
    gamma_vals = np.linspace(0.1, 2.5, 40)
    bifurcation_scan(params, gamma_vals)
    plt.savefig("bifurcation_phi_vs_gamma.png", dpi=150)

    # 1D snapshot (no animation)
    x, t_arr, phi_hist, v_hist, S_hist = run_rsvp_1d_simulation(
        L=10.0, nx=256, t_final=20.0, dt=1e-3, params=params
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, phi_hist[0], label="t=0")
    ax.plot(x, phi_hist[-1], label=f"t={t_arr[-1]:.1f}")
    ax.set_xlabel("x")
    ax.set_ylabel(r"$\Phi(x)$")
    ax.set_title("1D RSVP Collapse (Initial vs Final)")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()
    plt.savefig("rsvp_1d_collapse_phi.png", dpi=150)

    print("RSVP simulation suite: figures written to current directory.")


if __name__ == "__main__":
    main()
