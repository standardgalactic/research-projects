
"""Lab 12 – Semantic Field Horizon (2D)
2D diffusion with global smoothing toward average.

Equation (discretized):
  dPhi/dt = D * laplacian(Phi) - lam * (Phi - mean(Phi))

Outputs JSON frames:
  data/lab12/frame_000.json, etc.
Each JSON:
{
  "step": int,
  "width": int,
  "height": int,
  "field": [ [float,...], ... ]
}
"""

import json, os, random
from pathlib import Path

NX = 32
NY = 32
N_STEPS = 120
DT = 0.05
D = 0.6
LAM = 0.1

def run(output_dir="data/lab12"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # initialize with a few random "negentropy islands"
    Phi = [[0.0 for _ in range(NX)] for _ in range(NY)]
    for _ in range(12):
        cx = random.randrange(NX)
        cy = random.randrange(NY)
        amp = random.uniform(0.5, 1.5)
        Phi[cy][cx] += amp

    def lap(x,y):
        # periodic boundaries
        def wrap(i, n): return i % n
        c = Phi[y][x]
        up = Phi[wrap(y-1,NY)][x]
        dn = Phi[wrap(y+1,NY)][x]
        lf = Phi[y][wrap(x-1,NX)]
        rt = Phi[y][wrap(x+1,NX)]
        return (up+dn+lf+rt-4*c)

    for step in range(N_STEPS):
        avg = sum(sum(row) for row in Phi) / (NX*NY)
        newPhi = [[0.0 for _ in range(NX)] for _ in range(NY)]
        for y in range(NY):
            for x in range(NX):
                d = D*lap(x,y) - LAM*(Phi[y][x]-avg)
                newPhi[y][x] = Phi[y][x] + d*DT
        Phi = newPhi

        frame = {
            "step": step,
            "width": NX,
            "height": NY,
            "field": Phi,
        }
        with open(out / f"frame_{step:03d}.json", "w") as f:
            json.dump(frame, f)

if __name__ == "__main__":
    run()
