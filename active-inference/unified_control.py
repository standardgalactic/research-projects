
"""
unified_control.py

Reference implementation of a unified control framework:

- Linear and nonlinear plants
- PCT-style controllers
- Active Inference controllers (minimal Gaussian FEP)
- Sparse narrative controllers (L1-regularised control policy)
- Sheaf-style consistency diagnostics
- Simulation and diagnostic utilities

This module is designed as a "living appendix" to a theoretical paper on
the equivalence and unification of control, inference, and sparse semantic
projection.

Dependencies: numpy, scipy (for linalg), matplotlib (for plotting in demos)
"""

from dataclasses import dataclass
from typing import Callable, Dict, Tuple, List, Optional
import numpy as np

try:
    from scipy import linalg
except ImportError:  # fall back if scipy is not available
    linalg = None


Array = np.ndarray


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def euler_step(f: Callable[[float, Array], Array], t: float, x: Array, dt: float) -> Array:
    """Single Euler integration step for x' = f(t,x)."""
    return x + dt * f(t, x)


def simulate_ode(
    f: Callable[[float, Array], Array],
    x0: Array,
    t0: float,
    t1: float,
    dt: float
) -> Tuple[Array, Array]:
    """
    Simulate ODE x' = f(t,x) with Euler method.

    Returns:
        ts: (T,) time points
        xs: (T, n) state trajectory
    """
    n_steps = int(np.ceil((t1 - t0) / dt)) + 1
    ts = np.linspace(t0, t0 + dt * (n_steps - 1), n_steps)
    xs = np.zeros((n_steps, x0.size))
    x = x0.copy()
    for i, t in enumerate(ts):
        xs[i] = x
        if i < n_steps - 1:
            x = euler_step(f, t, x, dt)
    return ts, xs


# ---------------------------------------------------------------------------
# Plant models
# ---------------------------------------------------------------------------

@dataclass
class LinearPlant:
    """
    Linear time-invariant plant:
        x' = A x + B u + w
        y = C x + v
    """
    A: Array
    B: Array
    C: Array
    process_noise_std: float = 0.0
    obs_noise_std: float = 0.0
    rng: np.random.Generator = np.random.default_rng()

    def step(self, x: Array, u: Array, dt: float) -> Tuple[Array, Array]:
        w = self.rng.normal(0.0, self.process_noise_std, size=x.shape)
        v = self.rng.normal(0.0, self.obs_noise_std, size=(self.C.shape[0],))
        x_next = x + dt * (self.A @ x + self.B @ u + w)
        y_next = self.C @ x_next + v
        return x_next, y_next


@dataclass
class NonlinearPlant:
    """
    Simple nonlinear plant:
        x' = A x + B u - alpha * x^3 + w
        y = C x + v
    """
    A: Array
    B: Array
    C: Array
    alpha: float = 1.0
    process_noise_std: float = 0.0
    obs_noise_std: float = 0.0
    rng: np.random.Generator = np.random.default_rng()

    def step(self, x: Array, u: Array, dt: float) -> Tuple[Array, Array]:
        w = self.rng.normal(0.0, self.process_noise_std, size=x.shape)
        v = self.rng.normal(0.0, self.obs_noise_std, size=(self.C.shape[0],))
        nonlinear_term = -self.alpha * (x ** 3)
        x_next = x + dt * (self.A @ x + self.B @ u + nonlinear_term + w)
        y_next = self.C @ x_next + v
        return x_next, y_next


# ---------------------------------------------------------------------------
# PCT controller
# ---------------------------------------------------------------------------

@dataclass
class PCTController:
    """
    Perceptual Control Theory (PCT) controller for linear plant output y.

    For scalar case:
        e = r - y
        u = k_p * e

    For vector case:
        e = r - y
        u = K @ e
    """
    K: Array  # gain matrix (m x p) for u in R^m, y in R^p
    reference: Array  # reference r in output space (R^p)

    def act(self, y: Array) -> Array:
        e = self.reference - y
        u = self.K @ e
        return u


# ---------------------------------------------------------------------------
# Active Inference controller (minimal Gaussian model)
# ---------------------------------------------------------------------------

@dataclass
class ActiveInferenceController:
    """
    Minimal active inference controller for linear-Gaussian model.

    Generative model (for simplicity, steady-state dynamics):
        p(s) = N(0, Sigma_s)
        p(o | s) = N(C s, Sigma_o)

    Recognition density q(s) = N(mu, Sigma_q) with fixed Sigma_q.
    Action a affects observations via o = y + B_a a (approximate mapping).

    We implement gradient descent on variational free energy F(mu, a)
    under a Laplace approximation, focusing on first-order moments.
    """
    C: Array               # observation matrix
    Sigma_s_inv: Array     # prior precision on s
    Sigma_o_inv: Array     # observation precision
    B_a: Array             # action-to-observation mapping
    mu: Array              # current posterior mean over s
    a: Array               # current action
    eta_mu: float = 0.1    # learning rate for mu
    eta_a: float = 0.1     # learning rate for a
    preference_o: Optional[Array] = None  # preferred observation r_o

    def free_energy_gradients(self, o: Array) -> Tuple[Array, Array]:
        """
        Compute gradients dF/dmu and dF/da for quadratic free energy:
            F(mu,a) = 0.5 * (mu^T Sigma_s^{-1} mu)
                      + 0.5 * (o - C mu)^T Sigma_o^{-1} (o - C mu)
                      + preference term
        """
        # prior term gradient: d/dmu 0.5 mu^T P mu = P mu
        g_mu_prior = self.Sigma_s_inv @ self.mu

        # likelihood term: 0.5 (o - C mu)^T R (o - C mu)
        # gradient wrt mu: - C^T R (o - C mu)
        prediction_error = o - self.C @ self.mu
        g_mu_likelihood = - self.C.T @ (self.Sigma_o_inv @ prediction_error)

        # optional preference term: treat it as prior on o
        if self.preference_o is not None:
            pe_pref = o - self.preference_o
            g_mu_pref = - self.C.T @ (self.Sigma_o_inv @ pe_pref)
            g_mu = g_mu_prior + g_mu_likelihood + g_mu_pref
        else:
            g_mu = g_mu_prior + g_mu_likelihood

        # gradient wrt action a: F depends on o(a)
        # assume o = o_env + B_a a, approximate do/da = B_a
        # dF/da = (dF/do) (do/da)
        # dF/do = R (o - C mu) + preference term
        g_o = self.Sigma_o_inv @ prediction_error
        if self.preference_o is not None:
            g_o = g_o + self.Sigma_o_inv @ (o - self.preference_o)
        g_a = self.B_a.T @ g_o

        return g_mu, g_a

    def update(self, o: Array) -> Array:
        """
        Perform one gradient step on mu and a, return updated action.
        """
        g_mu, g_a = self.free_energy_gradients(o)
        self.mu = self.mu - self.eta_mu * g_mu
        self.a = self.a - self.eta_a * g_a
        return self.a


# ---------------------------------------------------------------------------
# Sparse narrative controller
# ---------------------------------------------------------------------------

@dataclass
class SparseNarrativeController:
    """
    Sparse narrative controller:

    - Maintain a dictionary D of control "motifs" (columns)
    - Given current error e, solve an L1-regularised regression
        e ≈ D alpha
      and derive control as u = W alpha

    Here we implement a simple coordinate-descent LASSO-like update.
    """
    D: Array          # (p x k) dictionary mapping k motifs to p-dim error
    W: Array          # (m x k) mapping from motifs to control actions
    lam: float = 0.1  # L1 penalty
    n_iter: int = 10  # number of coordinate descent iterations

    def _soft_threshold(self, x: float, lam: float) -> float:
        if x > lam:
            return x - lam
        elif x < -lam:
            return x + lam
        else:
            return 0.0

    def infer_alpha(self, e: Array) -> Array:
        """
        Coordinate descent to approximately solve
            min_alpha ||e - D alpha||^2 + lam * ||alpha||_1
        """
        p, k = self.D.shape
        alpha = np.zeros(k)
        DtD = self.D.T @ self.D
        Dte = self.D.T @ e
        for _ in range(self.n_iter):
            for j in range(k):
                # residual without contribution of alpha_j
                rho_j = Dte[j] - (DtD[j, :] @ alpha) + DtD[j, j] * alpha[j]
                alpha_j = rho_j / (DtD[j, j] + 1e-8)
                alpha[j] = self._soft_threshold(alpha_j, self.lam / (DtD[j, j] + 1e-8))
        return alpha

    def act(self, e: Array) -> Array:
        alpha = self.infer_alpha(e)
        u = self.W @ alpha
        return u


# ---------------------------------------------------------------------------
# Sheaf-style consistency diagnostics
# ---------------------------------------------------------------------------

@dataclass
class SheafContext:
    """
    A simple numerical analogue of a sheaf context:
        - local estimate over variable indices 'vars'
        - local value vector (x_local) for those variables
    """
    name: str
    vars: List[int]
    x_local: Array


@dataclass
class SheafDiagnostic:
    """
    Diagnose "obstruction" as disagreement on overlaps between contexts.

    This is not a full sheaf implementation, but a numerical shadow of
    the Čech coboundary idea: if local sections cannot be reconciled on
    overlaps, we treat that as a psychological or modelling conflict.
    """
    contexts: List[SheafContext]

    def overlap_discrepancies(self) -> Dict[Tuple[int, int], float]:
        """
        Compute L2 discrepancy on overlaps between every pair of contexts.
        Returns a dict keyed by (i,j) indices, value = norm of mismatch.
        """
        discrepancies = {}
        for i, ci in enumerate(self.contexts):
            for j, cj in enumerate(self.contexts):
                if j <= i:
                    continue
                overlap = set(ci.vars).intersection(cj.vars)
                if not overlap:
                    continue
                overlap = sorted(list(overlap))
                idx_i = [ci.vars.index(v) for v in overlap]
                idx_j = [cj.vars.index(v) for v in overlap]
                xi = ci.x_local[idx_i]
                xj = cj.x_local[idx_j]
                discrepancies[(i, j)] = float(np.linalg.norm(xi - xj))
        return discrepancies

    def global_conflict_score(self) -> float:
        """
        Aggregate measure of global inconsistency.
        """
        disc = self.overlap_discrepancies()
        if not disc:
            return 0.0
        vals = np.array(list(disc.values()))
        return float(np.mean(vals))


# ---------------------------------------------------------------------------
# Closed-loop simulation utilities
# ---------------------------------------------------------------------------

def simulate_pct_closed_loop(
    plant: LinearPlant,
    controller: PCTController,
    x0: Array,
    t0: float,
    t1: float,
    dt: float
) -> Dict[str, Array]:
    """
    Simulate closed-loop system with PCT controller.
    """
    n_steps = int(np.ceil((t1 - t0) / dt)) + 1
    ts = np.linspace(t0, t0 + dt * (n_steps - 1), n_steps)
    x_dim = x0.size
    u_dim = plant.B.shape[1]
    y_dim = plant.C.shape[0]

    xs = np.zeros((n_steps, x_dim))
    ys = np.zeros((n_steps, y_dim))
    us = np.zeros((n_steps, u_dim))

    x = x0.copy()
    # initial observation
    y = plant.C @ x
    for i, t in enumerate(ts):
        xs[i] = x
        ys[i] = y
        u = controller.act(y)
        us[i] = u
        x, y = plant.step(x, u, dt)

    return {"t": ts, "x": xs, "y": ys, "u": us}


def simulate_active_inference_closed_loop(
    plant: LinearPlant,
    controller: ActiveInferenceController,
    x0: Array,
    t0: float,
    t1: float,
    dt: float
) -> Dict[str, Array]:
    """
    Simulate closed-loop system with active inference controller.
    """
    n_steps = int(np.ceil((t1 - t0) / dt)) + 1
    ts = np.linspace(t0, t0 + dt * (n_steps - 1), n_steps)
    x_dim = x0.size
    u_dim = plant.B.shape[1]
    y_dim = plant.C.shape[0]

    xs = np.zeros((n_steps, x_dim))
    ys = np.zeros((n_steps, y_dim))
    us = np.zeros((n_steps, u_dim))
    mus = np.zeros((n_steps, controller.mu.size))

    x = x0.copy()
    # initial observation
    y = plant.C @ x
    for i, t in enumerate(ts):
        xs[i] = x
        ys[i] = y
        mus[i] = controller.mu
        u = controller.update(y)
        us[i] = u
        x, y = plant.step(x, u, dt)

    return {"t": ts, "x": xs, "y": ys, "u": us, "mu": mus}


def closed_loop_eigenvalues(A_cl: Array) -> Optional[Array]:
    """
    Utility wrapper around scipy.linalg.eigvals if available.
    """
    if linalg is None:
        return None
    return linalg.eigvals(A_cl)


# End of unified_control.py
