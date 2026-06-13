"""
adm.metrics — First-class measurement for admissibility geometry.

Every good ecosystem ends up with metrics. Once you have graphs people
immediately ask: what is changing? These measurements let every experiment
produce numbers, not just pictures.

The core insight is that metrics should be computable from the live graph
state — not derived from theory in advance, but read off the instrument.

  reachable_volume     — total reachable states across all sources
  mean_fanout          — average admissible continuations per state
  bottleneck_density   — fraction of states that are bottlenecks
  sink_density         — fraction of states that are sinks
  hub_density          — fraction of states that are hubs
  repair_cost          — continuations restored per unit reachability gained
  trajectory_entropy   — entropy of fan-out distribution over a trajectory
  reconstruction_fidelity — how well trajectory residue predicts graph structure

Quantities appear here because they keep being useful in experiments,
not because they were planned in advance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from adm_core import State, Trajectory
from adm_graph import AdmissibilityGraph
from adm_repair import RepairResult


# ---------------------------------------------------------------------------
# AdmissibilityMetrics
# ---------------------------------------------------------------------------

@dataclass
class AdmissibilityMetrics:
    """
    A snapshot of measurable quantities for an AdmissibilityGraph.

    Compute with AdmissibilityMetrics.from_graph(g).
    Compare before/after damage or repair using delta().
    """
    label: str = ""

    # Volume
    state_count: int = 0
    continuation_count: int = 0
    constraint_count: int = 0
    reachable_volume: int = 0          # sum of reachable states across all sources

    # Density
    mean_fanout: float = 0.0
    sink_density: float = 0.0          # fraction of states that are sinks
    bottleneck_density: float = 0.0    # fraction that are bottlenecks (fanout == 1)
    hub_density: float = 0.0           # fraction with fanout >= 3
    mean_reachability: float = 0.0

    # Structural
    max_fanout: int = 0
    min_fanout_nonzero: int = 0        # minimum fanout among non-sink states
    fanout_variance: float = 0.0

    @classmethod
    def from_graph(cls, graph: AdmissibilityGraph, label: str = "") -> "AdmissibilityMetrics":
        s = graph.summary()
        states = list(graph.states)
        n = len(states)

        fanouts = [graph.admissibility_set(st).size for st in states]
        nonzero = [f for f in fanouts if f > 0]

        reachable_volume = sum(graph.reachability_map().values())
        mean_fanout = sum(fanouts) / max(n, 1)
        fanout_variance = (
            sum((f - mean_fanout) ** 2 for f in fanouts) / max(n, 1)
        )

        return cls(
            label=label or graph.label or "",
            state_count=n,
            continuation_count=s["continuations"],
            constraint_count=s["constraints"],
            reachable_volume=reachable_volume,
            mean_fanout=mean_fanout,
            sink_density=s["sinks"] / max(n, 1),
            bottleneck_density=s["bottlenecks"] / max(n, 1),
            hub_density=s["hubs"] / max(n, 1),
            mean_reachability=s["mean_reachability"],
            max_fanout=max(fanouts) if fanouts else 0,
            min_fanout_nonzero=min(nonzero) if nonzero else 0,
            fanout_variance=fanout_variance,
        )

    def delta(self, other: "AdmissibilityMetrics") -> "MetricsDelta":
        """Compute the change from self to other."""
        return MetricsDelta(before=self, after=other)

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "state_count": self.state_count,
            "continuation_count": self.continuation_count,
            "reachable_volume": self.reachable_volume,
            "mean_fanout": round(self.mean_fanout, 3),
            "sink_density": round(self.sink_density, 3),
            "bottleneck_density": round(self.bottleneck_density, 3),
            "hub_density": round(self.hub_density, 3),
            "mean_reachability": round(self.mean_reachability, 3),
            "max_fanout": self.max_fanout,
            "min_fanout_nonzero": self.min_fanout_nonzero,
            "fanout_variance": round(self.fanout_variance, 3),
        }

    def __repr__(self) -> str:
        return (
            f"AdmissibilityMetrics({self.label!r}, "
            f"vol={self.reachable_volume}, "
            f"fanout={self.mean_fanout:.2f}, "
            f"sinks={self.sink_density:.0%}, "
            f"hubs={self.hub_density:.0%})"
        )


# ---------------------------------------------------------------------------
# MetricsDelta
# ---------------------------------------------------------------------------

@dataclass
class MetricsDelta:
    """
    The change in metrics between two graph states.

    The primary use is before/after damage or repair:
        pre  = AdmissibilityMetrics.from_graph(g, "pre")
        damage_record = g.damage_random(0.3)
        post = AdmissibilityMetrics.from_graph(g, "post_damage")
        delta = pre.delta(post)
        print(delta)
    """
    before: AdmissibilityMetrics
    after: AdmissibilityMetrics

    @property
    def volume_change(self) -> int:
        return self.after.reachable_volume - self.before.reachable_volume

    @property
    def volume_change_pct(self) -> float:
        if self.before.reachable_volume == 0:
            return 0.0
        return self.volume_change / self.before.reachable_volume

    @property
    def fanout_change(self) -> float:
        return self.after.mean_fanout - self.before.mean_fanout

    @property
    def sink_density_change(self) -> float:
        return self.after.sink_density - self.before.sink_density

    @property
    def hub_density_change(self) -> float:
        return self.after.hub_density - self.before.hub_density

    def __repr__(self) -> str:
        return (
            f"MetricsDelta("
            f"vol={self.volume_change:+d} ({self.volume_change_pct:+.1%}), "
            f"fanout={self.fanout_change:+.2f}, "
            f"sinks={self.sink_density_change:+.1%}, "
            f"hubs={self.hub_density_change:+.1%})"
        )


# ---------------------------------------------------------------------------
# TrajectoryMetrics
# ---------------------------------------------------------------------------

@dataclass
class TrajectoryMetrics:
    """
    Measurements derived from a single Trajectory.

    trajectory_entropy captures how predictable the navigability profile is.
    High entropy = variable fan-out throughout (many different options at
    different steps). Low entropy = uniform fan-out (consistently open or
    consistently constrained).

    A trajectory that passes through a sharp bottleneck will show low
    entropy because the distribution is dominated by that narrow step.
    """
    label: str = ""
    length: int = 0
    mean_fanout: float = 0.0
    min_fanout: int = 0
    max_fanout: int = 0
    bottleneck_count: int = 0
    sink_count: int = 0
    trajectory_entropy: float = 0.0    # Shannon entropy of fan-out distribution
    post_bottleneck_recovery_rate: float = 0.0  # fraction of bottlenecks followed by increase
    navigability_arc: str = ""         # "rising", "falling", "stable", "volatile"

    @classmethod
    def from_trajectory(cls, traj: Trajectory) -> "TrajectoryMetrics":
        if not traj.steps:
            return cls(label=traj.label or "")

        sizes = traj.admissibility_sizes
        n = len(sizes)

        # Shannon entropy of the fan-out distribution
        total = sum(sizes)
        if total > 0:
            probs = [s / total for s in sizes if s > 0]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        else:
            entropy = 0.0

        # Post-bottleneck recovery rate
        bottlenecks = traj.bottleneck_indices
        recoveries = sum(
            1 for b in bottlenecks
            if b + 1 < n and sizes[b + 1] > sizes[b]
        )
        recovery_rate = recoveries / max(len(bottlenecks), 1) if bottlenecks else 0.0

        # Navigability arc
        first_half = sizes[:n//2]
        second_half = sizes[n//2:]
        mean_first = sum(first_half) / max(len(first_half), 1)
        mean_second = sum(second_half) / max(len(second_half), 1)
        variance = sum((s - (total/n))**2 for s in sizes) / max(n, 1)

        if variance < 0.5:
            arc = "stable"
        elif mean_second > mean_first * 1.2:
            arc = "rising"
        elif mean_second < mean_first * 0.8:
            arc = "falling"
        else:
            arc = "volatile"

        return cls(
            label=traj.label or "",
            length=n,
            mean_fanout=total / n,
            min_fanout=min(sizes),
            max_fanout=max(sizes),
            bottleneck_count=len(bottlenecks),
            sink_count=len(traj.sink_indices),
            trajectory_entropy=entropy,
            post_bottleneck_recovery_rate=recovery_rate,
            navigability_arc=arc,
        )

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "length": self.length,
            "mean_fanout": round(self.mean_fanout, 3),
            "min_fanout": self.min_fanout,
            "max_fanout": self.max_fanout,
            "bottleneck_count": self.bottleneck_count,
            "sink_count": self.sink_count,
            "trajectory_entropy": round(self.trajectory_entropy, 3),
            "post_bottleneck_recovery_rate": round(self.post_bottleneck_recovery_rate, 3),
            "navigability_arc": self.navigability_arc,
        }

    def __repr__(self) -> str:
        return (
            f"TrajectoryMetrics({self.label!r}, "
            f"len={self.length}, "
            f"entropy={self.trajectory_entropy:.2f}, "
            f"arc={self.navigability_arc}, "
            f"bottlenecks={self.bottleneck_count})"
        )


# ---------------------------------------------------------------------------
# RepairEfficiency
# ---------------------------------------------------------------------------

def repair_efficiency(before: AdmissibilityMetrics, after: AdmissibilityMetrics, operations: int) -> float:
    """
    Recovered reachable volume per repair operation.

    repair_efficiency = (after.reachable_volume - before.reachable_volume) / operations

    A high value means each repair operation restored a lot of reachability.
    A low value means repair was expensive relative to what it recovered.
    Negative means the repair made things worse (possible with naive strategies).
    """
    if operations == 0:
        return 0.0
    return (after.reachable_volume - before.reachable_volume) / operations


# ---------------------------------------------------------------------------
# MetricsSeries — track metrics over time
# ---------------------------------------------------------------------------

class MetricsSeries:
    """
    A time series of AdmissibilityMetrics snapshots.

    Used to track how a graph evolves across an experiment:
      - during progressive damage
      - during constraint accumulation
      - during repair
      - across repeated perturbations

    Automatically detects inflection points in reachable_volume.
    """

    def __init__(self, label: str = "") -> None:
        self.label = label
        self.snapshots: List[AdmissibilityMetrics] = []
        self.event_labels: List[str] = []

    def record(self, graph: AdmissibilityGraph, event: str = "") -> AdmissibilityMetrics:
        m = AdmissibilityMetrics.from_graph(graph, label=event)
        self.snapshots.append(m)
        self.event_labels.append(event)
        return m

    @property
    def volumes(self) -> List[int]:
        return [s.reachable_volume for s in self.snapshots]

    @property
    def fanouts(self) -> List[float]:
        return [s.mean_fanout for s in self.snapshots]

    def inflection_points(self) -> List[int]:
        """
        Indices where reachable_volume changed direction.
        Inflections are points of interest — where damage or repair
        crossed a threshold.
        """
        vols = self.volumes
        inflections = []
        for i in range(1, len(vols) - 1):
            prev_diff = vols[i] - vols[i-1]
            next_diff = vols[i+1] - vols[i]
            if (prev_diff > 0 and next_diff < 0) or (prev_diff < 0 and next_diff > 0):
                inflections.append(i)
        return inflections

    def print_series(self) -> None:
        print(f"\nMetricsSeries: {self.label}")
        print(f"  {'event':<28} {'vol':>8} {'fanout':>8} {'sinks':>8} {'hubs':>8}")
        print("  " + "─" * 60)
        for m, ev in zip(self.snapshots, self.event_labels):
            print(
                f"  {ev:<28} {m.reachable_volume:>8} "
                f"{m.mean_fanout:>8.2f} "
                f"{m.sink_density:>7.0%} "
                f"{m.hub_density:>7.0%}"
            )
        inflections = self.inflection_points()
        if inflections:
            events = [self.event_labels[i] for i in inflections]
            print(f"  Inflection points: {events}")
