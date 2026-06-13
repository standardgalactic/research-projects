"""
adm.core — Irreducible primitives of the Admissibility Program.

The fundamental objects here are not representations of things.
They are constraints on what comes next.

  State       — a position in the space of distinctions
  Continuation — a possible next state (forward-facing, not a stored record)
  Constraint  — a restriction on which continuations remain admissible
  Trajectory  — a sequence of states with a recorded admissibility history
  AdmissibilitySet — the live set of continuations available from a state

Projection is intentionally absent from this layer.
It emerges when constraints destroy distinctions — one level up.
"""

from .primitives import State, Continuation, Constraint, Trajectory, AdmissibilitySet

__all__ = [
    "State",
    "Continuation",
    "Constraint",
    "Trajectory",
    "AdmissibilitySet",
]
