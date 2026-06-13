"""
Experiment 05: Generative Compression Hypothesis

Two generators can produce identical reachable inventories but
different reachable volumes.

This is the direct computational demonstration:
  - Same state set
  - Same constraints
  - Different generation protocols
  - → Different reachable volumes

The hypothesis is not merely that dense graphs are more reachable
than sparse ones (trivially true). The interesting version is:

  Given identical constraint intensity, how much does generation
  protocol alone determine reachable volume?

  And: is there a generation protocol that maximizes reachable volume
  under a given constraint budget?

This connects to the compression aspect of the framework: the generator
defines the uncompressed possibility space; constraints compress it;
the question is whether two different compressions of two different
possibility spaces can produce the same admissible output.

Run: python -m experiments.exp05_generator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_core import Constraint, Continuation
from adm_generator import (
    DenseGenerator,
    SparseGenerator,
    LayeredGenerator,
    GrowthGenerator,
    compare_generators,
)
from adm_metrics import AdmissibilityMetrics
from adm_visual import TerminalRenderer


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 05 — Generative Compression Hypothesis")
    print("=" * 70)
    print("""
Two generators produce different reachable volumes even under
identical constraints. We test this across constraint intensities.

Generators compared:
  Dense    — all forward edges (maximum inventory)
  Sparse   — random 20% of forward edges
  Layered  — edges only between adjacent layers
  Growth   — preferential attachment (power-law degree distribution)

We apply increasing weight constraints and observe how each generator's
reachable volume responds. The question: which generation protocol is
most constraint-resilient?
""")

    N = 15

    # Shared state pool — same states, different generation protocols
    from adm_core import State
    shared_states = [State(label=f"n{i}") for i in range(N)]

    generators = [
        DenseGenerator(n=N, label="dense"),
        SparseGenerator(n=N, density=0.25, seed=42, label="sparse_25%"),
        LayeredGenerator(layers=4, width=4, label="layered_4x4"),
        GrowthGenerator(n=N, m=2, seed=42, label="growth_m2"),
    ]

    # Test under no constraint first
    print("── Baseline (no constraints) ──")
    print(f"\n  {'generator':<18} {'candidates':>12} {'reachable_vol':>14} {'mean_fanout':>12} {'sinks':>8}")
    print("  " + "─" * 68)

    baseline = compare_generators(generators, shared_states=shared_states)
    for r in baseline:
        print(
            f"  {r['label']:<18} {r['candidates']:>12} "
            f"{r['reachable_volume']:>14} "
            f"{r['mean_fanout']:>12.3f} "
            f"{r['sink_density']:>7.0%}"
        )

    # Sweep constraint intensities
    print("\n── Constraint intensity sweep (weight threshold) ──")
    thresholds = [0.5, 0.8, 1.0, 1.2, 1.5]

    print(f"\n  {'generator':<18} ", end="")
    for t in thresholds:
        print(f"  w≥{t:.1f}:vol", end="")
    print()
    print("  " + "─" * (18 + len(thresholds) * 14 + 2))

    for gen in generators:
        print(f"  {gen.label:<18} ", end="")
        for t in thresholds:
            c = Constraint(
                predicate=lambda cont, thresh=t: cont.weight >= thresh,
                name=f"w>={t}"
            )
            results = compare_generators([gen], shared_states=shared_states, constraints=[c])
            vol = results[0]["reachable_volume"]
            print(f"  {vol:>11}", end="")
        print()

    # The key test: identical output, different volume?
    print("\n── Compression equivalence test ──")
    print("""
Do any two generators produce identical admissible continuation sets
but different reachable volumes?

(Checking with a moderate weight constraint...)
""")

    c_moderate = Constraint(
        predicate=lambda cont: cont.weight >= 1.0,
        name="w>=1.0"
    )

    results_constrained = compare_generators(
        generators,
        shared_states=shared_states,
        constraints=[c_moderate],
    )

    volumes = [(r["label"], r["reachable_volume"], r["candidates"]) for r in results_constrained]
    volumes.sort(key=lambda x: x[1], reverse=True)

    print(f"  {'generator':<18} {'candidates':>12} {'reachable_vol':>14}")
    print("  " + "─" * 48)
    for label, vol, cands in volumes:
        print(f"  {label:<18} {cands:>12} {vol:>14}")

    vols = [v for _, v, _ in volumes]
    if len(set(vols)) < len(vols):
        print("\n  ✓ Compression equivalence observed: different generators, same volume")
        print("    This means reachable volume is not determined by generation protocol alone.")
    else:
        print("\n  ✗ No compression equivalence at this constraint level.")
        print("    Generators produce distinct volumes. Try different constraint intensity.")

    max_vol = max(vols)
    min_vol = min(vols)
    compression_ratio = min_vol / max(max_vol, 1)
    print(f"\n  Volume range: [{min_vol}, {max_vol}]")
    print(f"  Compression ratio (min/max): {compression_ratio:.2f}")
    print(f"  → Generation protocol accounts for {(1-compression_ratio)*100:.0f}% of volume variation")


if __name__ == "__main__":
    run()
