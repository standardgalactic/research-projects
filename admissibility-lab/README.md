# adm-lab

[The Eight-Letter Keyboard](https://standardgalactic.github.io/research-projects/admissibility-lab/eight_letter_keyboard.pdf)

* [The Eight-Letter Motor Phonology](https://standardgalactic.github.io/research-projects/admissibility-lab/The_Eight_Letter_Motor_Phonology.pdf)

[Motor Phonology and Symbolic Reachability](https://standardgalactic.github.io/research-projects/admissibility-lab/motor_phonology.pdf)

* [The Motor Manifold](https://standardgalactic.github.io/research-projects/admissibility-lab/The_Motor_Manifold.pdf)

* [The Reconstruction Imperative](https://standardgalactic.github.io/research-projects/admissibility-lab/The_Reconstruction_Imperative-extended.pdf)

[Continuations Before Objects](https://standardgalactic.github.io/research-projects/admissibility-lab/continuations_before_objects.pdf)

* [Reachability Geometry](https://standardgalactic.github.io/research-projects/admissibility-lab/Reachability_Geometry.pdf)

[Audio Overviews](https://standardgalactic.github.io/research-projects/admissibility-lab/)

A Python laboratory for observing admissibility geometry.

This is not a visualization of existing theorems.
It is an instrument for generating observations — a place where you
discover properties of the theory you did not anticipate.

---

## What this is

The Admissibility Program has produced extensive mathematical ontology.
What it currently lacks is a **laboratory**: a place where the theory
is pressured to produce definitions by being repeatedly observed.

`adm-lab` is built on the insight that the most important concepts
in any framework tend to be discovered archaeologically — you run
experiments, recurring structures appear, and only afterward do you
prove theorems about them.

The generative kernel is:

```
State → AdmissibilitySet
```

A state is not a record. It is a locus from which continuations project.
An admissibility set is not a static list. It is the live set of what
can come next, under current constraints.

Everything else follows from watching this structure respond to damage,
constraint accumulation, repair, and traversal.

---

## Project structure

```
adm-lab/
├── adm_core/           # Irreducible primitives
│   └── primitives.py   # State, Continuation, Constraint, Trajectory, AdmissibilitySet
├── adm_graph/          # Continuation graphs, reachability, fiber computation
├── adm_repair/         # Repair simulator and strategies
├── adm_visual/         # Terminal and matplotlib rendering
├── experiments/        # Executable thought experiments
│   ├── factories.py            # Canonical graph factories
│   ├── exp01_repair_corridor.py
│   ├── exp02_sink_formation.py
│   ├── exp03_trajectory_archaeology.py
│   └── run_all.py
└── tests/
    └── test_core.py
```

---

## Installation

```bash
pip install matplotlib networkx   # optional, for plot rendering
```

No other dependencies. The core and repair modules use only the standard library.

---

## Quick start

```python
from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph
from adm_visual import TerminalRenderer

# Build a small graph
g = AdmissibilityGraph(label="demo")
states = [State(label=f"s{i}") for i in range(5)]
for i in range(4):
    g.add_continuation(Continuation(states[i], states[i+1]))
# Add a branch
g.add_continuation(Continuation(states[2], states[4]))

# Inspect
renderer = TerminalRenderer()
renderer.render_graph_summary(g)
renderer.render_fan_out_map(g)

# Damage and observe
record = g.damage_random(fraction=0.4, rng_seed=42)
print("After damage:")
renderer.render_graph_summary(g)

# Repair
record.restore()
print("After repair:")
renderer.render_graph_summary(g)
```

---

## Running experiments

```bash
# All experiments
python -m experiments.run_all

# Individual
python -m experiments.exp01_repair_corridor
python -m experiments.exp02_sink_formation
python -m experiments.exp03_trajectory_archaeology

# Tests
python -m tests.test_core
```

---

## Core concepts

### State
A position in the space of distinctions. Identity is by id, not content:
two states with identical content that arose through different histories
are distinct. This models irreversibility as an architectural principle.

### Continuation
A possible next state. Not a stored record — a potential. The framework
is forward-facing throughout.

### Constraint
A predicate over continuations. Constraints narrow admissibility sets.
Projection is not in `adm_core` — it emerges one level up when constraints
destroy distinctions, collapsing multiple states into one.

### AdmissibilitySet
The live set of continuations available from a state under current
constraints. An empty set is an **admissibility sink** — the formal
signature of agency collapse.

### Trajectory
A sequence of states with full admissibility history. The key diagnostic
object: you can look back and ask when fan-out narrowed, when sinks
appeared, and where bottlenecks were.

### Repair
Not error-correction (restore prior state) nor exception-handling
(branch to alternative). Repair is ontologically primary: the system
is always already in a repair-eligible condition. The repair simulator
runs damage+recovery experiments to discover structural invariants that
the current mathematics does not yet describe.

---

## Phenomena to look for

Running experiments, you may observe:

- **Continuation bottlenecks** — states where fan-out drops to 1 before recovering
- **Admissibility sinks** — states from which no continuation survives constraints
- **Repair corridors** — paths that repair consistently routes through
- **Projection singularities** — points where many states collapse to one image
- **Agency collapse regions** — zones where navigability drops to near-zero
- **Lamphron ridges** — gradient structures in the reachability field (adm.field, forthcoming)

The goal is that these become important **because they keep appearing**,
not because they were posited in advance.

---

## Relation to the broader Admissibility Program

`adm-lab` is the laboratory layer of a larger ecosystem:

| Module | Status | Description |
|--------|--------|-------------|
| `adm.core` | ✓ this repo | Primitives: State, Continuation, Constraint, Trajectory |
| `adm.graph` | ✓ this repo | Continuation graphs, reachability, fibers |
| `adm.repair` | ✓ this repo | Repair simulator and strategies |
| `adm.visual` | ✓ this repo | Terminal and matplotlib rendering |
| `adm.field` | planned | RSVP field simulations, lamphron dynamics |
| `adm.path` | planned | Continuation-preserving pathfinding, geodesics |
| `adm.memory` | planned | MEM|8 experimentation, residue fields |
| `adm.social` | planned | Agency collapse in social systems |
| `adm.learn` | planned | Balbach–Zeugmann learning experiments |

The mathematical foundations are documented in the RSVP-Monograph and
associated papers. `adm-lab` exists to pressure those foundations
by making them runnable.

---

## Philosophy

> The visualizer would pressure the theory to produce definitions.

Right now many concepts exist because they are mathematically plausible.
A phenomenological instrument forces them to exist because they are
repeatedly observed. A continuation bottleneck becomes important because
it keeps appearing in experiments. A repair corridor becomes important
because systems keep healing through the same structures.

The theory becomes less deductive and more archaeological.
You start uncovering recurring objects in admissibility space.
Only afterward do you prove theorems about them.

---

*Flyxion / Admissibility Program*
