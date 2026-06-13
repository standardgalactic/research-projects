"""
adm_lab.factories — Canonical graph factories for experiments.

These are not toy examples. They are designed to produce structures
where admissibility phenomena appear clearly enough to be studied.

Each factory returns a fresh AdmissibilityGraph suitable for use
in a RepairSimulator or direct inspection.
"""

from __future__ import annotations

import math
import random
from typing import Optional

from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph


def make_chain(n: int = 10, label: str = "chain") -> AdmissibilityGraph:
    """
    Linear chain: s0 → s1 → … → sn-1
    Maximally fragile under damage: any single edge removal creates a sink.
    """
    g = AdmissibilityGraph(label=label)
    states = [State(label=f"s{i}") for i in range(n)]
    for i in range(n - 1):
        g.add_continuation(Continuation(states[i], states[i+1]))
    return g


def make_grid(rows: int = 4, cols: int = 4, label: str = "grid") -> AdmissibilityGraph:
    """
    Rectangular grid with rightward and downward edges.
    Corner states (bottom-right) become sinks.
    Interesting for observing repair corridors.
    """
    g = AdmissibilityGraph(label=label)
    states = {}
    for r in range(rows):
        for c in range(cols):
            s = State(label=f"r{r}c{c}")
            states[(r, c)] = s

    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                g.add_continuation(Continuation(states[(r, c)], states[(r, c+1)]))
            if r + 1 < rows:
                g.add_continuation(Continuation(states[(r, c)], states[(r+1, c)]))

    return g


def make_hub_and_spoke(
    spokes: int = 6,
    spoke_length: int = 3,
    label: str = "hub_spoke",
) -> AdmissibilityGraph:
    """
    Central hub with radiating spokes.
    The hub has high fan-out; spoke tips are sinks.
    Tests whether hub-first repair strategy outperforms random.
    """
    g = AdmissibilityGraph(label=label)
    hub = State(label="hub")

    for i in range(spokes):
        prev = hub
        for j in range(spoke_length):
            node = State(label=f"spoke{i}_d{j}")
            g.add_continuation(Continuation(prev, node))
            prev = node

    return g


def make_random_dag(
    n: int = 20,
    edge_density: float = 0.15,
    seed: Optional[int] = None,
    label: str = "random_dag",
) -> AdmissibilityGraph:
    """
    Random directed acyclic graph.
    Edge density controls connectivity.
    The canonical general-purpose experiment substrate.
    """
    rng = random.Random(seed)
    g = AdmissibilityGraph(label=label)
    states = [State(label=f"n{i}") for i in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < edge_density:
                w = round(rng.uniform(0.5, 2.0), 2)
                g.add_continuation(Continuation(states[i], states[j], weight=w))

    return g


def make_bottleneck(
    pre_size: int = 5,
    post_size: int = 5,
    label: str = "bottleneck",
) -> AdmissibilityGraph:
    """
    Two fully-connected clusters joined by a single bottleneck state.
    The bottleneck state has fan-out 1 after the bridge — directly tests
    bottleneck detection and the effect of bottleneck damage.
    """
    g = AdmissibilityGraph(label=label)
    pre = [State(label=f"pre{i}") for i in range(pre_size)]
    neck = State(label="neck")
    post = [State(label=f"post{i}") for i in range(post_size)]

    for p in pre:
        g.add_continuation(Continuation(p, neck))

    for q in post:
        g.add_continuation(Continuation(neck, q))

    # intra-cluster edges
    for i in range(pre_size):
        for j in range(i+1, pre_size):
            g.add_continuation(Continuation(pre[i], pre[j]))

    for i in range(post_size):
        for j in range(i+1, post_size):
            g.add_continuation(Continuation(post[i], post[j]))

    return g


def make_repair_corridor_test(
    n: int = 15,
    seed: Optional[int] = None,
    label: str = "repair_corridor",
) -> AdmissibilityGraph:
    """
    A graph designed to exhibit repair corridors: a primary path with
    high-fan-out hubs, and peripheral paths with lower connectivity.

    After damage, the question is: does repair tend to route through the
    high-fan-out spine, or is recovery distributed?
    """
    rng = random.Random(seed)
    g = AdmissibilityGraph(label=label)

    # Spine: high-connectivity chain
    spine = [State(label=f"sp{i}") for i in range(n // 2)]
    for i in range(len(spine) - 1):
        g.add_continuation(Continuation(spine[i], spine[i+1]))
        # back-links to make it robust
        if i > 0:
            g.add_continuation(Continuation(spine[i], spine[i-1]))

    # Periphery: low-connectivity branches
    for i, s in enumerate(spine[::2]):
        branch = State(label=f"br{i}")
        g.add_continuation(Continuation(s, branch))
        leaf = State(label=f"lf{i}")
        g.add_continuation(Continuation(branch, leaf))

    # Cross-links
    for _ in range(n // 4):
        a = rng.choice(spine)
        b = rng.choice(spine)
        if a.id != b.id:
            g.add_continuation(Continuation(a, b, weight=rng.uniform(0.5, 1.5)))

    return g


def apply_weight_constraint(
    graph: AdmissibilityGraph,
    min_weight: float = 1.0,
    name: str = "weight_threshold",
) -> AdmissibilityGraph:
    """
    Apply a weight-threshold constraint to a graph.
    Returns the same graph (modified in place) for chaining.
    Continuations below min_weight become inadmissible.
    """
    c = Constraint(
        predicate=lambda cont: cont.weight >= min_weight,
        name=name,
    )
    graph.add_constraint(c)
    return graph
