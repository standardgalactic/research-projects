"""
adm_core.primitives

The five irreducible objects of the admissibility framework.

Design principle: every object is forward-facing.
A State is not a stored record — it is a locus from which continuations project.
A Constraint is not a property — it is a filter on the future.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Iterator, Optional, Sequence


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class State:
    """
    A position in the space of distinctions.

    States carry an identifier and an arbitrary payload (the 'content' of the
    distinction).  Equality is by identity, not by content — two states with
    identical content that arose through different histories are distinct.

    This models the irreversibility principle: arriving at the same content
    via different paths leaves different residues.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: Any = None
    label: Optional[str] = None

    def __repr__(self) -> str:
        tag = self.label or self.id
        return f"State({tag!r})"

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return NotImplemented
        return self.id == other.id


# ---------------------------------------------------------------------------
# Continuation
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Continuation:
    """
    A possible next state — a directed forward possibility.

    A Continuation is not a stored record of what happened.
    It is a potential: what could come next from a given State.

    source → target with an optional weight representing the cost or
    resistance of this transition.
    """
    source: State
    target: State
    weight: float = 1.0
    label: Optional[str] = None

    def __repr__(self) -> str:
        src = self.source.label or self.source.id
        tgt = self.target.label or self.target.id
        return f"Continuation({src!r} → {tgt!r}, w={self.weight:.2f})"

    def __hash__(self) -> int:
        return hash((self.source.id, self.target.id))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Continuation):
            return NotImplemented
        return self.source.id == other.source.id and self.target.id == other.target.id


# ---------------------------------------------------------------------------
# Constraint
# ---------------------------------------------------------------------------

@dataclass
class Constraint:
    """
    A restriction on which continuations remain admissible.

    A Constraint is a predicate over Continuations.  When applied to a
    Continuation, it returns True if that continuation survives, False if
    it is eliminated.

    Constraints compose: applying multiple constraints narrows the
    admissibility set.  Removing a constraint widens it — but widening
    does not restore what was lost if the trajectory has already moved on.

    Parameters
    ----------
    predicate : callable
        A function (Continuation) → bool.
    name : str
        A human-readable label for introspection and experiment logging.
    """
    predicate: Callable[[Continuation], bool]
    name: str = "unnamed_constraint"

    def apply(self, continuation: Continuation) -> bool:
        """Return True if the continuation survives this constraint."""
        return self.predicate(continuation)

    def __repr__(self) -> str:
        return f"Constraint({self.name!r})"


# ---------------------------------------------------------------------------
# AdmissibilitySet
# ---------------------------------------------------------------------------

class AdmissibilitySet:
    """
    The live set of continuations available from a state under active constraints.

    This is the central object of the framework.  It is not a static list —
    it is recomputed each time constraints change.  The size of this set
    is a measure of the state's navigability.

    An empty AdmissibilitySet is an admissibility sink: the system has
    no forward options.  This is the formal signature of agency collapse.
    """

    def __init__(
        self,
        state: State,
        candidates: Sequence[Continuation],
        constraints: Sequence[Constraint] = (),
    ) -> None:
        self.state = state
        self._candidates = list(candidates)
        self._constraints = list(constraints)
        self._admissible: Optional[FrozenSet[Continuation]] = None

    def _compute(self) -> FrozenSet[Continuation]:
        result = []
        for c in self._candidates:
            if c.source.id == self.state.id:
                if all(constraint.apply(c) for constraint in self._constraints):
                    result.append(c)
        return frozenset(result)

    @property
    def admissible(self) -> FrozenSet[Continuation]:
        if self._admissible is None:
            self._admissible = self._compute()
        return self._admissible

    def add_constraint(self, constraint: Constraint) -> "AdmissibilitySet":
        """Return a new AdmissibilitySet with an additional constraint applied."""
        return AdmissibilitySet(
            self.state,
            self._candidates,
            self._constraints + [constraint],
        )

    def remove_constraint(self, name: str) -> "AdmissibilitySet":
        """Return a new AdmissibilitySet with the named constraint removed."""
        remaining = [c for c in self._constraints if c.name != name]
        return AdmissibilitySet(self.state, self._candidates, remaining)

    @property
    def size(self) -> int:
        return len(self.admissible)

    @property
    def is_sink(self) -> bool:
        """True if no continuations survive — an admissibility sink."""
        return self.size == 0

    @property
    def fan_out(self) -> int:
        """Alias for size. High fan-out states are repair-corridor candidates."""
        return self.size

    def __iter__(self) -> Iterator[Continuation]:
        return iter(self.admissible)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        tag = self.state.label or self.state.id
        return f"AdmissibilitySet(state={tag!r}, size={self.size})"


# ---------------------------------------------------------------------------
# Trajectory
# ---------------------------------------------------------------------------

@dataclass
class Trajectory:
    """
    A sequence of states with a recorded admissibility history.

    A Trajectory is the record of a path taken through the continuation
    space — but crucially, it also records the admissibility set *at each
    step*, not just the state reached.

    This means you can look back and ask:
      - How many options were available at step k?
      - When did the admissibility set first narrow to 1?
      - At what point did navigability collapse?
      - Which constraints were active during recovery?

    The admissibility history is the empirical record the repair simulator
    needs.
    """
    steps: list[tuple[State, AdmissibilitySet]] = field(default_factory=list)
    label: Optional[str] = None

    def append(self, state: State, adm_set: AdmissibilitySet) -> None:
        self.steps.append((state, adm_set))

    @property
    def states(self) -> list[State]:
        return [s for s, _ in self.steps]

    @property
    def admissibility_sizes(self) -> list[int]:
        """The fan-out sequence over time — the navigability profile."""
        return [a.size for _, a in self.steps]

    @property
    def sink_indices(self) -> list[int]:
        """Steps at which the system entered an admissibility sink."""
        return [i for i, (_, a) in enumerate(self.steps) if a.is_sink]

    @property
    def bottleneck_indices(self) -> list[int]:
        """
        Steps where fan-out was locally minimal and non-zero.
        A bottleneck is not a sink — the system can still proceed,
        but through a narrow passage.
        """
        sizes = self.admissibility_sizes
        bottlenecks = []
        for i in range(1, len(sizes) - 1):
            if sizes[i] > 0 and sizes[i] < sizes[i-1] and sizes[i] <= sizes[i+1]:
                bottlenecks.append(i)
        return bottlenecks

    def __len__(self) -> int:
        return len(self.steps)

    def __repr__(self) -> str:
        tag = self.label or "unlabeled"
        return f"Trajectory({tag!r}, steps={len(self.steps)})"
