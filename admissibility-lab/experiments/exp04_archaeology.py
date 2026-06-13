"""
Experiment 04: Trajectory Archaeology

The archaeological question: given only trajectories recorded from an
unknown graph, how much structural information can be recovered from
the residue alone?

We walk N trajectories through a graph, then discard the graph.
From the residue we attempt to identify:
  - hubs (high mean fan-out in observations)
  - sinks (trajectories frequently terminate here)
  - bottlenecks (frequently observed at narrow points)

We measure reconstruction fidelity at each checkpoint and produce
a fidelity curve: fidelity as a function of trajectory count.

The key question is where the curve saturates — how many trajectories
are sufficient for reliable reconstruction of each structural feature?

Different features may saturate at different trajectory counts.
Sinks tend to be easy (any trajectory that hits one reveals it).
Hubs require multiple trajectories through the same state.
Bottlenecks may require trajectories from diverse starting points.

Run: python -m experiments.exp04_archaeology
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_archaeology import ArchaeologyExperiment
from adm_visual import TerminalRenderer
from experiments.factories import (
    make_random_dag,
    make_hub_and_spoke,
    make_bottleneck,
    make_repair_corridor_test,
)


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 04 — Trajectory Archaeology")
    print("=" * 70)
    print("""
Question: how much trajectory residue is required to reconstruct
the structural features of the original graph?

We test four graph types with different structural profiles.
For each, we measure how fidelity grows with trajectory count.

This directly addresses the MEM|8 / Phoenix / Replay Invariance cluster:
what is preserved in the residue when the source is no longer present?
""")

    graph_factories = {
        "random_dag":      lambda: make_random_dag(n=20, edge_density=0.18, seed=42),
        "hub_and_spoke":   lambda: make_hub_and_spoke(spokes=5, spoke_length=3),
        "bottleneck":      lambda: make_bottleneck(pre_size=4, post_size=4),
        "repair_corridor": lambda: make_repair_corridor_test(n=14, seed=7),
    }

    saturation_results = {}

    for name, factory in graph_factories.items():
        print(f"\n{'─'*60}")
        print(f"Graph: {name}")
        print('─'*60)
        g = factory()
        renderer.render_graph_summary(g)

        exp = ArchaeologyExperiment(graph=g, seed=2024)
        curve = exp.run(
            max_trajectories=300,
            measure_every=20,
            max_steps_per_walk=40,
            verbose=True,
        )

        sat = exp.saturation_point(curve, threshold=0.7)
        saturation_results[name] = sat
        if sat:
            print(f"\n  → Saturation (fidelity ≥ 70%) reached at {sat} trajectories")
        else:
            print(f"\n  → Saturation (fidelity ≥ 70%) not reached within 300 trajectories")

    print("\n" + "=" * 70)
    print("SATURATION SUMMARY")
    print("=" * 70)
    print(f"\n  {'graph':<22} {'trajectories_to_70%_fidelity'}")
    print("  " + "─" * 45)
    for name, sat in saturation_results.items():
        val = str(sat) if sat else "not reached"
        print(f"  {name:<22} {val}")

    print("""
Interpretation guide:

  Low saturation count → structure is easily legible from trajectories
    (information is "surface-level" — visible in short walks)

  High saturation count → structure requires deep exploration
    (information is "buried" — only revealed by diverse long trajectories)

  Not reached → some structural features may not be trajectory-legible at all
    (they require direct graph inspection, not walk-based inference)

The difference between feature types (hub vs sink vs bottleneck) is
particularly interesting: which features appear first in the residue?
""")


if __name__ == "__main__":
    run()
