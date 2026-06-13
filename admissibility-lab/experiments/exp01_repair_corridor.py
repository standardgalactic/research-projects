"""
Experiment 01: Repair Corridor Discovery

Question: Does repair tend to route through high-fan-out states (hubs),
or is recovery distributed across the graph?

This is one of the simplest questions the repair simulator can answer,
and the answer is not obvious a priori.

Hypothesis: Hub-first repair restores more reachability than random repair
at the same recovery cost, because hubs are topological relay points.

If this is consistently true across graph types and damage levels,
"repair corridor" becomes a quantity worth formalizing.
If it is NOT consistently true, the hypothesis needs revision.

Both outcomes are interesting.

Run: python -m experiments.exp01_repair_corridor
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from experiments.factories import (
    make_random_dag,
    make_hub_and_spoke,
    make_bottleneck,
    make_repair_corridor_test,
)
from adm_repair import (
    RepairSimulator,
    strategy_hub_first,
    strategy_sink_rescue,
    strategy_random_partial,
)
from adm_visual import TerminalRenderer


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 01 — Repair Corridor Discovery")
    print("=" * 70)
    print("""
Question: Does repair route preferentially through hubs?

We run the same damage+repair protocol across four graph types:
  - random DAG (general case)
  - hub-and-spoke (extreme hub structure)
  - bottleneck graph (single narrow passage)
  - repair corridor test (spine + periphery)

Strategy comparison:
  - hub_first: prioritize continuations touching high-fan-out states
  - sink_rescue: prioritize restoring states that became sinks
  - random_50%: restore a random 50% of damage (control)
""")

    graph_factories = {
        "random_dag":      lambda: make_random_dag(n=20, edge_density=0.18, seed=42),
        "hub_and_spoke":   lambda: make_hub_and_spoke(spokes=6, spoke_length=3),
        "bottleneck":      lambda: make_bottleneck(pre_size=5, post_size=5),
        "repair_corridor": lambda: make_repair_corridor_test(n=16, seed=7),
    }

    strategies = [
        strategy_hub_first,
        strategy_sink_rescue,
        strategy_random_partial(0.5, seed=99),
    ]

    all_results = {}

    for graph_name, factory in graph_factories.items():
        print(f"\n{'─'*60}")
        print(f"Graph type: {graph_name}")
        print('─'*60)

        # Show baseline
        g = factory()
        renderer.render_graph_summary(g)

        sim = RepairSimulator(graph_factory=factory, seed=1337)
        results = sim.run(
            trials=200,
            damage_fractions=[0.2, 0.4, 0.6],
            strategies=strategies,
            verbose=True,
        )
        all_results[graph_name] = results

    print("\n" + "=" * 70)
    print("CROSS-GRAPH OBSERVATIONS")
    print("=" * 70)

    for graph_name, results in all_results.items():
        hub_results = [r for r in results if "hub_first" in r.strategy_name]
        rand_results = [r for r in results if "random" in r.strategy_name]

        if hub_results and rand_results:
            hub_reach = sum(r.reachability_restored for r in hub_results) / len(hub_results)
            rand_reach = sum(r.reachability_restored for r in rand_results) / len(rand_results)
            direction = "✓ HUB > RANDOM" if hub_reach > rand_reach else "✗ HUB ≤ RANDOM"
            print(f"  {graph_name:<20} {direction}  (hub={hub_reach:.3f}, rand={rand_reach:.3f})")

    print("""
Interpretation guide:
  ✓ HUB > RANDOM across all graph types → "repair corridor" is a real structural feature
  ✗ HUB ≤ RANDOM on some graph types   → hub-first is graph-topology-dependent;
                                         the corridor hypothesis needs refinement
""")


if __name__ == "__main__":
    run()
