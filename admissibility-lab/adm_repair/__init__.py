"""
adm.repair — Repair Theory implementation.

Repair is not error-correction (restore prior state) or exception-handling
(branch to alternative).  Repair is ontologically primary: the system is
always already in a repair-eligible condition.

The repair simulator runs experiments:
  - damage a graph by a specified protocol
  - attempt repair by various strategies
  - record what survived, what was reconstructed, what could not be recovered
  - accumulate observations across thousands of trials to discover invariants

The RepairSimulator is the laboratory instrument.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from adm_core import State, Continuation, Constraint, Trajectory
from adm_graph import AdmissibilityGraph, GraphDamageRecord


# ---------------------------------------------------------------------------
# Repair strategies
# ---------------------------------------------------------------------------

RepairStrategy = Callable[[AdmissibilityGraph, GraphDamageRecord], int]
"""
A repair strategy is a function that takes the damaged graph and the damage
record, attempts some restoration, and returns the number of continuations
recovered.
"""


def strategy_full_restore(
    graph: AdmissibilityGraph,
    record: GraphDamageRecord,
) -> int:
    """Restore everything. Baseline upper bound."""
    n = record.damage_count
    record.restore()
    return n


def strategy_hub_first(
    graph: AdmissibilityGraph,
    record: GraphDamageRecord,
    hub_threshold: int = 2,
) -> int:
    """
    Restore continuations that connect to high-fan-out states first.
    Hypothesis: repair corridors route through hubs.
    """
    hub_ids = {s.id for s in graph.hubs(threshold=hub_threshold)}
    hub_conts = [
        c for c in record.removed_continuations
        if c.source.id in hub_ids or c.target.id in hub_ids
    ]
    for cont in hub_conts:
        graph.add_continuation(cont)
        record.removed_continuations.discard(cont)
    return len(hub_conts)


def strategy_sink_rescue(
    graph: AdmissibilityGraph,
    record: GraphDamageRecord,
) -> int:
    """
    Restore continuations that would rescue states currently in sink condition.
    Priority: states with no outgoing continuations get at least one restored.
    """
    restored = 0
    sink_ids = {s.id for s in graph.sinks()}
    rescued = set()

    for cont in list(record.removed_continuations):
        if cont.source.id in sink_ids and cont.source.id not in rescued:
            graph.add_continuation(cont)
            record.removed_continuations.discard(cont)
            rescued.add(cont.source.id)
            restored += 1

    return restored


def strategy_random_partial(
    fraction: float = 0.5,
    seed: Optional[int] = None,
) -> RepairStrategy:
    """Factory: repair a random fraction of damage."""
    def _strategy(graph: AdmissibilityGraph, record: GraphDamageRecord) -> int:
        return record.partial_restore(fraction, rng_seed=seed)
    _strategy.__name__ = f"strategy_random_partial({fraction:.0%})"
    return _strategy


# ---------------------------------------------------------------------------
# RepairExperiment result
# ---------------------------------------------------------------------------

@dataclass
class RepairResult:
    """
    The record of a single repair experiment.

    Fields are designed for statistical aggregation across many trials
    to discover invariants the mathematics doesn't yet describe.
    """
    trial_id: int
    damage_fraction: float
    damage_count: int
    strategy_name: str

    # pre-damage
    pre_states: int = 0
    pre_continuations: int = 0
    pre_sinks: int = 0
    pre_mean_fan_out: float = 0.0
    pre_mean_reachability: float = 0.0

    # post-damage (before repair)
    post_damage_sinks: int = 0
    post_damage_mean_fan_out: float = 0.0
    post_damage_mean_reachability: float = 0.0

    # post-repair
    recovered: int = 0
    post_repair_sinks: int = 0
    post_repair_mean_fan_out: float = 0.0
    post_repair_mean_reachability: float = 0.0

    # derived
    @property
    def recovery_rate(self) -> float:
        if self.damage_count == 0:
            return 1.0
        return self.recovered / self.damage_count

    @property
    def sink_increase(self) -> int:
        return self.post_damage_sinks - self.pre_sinks

    @property
    def sink_reduction_by_repair(self) -> int:
        return self.post_damage_sinks - self.post_repair_sinks

    @property
    def reachability_loss(self) -> float:
        return self.pre_mean_reachability - self.post_damage_mean_reachability

    @property
    def reachability_restored(self) -> float:
        return self.post_repair_mean_reachability - self.post_damage_mean_reachability

    def as_dict(self) -> dict:
        return {
            "trial_id": self.trial_id,
            "damage_fraction": self.damage_fraction,
            "damage_count": self.damage_count,
            "strategy": self.strategy_name,
            "pre_sinks": self.pre_sinks,
            "pre_mean_fan_out": round(self.pre_mean_fan_out, 3),
            "pre_mean_reachability": round(self.pre_mean_reachability, 3),
            "post_damage_sinks": self.post_damage_sinks,
            "post_damage_mean_fan_out": round(self.post_damage_mean_fan_out, 3),
            "post_damage_mean_reachability": round(self.post_damage_mean_reachability, 3),
            "recovered": self.recovered,
            "recovery_rate": round(self.recovery_rate, 3),
            "post_repair_sinks": self.post_repair_sinks,
            "post_repair_mean_fan_out": round(self.post_repair_mean_fan_out, 3),
            "post_repair_mean_reachability": round(self.post_repair_mean_reachability, 3),
            "sink_increase": self.sink_increase,
            "sink_reduction_by_repair": self.sink_reduction_by_repair,
            "reachability_loss": round(self.reachability_loss, 3),
            "reachability_restored": round(self.reachability_restored, 3),
        }


# ---------------------------------------------------------------------------
# RepairSimulator
# ---------------------------------------------------------------------------

class RepairSimulator:
    """
    The primary laboratory instrument for repair experiments.

    Usage pattern:
        sim = RepairSimulator(graph_factory=my_factory)
        results = sim.run(
            trials=1000,
            damage_fractions=[0.1, 0.3, 0.5],
            strategies=[strategy_hub_first, strategy_sink_rescue],
        )
        sim.report(results)

    The graph_factory is called fresh for each trial, ensuring independence.
    """

    def __init__(
        self,
        graph_factory: Callable[[], AdmissibilityGraph],
        seed: Optional[int] = None,
    ) -> None:
        self.graph_factory = graph_factory
        self.rng = random.Random(seed)

    def _snapshot_summary(self, graph: AdmissibilityGraph) -> dict:
        s = graph.summary()
        return {
            "states": s["states"],
            "continuations": s["continuations"],
            "sinks": s["sinks"],
            "mean_fan_out": s["mean_fan_out"],
            "mean_reachability": s["mean_reachability"],
        }

    def run_trial(
        self,
        trial_id: int,
        damage_fraction: float,
        strategy: RepairStrategy,
        strategy_name: str,
    ) -> RepairResult:
        graph = self.graph_factory()
        pre = self._snapshot_summary(graph)

        record = graph.damage_random(
            fraction=damage_fraction,
            rng_seed=self.rng.randint(0, 2**31),
        )
        post_damage = self._snapshot_summary(graph)

        recovered = strategy(graph, record)
        post_repair = self._snapshot_summary(graph)

        return RepairResult(
            trial_id=trial_id,
            damage_fraction=damage_fraction,
            damage_count=record.damage_count + recovered,  # total originally removed
            strategy_name=strategy_name,
            pre_states=pre["states"],
            pre_continuations=pre["continuations"],
            pre_sinks=pre["sinks"],
            pre_mean_fan_out=pre["mean_fan_out"],
            pre_mean_reachability=pre["mean_reachability"],
            post_damage_sinks=post_damage["sinks"],
            post_damage_mean_fan_out=post_damage["mean_fan_out"],
            post_damage_mean_reachability=post_damage["mean_reachability"],
            recovered=recovered,
            post_repair_sinks=post_repair["sinks"],
            post_repair_mean_fan_out=post_repair["mean_fan_out"],
            post_repair_mean_reachability=post_repair["mean_reachability"],
        )

    def run(
        self,
        trials: int = 100,
        damage_fractions: Optional[List[float]] = None,
        strategies: Optional[List[RepairStrategy]] = None,
        verbose: bool = True,
    ) -> List[RepairResult]:
        """
        Run the repair experiment battery.

        Each combination of (damage_fraction, strategy) is run `trials` times.
        Results accumulate for statistical analysis.
        """
        if damage_fractions is None:
            damage_fractions = [0.1, 0.2, 0.3, 0.5]
        if strategies is None:
            strategies = [strategy_full_restore, strategy_hub_first, strategy_sink_rescue]

        results = []
        trial_id = 0
        t0 = time.time()

        for frac in damage_fractions:
            for strategy in strategies:
                name = getattr(strategy, "__name__", repr(strategy))
                for _ in range(trials):
                    r = self.run_trial(trial_id, frac, strategy, name)
                    results.append(r)
                    trial_id += 1

                if verbose:
                    subset = [r for r in results if r.damage_fraction == frac and r.strategy_name == name]
                    mean_recovery = sum(r.recovery_rate for r in subset) / len(subset)
                    mean_sink_change = sum(r.sink_increase for r in subset) / len(subset)
                    print(
                        f"  frac={frac:.0%}  strategy={name:<35}  "
                        f"mean_recovery={mean_recovery:.1%}  "
                        f"mean_sink_increase={mean_sink_change:+.1f}"
                    )

        elapsed = time.time() - t0
        if verbose:
            print(f"\n{trial_id} trials completed in {elapsed:.1f}s")

        return results

    def report(self, results: List[RepairResult]) -> None:
        """
        Print a structured observation report.

        This is not a summary — it's a field report.  The goal is to surface
        recurring structures: quantities that appear across conditions and
        demand explanation.
        """
        print("\n" + "="*70)
        print("REPAIR EXPERIMENT — OBSERVATION REPORT")
        print("="*70)

        fracs = sorted({r.damage_fraction for r in results})
        strategies = sorted({r.strategy_name for r in results})

        for frac in fracs:
            print(f"\n── Damage fraction: {frac:.0%} ──")
            for strat in strategies:
                subset = [r for r in results if r.damage_fraction == frac and r.strategy_name == strat]
                if not subset:
                    continue

                mean_recovery = sum(r.recovery_rate for r in subset) / len(subset)
                mean_reach_loss = sum(r.reachability_loss for r in subset) / len(subset)
                mean_reach_restored = sum(r.reachability_restored for r in subset) / len(subset)
                mean_sink_inc = sum(r.sink_increase for r in subset) / len(subset)
                mean_sink_red = sum(r.sink_reduction_by_repair for r in subset) / len(subset)

                print(f"  {strat}")
                print(f"    recovery rate:              {mean_recovery:.1%}")
                print(f"    reachability loss:          {mean_reach_loss:+.3f}")
                print(f"    reachability restored:      {mean_reach_restored:+.3f}")
                print(f"    sink increase (damage):     {mean_sink_inc:+.1f}")
                print(f"    sink reduction (repair):    {mean_sink_red:+.1f}")

        print("\n── Cross-strategy observations ──")
        # Flag if hub-first consistently outperforms random on reachability restoration
        for frac in fracs:
            hub_subset = [r for r in results if r.damage_fraction == frac and "hub_first" in r.strategy_name]
            rand_subset = [r for r in results if r.damage_fraction == frac and "random" in r.strategy_name]
            if hub_subset and rand_subset:
                hub_reach = sum(r.reachability_restored for r in hub_subset) / len(hub_subset)
                rand_reach = sum(r.reachability_restored for r in rand_subset) / len(rand_subset)
                if hub_reach > rand_reach:
                    print(f"  frac={frac:.0%}: hub-first restores more reachability than random ({hub_reach:.3f} vs {rand_reach:.3f})")
                else:
                    print(f"  frac={frac:.0%}: hub-first does NOT outperform random on reachability ({hub_reach:.3f} vs {rand_reach:.3f})")

        print("="*70)

    def export_csv(self, results: List[RepairResult], path: str) -> None:
        """Export results to CSV for external analysis."""
        import csv
        if not results:
            return
        fieldnames = list(results[0].as_dict().keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r.as_dict())
        print(f"Results exported to {path}")
