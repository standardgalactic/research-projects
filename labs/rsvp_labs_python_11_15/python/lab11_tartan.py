
"""Lab 11 – TARTAN Lattice
Python engine: generates JSON snapshots of a lattice of nodes and morphisms.

Outputs:
  data/lab11/frame_000.json, frame_001.json, ... etc.

Each frame JSON:
{
  "step": int,
  "nodes": [
    {"i": int, "j": int, "energy": float}
  ],
  "edges": [
    {"i": int, "j": int, "k": int, "l": int, "tension": float}
  ]
}
"""

import json, os, math, random
from pathlib import Path

GRID_N = 8
N_STEPS = 120
DT = 0.05
ALPHA = 1.0   # tension relaxation
BETA = 0.2    # node response to tension

def idx(i,j):
    return i*GRID_N + j

def run(output_dir="data/lab11"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # node energies
    E = [random.uniform(-1,1) for _ in range(GRID_N*GRID_N)]
    # simple symmetric edge tensions between nearest neighbors (i,j)-(i+1,j) and (i,j)-(i,j+1)
    horiz = [[0.0]*(GRID_N-1) for _ in range(GRID_N)]
    vert  = [[0.0]*GRID_N for _ in range(GRID_N-1)]

    for step in range(N_STEPS):
        # update edge tensions towards difference of neighbor node energies
        for i in range(GRID_N):
            for j in range(GRID_N-1):
                diff = E[idx(i,j+1)] - E[idx(i,j)]
                horiz[i][j] += -ALPHA*(horiz[i][j] - diff)*DT
        for i in range(GRID_N-1):
            for j in range(GRID_N):
                diff = E[idx(i+1,j)] - E[idx(i,j)]
                vert[i][j] += -ALPHA*(vert[i][j] - diff)*DT

        # update node energies based on incident tension
        newE = E[:]
        for i in range(GRID_N):
            for j in range(GRID_N):
                acc = 0.0
                # horizontal neighbors
                if j>0:
                    acc += horiz[i][j-1]
                if j<GRID_N-1:
                    acc -= horiz[i][j]
                # vertical neighbors
                if i>0:
                    acc += vert[i-1][j]
                if i<GRID_N-1:
                    acc -= vert[i][j]
                newE[idx(i,j)] += BETA*acc*DT
        E = newE

        # package snapshot
        nodes = [
            {"i": i, "j": j, "energy": E[idx(i,j)]}
            for i in range(GRID_N) for j in range(GRID_N)
        ]
        edges = []
        for i in range(GRID_N):
            for j in range(GRID_N-1):
                edges.append({
                    "i": i, "j": j,
                    "k": i, "l": j+1,
                    "tension": horiz[i][j]
                })
        for i in range(GRID_N-1):
            for j in range(GRID_N):
                edges.append({
                    "i": i, "j": j,
                    "k": i+1, "l": j,
                    "tension": vert[i][j]
                })

        frame = {"step": step, "nodes": nodes, "edges": edges}
        with open(out / f"frame_{step:03d}.json", "w") as f:
            json.dump(frame, f)

if __name__ == "__main__":
    run()
