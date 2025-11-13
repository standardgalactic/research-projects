
"""Lab 14 – Deck-0 Entropy Reservoir (Python)
Coupled energies:
  dE_v/dt = -k*(E_v - E_h) + eta(t)
  dE_h/dt = eps*(E_v - E_h)

Outputs:
  data/lab14/timeseries.json
{
  "dt": float,
  "k": float,
  "eps": float,
  "series": [ [t, E_v, E_h], ... ]
}
"""

import json, math, random
from pathlib import Path

DT = 0.02
N_STEPS = 4000
K = 0.3
EPS = 0.1
ETA_AMP = 0.3

def run(output_path="data/lab14/timeseries.json", k=K, eps=EPS):
    E_v = 1.0
    E_h = 0.0
    series = []
    t = 0.0
    for n in range(N_STEPS):
        eta = (random.random()-0.5)*ETA_AMP
        dEv = -k*(E_v-E_h) + eta
        dEh = eps*(E_v-E_h)
        E_v += dEv*DT
        E_h += dEh*DT
        if E_v < 0: E_v = 0
        if E_h < 0: E_h = 0
        t += DT
        series.append([t,E_v,E_h])

    out = Path(output_path)
    out.parent.mkdir(parents=True,exist_ok=True)
    with open(out, "w") as f:
        json.dump({
            "dt": DT, "k": k, "eps": eps,
            "series": series
        }, f)

if __name__ == "__main__":
    run()
