"""
adm.archaeology — Trajectory reconstruction experiments.

The core question: given a set of trajectories recorded from an unknown graph,
how much of the original graph structure can be recovered from the trajectory
residue alone?

This connects MEM|8, Phoenix, Replay Invariance, and Generative Compression
to a single computational substrate. All of them are asking: what survives
in the residue when the generating structure is no longer directly accessible?

The experimental protocol:
  1. Generate a graph (the "ground truth")
  2. Walk N trajectories through the graph, recording full admissibility history
  3. Discard the graph
  4. Attempt to reconstruct structural features from trajectory residue alone
  5. Measure reconstruction fidelity as a function of trajectory count

Reconstruction fidelity is the key measurement:
  - Can we identify which states were hubs? (high fan-out in trajectories)
  - Can we identify which states were sinks? (trajectories end there)
  - Can we identify bottlenecks? (fan-out dips in many trajectories at same step)
  - Can we identify repair corridors? (trajectories consistently route through same states)

The question "how many trajectories are required for reliable reconstruction?"
directly measures the information content of the admissibility structure.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from adm_core import State, Trajectory
from adm_graph import AdmissibilityGraph
from adm_metrics import TrajectoryMetrics


# ---------------------------------------------------------------------------
# TrajectoryResidueRecord
# ---------------------------------------------------------------------------

@dataclass
class TrajectoryResidueRecord:
    """
    What remains of a graph after you discard it, keeping only trajectories.

    Built from a collection of Trajectory objects. Contains:
      - visit counts per state id
      - fan-out observations per state id (across all visits)
      - transition counts (source_id, target_id) → count
      - sink observations (states where trajectories terminated)
      - bottleneck observations (states where fan-out dropped locally)
    """
    state_visits: Counter = field(default_factory=Counter)
    fanout_observations: Dict[str, List[int]] = field(default_factory=lambda: defaultdict(list))
    transition_counts: Counter = field(default_factory=Counter)
    observed_sinks: Counter = field(default_factory=Counter)
    observed_bottlenecks: Counter = field(default_factory=Counter)
    trajectory_count: int = 0
    state_labels: Dict[str, str] = field(default_factory=dict)  # id → label

    def ingest(self, traj: Trajectory) -> None:
        """Record observations from a trajectory."""
        self.trajectory_count += 1
        sizes = traj.admissibility_sizes
        bottleneck_indices = set(traj.bottleneck_indices)
        sink_indices = set(traj.sink_indices)

        for i, (state, adm) in enumerate(traj.steps):
            sid = state.id
            self.state_visits[sid] += 1
            self.fanout_observations[sid].append(adm.size)
            if state.label:
                self.state_labels[sid] = state.label
            if i in sink_indices:
                self.observed_sinks[sid] += 1
            if i in bottleneck_indices:
                self.observed_bottlenecks[sid] += 1

        # Record transitions
        for i in range(len(traj.steps) - 1):
            src = traj.steps[i][0]
            tgt = traj.steps[i+1][0]
            self.transition_counts[(src.id, tgt.id)] += 1

    def mean_fanout(self, state_id: str) -> float:
        obs = self.fanout_observations.get(state_id, [])
        return sum(obs) / max(len(obs), 1)

    def inferred_hubs(self, min_fanout: float = 2.5) -> List[str]:
        """State ids where mean observed fan-out suggests hub status."""
        return [
            sid for sid in self.state_visits
            if self.mean_fanout(sid) >= min_fanout
        ]

    def inferred_sinks(self, min_sink_rate: float = 0.3) -> List[str]:
        """State ids where trajectories frequently terminated."""
        return [
            sid for sid in self.state_visits
            if self.observed_sinks[sid] / max(self.state_visits[sid], 1) >= min_sink_rate
        ]

    def inferred_bottlenecks(self, min_bottleneck_rate: float = 0.2) -> List[str]:
        """State ids frequently observed at bottleneck positions."""
        return [
            sid for sid in self.state_visits
            if self.observed_bottlenecks[sid] / max(self.state_visits[sid], 1) >= min_bottleneck_rate
        ]

    def inferred_repair_corridors(self, top_n: int = 5) -> List[Tuple[str, str]]:
        """
        Transitions that appear most frequently — repair corridors tend to
        be routes that trajectories keep returning to.
        """
        return [pair for pair, _ in self.transition_counts.most_common(top_n)]


# ---------------------------------------------------------------------------
# ReconstructionFidelity
# ---------------------------------------------------------------------------

@dataclass
class ReconstructionFidelity:
    """
    How well does the trajectory residue predict actual graph structure?

    Computed by comparing inferred structural features against ground truth.
    """
    hub_precision: float = 0.0      # fraction of inferred hubs that are real hubs
    hub_recall: float = 0.0         # fraction of real hubs that were inferred
    sink_precision: float = 0.0
    sink_recall: float = 0.0
    bottleneck_precision: float = 0.0
    bottleneck_recall: float = 0.0
    trajectory_count: int = 0

    @property
    def hub_f1(self) -> float:
        p, r = self.hub_precision, self.hub_recall
        return 2 * p * r / max(p + r, 1e-9)

    @property
    def overall_fidelity(self) -> float:
        """Mean F1 across all structural feature types."""
        return (self.hub_f1 + self._sink_f1 + self._bottleneck_f1) / 3.0

    @property
    def _sink_f1(self) -> float:
        p, r = self.sink_precision, self.sink_recall
        return 2 * p * r / max(p + r, 1e-9)

    @property
    def _bottleneck_f1(self) -> float:
        p, r = self.bottleneck_precision, self.bottleneck_recall
        return 2 * p * r / max(p + r, 1e-9)

    def as_dict(self) -> dict:
        return {
            "trajectory_count": self.trajectory_count,
            "hub_precision": round(self.hub_precision, 3),
            "hub_recall": round(self.hub_recall, 3),
            "hub_f1": round(self.hub_f1, 3),
            "sink_precision": round(self.sink_precision, 3),
            "sink_recall": round(self.sink_recall, 3),
            "sink_f1": round(self._sink_f1, 3),
            "bottleneck_precision": round(self.bottleneck_precision, 3),
            "bottleneck_recall": round(self.bottleneck_recall, 3),
            "bottleneck_f1": round(self._bottleneck_f1, 3),
            "overall_fidelity": round(self.overall_fidelity, 3),
        }


def _precision_recall(inferred: Set[str], ground_truth: Set[str]) -> Tuple[float, float]:
    if not inferred:
        return 0.0, 0.0
    precision = len(inferred & ground_truth) / len(inferred)
    recall = len(inferred & ground_truth) / max(len(ground_truth), 1)
    return precision, recall


# ---------------------------------------------------------------------------
# ArchaeologyExperiment
# ---------------------------------------------------------------------------

class ArchaeologyExperiment:
    """
    The trajectory archaeology instrument.

    Protocol:
      1. Build a graph (ground truth stored for fidelity measurement)
      2. Walk trajectories from random source states
      3. After each batch of trajectories, compute reconstruction fidelity
      4. Plot fidelity curve as function of trajectory count

    The fidelity curve answers: how many trajectories are required for
    reliable reconstruction of each structural feature?
    """

    def __init__(
        self,
        graph: AdmissibilityGraph,
        seed: Optional[int] = None,
    ) -> None:
        self.graph = graph
        self.rng = random.Random(seed)
        self._ground_truth_hubs: Set[str] = {s.id for s in graph.hubs(threshold=3)}
        self._ground_truth_sinks: Set[str] = {s.id for s in graph.sinks()}
        self._ground_truth_bottlenecks: Set[str] = {s.id for s in graph.bottlenecks(threshold=1)}

    def walk_trajectory(self, max_steps: int = 50) -> Trajectory:
        """Walk from a random source state."""
        states = list(self.graph.states)
        if not states:
            return Trajectory()
        source = self.rng.choice(states)
        return self.graph.walk(source, max_steps=max_steps)

    def measure_fidelity(
        self,
        residue: TrajectoryResidueRecord,
        hub_min_fanout: float = 2.5,
        sink_min_rate: float = 0.3,
        bottleneck_min_rate: float = 0.2,
    ) -> ReconstructionFidelity:
        inferred_hubs = set(residue.inferred_hubs(hub_min_fanout))
        inferred_sinks = set(residue.inferred_sinks(sink_min_rate))
        inferred_bottlenecks = set(residue.inferred_bottlenecks(bottleneck_min_rate))

        hub_p, hub_r = _precision_recall(inferred_hubs, self._ground_truth_hubs)
        sink_p, sink_r = _precision_recall(inferred_sinks, self._ground_truth_sinks)
        btn_p, btn_r = _precision_recall(inferred_bottlenecks, self._ground_truth_bottlenecks)

        return ReconstructionFidelity(
            hub_precision=hub_p,
            hub_recall=hub_r,
            sink_precision=sink_p,
            sink_recall=sink_r,
            bottleneck_precision=btn_p,
            bottleneck_recall=btn_r,
            trajectory_count=residue.trajectory_count,
        )

    def run(
        self,
        max_trajectories: int = 200,
        measure_every: int = 10,
        max_steps_per_walk: int = 50,
        verbose: bool = True,
    ) -> List[ReconstructionFidelity]:
        """
        Run the archaeology experiment.

        Walks trajectories incrementally, measuring fidelity at each checkpoint.
        Returns the fidelity curve — fidelity as a function of trajectory count.
        """
        residue = TrajectoryResidueRecord()
        fidelity_curve: List[ReconstructionFidelity] = []

        if verbose:
            print(f"\nArchaeology experiment: {self.graph.label or 'unnamed'}")
            print(f"  Ground truth — hubs: {len(self._ground_truth_hubs)}, "
                  f"sinks: {len(self._ground_truth_sinks)}, "
                  f"bottlenecks: {len(self._ground_truth_bottlenecks)}")
            print(f"  {'trajs':>6}  {'hub_f1':>8}  {'sink_f1':>8}  {'btn_f1':>8}  {'overall':>8}")
            print("  " + "─" * 50)

        for i in range(1, max_trajectories + 1):
            traj = self.walk_trajectory(max_steps=max_steps_per_walk)
            residue.ingest(traj)

            if i % measure_every == 0 or i == max_trajectories:
                fidelity = self.measure_fidelity(residue)
                fidelity_curve.append(fidelity)

                if verbose:
                    print(
                        f"  {i:>6}  "
                        f"{fidelity.hub_f1:>8.3f}  "
                        f"{fidelity._sink_f1:>8.3f}  "
                        f"{fidelity._bottleneck_f1:>8.3f}  "
                        f"{fidelity.overall_fidelity:>8.3f}"
                    )

        return fidelity_curve

    def saturation_point(
        self,
        fidelity_curve: List[ReconstructionFidelity],
        threshold: float = 0.8,
    ) -> Optional[int]:
        """
        First trajectory count at which overall fidelity exceeds threshold.
        Returns None if threshold was never reached.

        This is the key quantity: how many trajectories are required for
        reliable structural reconstruction?
        """
        for f in fidelity_curve:
            if f.overall_fidelity >= threshold:
                return f.trajectory_count
        return None
