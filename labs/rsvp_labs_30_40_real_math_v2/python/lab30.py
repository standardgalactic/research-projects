
"""Lab 30 — Homeostatic Learning Loop

Simple linear network with Hebbian plasticity plus homeostatic weight norm control:

    ΔW_Hebb  = η * x ⊗ y
    ΔW_homeo = -λ * (||W||_F - r0) * W / ||W||_F

W is updated as: W <- W + (ΔW_Hebb + ΔW_homeo) * dt
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    n_in=4,
    n_out=3,
    eta=0.1,
    lam=0.2,
    r0=1.0,
    dt=0.1,
    n_patterns=5,
    seed=0,
)

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed", 0))
    W = rng.normal(scale=0.1, size=(params["n_in"], params["n_out"]))
    X = rng.normal(size=(params["n_patterns"], params["n_in"]))
    Y = rng.normal(size=(params["n_patterns"], params["n_out"]))
    state = dict(
        t=0.0,
        step=0,
        W=W,
        X=X,
        Y=Y,
        mse_history=[],
        norm_history=[],
    )
    return state

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]

    W = state["W"]
    X = state["X"]
    Y = state["Y"]
    rng = np.random.default_rng()

    idx = rng.integers(0, X.shape[0])
    x = X[idx]
    y_target = Y[idx]

    y_hat = x @ W
    err = y_target - y_hat

    dW_hebb = params["eta"] * np.outer(x, y_target)

    norm = np.linalg.norm(W)
    if norm == 0:
        dW_homeo = 0.0 * W
    else:
        dW_homeo = -params["lam"] * (norm - params["r0"]) * (W / norm)

    W = W + (dW_hebb + dW_homeo) * dt

    mse = float(np.mean(err**2))
    state["W"] = W
    state["t"] += dt
    state["step"] += 1
    state["mse_history"].append(mse)
    state["norm_history"].append(float(np.linalg.norm(W)))
    return state

def frame(state):
    W = state["W"]
    return dict(
        t=state["t"],
        step=state["step"],
        W=W.tolist(),
        weight_norm=float(np.linalg.norm(W)),
        mse_history=state["mse_history"],
        norm_history=state["norm_history"],
    )

def run(output_dir=None, steps=200):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab30"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    params = default_params
    s = init(params)
    for _ in range(steps):
        s = step(s, params)
    fr = frame(s)
    with open(output_dir / "frame_000.json", "w") as f:
        json.dump(fr, f)
    print(f"Lab30: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
