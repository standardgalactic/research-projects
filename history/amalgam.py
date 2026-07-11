"""
Amalgamation test.

Construction: given systems X, X' and ordered pairs (x,y) in X,
(x',y') in X', form Y = X ⊔ X' / (x~x', y~y').  Generators of Y are
the disjoint union of generators (acting through the identification).

Claim A (equality forcing): if E_X(x,y) = E_X'(x',y') and
E_X(y,x) = E_X'(y',x'), both inclusions are E-sufficient.

Claim B ((I)-violation for co-tests): glue a second copy T of the
twelve-state system at (t,t') = ((0,0),(1,0)) to the pair
(x,y) = ((0,0),(0,2)) of X = C.  Since E_T(t,t') = 2 = E_X(x,y) and
E_T(t',t) = inf >= E_X(y,x), the inclusion of X is E-sufficient, and
the inclusion of T is a morphism covering the glued pair.  Hence
Phi^{C,(0,0),(1,0)} takes value 1 at ((0,0),(0,2)) in X but value 0 at
its image in Y: condition (I) fails in the category.

We verify both claims by direct computation of E on the amalgams.
"""

import math, heapq

L, P = 3, 4
def op_a(s): l, p = s; return (l, (p + 1) % P)
def op_b(s): l, p = s; return (l + 1, p) if l < L - 1 else (l, 0)

def make_C(tag):
    """The twelve-state system, states tagged to keep copies disjoint."""
    states = [(tag, l, p) for l in range(L) for p in range(P)]
    edges = []  # (src, dst, cost, label)
    for (t, l, p) in states:
        edges.append(((t, l, p), (t,) + op_a((l, p)), 1.0, "a"))
        edges.append(((t, l, p), (t,) + op_b((l, p)), 2.0, "b"))
    return states, edges

def make_V(s_cost, t_cost):
    """Two-state system V_{s,t}: v0->v1 cost s, v1->v0 cost t (omit if inf)."""
    states = [("V", 0), ("V", 1)]
    edges = []
    if math.isfinite(s_cost): edges.append((("V", 0), ("V", 1), s_cost, "f"))
    if math.isfinite(t_cost): edges.append((("V", 1), ("V", 0), t_cost, "r"))
    return states, edges

def dijkstra_all(states, edges):
    adj = {}
    for u, v, c, _ in edges:
        adj.setdefault(u, []).append((v, c))
    D = {}
    for src in states:
        dist = {s: math.inf for s in states}; dist[src] = 0.0
        pq = [(0.0, src)]
        while pq:
            d, s = heapq.heappop(pq)
            if d > dist[s]: continue
            for v, c in adj.get(s, []):
                if d + c < dist[v]:
                    dist[v] = d + c; heapq.heappush(pq, (d + c, v))
        D[src] = dist
    return D

def amalgam(sys1, sys2, pair1, pair2):
    """Glue pair2 of sys2 onto pair1 of sys1; return states, edges, rename map."""
    (st1, ed1), (st2, ed2) = sys1, sys2
    (x, y), (xp, yp) = pair1, pair2
    ren = {xp: x, yp: y}
    f = lambda s: ren.get(s, s)
    states = st1 + [s for s in st2 if s not in ren]
    edges = ed1 + [(f(u), f(v), c, lb) for (u, v, c, lb) in ed2]
    return states, edges, f

def eq(a, b):
    return a == b or (math.isinf(a) and math.isinf(b))

# ---------- Claim A: matched-boundary amalgam is two-sided sufficient ----------
X = make_C("X")
DX = dijkstra_all(*X)
x, y = ("X", 0, 0), ("X", 0, 2)          # E=(2,2)
V = make_V(2.0, 2.0)                      # matching value pair
DV = dijkstra_all(*V)
Ys, Ye, f = amalgam(X, V, (x, y), (("V", 0), ("V", 1)))
DY = dijkstra_all(Ys, Ye)

okX = all(eq(DY[a][b], DX[a][b]) for a in X[0] for b in X[0])
vmap = {("V", 0): x, ("V", 1): y}
okV = all(eq(DY[vmap[a]][vmap[b]], DV[a][b]) for a in V[0] for b in V[0])
print(f"Claim A  (glue C-pair E=(2,2) to V_(2,2)):")
print(f"  inclusion of C is E-sufficient: {okX}")
print(f"  inclusion of V is E-sufficient: {okV}")

# ---------- Claim B: co-test (I)-violation ----------
T = make_C("T")
DT = dijkstra_all(*T)
t0, t1 = ("T", 0, 0), ("T", 1, 0)        # E_T = (2, inf)
print(f"\nClaim B  (glue second copy of C at ((0,0),(1,0)) onto C-pair ((0,0),(0,2))):")
print(f"  boundary check: E_T(t,t')={DT[t0][t1]}  E_X(x,y)={DX[x][y]}  "
      f"E_T(t',t)={DT[t1][t0]}  E_X(y,x)={DX[y][x]}")
Zs, Ze, g = amalgam(X, T, (x, y), (t0, t1))
DZ = dijkstra_all(Zs, Ze)
okX2 = all(eq(DZ[a][b], DX[a][b]) for a in X[0] for b in X[0])
print(f"  inclusion of X is E-sufficient: {okX2}")
# the inclusion of T is a morphism (identity generator assignment) covering
# the glued pair; whether it is sufficient is irrelevant to (I)-violation:
tmap = lambda s: {t0: x, t1: y}.get(s, s)
suffT = all(eq(DZ[tmap(a)][tmap(b)], DT[a][b]) for a in T[0] for b in T[0])
print(f"  inclusion of T is E-sufficient (not required): {suffT}")
print(f"  => co-test Phi^(C,(0,0),(1,0)) at ((0,0),(0,2)):")
print(f"     value in X: 1 (no cover, per crosstest.py)")
print(f"     value at image in amalgam: 0 (covered by the T-inclusion)")
print(f"     while the X-inclusion is E-sufficient  =>  condition (I) FAILS")
