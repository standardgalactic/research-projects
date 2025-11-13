
"""Lab 13 – Ethical Gradient Flow
Gradient descent on V(x,y) = (x^2 - y)^2 + lambda * x * y.

Outputs trajectories as JSON:
  data/lab13/trajectory.json
{
  "lambda": float,
  "dt": float,
  "points": [ [t,x,y], ... ]
}
"""

import json, math

LAM = 0.5
DT = 0.01
N_STEPS = 2000

def V(x,y, lam=LAM):
    return (x*x - y)**2 + lam*x*y

def gradV(x,y, lam=LAM):
    dVdx = 4*x*(x*x - y) + lam*y
    dVdy = -2*(x*x - y) + lam*x
    return dVdx, dVdy

def run(output_path="data/lab13/trajectory.json", lam=LAM):
    x,y = 1.0, 0.0
    pts = []
    for n in range(N_STEPS):
        dVdx,dVdy = gradV(x,y,lam)
        x -= DT*dVdx
        y -= DT*dVdy
        t = n*DT
        pts.append([t,x,y])

    traj = {"lambda": lam, "dt": DT, "points": pts}
    with open(output_path, "w") as f:
        json.dump(traj, f)

if __name__ == "__main__":
    run()
