"""
Experiment 02: Admissibility Sink Formation

Question: How does constraint accumulation produce sinks?

Adding constraints narrows admissibility sets.
At some threshold, states lose all outgoing continuations and become sinks.

This experiment watches the phase transition:
  - Start with a healthy graph
  - Add constraints one at a time (weight thresholds, increasingly strict)
  - Record when each state becomes a sink
  - Map the "sink formation curve"

The sink formation curve may reveal:
  - Phase transition behavior (sudden collapse vs gradual degradation)
  - Which states are most constraint-sensitive
  - Whether there are "stable cores" that resist constraint-induced collapse

This is the constraint-accumulation analog of agency collapse.

Run: python -m experiments.exp02_sink_formation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import random
from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph
from adm_visual import TerminalRenderer
from experiments.factories import make_random_dag, apply_weight_constraint


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 02 — Admissibility Sink Formation Under Constraint Accumulation")
    print("=" * 70)
    print("""
We observe how increasing weight constraints progressively eliminate
admissible continuations, turning navigable states into sinks.

The weight threshold sweeps from permissive (0.1) to strict (2.0).
At each threshold level we record: how many sinks? How many hubs?
What is mean reachability?

We are looking for phase transitions — abrupt changes in the sink count.
""")

    rng = random.Random(42)
    g = make_random_dag(n=25, edge_density=0.20, seed=42)

    print("Baseline graph:")
    renderer.render_graph_summary(g)
    renderer.render_fan_out_map(g)

    thresholds = [round(t * 0.1, 1) for t in range(1, 22)]  # 0.1 to 2.1

    print("\n Weight threshold sweep:")
    print(f"  {'threshold':<12} {'sinks':<8} {'hubs':<8} {'mean_fan':<12} {'mean_reach'}")
    print("  " + "─" * 56)

    prev_sinks = 0
    phase_transitions = []

    for thresh in thresholds:
        # fresh graph each time — constraints are cumulative
        g_test = make_random_dag(n=25, edge_density=0.20, seed=42)
        apply_weight_constraint(g_test, min_weight=thresh, name=f"w>{thresh}")

        s = g_test.summary()
        sinks = s["sinks"]
        hubs = s["hubs"]
        mean_fan = s["mean_fan_out"]
        mean_reach = s["mean_reachability"]

        delta = sinks - prev_sinks
        marker = f"  ← +{delta} sinks" if delta >= 3 else ""
        if delta >= 3:
            phase_transitions.append((thresh, delta))

        print(
            f"  {thresh:<12.1f} {sinks:<8} {hubs:<8} "
            f"{mean_fan:<12.3f} {mean_reach:.3f}{marker}"
        )
        prev_sinks = sinks

    print("\n Phase transitions detected (threshold levels where ≥3 new sinks appeared):")
    if phase_transitions:
        for thresh, delta in phase_transitions:
            print(f"  weight > {thresh:.1f} → +{delta} sinks")
    else:
        print("  None detected — sink formation was gradual on this graph.")

    print("""
Interpretation:
  Abrupt transitions suggest "weak links" — continuations whose weights
  cluster near the threshold, creating batch elimination.

  Gradual degradation suggests weight is uniformly distributed,
  and constraint tightening produces smooth navigability loss.

  The presence or absence of phase transitions is a property of the graph
  structure, not the constraint type. Discovering when this matters is part
  of what the laboratory is for.
""")


if __name__ == "__main__":
    run()
