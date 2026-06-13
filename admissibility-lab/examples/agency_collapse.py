"""
examples/agency_collapse.py — adm.collapse-demo

You create a graph.
You compress it (add constraints).
You watch navigable futures disappear.

Agency collapse is the formal signature of an admissibility sink:
a state from which no continuation survives.

This demo makes it visible in real time:
  - Start with a navigable space
  - Add constraints progressively
  - Watch fan-out contract
  - Observe the collapse threshold

No monograph required.

Usage: python examples/agency_collapse.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph
from adm_metrics import AdmissibilityMetrics, MetricsSeries
from adm_visual import TerminalRenderer
from experiments.factories import make_random_dag


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("AGENCY COLLAPSE DEMO")
    print("=" * 70)
    print("""
Agency collapse: a state loses all admissible continuations.
The system cannot proceed. All futures become inadmissible.

We demonstrate this by progressively tightening constraints
and watching fan-out contract toward zero.
""")

    g = make_random_dag(n=20, edge_density=0.25, seed=42)
    g.label = "agency_collapse_demo"

    print("Starting state — full navigability:")
    renderer.render_graph_summary(g)
    renderer.render_fan_out_map(g)

    series = MetricsSeries(label="agency_collapse")
    series.record(g, event="unconstrained")

    # Progressive constraint tightening
    thresholds = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    constraint_names = []

    print("\n── Progressive constraint tightening ──\n")
    print(f"  {'constraint':<22} {'sinks':>8} {'bottlenecks':>12} {'hubs':>8} {'mean_fan':>10}")
    print("  " + "─" * 64)

    collapse_threshold = None

    for thresh in thresholds:
        name = f"weight≥{thresh:.1f}"
        c = Constraint(
            predicate=lambda cont, t=thresh: cont.weight >= t,
            name=name,
        )
        # Remove previous weight constraint, add new one
        if constraint_names:
            g.remove_constraint(constraint_names[-1])
        g.add_constraint(c)
        constraint_names.append(name)

        m = series.record(g, event=name)
        s = g.summary()

        print(
            f"  {name:<22} {s['sinks']:>8} {s['bottlenecks']:>12} "
            f"{s['hubs']:>8} {s['mean_fan_out']:>10.3f}"
        )

        # Detect collapse threshold
        if collapse_threshold is None and m.sink_density > 0.5:
            collapse_threshold = thresh
            print(f"\n  ⚑ COLLAPSE THRESHOLD REACHED at weight≥{thresh:.1f}")
            print(f"    {m.sink_density:.0%} of states now have no admissible continuations.")
            print(f"    The system has entered agency collapse.\n")

    print("\n── Final state — collapsed ──")
    renderer.render_fan_out_map(g)

    series.print_series()

    # Now demonstrate recovery
    print("\n── Constraint relaxation (partial recovery) ──")
    print("""
What happens when we relax the constraint?
Note: relaxation restores navigability but not history.
The trajectory that passed through the collapsed state is gone.
""")

    # Relax back to moderate constraint
    for name in constraint_names:
        g.remove_constraint(name)

    moderate = Constraint(
        predicate=lambda cont: cont.weight >= 0.8,
        name="weight≥0.8_relaxed",
    )
    g.add_constraint(moderate)
    relaxed_m = AdmissibilityMetrics.from_graph(g, "after_relaxation")

    print(f"  Reachable volume after relaxation: {relaxed_m.reachable_volume}")
    print(f"  Sink density after relaxation:     {relaxed_m.sink_density:.0%}")
    print(f"  Hub density after relaxation:      {relaxed_m.hub_density:.0%}")

    print("\n" + "=" * 70)
    print("KEY OBSERVATION")
    print("=" * 70)
    print(f"""
  Collapse threshold: weight≥{collapse_threshold or '?'}
  At collapse: >50% of states become admissibility sinks.

  Relaxing the constraint restores navigability.
  But the system cannot return to states it was in before the collapse.
  Irreversibility is architectural — constraint removal is not time reversal.

  This is the formal structure of agency collapse:
    not destruction of states, but elimination of admissible continuations.
  
  The states still exist. The futures have gone.
""")


if __name__ == "__main__":
    run()
