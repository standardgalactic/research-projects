
"""Lab 31 — Functor Field Collisions

Two scalar fields F_A, F_B on a 2D grid with coupled dynamics:

  ∂_t F_A = c1 ∇² F_A - μ(F_A - F_B) - σ tanh(F_A - F_B)
  ∂_t F_B = c2 ∇² F_B - μ(F_B - F_A) - σ tanh(F_B - F_A)

Collision energy C(t) = mean((F_A - F_B)^2).
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    n=64,
    c1=0.2,
    c2=0.2,
    mu=0.15,
    sigma=0.1,
    dt=0.1,
    steps=200,
    seed=0,
)

def _laplacian(field):
    up    = np.roll(field, -1, axis=0)
    down  = np.roll(field,  1, axis=0)
    left  = np.roll(field, -1, axis=1)
    right = np.roll(field,  1, axis=1)
    return up + down + left + right - 4.0 * field

def init(params=None):
    if params is None:
        params = default_params
    n = params["n"]
    rng = np.random.default_rng(params.get("seed", 0))
    FA = rng.normal(scale=0.2, size=(n, n))
    FB = rng.normal(scale=0.2, size=(n, n))
    return dict(t=0.0, FA=FA, FB=FB, collisions=[])

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]

    FA = state["FA"]
    FB = state["FB"]

    lapA = _laplacian(FA)
    lapB = _laplacian(FB)

    diffAB = FA - FB
    diffBA = -diffAB

    dFA = params["c1"] * lapA - params["mu"] * diffAB - params["sigma"] * np.tanh(diffAB)
    dFB = params["c2"] * lapB - params["mu"] * diffBA - params["sigma"] * np.tanh(diffBA)

    FA = FA + dt * dFA
    FB = FB + dt * dFB

    state["FA"] = FA
    state["FB"] = FB
    state["t"] += dt
    C = float(np.mean(diffAB**2))
    state["collisions"].append(C)
    return state

def frame(state):
    FA = state["FA"]
    FB = state["FB"]
    C = float(np.mean((FA - FB)**2))
    return dict(
        t=state["t"],
        F_A=FA.tolist(),
        F_B=FB.tolist(),
        collision_energy=C,
        collision_history=state["collisions"],
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab31"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    params = default_params
    if steps is None:
        steps = params["steps"]
    s = init(params)
    for _ in range(steps):
        s = step(s, params)
    fr = frame(s)
    with open(output_dir / "frame_000.json", "w") as f:
        json.dump(fr, f)
    print(f"Lab31: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
