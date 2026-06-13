"""
Experiment 03: Trajectory Navigability and Bottleneck Archaeology

Question: When you look back at a completed trajectory, where were
the bottlenecks — and were they predictable from local structure?

This is the "archaeological" experiment: given a trajectory that has
already been walked, can you identify the structural features that
made certain steps narrow? Were the bottlenecks visible in advance,
or did they emerge from the interaction of the path with the graph?

Observations to collect:
  - Bottleneck position distribution (early vs late in trajectory)
  - Whether bottleneck states have low in-degree (structural) vs low
    out-degree (continuation-limited)
  - Whether the step after a bottleneck tends toward high fan-out (recovery)
    or low fan-out (cascade)

Run: python -m experiments.exp03_trajectory_archaeology
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
from adm_graph import AdmissibilityGraph
from adm_core import State, Continuation
from adm_visual import TerminalRenderer
from experiments.factories import make_random_dag, make_repair_corridor_test


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 03 — Trajectory Navigability and Bottleneck Archaeology")
    print("=" * 70)
    print("""
We walk trajectories through various graph types and then examine
the admissibility history to find bottleneck patterns.

For each trajectory we ask:
  - Where in the trajectory did bottlenecks occur?
  - What followed a bottleneck? Recovery (fan-out increase) or cascade?
  - Were bottlenecks structurally predictable from the source state?
""")

    def walk_and_analyze(graph: AdmissibilityGraph, source: State, label: str) -> None:
        traj = graph.walk(source, max_steps=50)
        traj.label = label

        renderer.render_trajectory(traj)

        sizes = traj.admissibility_sizes
        bottlenecks = traj.bottleneck_indices
        sinks = traj.sink_indices

        print(f"\n  Summary for '{label}':")
        print(f"    total steps:     {len(traj)}")
        print(f"    bottlenecks at:  {bottlenecks if bottlenecks else 'none'}")
        print(f"    sinks at:        {sinks if sinks else 'none'}")

        # Post-bottleneck analysis
        recoveries = 0
        cascades = 0
        for b in bottlenecks:
            if b + 1 < len(sizes):
                if sizes[b + 1] > sizes[b]:
                    recoveries += 1
                else:
                    cascades += 1

        if bottlenecks:
            print(f"    post-bottleneck recovery: {recoveries}/{len(bottlenecks)}")
            print(f"    post-bottleneck cascade:  {cascades}/{len(bottlenecks)}")

        # Navigability arc
        if sizes:
            peak = max(sizes)
            trough = min(s for s in sizes if s > 0) if any(s > 0 for s in sizes) else 0
            print(f"    navigability range:  [{trough}, {peak}]")
            print(f"    mean fan-out:        {sum(sizes)/len(sizes):.2f}")
        print()

    # Experiment A: random DAGs, multiple seeds
    print("\n── Graph type: Random DAG ──")
    for seed in [1, 7, 42, 99]:
        g = make_random_dag(n=15, edge_density=0.2, seed=seed)
        states = list(g.states)
        if states:
            source = states[0]
            walk_and_analyze(g, source, label=f"dag_seed{seed}")

    # Experiment B: repair corridor spine (follow the spine)
    print("\n── Graph type: Repair Corridor (spine walk) ──")
    g = make_repair_corridor_test(n=16, seed=7)
    states = list(g.states)
    spine_states = [s for s in states if s.label and s.label.startswith("sp")]
    if spine_states:
        walk_and_analyze(g, spine_states[0], label="corridor_spine")

    print("""
Cross-trajectory observations:
  If post-bottleneck recovery > cascade consistently:
    Bottlenecks are transient passages — the graph is self-recovering.
    "Repair corridor" concept gains empirical grounding.

  If post-bottleneck cascade dominates:
    Bottlenecks tend toward sink formation.
    The framework needs a concept for "cascade-prone bottlenecks."

  If recovery/cascade ratio varies by graph type:
    Graph topology determines which regime applies.
    The distinction between graph types becomes theoretically important.
""")


if __name__ == "__main__":
    run()
