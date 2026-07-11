"""
Cross-system invariant test.

Co-test invariant, test pair p = ((0,0),(1,0)) in the twelve-state
system T = C:  Phi_X(x,y) = 0 if there is an admissibility morphism
F: C -> X with F(0,0)=x, F(1,0)=y, else 1.

Monotone over the whole category by composition. On X = C itself the
witnessing morphisms are exactly the endomorphisms, so Phi's values on
C are computable: Phi(x,y)=0 iff (x,y) is in the End(C)-image of p.

We compute: the image set, Phi on all 132 pairs, its distribution over
E-level sets (separation test), and direct verification of (M) and (I)
under all 22 endomorphisms.
"""

import math, heapq
from collections import defaultdict

L, P = 3, 4
states = [(l, p) for l in range(L) for p in range(P)]
def op_a(s): l, p = s; return (l, (p + 1) % P)
def op_b(s): l, p = s; return (l + 1, p) if l < L - 1 else (l, 0)
OP = {"a": op_a, "b": op_b}
def apply_word(word, s):
    for w in word: s = OP[w](s)
    return s

def dijkstra(src):
    dist = {s: math.inf for s in states}; dist[src] = 0.0
    pq = [(0.0, src)]
    while pq:
        d, s = heapq.heappop(pq)
        if d > dist[s]: continue
        for name, c in (("a", 1.0), ("b", 2.0)):
            t = OP[name](s)
            if d + c < dist[t]:
                dist[t] = d + c; heapq.heappush(pq, (d + c, t))
    return dist
E = {s: dijkstra(s) for s in states}

WA = [(), ("a",)]
WB = [(), ("a",), ("b",), ("a", "a")]
def build_F(s0, wa, wb):
    F = {(0, 0): s0}; frontier = [(0, 0)]
    while frontier:
        C = frontier.pop()
        for gen, w in (("a", wa), ("b", wb)):
            Cn = OP[gen](C); tgt = apply_word(w, F[C])
            if Cn in F:
                if F[Cn] != tgt: return None
            else:
                F[Cn] = tgt; frontier.append(Cn)
    if len(F) != len(states): return None
    for C in states:
        if F[op_a(C)] != apply_word(wa, F[C]): return None
        if F[op_b(C)] != apply_word(wb, F[C]): return None
    return F

endos = []
for s0 in states:
    for wa in WA:
        for wb in WB:
            F = build_F(s0, wa, wb)
            if F is not None: endos.append(F)
print(f"endomorphisms: {len(endos)}")

def sufficient(F):
    for C in states:
        for Cp in states:
            e1, e2 = E[C][Cp], E[F[C]][F[Cp]]
            if not (e1 == e2 or (math.isinf(e1) and math.isinf(e2))):
                return False
    return True

# ---- co-test invariant for test pair p ----
p = ((0, 0), (1, 0))
image = {(F[p[0]], F[p[1]]) for F in endos}
image = {q for q in image if q[0] != q[1]}   # collapsed images constrain the diagonal only
print(f"\nEnd(C)-image of test pair {p} (off-diagonal): {sorted(image)}")

pairs = [(C, Cp) for C in states for Cp in states if C != Cp]
Phi = {q: (0 if q in image else 1) for q in pairs}

# separation across E-levels
byE = defaultdict(lambda: defaultdict(list))
for q in pairs:
    e = E[q[0]][q[1]]
    key = 'inf' if math.isinf(e) else e
    byE[key][Phi[q]].append(q)
print("\nPhi values per E-level (level: {value: count}):")
sep = []
for e in sorted(byE, key=lambda x: (x == 'inf', x)):
    counts = {v: len(qs) for v, qs in byE[e].items()}
    print(f"  E={e}: {counts}")
    if len(counts) > 1: sep.append(e)
print(f"levels separated by Phi: {sep}")
if 2.0 in byE and len(byE[2.0]) > 1:
    print(f"  E=2 witnesses: Phi=0 e.g. {byE[2.0][0][:3]},  Phi=1 e.g. {byE[2.0][1][:3]}")

# ---- verify (M) and (I) under all endomorphisms ----
okM, okI = True, True
for F in endos:
    suf = sufficient(F)
    for q in pairs:
        img = (F[q[0]], F[q[1]])
        if img[0] == img[1]: continue
        if Phi[img] > Phi[q]: okM = False
        if suf and Phi[img] != Phi[q]: okI = False
print(f"\n(M) holds under all endomorphisms: {okM}")
print(f"(I) holds under all E-sufficient endomorphisms: {okI}")

# ---- how many mutually inequivalent co-test invariants? ----
# Each pair q defines a co-test; two co-tests coincide on C iff their
# End(C)-upward images coincide. Count distinct restrictions.
def img_of(q):
    s = {(F[q[0]], F[q[1]]) for F in endos}
    return frozenset(x for x in s if x[0] != x[1])
distinct = {img_of(q) for q in pairs}
print(f"\ndistinct co-test invariant restrictions on C: {len(distinct)} (of {len(pairs)} test pairs)")
