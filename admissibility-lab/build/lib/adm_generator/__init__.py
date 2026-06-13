"""
adm.generator — Separating generation from constraint filtering.

The Generative Compression Hypothesis: two generators can produce
identical reachable inventories but different reachable volumes.

This module separates what generates continuations from what constrains them.
Currently these are conflated in the factory functions: graph structure
determines both what continuations exist and (implicitly) which are reachable.

Separating them makes the compression hypothesis directly testable:
    gen_A = DenseGenerator(n=20)
    gen_B = SparseGenerator(n=20)
    # same states, same inventory of possible continuations...
    g_A = gen_A.build(constraints=[heavy_constraint])
    g_B = gen_B.build(constraints=[heavy_constraint])
    # ...but different reachable volumes.

A Generator is a protocol for producing a set of candidate Continuations
from a set of States. Constraints are applied afterward.

This makes the generator/constraint split the computational instantiation
of the framework's core asymmetry: generation is unconstrained possibility,
admissibility is what survives.
"""

from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Sequence

from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph


# ---------------------------------------------------------------------------
# Base Generator
# ---------------------------------------------------------------------------

class Generator(ABC):
    """
    Abstract base: produces candidate Continuations from a set of States.

    Subclasses implement _generate_candidates().
    The build() method applies constraints and returns the graph.
    """

    def __init__(self, label: str = "") -> None:
        self.label = label

    @abstractmethod
    def _generate_candidates(self, states: List[State]) -> List[Continuation]:
        """Produce all candidate continuations (before constraint filtering)."""
        ...

    def build(
        self,
        states: List[State],
        constraints: Sequence[Constraint] = (),
    ) -> AdmissibilityGraph:
        """
        Build an AdmissibilityGraph from states, candidates, and constraints.
        """
        candidates = self._generate_candidates(states)
        g = AdmissibilityGraph(label=self.label)
        for cont in candidates:
            g.add_continuation(cont)
        for c in constraints:
            g.add_constraint(c)
        return g

    @property
    def name(self) -> str:
        return self.__class__.__name__


# ---------------------------------------------------------------------------
# Concrete generators
# ---------------------------------------------------------------------------

class DenseGenerator(Generator):
    """
    Generates all forward edges in a topologically ordered set of states.
    Maximum possible continuation inventory for n states: n*(n-1)/2 edges.

    This is the upper bound on reachable volume for a given state set.
    """

    def __init__(self, n: int = 10, seed: Optional[int] = None, label: str = "") -> None:
        super().__init__(label or f"dense_{n}")
        self.n = n
        self.seed = seed

    def _generate_candidates(self, states: List[State]) -> List[Continuation]:
        conts = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                conts.append(Continuation(states[i], states[j], weight=1.0))
        return conts

    def make_states(self) -> List[State]:
        return [State(label=f"d{i}") for i in range(self.n)]

    def build_default(self, constraints: Sequence[Constraint] = ()) -> AdmissibilityGraph:
        return self.build(self.make_states(), constraints)


class SparseGenerator(Generator):
    """
    Generates only a random subset of forward edges.
    Same state set as DenseGenerator but fewer candidate continuations.

    Demonstrates that constraint-identical graphs can differ in reachable
    volume purely through generation protocol differences.
    """

    def __init__(
        self,
        n: int = 10,
        density: float = 0.2,
        seed: Optional[int] = None,
        label: str = "",
    ) -> None:
        super().__init__(label or f"sparse_{n}_{density:.0%}")
        self.n = n
        self.density = density
        self.seed = seed

    def _generate_candidates(self, states: List[State]) -> List[Continuation]:
        rng = random.Random(self.seed)
        conts = []
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                if rng.random() < self.density:
                    conts.append(Continuation(states[i], states[j], weight=1.0))
        return conts

    def make_states(self) -> List[State]:
        return [State(label=f"s{i}") for i in range(self.n)]

    def build_default(self, constraints: Sequence[Constraint] = ()) -> AdmissibilityGraph:
        return self.build(self.make_states(), constraints)


class LayeredGenerator(Generator):
    """
    Generates edges only between adjacent layers (like a neural network).
    Each layer has `width` states; edges go from layer k to layer k+1 only.

    Demonstrates generation protocol as architectural constraint:
    the layer structure limits reachability independently of filtering constraints.
    """

    def __init__(
        self,
        layers: int = 4,
        width: int = 3,
        skip_connections: bool = False,
        seed: Optional[int] = None,
        label: str = "",
    ) -> None:
        super().__init__(label or f"layered_{layers}x{width}")
        self.layers = layers
        self.width = width
        self.skip_connections = skip_connections
        self.seed = seed

    def make_states(self) -> List[State]:
        return [
            State(label=f"L{l}n{n}")
            for l in range(self.layers)
            for n in range(self.width)
        ]

    def _generate_candidates(self, states: List[State]) -> List[Continuation]:
        # reconstruct layer structure from labels
        by_layer: dict[int, List[State]] = {}
        for s in states:
            if s.label and s.label.startswith("L"):
                try:
                    l = int(s.label[1:s.label.index("n")])
                    by_layer.setdefault(l, []).append(s)
                except (ValueError, AttributeError):
                    pass

        conts = []
        for l in range(self.layers - 1):
            for src in by_layer.get(l, []):
                for tgt in by_layer.get(l + 1, []):
                    conts.append(Continuation(src, tgt))
            if self.skip_connections and l + 2 < self.layers:
                for src in by_layer.get(l, []):
                    for tgt in by_layer.get(l + 2, []):
                        conts.append(Continuation(src, tgt, weight=0.5))
        return conts

    def build_default(self, constraints: Sequence[Constraint] = ()) -> AdmissibilityGraph:
        return self.build(self.make_states(), constraints)


class GrowthGenerator(Generator):
    """
    Generates a graph by preferential attachment: new states connect
    preferentially to high-fanout existing states.

    Produces power-law fanout distributions — the same kind of structure
    found in citation networks, web graphs, and biological networks.
    Tests whether hub-first repair generalizes to naturally-grown graphs.
    """

    def __init__(
        self,
        n: int = 20,
        m: int = 2,
        seed: Optional[int] = None,
        label: str = "",
    ) -> None:
        super().__init__(label or f"growth_{n}_m{m}")
        self.n = n
        self.m = m  # edges added per new state
        self.seed = seed

    def make_states(self) -> List[State]:
        return [State(label=f"g{i}") for i in range(self.n)]

    def _generate_candidates(self, states: List[State]) -> List[Continuation]:
        rng = random.Random(self.seed)
        if len(states) < 2:
            return []

        conts = []
        degrees: dict[str, int] = {s.id: 0 for s in states}

        # seed with first edge
        conts.append(Continuation(states[0], states[1]))
        degrees[states[0].id] += 1
        degrees[states[1].id] += 1

        for i in range(2, len(states)):
            new_state = states[i]
            # preferential attachment: choose targets weighted by degree
            existing = states[:i]
            weights = [degrees[s.id] + 1 for s in existing]  # +1 avoids zero
            total_w = sum(weights)
            probs = [w / total_w for w in weights]

            chosen = set()
            attempts = 0
            while len(chosen) < min(self.m, len(existing)) and attempts < 100:
                r = rng.random()
                cumulative = 0.0
                for j, p in enumerate(probs):
                    cumulative += p
                    if r <= cumulative:
                        chosen.add(j)
                        break
                attempts += 1

            for j in chosen:
                target = existing[j]
                conts.append(Continuation(new_state, target))
                degrees[new_state.id] += 1
                degrees[target.id] += 1

        return conts

    def build_default(self, constraints: Sequence[Constraint] = ()) -> AdmissibilityGraph:
        return self.build(self.make_states(), constraints)


# ---------------------------------------------------------------------------
# Generative Compression experiment helper
# ---------------------------------------------------------------------------

def compare_generators(
    generators: List[Generator],
    shared_states: Optional[List[State]] = None,
    constraints: Sequence[Constraint] = (),
) -> List[dict]:
    """
    Build graphs from multiple generators with the same constraint set,
    then compare reachable volumes.

    This is the direct computational demonstration of the Generative
    Compression Hypothesis: identical constraints, different volumes.

    Returns a list of result dicts, one per generator.
    """
    from adm_metrics import AdmissibilityMetrics

    results = []
    for gen in generators:
        if shared_states is not None:
            g = gen.build(shared_states, constraints)
        elif hasattr(gen, "build_default"):
            g = gen.build_default(constraints)
        else:
            raise ValueError(f"Generator {gen.name} needs shared_states or build_default")

        m = AdmissibilityMetrics.from_graph(g, label=gen.label or gen.name)
        results.append({
            "generator": gen.name,
            "label": gen.label,
            "candidates": len(list(g.continuations)),
            **m.as_dict(),
        })

    return results
