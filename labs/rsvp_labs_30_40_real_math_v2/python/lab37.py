
"""Lab 37 — Holographic Steganography Network

Reuse Lab 32 encoding and create N observer projections via random linear filters.
We then compute reconstruction quality when averaging K observers.
"""

import json
import numpy as np
from pathlib import Path
import lab32 as lab32_mod  # relative import within python package if used that way

default_params = dict(
    n_observers=6,
    k_required=3,
    seed=0,
)

def init(params=None):
    if params is None:
        params = default_params
    # get encoded field from Lab 32
    base_state = lab32_mod.init()
    S = base_state["S"]
    rng = np.random.default_rng(params.get("seed",0))
    n = S.shape[0]
    observers = []
    for _ in range(params["n_observers"]):
        kernel = rng.normal(size=(3,3))
        kernel /= np.sum(np.abs(kernel)) + 1e-8
        obs = np.zeros_like(S)
        # simple valid conv ignoring boundary
        for i in range(1,n-1):
            for j in range(1,n-1):
                patch = S[i-1:i+2, j-1:j+2]
                obs[i,j] = np.sum(patch*kernel)
        observers.append(dict(kernel=kernel, view=obs))
    return dict(t=0.0, S=S, observers=observers)

def step(state, params=None, dt=0.0):
    return state

def frame(state, params=None):
    if params is None:
        params = default_params
    S = state["S"]
    obs_views = [o["view"] for o in state["observers"]]
    n_obs = len(obs_views)
    # reconstruction quality for using first K observers
    qualities = []
    for K in range(1, n_obs+1):
        recon = np.mean(obs_views[:K], axis=0)
        mse = float(np.mean((recon - S)**2))
        qualities.append(mse)
    return dict(
        t=state["t"],
        encoded=S.tolist(),
        observers=[o["view"].tolist() for o in state["observers"]],
        qualities=qualities,
    )

def run(output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab37"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    s = init(default_params)
    fr = frame(s, default_params)
    with open(output_dir/"frame_000.json","w") as f:
        json.dump(fr,f)
    print(f"Lab37: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
