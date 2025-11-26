
from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Callable

import jax
import jax.numpy as jnp
from jax import jit

from .fields import RSVPFields


@dataclass(frozen=True)
class DynamicsParams:
    """All tunable coefficients in one immutable container – perfect for sweeps."
    """
    dt: float = 0.025

    # Diffusion
    D_Phi: float = 0.08
    D_S: float = 0.18

    # Vector field friction / inertia
    gamma: float = 0.92
    beta: float = 0.0

    # Dissipation & constraint formation
    kappa: float = 0.06
    chi: float = 0.12

    # Entropy bounds & numerical safety
    S_max: float = 1.0
    S_floor: float = 1e-6
    Phi_decay: float = 0.0008


class Dynamics(NamedTuple):
    Phi: jnp.ndarray
    vx: jnp.ndarray
    vy: jnp.ndarray
    S: jnp.ndarray


@jit
def step_fields(
    fields: RSVPFields,
    params: DynamicsParams,
    key: jax.random.PRNGKey | None = None,
) -> RSVPFields:
    """Single RSVP time-step – pure function, fully differentiable."
    """
    Phi, vx, vy, S = fields.Phi, fields.vx, fields.vy, fields.S
    dx = fields.dx
    dt = params.dt

    # Laplacians with periodic BC
    lap_Phi = (
        jnp.roll(Phi, 1, 0) + jnp.roll(Phi, -1, 0) +
        jnp.roll(Phi, 1, 1) + jnp.roll(Phi, -1, 1) - 4 * Phi
    ) / (dx * dx)

    lap_S = (
        jnp.roll(S, 1, 0) + jnp.roll(S, -1, 0) +
        jnp.roll(S, 1, 1) + jnp.roll(S, -1, 1) - 4 * S
    ) / (dx * dx)

    # Gradients
    dPhi_dx = (jnp.roll(Phi, -1, 1) - jnp.roll(Phi, 1, 1)) / (2 * dx)
    dPhi_dy = (jnp.roll(Phi, -1, 0) - jnp.roll(Phi, 1, 0)) / (2 * dx)
    dS_dx = (jnp.roll(S, -1, 1) - jnp.roll(S, 1, 1)) / (2 * dx)
    dS_dy = (jnp.roll(S, -1, 0) - jnp.roll(S, 1, 0)) / (2 * dx)

    grad_Phi_sq = dPhi_dx**2 + dPhi_dy**2

    # Advection
    adv_Phi = vx * dPhi_dx + vy * dPhi_dy
    adv_S = vx * dS_dx + vy * dS_dy

    # Phi update
    new_Phi = Phi + dt * (
        params.D_Phi * lap_Phi +
        adv_Phi -
        params.Phi_decay * Phi
    )

    # v update
    new_vx = (
        -dPhi_dx -
        params.gamma * vx +
        params.beta * vx * dPhi_dx -
        dS_dx
    )
    new_vy = (
        -dPhi_dy -
        params.gamma * vy +
        params.beta * vy * dPhi_dy -
        dS_dy
    )

    # S update
    new_S = S + dt * (
        params.D_S * lap_S -
        adv_S +
        params.kappa * grad_Phi_sq -
        params.chi * S * (1.0 - S / params.S_max)
    )

    new_S = jnp.clip(new_S, params.S_floor, params.S_max)
    new_Phi = jnp.clip(new_Phi, 0.0, None)

    return fields.replace(Phi=new_Phi, vx=new_vx, vy=new_vy, S=new_S)


@jit
def run_n_steps(
    fields: RSVPFields,
    n_steps: int,
    params: DynamicsParams,
    agent_act_fn: Callable[[RSVPFields, jax.random.PRNGKey | None], RSVPFields] | None = None,
    key: jax.random.PRNGKey | None = None,
) -> RSVPFields:
    """Fast multi-step integration with optional per-step agent callback."
    """
    def _body(carry, _):
        f, k = carry
        if k is not None:
            k, sub = jax.random.split(k)
        else:
            sub = None
        f = step_fields(f, params, key=sub)
        if agent_act_fn is not None:
            f = agent_act_fn(f, sub)
        return (f, k), None

    (final_fields, _), _ = jax.lax.scan(
        _body,
        (fields, key),
        xs=None,
        length=n_steps,
    )
    return final_fields


PARAMS_FOREST = DynamicsParams(D_Phi=0.07, D_S=0.20, kappa=0.05, chi=0.15)
PARAMS_SUPPLYCHAIN = DynamicsParams(D_Phi=0.12, D_S=0.14, gamma=0.88, kappa=0.08)
PARAMS_MEME = DynamicsParams(D_Phi=0.20, D_S=0.25, gamma=0.80, chi=0.20, beta=0.15)
PARAMS_CIVILIZATION = DynamicsParams(dt=0.05, D_Phi=0.04, D_S=0.30, gamma=0.95, chi=0.08)
