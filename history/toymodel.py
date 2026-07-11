"""
Twelve-state continuation system.

States: C = (level l, phase p), l in {0,1,2}, p in {0,1,2,3}.  |C| = 12.

Operations (total maps, noncommuting on the top level):
  a: (l,p) -> (l, (p+1) mod 4)            cost 1   (cheap cyclic adjustment)
  b: (l,p) -> (l+1, p) if l < 2           cost 2   (irreversible promotion)
     (2,p) -> (2, 0)                      cost 2   (saturation resets phase)

No operation decreases l: executable cost E is infinite downward.

Directed repair contrast R (defined independently of the operations):
  R((l,p),(l',p')) = 1*max(l'-l,0) + 5*max(l-l',0) + 0.5*d_cyc(p,p')
  Upgrading structure is cheap to *recognize* (1/level),
  downgrading is expensive but finite (5/level),
  phase mismatch costs 0.5 per cyclic step.
"""

import itertools, math, heapq

L, P = 3, 4
states = [(l, p) for l in range(L) for p in range(P)]
idx = {s: i for i, s in enumerate(states)}

def op_a(s):
    l, p = s
    return (l, (p + 1) % P)

def op_b(s):
    l, p = s
    return (l + 1, p) if l < L - 1 else (l, 0)

OPS = {"a": (op_a, 1.0), "b": (op_b, 2.0)}

# ---- Executable cost E: shortest path over operation applications ----
def dijkstra(src):
    dist = {s: math.inf for s in states}
    dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, s = heapq.heappop(pq)
        if d > dist[s]:
            continue
        for name, (f, c) in OPS.items():
            t = f(s)
            if d + c < dist[t]:
                dist[t] = d + c
                heapq.heappush(pq, (d + c, t))
    return dist

E = {s: dijkstra(s) for s in states}

# ---- Directed repair contrast R ----
def dcyc(p, q):
    d = abs(p - q) % P
    return min(d, P - d)

def R(s, t):
    (l, p), (lp, pp) = s, t
    return 1.0 * max(lp - l, 0) + 5.0 * max(l - lp, 0) + 0.5 * dcyc(p, pp)

# ---- Comparison-execution gap G = E - R ----
print("=== Comparison-execution gap G(C,C') = E - R  (inf where unreachable) ===")
gaps = []
for s in states:
    for t in states:
        if s == t:
            continue
        e, r = E[s][t], R(s, t)
        g = e - r
        gaps.append((g, s, t, e, r))

finite = [x for x in gaps if math.isfinite(x[0])]
infinite = [x for x in gaps if not math.isfinite(x[0])]
print(f"pairs: {len(gaps)}, finite G: {len(finite)}, infinite G (reachability failure): {len(infinite)}")
finite.sort(key=lambda x: -x[0])
print("largest finite gaps (representationally near, operationally far):")
for g, s, t, e, r in finite[:5]:
    print(f"  {s} -> {t}:  E={e:4.1f}  R={r:4.1f}  G={g:4.1f}")
neg = [x for x in finite if x[0] < 0]
print(f"pairs with G<0 (coherence violation R>E): {len(neg)}")
if neg:
    for g, s, t, e, r in neg[:5]:
        print(f"  {s} -> {t}:  E={e:4.1f}  R={r:4.1f}  G={g:4.1f}")

# ---- Torsion witness: operational noncommutativity ----
print("\n=== Noncommutativity of a,b ===")
for s in states:
    ab, ba = op_a(op_b(s)), op_b(op_a(s))
    if ab != ba:
        print(f"  at {s}: a∘b = {ab},  b∘a = {ba}")

# ---- Admissible subset and Pythagorean defect ----
A = [(1, p) for p in range(P)]  # middle level is 'admissible'
print(f"\n=== Admissible subset A = {A} ===")

def proj(s):
    return min(A, key=lambda t: R(s, t))

print("Pythagorean defect Δ(C,C') = R(C,C') - R(C,C*) - R(C*,C'), C' in A:")
rows = []
for s in states:
    cstar = proj(s)
    for t in A:
        d = R(s, t) - R(s, cstar) - R(cstar, t)
        rows.append((d, s, cstar, t))
nonzero = [r for r in rows if abs(r[0]) > 1e-9]
print(f"projection pairs: {len(rows)}, nonzero Δ: {len(nonzero)}")
mn, mx = min(rows)[0], max(rows)[0]
print(f"Δ range: [{mn:.2f}, {mx:.2f}]")
for d, s, cs, t in sorted(rows)[:3] + sorted(rows)[-3:]:
    print(f"  C={s}  C*={cs}  C'={t}:  Δ={d:5.2f}")

# ---- Same defect computed with E instead of R (executable Pythagoras) ----
print("\n=== Executable defect Δ_E (where finite) ===")
def projE(s):
    reach = [(E[s][t], t) for t in A if math.isfinite(E[s][t])]
    return min(reach)[1] if reach else None

cnt, nz = 0, 0
worst = None
for s in states:
    cs = projE(s)
    if cs is None:
        continue
    for t in A:
        if not math.isfinite(E[s][t]):
            continue
        d = E[s][t] - E[s][cs] - E[cs][t]
        cnt += 1
        if abs(d) > 1e-9:
            nz += 1
            if worst is None or abs(d) > abs(worst[0]):
                worst = (d, s, cs, t)
print(f"finite projection pairs: {cnt}, nonzero Δ_E: {nz}")
if worst:
    d, s, cs, t = worst
    print(f"  worst: C={s}  C*={cs}  C'={t}:  Δ_E={d:.2f}")
