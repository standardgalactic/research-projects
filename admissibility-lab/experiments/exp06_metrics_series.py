"""
Experiment 06: Metrics Series — Tracking Quantities Through Damage and Repair

Every good ecosystem ends up with metrics. This experiment runs the full
damage → repair cycle while tracking a MetricsSeries, producing a
before/after/restored record with all quantities measured at each stage.

The goal: produce numbers, not just pictures.

    before_damage:  reachable_volume = 1240
    after_damage:   reachable_volume = 380
    after_repair:   reachable_volume = 1175

From these numbers, repair_efficiency emerges naturally:
    recovered_volume / repair_operations

And repair_efficiency can be compared across strategies —
which is how repair corridors become measurable rather than merely observed.

Run: python -m experiments.exp06_metrics_series
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_metrics import AdmissibilityMetrics, MetricsSeries, MetricsDelta, repair_efficiency
from adm_repair import (
    strategy_hub_first,
    strategy_sink_rescue,
    strategy_full_restore,
    strategy_random_partial,
)
from adm_visual import TerminalRenderer
from experiments.factories import make_random_dag, make_hub_and_spoke, make_repair_corridor_test


def run_cycle(graph_factory, strategy, strategy_name: str, damage_frac: float, seed: int = 42):
    """Run one damage-repair cycle and return the MetricsSeries."""
    g = graph_factory()
    series = MetricsSeries(label=f"{g.label}|{strategy_name}|dmg={damage_frac:.0%}")

    series.record(g, event="pre_damage")
    record = g.damage_random(fraction=damage_frac, rng_seed=seed)
    series.record(g, event="post_damage")

    ops = strategy(g, record)
    series.record(g, event=f"post_repair({ops}_ops)")

    return series, ops


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("EXPERIMENT 06 — Metrics Series Through Damage and Repair")
    print("=" * 70)
    print("""
We track all quantities through the full damage-repair cycle.
The output is numbers: reachable_volume, mean_fanout, sink_density,
hub_density at each stage. From these we compute repair_efficiency.
""")

    strategies = [
        (strategy_full_restore, "full_restore"),
        (strategy_hub_first, "hub_first"),
        (strategy_sink_rescue, "sink_rescue"),
        (strategy_random_partial(0.5, seed=7), "random_50%"),
    ]

    damage_fractions = [0.2, 0.4, 0.6]

    graph_factories = {
        "random_dag":    lambda: make_random_dag(n=20, edge_density=0.2, seed=42),
        "hub_and_spoke": lambda: make_hub_and_spoke(spokes=5, spoke_length=3),
        "repair_corridor": lambda: make_repair_corridor_test(n=14, seed=7),
    }

    print("\nReachable volume: before → after_damage → after_repair")
    print("─" * 70)

    efficiency_table = []

    for graph_name, factory in graph_factories.items():
        print(f"\n  Graph: {graph_name}")
        print(f"  {'strategy':<20} {'dmg%':>6} {'pre':>8} {'damaged':>10} {'repaired':>10} {'eff':>8}")
        print("  " + "─" * 66)

        for damage_frac in damage_fractions:
            for strategy_fn, strategy_name in strategies:
                series, ops = run_cycle(factory, strategy_fn, strategy_name, damage_frac)
                vols = series.volumes

                if len(vols) >= 3:
                    pre, post_dmg, post_rep = vols[0], vols[1], vols[2]
                else:
                    continue

                eff = repair_efficiency(
                    series.snapshots[1],
                    series.snapshots[2],
                    max(ops, 1),
                )

                print(
                    f"  {strategy_name:<20} {damage_frac:>5.0%} "
                    f"{pre:>8} {post_dmg:>10} {post_rep:>10} "
                    f"{eff:>8.2f}"
                )

                efficiency_table.append({
                    "graph": graph_name,
                    "strategy": strategy_name,
                    "damage_frac": damage_frac,
                    "pre_vol": pre,
                    "post_damage_vol": post_dmg,
                    "post_repair_vol": post_rep,
                    "ops": ops,
                    "efficiency": eff,
                })

    print("\n" + "=" * 70)
    print("EFFICIENCY RANKING (by mean repair_efficiency across damage levels)")
    print("=" * 70)

    from collections import defaultdict
    strategy_effs = defaultdict(list)
    for row in efficiency_table:
        strategy_effs[row["strategy"]].append(row["efficiency"])

    ranked = sorted(
        strategy_effs.items(),
        key=lambda kv: sum(kv[1]) / len(kv[1]),
        reverse=True,
    )

    print(f"\n  {'strategy':<22} {'mean_efficiency':>16} {'n_trials':>10}")
    print("  " + "─" * 52)
    for strat, effs in ranked:
        mean_eff = sum(effs) / len(effs)
        print(f"  {strat:<22} {mean_eff:>16.3f} {len(effs):>10}")

    print("""
repair_efficiency = recovered_reachable_volume / repair_operations

A high value means each restoration operation recovered a lot of
reachable space. This is the quantity repair corridors are designed
to maximize: a corridor-aware strategy should recover more volume
per operation than a random one.

If full_restore has highest efficiency, it means the recovered operations
all contributed to reachability — every restored edge mattered.
If hub_first beats random_50%, it means hub-awareness is genuinely
routing repair through high-leverage positions.
""")

    # Also show a sample MetricsSeries in full
    print("=" * 70)
    print("SAMPLE: Full MetricsSeries for hub_and_spoke, 40% damage, hub_first")
    print("=" * 70)
    g = make_hub_and_spoke(spokes=5, spoke_length=3)
    series = MetricsSeries(label="sample_hub_spoke")
    series.record(g, event="baseline")
    r1 = g.damage_random(fraction=0.4, rng_seed=1)
    series.record(g, event="after_40%_damage")
    ops = strategy_hub_first(g, r1)
    series.record(g, event=f"after_hub_repair({ops}ops)")
    series.print_series()


if __name__ == "__main__":
    run()
