
"""Lab 34 — TARTAN Hypernetwork

3D tensor T[i,j,k] with neighbor averaging:

    T <- α T + β * neighbor_avg(T) + η * noise

We also compute a crude 'braid index' as the variance across the k-axis.
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    shape=(16,16,8),
    alpha=0.9,
    beta=0.1,
    eta=0.01,
    steps=100,
    dt=1.0,
    seed=0,
)

def _neighbor_avg(T):
    # 6-neighbor average in 3D with periodic boundaries
    x = np.roll(T, 1, axis=0) + np.roll(T, -1, axis=0)
    y = np.roll(T, 1, axis=1) + np.roll(T, -1, axis=1)
    z = np.roll(T, 1, axis=2) + np.roll(T, -1, axis=2)
    return (x + y + z) / 6.0

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed",0))
    T = rng.normal(scale=0.2, size=params["shape"])
    return dict(t=0.0, T=T)

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]
    rng = np.random.default_rng()
    T = state["T"]
    navg = _neighbor_avg(T)
    T = params["alpha"] * T + params["beta"] * navg + params["eta"] * rng.normal(size=T.shape)
    state["T"] = T
    state["t"] += dt
    return state

def frame(state):
    T = state["T"]
    proj = T.mean(axis=2)
    braid_index = float(np.var(T, axis=2).mean())
    return dict(
        t=state["t"],
        projection=proj.tolist(),
        braid_index=braid_index,
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab34"
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
    print(f"Lab34: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
