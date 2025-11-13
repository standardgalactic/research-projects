
"""Lab 32 — Holographic Steganography

Hide a message pattern M(x,y) in the phase of a carrier wave on top of a base field B(x,y):

  S(x,y) = B(x,y) + ε * sin(kx + φ(x,y)),  where φ ∝ M.
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    n=96,
    epsilon=0.1,
    k=4.0,
    seed=0,
)

def _base_field(n, rng):
    x = rng.normal(size=(n, n))
    for _ in range(4):
        x = 0.25 * (np.roll(x,1,0)+np.roll(x,-1,0)+np.roll(x,1,1)+np.roll(x,-1,1))
    return x

def _message_pattern(n):
    yy, xx = np.mgrid[0:n, 0:n]
    cx, cy = n/2, n/2
    r = np.sqrt((xx-cx)**2 + (yy-cy)**2)
    M = np.zeros((n,n))
    M[(r>n*0.18) & (r<n*0.28)] = 1.0
    return M

def init(params=None):
    if params is None:
        params = default_params
    rng = np.random.default_rng(params.get("seed",0))
    n = params["n"]
    B = _base_field(n, rng)
    M = _message_pattern(n)
    M_norm = (M - M.min()) / (M.max() - M.min() + 1e-8)
    yy, xx = np.mgrid[0:n, 0:n]
    phase = M_norm * np.pi
    carrier = params["k"] * xx * (2*np.pi/n)
    S = B + params["epsilon"] * np.sin(carrier + phase)
    return dict(t=0.0, B=B, M=M, S=S)

def step(state, params=None, dt=0.0):
    return state

def frame(state):
    return dict(
        t=state["t"],
        base=state["B"].tolist(),
        message=state["M"].tolist(),
        encoded=state["S"].tolist(),
    )

def run(output_dir=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab32"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    s = init(default_params)
    fr = frame(s)
    with open(output_dir/"frame_000.json","w") as f:
        json.dump(fr,f)
    print(f"Lab32: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
