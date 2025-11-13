
"""Lab 40 — Observer Holography II: Bayesian Perception

We simulate:

- True field S_true: simple blob pattern
- Observation O: S_true + Gaussian noise
- Reconstruction S_hat: gradient descent on energy

  E(S) = ||O - S||^2 / (2σ^2) + λ * ||∇S||^2

This is a crude MAP estimator with smoothness prior.
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    n=64,
    sigma=0.2,
    lam=0.2,
    steps=200,
    dt=0.2,
    seed=0,
)

def _make_true(n):
    yy, xx = np.mgrid[0:n, 0:n]
    cx, cy = n*0.35, n*0.6
    r2 = (xx-cx)**2 + (yy-cy)**2
    blob = np.exp(-r2/(2*(n*0.12)**2))
    return blob

def _laplacian(Z):
    return (
        np.roll(Z,1,0) + np.roll(Z,-1,0) +
        np.roll(Z,1,1) + np.roll(Z,-1,1) -
        4*Z
    )

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed",0))
    n = params["n"]
    S_true = _make_true(n)
    O = S_true + params["sigma"] * rng.normal(size=(n,n))
    S_hat = np.zeros_like(S_true)
    return dict(t=0.0, S_true=S_true, O=O, S_hat=S_hat, E_hist=[])

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]
    S_hat = state["S_hat"]
    O = state["O"]

    # gradient of data term
    grad_data = (S_hat - O) / (params["sigma"]**2)
    # gradient of smoothness term ~ -λ ∇² S_hat (since E ~ λ ||∇S||^2)
    grad_smooth = -params["lam"] * _laplacian(S_hat)
    grad = grad_data + grad_smooth

    S_hat = S_hat - dt * grad

    # energy scalar
    data_term = 0.5 * np.mean((O - S_hat)**2) / (params["sigma"]**2)
    smooth_term = params["lam"] * np.mean(np.square(np.gradient(S_hat)[0]) + np.square(np.gradient(S_hat)[1]))
    E = float(data_term + smooth_term)

    state["S_hat"] = S_hat
    state["t"] += dt
    state["E_hist"].append(E)
    return state

def frame(state):
    return dict(
        t=state["t"],
        true=state["S_true"].tolist(),
        obs=state["O"].tolist(),
        recon=state["S_hat"].tolist(),
        E_hist=state["E_hist"],
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab40"
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
    print(f"Lab40: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
