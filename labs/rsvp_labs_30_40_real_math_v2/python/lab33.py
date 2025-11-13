
"""Lab 33 — BV Entropy Symplectics

Hamiltonian:
  H(q,p) = 1/2 (q^2 + p^2) + λ q^2 p^2

Symplectic Euler integration:
  p_{n+1} = p_n - dt * dH/dq(q_n, p_n)
  q_{n+1} = q_n + dt * dH/dp(q_n, p_{n+1})
"""

import json
import numpy as np
from pathlib import Path

default_params = dict(
    lambda_val=0.2,
    dt=0.02,
    steps=1000,
    q0=0.4,
    p0=0.0,
)

def _dH_dq(q,p,lam):
    return q + 2*lam*q*p*p

def _dH_dp(q,p,lam):
    return p + 2*lam*p*q*q

def _H(q,p,lam):
    return 0.5*(q*q + p*p) + lam*q*q*p*p

def init(params=None):
    if params is None:
        params = default_params
    return dict(
        t=0.0,
        q=params["q0"],
        p=params["p0"],
        q_hist=[],
        p_hist=[],
        E_hist=[],
    )

def step(state, params=None, dt=None):
    if params is None:
        params = default_params
    if dt is None:
        dt = params["dt"]
    lam = params["lambda_val"]

    q = state["q"]
    p = state["p"]

    p_next = p - dt * _dH_dq(q, p, lam)
    q_next = q + dt * _dH_dp(q, p_next, lam)

    E = float(_H(q_next, p_next, lam))

    state["q"] = q_next
    state["p"] = p_next
    state["t"] += dt
    state["q_hist"].append(float(q_next))
    state["p_hist"].append(float(p_next))
    state["E_hist"].append(E)
    return state

def frame(state):
    lam = default_params["lambda_val"]
    if state["E_hist"]:
        E = state["E_hist"][-1]
    else:
        E = float(_H(state["q"], state["p"], lam))
    return dict(
        t=state["t"],
        q=state["q"],
        p=state["p"],
        energy=E,
        q_hist=state["q_hist"],
        p_hist=state["p_hist"],
        E_hist=state["E_hist"],
    )

def run(output_dir=None, steps=None):
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "data" / "lab33"
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
    print(f"Lab33: wrote frame_000.json to {output_dir}")

if __name__ == "__main__":
    run()
