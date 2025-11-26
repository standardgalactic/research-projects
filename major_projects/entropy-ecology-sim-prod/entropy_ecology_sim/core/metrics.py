
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import jax
import jax.numpy as jnp


EPS = 1e-12


def _safe_log(x: jnp.ndarray) -> jnp.ndarray:
    return jnp.log(jnp.clip(x, EPS, None))


def _normalize_prob(x: jnp.ndarray) -> jnp.ndarray:
    total = jnp.sum(x)
    return x / (total + EPS)


@dataclass(frozen=True)
class PowerLawFit:
    alpha: float
    xmin: float
    n: int
    loglik: float


def power_law_exponent(
    sizes: jnp.ndarray,
    xmin: float | None = None,
) -> PowerLawFit:
    sizes = sizes[jnp.isfinite(sizes)]
    sizes = sizes[sizes > 0]

    n_all = sizes.size
    if n_all == 0:
        return PowerLawFit(alpha=jnp.nan, xmin=jnp.nan, n=0, loglik=jnp.nan)

    if xmin is None:
        xmin_val = jnp.min(sizes)
    else:
        xmin_val = float(xmin)

    tail = sizes[sizes >= xmin_val]
    n = tail.size
    if n < 5:
        return PowerLawFit(alpha=jnp.nan, xmin=float(xmin_val), n=int(n), loglik=jnp.nan)

    logs = _safe_log(tail / xmin_val)
    alpha_hat = 1.0 + n / (jnp.sum(logs) + EPS)

    loglik = (
        n * _safe_log(alpha_hat - 1.0)
        + n * (alpha_hat - 1.0) * _safe_log(xmin_val)
        - alpha_hat * jnp.sum(_safe_log(tail))
    )

    return PowerLawFit(
        alpha=float(alpha_hat),
        xmin=float(xmin_val),
        n=int(n),
        loglik=float(loglik),
    )


def transfer_entropy(
    S_t0: jnp.ndarray,
    S_t1: jnp.ndarray,
    n_bins: int = 16,
) -> float:
    x = jnp.ravel(S_t0)
    y = jnp.ravel(S_t1)

    x = jnp.clip(x, 0.0, 1.0)
    y = jnp.clip(y, 0.0, 1.0)

    bins = jnp.linspace(0.0, 1.0, n_bins + 1)

    x_idx = jnp.digitize(x, bins) - 1
    y_idx = jnp.digitize(y, bins) - 1

    x_idx = jnp.clip(x_idx, 0, n_bins - 1)
    y_idx = jnp.clip(y_idx, 0, n_bins - 1)

    joint_counts = jnp.zeros((n_bins, n_bins))
    joint_counts = joint_counts.at[x_idx, y_idx].add(1.0)

    p_xy = _normalize_prob(joint_counts)
    p_x = jnp.sum(p_xy, axis=1, keepdims=True)
    p_y = jnp.sum(p_xy, axis=0, keepdims=True)

    with jax.numpy.errstate(divide="ignore", invalid="ignore"):
        ratio = p_xy / (p_x * p_y + EPS)
        mi = jnp.sum(p_xy * _safe_log(ratio))

    mi_bits = mi / jnp.log(2.0)
    return float(mi_bits)


def fisher_information_gradient(Phi: jnp.ndarray, dx: float = 1.0) -> float:
    Phi = jnp.clip(Phi, EPS, None)
    p = _normalize_prob(Phi)
    log_p = _safe_log(p)

    dlogp_dx = (jnp.roll(log_p, -1, axis=1) - jnp.roll(log_p, 1, axis=1)) / (2 * dx)
    dlogp_dy = (jnp.roll(log_p, -1, axis=0) - jnp.roll(log_p, 1, axis=0)) / (2 * dx)

    grad_sq = dlogp_dx**2 + dlogp_dy**2
    F = jnp.sum(p * grad_sq)

    return float(F)


@dataclass(frozen=True)
class RegimeShiftResult:
    score: float
    t_peak: int
    mean_series: jnp.ndarray
    diff_series: jnp.ndarray


def regime_shift_score(
    history: Sequence[jnp.ndarray],
) -> RegimeShiftResult:
    if len(history) < 3:
        return RegimeShiftResult(
            score=0.0,
            t_peak=0,
            mean_series=jnp.zeros((len(history),)),
            diff_series=jnp.zeros((max(len(history) - 1, 1),)),
        )

    S_stack = jnp.stack(history, axis=0)
    mean_series = jnp.mean(S_stack, axis=(1, 2))

    diff_series = jnp.abs(jnp.diff(mean_series))
    max_diff = jnp.max(diff_series)
    std_diff = jnp.std(diff_series) + EPS

    s_raw = max_diff / std_diff
    score = 1.0 - jnp.exp(-s_raw)

    t_peak = int(jnp.argmax(diff_series))

    return RegimeShiftResult(
        score=float(score),
        t_peak=t_peak,
        mean_series=mean_series,
        diff_series=diff_series,
    )


def lyapunov_spectrum_from_timeseries(
    fields: jnp.ndarray,
) -> jnp.ndarray:
    if fields.ndim != 3:
        raise ValueError("fields must have shape [T, H, W]")

    T = fields.shape[0]
    if T < 3:
        return jnp.array([jnp.nan])

    x = fields.reshape(T, -1)

    x_t = x[:-1]
    x_tp1 = x[1:]
    diffs = x_tp1 - x_t

    norm_x = jnp.linalg.norm(x_t, axis=1) + EPS
    norm_diff = jnp.linalg.norm(diffs, axis=1) + EPS

    ratios = norm_diff / norm_x
    lambdas = _safe_log(ratios)

    lambda_leading = jnp.mean(lambdas)
    return jnp.array([lambda_leading])


__all__ = [
    "PowerLawFit",
    "RegimeShiftResult",
    "power_law_exponent",
    "transfer_entropy",
    "fisher_information_gradient",
    "regime_shift_score",
    "lyapunov_spectrum_from_timeseries",
]
