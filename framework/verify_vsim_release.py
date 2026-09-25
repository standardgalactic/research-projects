"""
Checks on the released VSIM figure data.
Clone first:
  git clone https://github.com/SpinX-Lab/Voltage-controlled-Spintronic-Ising-Machine.git vsim
  cd vsim && python3 ../verify_vsim_release.py
Requires numpy. Public domain.
"""
import itertools
import numpy as np

# ---------- Fig. 4: global routing (instance as defined in plot_Fig4.ipynb) ----------
T = [(6, 12), (0, 7), (6, 0), (8, 10), (14, 5), (4, 5), (12, 3)]          # terminals
S = [(6, 5), (6, 7), (6, 10), (8, 3), (12, 10), (12, 5), (6, 3), (4, 7)]  # candidate Steiner points
P = T + S
V, U = len(P), len(T)
d = np.array([[abs(a[0]-b[0]) + abs(a[1]-b[1]) for b in P] for a in P])
br = np.array([[0 if (a[0] == b[0] or a[1] == b[1]) else 1 for b in P] for a in P])

def components(s):
    """Same terms as calculate_Hamiltonian in plot_Fig4.ipynb."""
    e = (s[0:V, :] + 1) // 2
    x = (s[V:2*V, :] + 1) // 2
    Hc1 = sum((sum(e[m, n] for m in range(V) if m != n) - 1)**2 for n in range(1, U))
    Hc2 = sum(x[m, k] + x[m, n]*x[n, k] - x[m, n]*x[m, k] - x[m, k]*x[n, k]
              for k in range(3, V) for m in range(1, k-1) for n in range(m+1, k))
    Hc3 = sum(e[m, n]*(1 - x[m, n]) + e[n, m]*x[m, n] for n in range(2, V) for m in range(1, n))
    Hc4 = sum(V*e[m, n]*e[k, n] for n in range(U, V) for m in range(V)
              for k in range(m+1, V) if m != n and k != n)
    Hc5 = sum((1 - sum(e[m, n] for m in range(V) if m != n)) *
              sum(e[n, m] for m in range(1, V) if m != n) for n in range(U, V))
    Hc6 = sum(br[m, n]*e[m, n] for m in range(V) for n in range(1, V))
    Opt = sum(d[m, n]*e[m, n] for m in range(V) for n in range(1, V))
    return Opt, Hc1, Hc2, Hc3, Hc4, Hc5, Hc6

def H(c):  # weights as in the notebook: 10, 10, 6, 6
    return c[0] + 10*c[1] + 10*(c[2] + c[3]) + 6*(c[4] + c[5]) + 6*c[6]

traj = np.load("data/Fig4/MTJ_s_process.npy")
Hs = np.array([H(components(traj[t])) for t in range(len(traj))])
print("Fig 4: trajectory min H =", Hs.min(), "final H =", Hs[-1],
      "final components =", components(traj[-1]))

def mst(nodes):
    inT, cost, par = {nodes[0]}, 0, {}
    while len(inT) < len(nodes):
        cand = [(d[a, b], a, b) for a in inT for b in nodes if b not in inT and not br[a, b]]
        if not cand:
            return None, None
        w, a, b = min(cand)
        cost += w; par[b] = a; inT.add(b)
    return cost, par

best = None
for r in range(len(S) + 1):
    for sub in itertools.combinations(range(U, V), r):
        c, par = mst(list(range(U)) + list(sub))
        if c is not None and (best is None or c < best[0]):
            best = (c, sub, par)
print("Fig 4: exhaustive minimum tree length =", best[0])

# encode that tree as spins and evaluate with the notebook's Hamiltonian
cost, sub, par = best
order = [0] + [n for n in par]            # insertion order from the root
rank = {n: i for i, n in enumerate(order)}
for n in range(V):
    rank.setdefault(n, len(rank))
s = -np.ones((2*V, V), dtype=np.int32)
for child, parent in par.items():
    s[parent, child] = 1
for m in range(V):
    for n in range(V):
        if m != n and rank[m] < rank[n]:
            s[V + m, n] = 1
print("Fig 4: that tree under the notebook Hamiltonian:", components(s), "H =", H(components(s)))

# ---------- Fig. 5: layer assignment, released J and h ----------
J = np.load("data/Fig5/J.npy"); h = np.load("data/Fig5/h.npy")
E = lambda v: -(v @ J @ v) - h @ v   # equals the notebook's lambda_D*H_D + lambda_V*H_V up to a constant
for k in (1, 2):
    tr = np.load(f"data/Fig5/s_process_{k}.npy").astype(float)
    e = np.array([E(v) for v in tr])
    print(f"Fig 5 trajectory {k}: min E = {e.min():.4f}, final E = {e[-1]:.4f}")

rng = np.random.default_rng(0)
bestE = np.inf
Js = 2*J
for rep in range(2000):
    v = rng.choice([-1., 1.], len(h)); L = Js @ v + h
    for Tt in np.geomspace(50, 0.01, 4000):
        i = rng.integers(len(h)); dE = 2*v[i]*L[i]
        if dE <= 0 or rng.random() < np.exp(-dE/Tt):
            L -= 2*v[i]*Js[:, i]; v[i] = -v[i]
    bestE = min(bestE, E(v))
print(f"Fig 5: best E over 2000 classical annealing restarts = {bestE:.4f}")
