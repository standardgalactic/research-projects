
"""Lab 35 — Observer Holography

Create a 3D scalar field Φ(x,y,z) as a sum of Gaussians, then compute:

- a central slice in z
- a simple projection by averaging along z (as if an observer integrates along depth)
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    shape=(48,48,24),
    n_blobs=3,
    seed=0,
)

def _make_volume(params):
    nx, ny, nz = params["shape"]
    rng = np.random.default_rng(params.get("seed",0))
    vol = np.zeros((nx,ny,nz))
    for _ in range(params["n_blobs"]):
        cx, cy, cz = rng.integers(0,nx), rng.integers(0,ny), rng.integers(0,nz)
        sx, sy, sz = rng.uniform(3,8), rng.uniform(3,8), rng.uniform(2,6)
        x,y,z = np.mgrid[0:nx,0:ny,0:nz]
        blob = np.exp(-(((x-cx)/sx)**2 + ((y-cy)/sy)**2 + ((z-cz)/sz)**2))
        vol += blob
    return vol

def init(params=None):
    if params is None:
        params = default_params
    vol = _make_volume(params)
    return dict(t=0.0, vol=vol)

def step(state, params=None, dt=0.0):
    return state

def frame(state):
    vol = state["vol"]
    nz = vol.shape[2]
    slice_xy = vol[:,:,nz//2]
    proj = vol.mean(axis=2)
    return dict(
        t=state["t"],
        slice=slice_xy.tolist(),
        projection=proj.tolist(),
    )

def run(output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab35"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    s = init(default_params)
    fr = frame(s)
    with open(output_dir/"frame_000.json","w") as f:
        json.dump(fr,f)
    print(f"Lab35: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
