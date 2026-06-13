"""
adm.graph — Continuation graphs, reachability structures, fiber computation.

Projection is introduced here as a derived operation: what happens when
constraints destroy distinctions, collapsing multiple states into one.

The central object is the AdmissibilityGraph: a directed graph whose edges
are Continuations and whose nodes are States, with a live constraint set
that can be modified to observe how reachability changes.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterator, List, Optional, Set, Tuple

from adm_core import (
    AdmissibilitySet,
    Constraint,
    Continuation,
    State,
    Trajectory,
)


# ---------------------------------------------------------------------------
# AdmissibilityGraph
# ---------------------------------------------------------------------------

class AdmissibilityGraph:
    """
    A directed graph of States connected by Continuations, governed by
    a live set of Constraints.

    This is the primary instrument for observing admissibility geometry.
    You can:
      - add / remove states and continuations
      - add / remove constraints (watching reachability respond)
      - damage the graph (edge removal, state isolation)
      - query reachability, fibers, bottlenecks, sinks
      - run repair protocols
    """

    def __init__(self, label: Optional[str] = None) -> None:
        self.label = label
        self._states: Dict[str, State] = {}
        self._continuations: Set[Continuation] = set()
        self._constraints: List[Constraint] = []
        # adjacency index: source_id → set of Continuations
        self._out: Dict[str, Set[Continuation]] = defaultdict(set)
        self._in: Dict[str, Set[Continuation]] = defaultdict(set)

    # --- construction -------------------------------------------------------

    def add_state(self, state: State) -> "AdmissibilityGraph":
        self._states[state.id] = state
        return self

    def add_continuation(self, cont: Continuation) -> "AdmissibilityGraph":
        if cont.source.id not in self._states:
            self.add_state(cont.source)
        if cont.target.id not in self._states:
            self.add_state(cont.target)
        self._continuations.add(cont)
        self._out[cont.source.id].add(cont)
        self._in[cont.target.id].add(cont)
        return self

    def add_constraint(self, constraint: Constraint) -> "AdmissibilityGraph":
        self._constraints.append(constraint)
        return self

    def remove_constraint(self, name: str) -> "AdmissibilityGraph":
        self._constraints = [c for c in self._constraints if c.name != name]
        return self

    # --- admissibility set for a state -------------------------------------

    def admissibility_set(self, state: State) -> AdmissibilitySet:
        candidates = list(self._out.get(state.id, set()))
        return AdmissibilitySet(state, candidates, self._constraints)

    # --- reachability -------------------------------------------------------

    def reachable(self, source: State) -> Set[State]:
        """
        BFS over admissible continuations from source.
        Returns all states reachable under current constraints.
        """
        visited: Set[str] = set()
        queue = deque([source])
        result: Set[State] = set()

        while queue:
            current = queue.popleft()
            if current.id in visited:
                continue
            visited.add(current.id)
            result.add(current)
            adm = self.admissibility_set(current)
            for cont in adm:
                if cont.target.id not in visited:
                    queue.append(cont.target)

        return result

    def reachability_map(self) -> Dict[str, int]:
        """
        For each state, compute how many other states it can reach.
        High-reach states are navigability hubs.
        Zero-reach states (excluding self) are admissibility sinks.
        """
        result = {}
        for sid, state in self._states.items():
            reachable = self.reachable(state)
            result[sid] = len(reachable) - 1  # exclude self
        return result

    # --- structural analysis ------------------------------------------------

    def fan_out_map(self) -> Dict[str, int]:
        """Immediate continuation count for each state under current constraints."""
        return {
            sid: self.admissibility_set(state).size
            for sid, state in self._states.items()
        }

    def sinks(self) -> List[State]:
        """States with no admissible outgoing continuations."""
        return [
            state for sid, state in self._states.items()
            if self.admissibility_set(state).is_sink
        ]

    def bottlenecks(self, threshold: int = 1) -> List[State]:
        """
        States where fan-out is <= threshold but > 0.
        These are narrow passages — not sinks, but constrained.
        """
        return [
            state for sid, state in self._states.items()
            if 0 < self.admissibility_set(state).size <= threshold
        ]

    def hubs(self, threshold: int = 3) -> List[State]:
        """States with fan-out >= threshold. Repair corridors tend to route through hubs."""
        return [
            state for sid, state in self._states.items()
            if self.admissibility_set(state).size >= threshold
        ]

    # --- fiber computation --------------------------------------------------

    def fiber(self, target: State) -> Set[State]:
        """
        The fiber over a target state: all states that have an admissible
        continuation leading to target.

        In projection: states that map to the same image share a fiber.
        The fiber reveals how many distinctions are preserved vs collapsed.
        """
        result = set()
        for cont in self._in.get(target.id, set()):
            # check if this continuation is admissible from its source
            adm = self.admissibility_set(cont.source)
            if cont in adm.admissible:
                result.add(cont.source)
        return result

    def fiber_sizes(self) -> Dict[str, int]:
        """Fiber size for each state. Large fibers indicate projection collapse."""
        return {
            sid: len(self.fiber(state))
            for sid, state in self._states.items()
        }

    # --- damage and repair ---------------------------------------------------

    def damage_edges(self, edge_ids: Set[Tuple[str, str]]) -> "GraphDamageRecord":
        """
        Remove continuations by (source_id, target_id) pairs.
        Returns a DamageRecord that can be used to attempt repair.
        """
        removed = set()
        for cont in list(self._continuations):
            key = (cont.source.id, cont.target.id)
            if key in edge_ids:
                self._continuations.discard(cont)
                self._out[cont.source.id].discard(cont)
                self._in[cont.target.id].discard(cont)
                removed.add(cont)
        return GraphDamageRecord(graph=self, removed_continuations=removed)

    def damage_random(self, fraction: float, rng_seed: Optional[int] = None) -> "GraphDamageRecord":
        """
        Remove a random fraction of continuations.
        The canonical repair experiment entry point.
        """
        import random
        rng = random.Random(rng_seed)
        all_conts = list(self._continuations)
        n = max(1, int(len(all_conts) * fraction))
        to_remove = rng.sample(all_conts, min(n, len(all_conts)))
        edge_ids = {(c.source.id, c.target.id) for c in to_remove}
        return self.damage_edges(edge_ids)

    def isolate_state(self, state: State) -> "GraphDamageRecord":
        """Remove all continuations to and from a state."""
        edge_ids = set()
        for cont in self._out.get(state.id, set()):
            edge_ids.add((cont.source.id, cont.target.id))
        for cont in self._in.get(state.id, set()):
            edge_ids.add((cont.source.id, cont.target.id))
        return self.damage_edges(edge_ids)

    # --- traversal ----------------------------------------------------------

    def walk(self, source: State, max_steps: int = 100) -> Trajectory:
        """
        Greedy walk: at each step take the highest-weight admissible continuation.
        Records full admissibility history.
        """
        traj = Trajectory(label=f"walk_from_{source.label or source.id}")
        current = source
        visited: Set[str] = set()

        for _ in range(max_steps):
            adm = self.admissibility_set(current)
            traj.append(current, adm)

            if adm.is_sink or current.id in visited:
                break

            visited.add(current.id)
            best = max(adm.admissible, key=lambda c: c.weight)
            current = best.target

        return traj

    # --- summary ------------------------------------------------------------

    def summary(self) -> dict:
        fan_out = self.fan_out_map()
        reach = self.reachability_map()
        return {
            "states": len(self._states),
            "continuations": len(self._continuations),
            "constraints": len(self._constraints),
            "sinks": len(self.sinks()),
            "bottlenecks": len(self.bottlenecks()),
            "hubs": len(self.hubs()),
            "mean_fan_out": sum(fan_out.values()) / max(len(fan_out), 1),
            "mean_reachability": sum(reach.values()) / max(len(reach), 1),
        }

    def __repr__(self) -> str:
        tag = self.label or "unlabeled"
        return (
            f"AdmissibilityGraph({tag!r}, "
            f"states={len(self._states)}, "
            f"conts={len(self._continuations)}, "
            f"constraints={len(self._constraints)})"
        )

    # --- iteration ----------------------------------------------------------

    @property
    def states(self) -> Iterator[State]:
        return iter(self._states.values())

    @property
    def continuations(self) -> Iterator[Continuation]:
        return iter(self._continuations)


# ---------------------------------------------------------------------------
# GraphDamageRecord
# ---------------------------------------------------------------------------

@dataclass
class GraphDamageRecord:
    """
    Records what was removed from a graph during a damage operation.
    Enables repair attempts and before/after analysis.
    """
    graph: AdmissibilityGraph
    removed_continuations: Set[Continuation]

    def restore(self) -> None:
        """Restore all removed continuations to the graph."""
        for cont in self.removed_continuations:
            self.graph.add_continuation(cont)

    def partial_restore(self, fraction: float, rng_seed: Optional[int] = None) -> int:
        """
        Restore a fraction of removed continuations (simulating partial repair).
        Returns the number of continuations restored.
        """
        import random
        rng = random.Random(rng_seed)
        pool = list(self.removed_continuations)
        n = max(1, int(len(pool) * fraction))
        to_restore = rng.sample(pool, min(n, len(pool)))
        for cont in to_restore:
            self.graph.add_continuation(cont)
            self.removed_continuations.discard(cont)
        return len(to_restore)

    @property
    def damage_count(self) -> int:
        return len(self.removed_continuations)
