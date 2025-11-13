
"""Lab 39 — Meta-Observer Collapse (Adaptive Kuramoto)

N phases θ_i with adaptive coupling matrix K_ij:

  θdot_i = ω_i + (1/N) Σ_j K_ij sin(θ_j - θ_i)

  Kdot_ij = α (cos(θ_i-θ_j) - K_ij) - β K_ij
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    N=16,
    alpha=0.1,
    beta=0.05,
    K0=0.0,
    dt=0.05,
    steps=400,
    seed=0,
)

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed",0))
    N = params["N"]
    theta = rng.uniform(0, 2*np.pi, size=N)
    omega = rng.normal(scale=0.1, size=N)
    K = np.full((N,N), params["K0"])
    np.fill_diagonal(K, 0.0)
    return dict(t=0.0, theta=theta, omega=omega, K=K, R_hist=[])

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]
    theta = state["theta"]
    omega = state["omega"]
    K = state["K"]
    N = theta.size

    # Kuramoto dynamics
    theta_diff = theta.reshape(1,-1) - theta.reshape(-1,1)
    coupling_term = (K * np.sin(theta_diff)).sum(axis=1) / N
    theta = theta + dt * (omega + coupling_term)

    # adaptive K
    cos_diff = np.cos(theta_diff)
    dK = params["alpha"] * (cos_diff - K) - params["beta"] * K
    np.fill_diagonal(dK, 0.0)
    K = K + dt * dK

    # order parameter
    R = np.abs(np.mean(np.exp(1j*theta)))
    state["theta"], state["K"] = theta, K
    state["t"] += dt
    state["R_hist"].append(float(R))
    return state

def frame(state):
    theta = state["theta"]
    K = state["K"]
    R = float(np.abs(np.mean(np.exp(1j*theta))))
    return dict(
        t=state["t"],
        theta=theta.tolist(),
        K=K.tolist(),
        R=R,
        R_hist=state["R_hist"],
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab39"
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
    with open(output_dir/"frame_000.json","w") as f:
        json.dump(fr,f)
    print(f"Lab39: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
