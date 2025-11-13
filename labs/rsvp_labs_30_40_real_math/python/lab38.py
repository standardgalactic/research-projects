
"""Lab 38 — Dissipative Morphogenesis 2.0

Gray–Scott reaction–diffusion system:

  ∂_t U = D_u ∇²U - U V^2 + f(1-U)
  ∂_t V = D_v ∇²V + U V^2 - (f+k)V
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    n=80,
    Du=0.16,
    Dv=0.08,
    f=0.060,
    k=0.062,
    dt=1.0,
    steps=500,
)

def _laplacian(Z):
    return (
        np.roll(Z,1,0) + np.roll(Z,-1,0) +
        np.roll(Z,1,1) + np.roll(Z,-1,1) -
        4*Z
    )

def init(params=None):
    if params is None:
        params = default_params
    n = params["n"]
    U = np.ones((n,n))
    V = np.zeros((n,n))
    # add small square perturbation
    r = slice(n//2-5, n//2+5)
    U[r,r] = 0.5
    V[r,r] = 0.25
    return dict(t=0.0, U=U, V=V)

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]
    U, V = state["U"], state["V"]
    Lu = _laplacian(U)
    Lv = _laplacian(V)
    uvv = U * V * V
    dU = params["Du"]*Lu - uvv + params["f"]*(1-U)
    dV = params["Dv"]*Lv + uvv - (params["f"]+params["k"])*V
    U = U + dt*dU
    V = V + dt*dV
    state["U"], state["V"] = U, V
    state["t"] += dt
    return state

def frame(state):
    return dict(
        t=state["t"],
        U=state["U"].tolist(),
        V=state["V"].tolist(),
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab38"
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
    print(f"Lab38: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
