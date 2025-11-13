
"""Lab 36 — BV Cohomology Explorer (Toy)

We construct a tiny chain complex:

   V2 --d2--> V1 --d1--> V0

with random integer matrices, then compute approximate Betti numbers:

   b0 = dim(ker d1)
   b1 = dim(ker d2) - dim(im d1)
   b2 = dim(V2) - dim(im d2)

using ranks from SVD.
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    dim2=4,
    dim1=5,
    dim0=3,
    seed=0,
)

def _rank(mat, tol=1e-6):
    if mat.size == 0:
        return 0
    s = np.linalg.svd(mat, compute_uv=False)
    return int(np.sum(s > tol))

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed",0))
    d2 = rng.integers(-1,2,size=(params["dim1"], params["dim2"])).astype(float)
    d1 = rng.integers(-1,2,size=(params["dim0"], params["dim1"])).astype(float)
    # enforce d1 d2 = 0 approximately by projecting
    d1d2 = d1 @ d2
    d2 = d2 - 0.1 * d2 @ d1d2.T  # crude correction
    return dict(t=0.0, d1=d1, d2=d2)

def step(state, params=None, dt=0.0):
    return state

def frame(state):
    d1 = state["d1"]
    d2 = state["d2"]
    n2 = d2.shape[1]
    n1 = d1.shape[1]
    n0 = d1.shape[0]

    # ranks
    r1 = _rank(d1)
    r2 = _rank(d2)
    # kernels via rank-nullity
    ker_d1 = n1 - r1
    ker_d2 = n2 - r2
    # approximated Betti numbers
    b0 = ker_d1
    b1 = max(ker_d2 - r1, 0)
    b2 = max(n2 - r2, 0)
    betti = [int(b0), int(b1), int(b2)]
    return dict(
        t=state["t"],
        betti=betti,
        d1=d1.tolist(),
        d2=d2.tolist(),
    )

def run(output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab36"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    s = init(default_params)
    fr = frame(s)
    with open(output_dir/"frame_000.json","w") as f:
        json.dump(fr,f)
    print(f"Lab36: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
