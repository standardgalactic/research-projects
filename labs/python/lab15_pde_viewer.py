
"""Lab 15 – RSVP PDE Viewer
Scalar field Phi on 2D grid with:
  dPhi/dt = D * laplacian(Phi) - dV/dPhi

Potentials:
  "quadratic": V = 0.5 * Phi^2
  "double_well": V = 0.25 * (Phi^2 - 1)^2

Outputs frames:
  data/lab15/<potential>/frame_000.json, ...
Each JSON:
{
  "step": int,
  "width": int,
  "height": int,
  "field": [ [float,...], ... ]
}
"""

import json, random
from pathlib import Path

NX = 32
NY = 32
N_STEPS = 120
DT = 0.05
D = 0.4

def dV_dPhi(phi, potential="quadratic"):
    if potential == "quadratic":
        return phi
    elif potential == "double_well":
        return phi*(phi*phi - 1.0)
    else:
        return phi

def run(output_root="data/lab15", potential="quadratic"):
    root = Path(output_root) / potential
    root.mkdir(parents=True,exist_ok=True)

    Phi = [[(random.random()-0.5)*0.3 for _ in range(NX)] for _ in range(NY)]

    def lap(x,y):
        def wrap(i,n): return i % n
        c = Phi[y][x]
        up = Phi[wrap(y-1,NY)][x]
        dn = Phi[wrap(y+1,NY)][x]
        lf = Phi[y][wrap(x-1,NX)]
        rt = Phi[y][wrap(x+1,NX)]
        return up+dn+lf+rt-4*c

    for step in range(N_STEPS):
        newPhi = [[0.0 for _ in range(NX)] for _ in range(NY)]
        for y in range(NY):
            for x in range(NX):
                d = D*lap(x,y) - dV_dPhi(Phi[y][x], potential)
                newPhi[y][x] = Phi[y][x] + d*DT
        Phi = newPhi

        frame = {
            "step": step,
            "width": NX,
            "height": NY,
            "field": Phi
        }
        with open(root / f"frame_{step:03d}.json", "w") as f:
            json.dump(frame, f)

if __name__ == "__main__":
    run(potential="quadratic")
