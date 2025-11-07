"""
fpc_dynamics.py

Fixed-Point Causality (FPC) dynamics module for the RSVP Analysis Suite (RAS).
Includes:
- deterministic ODE time-steppers (explicit Euler, RK4)
- simple delay-differential equation (DDE) integrator using fixed lag buffer
- stochastic SDE integrator (Euler-Maruyama)
- root-finding and fixed-point solvers (Newton, hybrid via scipy if present)
- constraint projection utilities to enforce linear/nonlinear constraints during evolution
- Jacobian estimation and linear stability analysis at fixed points

This starter module aims to cover the breadth of FPC experimental needs: delays, noise,
constraints, and stability diagnostics. Replace or extend integrators with more sophisticated
solvers for production experiments.
"""
from __future__ import annotations
from typing import Callable, Tuple, Optional, Dict, Any

import numpy as np

try:
    from scipy import optimize
    from scipy import linalg
except Exception:
    optimize = None
    linalg = None


Vector = np.ndarray


# ----------------------------- Time steppers -----------------------------

def euler_step(x: Vector, f: Callable[[Vector, float], Vector], t: float, dt: float) -> Vector:
    """Single explicit Euler step: x_{n+1} = x_n + dt * f(x_n, t)"""
    return x + dt * f(x, t)


def rk4_step(x: Vector, f: Callable[[Vector, float], Vector], t: float, dt: float) -> Vector:
    """Classic fourth-order Runge-Kutta step."""
    k1 = f(x, t)
    k2 = f(x + 0.5 * dt * k1, t + 0.5 * dt)
    k3 = f(x + 0.5 * dt * k2, t + 0.5 * dt)
    k4 = f(x + dt * k3, t + dt)
    return x + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def integrate_ode(x0: Vector, f: Callable[[Vector, float], Vector], t_span: Tuple[float, float], dt: float,
                  method: str = 'rk4', callback: Optional[Callable[[Vector, float], None]] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Integrate an ODE from t_span[0] to t_span[1] with fixed dt and return (times, trajectory).
    method: 'euler' or 'rk4'
    callback: optional function called at each step with (x, t) for logging.
    """
    t0, t1 = t_span
    nsteps = int(np.ceil((t1 - t0) / dt))
    xs = []
    ts = []
    x = x0.copy()
    t = t0
    step_fn = euler_step if method == 'euler' else rk4_step
    for i in range(nsteps):
        xs.append(x.copy())
        ts.append(t)
        if callback is not None:
            callback(x, t)
        x = step_fn(x, f, t, dt)
        t += dt
    return np.array(ts), np.array(xs)


# ----------------------------- Delay Differential Equation (simple) -----------------------------

def integrate_dde(x0_func: Callable[[float], Vector], f_delay: Callable[[Vector, Vector, float], Vector],
                  t_span: Tuple[float, float], dt: float, delay: float) -> Tuple[np.ndarray, np.ndarray]:
    """Integrate a simple fixed-lag DDE: x'(t) = f_delay(x(t), x(t - delay), t).

    x0_func: function providing history x(t) for t <= t0
    f_delay: function f_delay(x_now, x_lag, t)
    Returns (times, trajectory)
    """
    t0, t1 = t_span
    nsteps = int(np.ceil((t1 - t0) / dt))
    size = len(x0_func(t0))

    # buffer to store history; we keep M = ceil(delay/dt)+1 previous states
    M = int(np.ceil(delay / dt)) + 2
    buf = [x0_func(t0 - (M - 1 - i) * dt).copy() for i in range(M)]
    times = []
    traj = []

    t = t0
    x = x0_func(t0).copy()
    for i in range(nsteps):
        times.append(t)
        traj.append(x.copy())
        # find lagged state via interpolation in the buffer
        lag_t = t - delay
        if lag_t <= t0:
            x_lag = x0_func(lag_t)
        else:
            # linear interpolation between nearest buffer entries
            idx = int((lag_t - t0) // dt)
            idx = max(0, min(len(buf) - 2, idx))
            t_idx = t - (len(buf) - 1 - idx) * dt
            # fallback: use oldest
            x_lag = buf[idx]
        # Euler step for DDE
        dx = f_delay(x, x_lag, t)
        x = x + dt * dx
        # append to buffer
        buf.append(x.copy())
        if len(buf) > M:
            buf.pop(0)
        t += dt
    return np.array(times), np.array(traj)


# ----------------------------- Stochastic SDE (Euler-Maruyama) -----------------------------

def integrate_sde_em(x0: Vector, drift: Callable[[Vector, float], Vector], diffusion: Callable[[Vector, float], Vector],
                     t_span: Tuple[float, float], dt: float, rng: Optional[np.random.Generator] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Integrate SDE dx = drift(x,t) dt + diffusion(x,t) dW_t using Euler-Maruyama.

    diffusion returns the diagonal noise amplitude (vector) for simplicity.
    """
    if rng is None:
        rng = np.random.default_rng()
    t0, t1 = t_span
    nsteps = int(np.ceil((t1 - t0) / dt))
    x = x0.copy()
    xs = []
    ts = []
    t = t0
    for i in range(nsteps):
        xs.append(x.copy())
        ts.append(t)
        mu = drift(x, t)
        sigma = diffusion(x, t)
        dW = rng.normal(scale=np.sqrt(dt), size=x.shape)
        x = x + mu * dt + sigma * dW
        t += dt
    return np.array(ts), np.array(xs)


# ----------------------------- Fixed point solvers / root finding -----------------------------

def find_fixed_point(f: Callable[[Vector], Vector], x0: Vector, method: str = 'newton', tol: float = 1e-8, maxiter: int = 200) -> Tuple[Vector, Dict[str, Any]]:
    """Find x such that f(x) = 0. Wrapper supporting scipy if available, else simple Newton.

    f: maps R^n -> R^n
    Returns (x_sol, info)
    """
    n = x0.size
    if method == 'newton' and optimize is not None:
        try:
            sol = optimize.root(lambda x: f(x), x0, method='hybr', tol=tol)
            return sol.x, {'success': sol.success, 'nfev': sol.nfev}
        except Exception:
            # fallback to simple Newton
            pass
    # simple fixed-point iteration / damped Newton
    x = x0.copy()
    for i in range(maxiter):
        Fx = f(x)
        norm = np.linalg.norm(Fx)
        if norm < tol:
            return x, {'success': True, 'iter': i}
        # approximate Jacobian via finite differences
        J = approx_jacobian(lambda y: f(y), x)
        try:
            delta = np.linalg.solve(J, -Fx)
        except np.linalg.LinAlgError:
            delta = -0.1 * Fx
        # damping
        alpha = 1.0
        x = x + alpha * delta
    return x, {'success': False, 'iter': maxiter}


def approx_jacobian(f: Callable[[Vector], Vector], x: Vector, eps: float = 1e-6) -> np.ndarray:
    """Finite-difference Jacobian approximation (forward differences)."""
    x = x.astype(float)
    n = x.size
    Fx = f(x)
    m = Fx.size
    J = np.zeros((m, n), dtype=float)
    for i in range(n):
        xp = x.copy()
        xp[i] += eps
        J[:, i] = (f(xp) - Fx) / eps
    return J


# ----------------------------- Constraint projection utilities -----------------------------

def project_to_linear_constraint(x: Vector, A: np.ndarray, b: Vector) -> Vector:
    """Project x to solve A x = b in least-squares sense (linear constraints).
    Returns the projected vector x_proj minimizing ||x_proj - x|| subject to A x_proj = b.
    """
    # solve min ||x' - x||^2 s.t. A x' = b -> x' = x - A^T (A A^T)^{-1} (A x - b)
    AT = A.T
    M = A @ AT
    if linalg is not None:
        invM = linalg.pinv(M)
    else:
        invM = np.linalg.pinv(M)
    correction = AT @ (invM @ (A @ x - b))
    return x - correction


def enforce_nonlinear_constraint(x: Vector, g: Callable[[Vector], float], dg: Callable[[Vector], Vector], tol: float = 1e-8, maxiter: int = 50) -> Vector:
    """Project to a scalar nonlinear constraint g(x)=0 using Newton iterations on the constraint.
    dg is gradient of g returning vector of same size as x.
    """
    for i in range(maxiter):
        val = g(x)
        if abs(val) < tol:
            return x
        grad = dg(x)
        denom = grad.dot(grad)
        if denom == 0:
            break
        x = x - (val / denom) * grad
    return x


# ----------------------------- Linear stability analysis -----------------------------

def stability_at_fixed_point(f: Callable[[Vector], Vector], x_star: Vector) -> Dict[str, Any]:
    """Estimate Jacobian at x_star and compute eigenvalues to assess linear stability.
    Returns dict with Jacobian and eigenvalues.
    """
    J = approx_jacobian(lambda y: f(y), x_star)
    if linalg is not None:
        eigvals = linalg.eigvals(J)
    else:
        eigvals = np.linalg.eigvals(J)
    return {'J': J, 'eigvals': eigvals}


# ----------------------------- Demo harness -----------------------------

if __name__ == "__main__":
    print('FPC dynamics demo — ODE, DDE, SDE, fixed-point and stability examples')

    # simple linear system with stable fixed point at 0: x' = -x
    f = lambda x, t: -x
    x0 = np.array([1.0])
    ts, xs = integrate_ode(x0, lambda x, t: f(x, t), (0.0, 5.0), dt=0.01, method='rk4')
    print('ODE final state:', xs[-1])

    # DDE example: x' = -x(t) + 0.5 * x(t-delay)
    def history(t):
        return np.array([1.0])
    def f_delay(xnow, xlag, t):
        return -xnow + 0.5 * xlag
    ts_dde, xs_dde = integrate_dde(history, f_delay, (0.0, 10.0), dt=0.01, delay=0.5)
    print('DDE final state:', xs_dde[-1])

    # SDE example: Ornstein-Uhlenbeck-like
    drift = lambda x, t: -0.5 * x
    diffusion = lambda x, t: 0.2 * np.ones_like(x)
    ts_sde, xs_sde = integrate_sde_em(np.array([0.0]), drift, diffusion, (0.0, 5.0), dt=0.001)
    print('SDE sample final state:', xs_sde[-1])

    # fixed-point solve for g(x) = -x + sin(x) -> root near 0
    f_root = lambda x: -x + np.sin(x)
    x_sol, info = find_fixed_point(f_root, np.array([0.5]))
    print('Fixed point solve:', x_sol, info)

    # stability at fixed point
    stab = stability_at_fixed_point(f_root, x_sol)
    print('Eigenvalues at fixed point:', stab['eigvals'])

    print('Demo complete.')

