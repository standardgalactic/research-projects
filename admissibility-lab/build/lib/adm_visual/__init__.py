"""
adm.visual — Instrumentation for observing admissibility geometry.

This is not a visualization layer for communicating existing theorems.
It is an instrument for generating observations.

Two rendering backends:
  - Terminal: ASCII/ANSI output, no dependencies beyond stdlib
  - Plot: matplotlib-based, produces figures for inspection

The goal in both cases is the same: make the continuation geometry
*feel* — so you notice structures you didn't put there.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Tuple

from adm_core import State, Trajectory
from adm_graph import AdmissibilityGraph
from adm_repair import RepairResult


# ---------------------------------------------------------------------------
# Terminal renderer
# ---------------------------------------------------------------------------

class TerminalRenderer:
    """
    Render admissibility geometry to the terminal.

    Designed to work without any external dependencies.
    ANSI color codes used where available.
    """

    COLORS = {
        "reset":  "\033[0m",
        "red":    "\033[91m",
        "yellow": "\033[93m",
        "green":  "\033[92m",
        "cyan":   "\033[96m",
        "dim":    "\033[2m",
        "bold":   "\033[1m",
    }

    def __init__(self, color: bool = True) -> None:
        self.color = color and os.getenv("NO_COLOR") is None

    def _c(self, name: str, text: str) -> str:
        if not self.color:
            return text
        return f"{self.COLORS[name]}{text}{self.COLORS['reset']}"

    def render_graph_summary(self, graph: AdmissibilityGraph) -> None:
        s = graph.summary()
        label = graph.label or "unnamed"
        print(self._c("bold", f"\n╔══ AdmissibilityGraph: {label} ══"))
        print(f"  states:           {s['states']}")
        print(f"  continuations:    {s['continuations']}")
        print(f"  constraints:      {s['constraints']}")
        print(f"  sinks:            {self._c('red', str(s['sinks']))}")
        print(f"  bottlenecks:      {self._c('yellow', str(s['bottlenecks']))}")
        print(f"  hubs:             {self._c('green', str(s['hubs']))}")
        print(f"  mean fan-out:     {s['mean_fan_out']:.2f}")
        print(f"  mean reachability:{s['mean_reachability']:.2f}")
        print(self._c("dim", "╚" + "═" * 40))

    def render_fan_out_map(self, graph: AdmissibilityGraph, width: int = 40) -> None:
        fan = graph.fan_out_map()
        states = list(graph.states)
        max_fan = max(fan.values()) if fan else 1

        print(self._c("bold", "\n Fan-out profile (admissibility per state)"))
        print(self._c("dim", f"  {'state':<18} {'fan-out':<8} bar"))
        print(self._c("dim", "  " + "─" * 50))

        for state in sorted(states, key=lambda s: fan.get(s.id, 0), reverse=True):
            f = fan.get(state.id, 0)
            bar_len = int((f / max(max_fan, 1)) * width)
            bar = "█" * bar_len

            if f == 0:
                bar_colored = self._c("red", bar or "▪ SINK")
            elif f == 1:
                bar_colored = self._c("yellow", bar)
            elif f >= 3:
                bar_colored = self._c("green", bar)
            else:
                bar_colored = bar

            tag = state.label or state.id[:8]
            print(f"  {tag:<18} {f:<8} {bar_colored}")

    def render_trajectory(self, traj: Trajectory) -> None:
        label = traj.label or "unlabeled"
        print(self._c("bold", f"\n Trajectory: {label}"))
        print(self._c("dim", f"  steps={len(traj)}"))

        sizes = traj.admissibility_sizes
        bottlenecks = set(traj.bottleneck_indices)
        sinks = set(traj.sink_indices)

        for i, (state, adm) in enumerate(traj.steps):
            tag = state.label or state.id[:8]
            f = adm.size
            bar = "█" * min(f, 20)

            if i in sinks:
                marker = self._c("red", "⚑ SINK")
                bar_col = self._c("red", bar or "▪")
            elif i in bottlenecks:
                marker = self._c("yellow", "⬡ bottle")
                bar_col = self._c("yellow", bar)
            elif f >= 3:
                marker = self._c("green", "◈ hub")
                bar_col = self._c("green", bar)
            else:
                marker = ""
                bar_col = bar

            print(f"  [{i:>3}] {tag:<18} fan={f:<4} {bar_col:<22} {marker}")

    def render_reachability_map(self, graph: AdmissibilityGraph) -> None:
        reach = graph.reachability_map()
        states = list(graph.states)
        max_r = max(reach.values()) if reach else 1

        print(self._c("bold", "\n Reachability map (forward navigability)"))
        print(self._c("dim", f"  {'state':<18} {'reach':<8} bar"))
        print(self._c("dim", "  " + "─" * 50))

        for state in sorted(states, key=lambda s: reach.get(s.id, 0), reverse=True):
            r = reach.get(state.id, 0)
            bar_len = int((r / max(max_r, 1)) * 30)
            bar = "░" * bar_len

            if r == 0:
                col = "red"
            elif r < max_r * 0.3:
                col = "yellow"
            else:
                col = "green"

            tag = state.label or state.id[:8]
            print(f"  {tag:<18} {r:<8} {self._c(col, bar)}")

    def render_repair_results(self, results: List[RepairResult]) -> None:
        """Compact observation display for repair experiment results."""
        print(self._c("bold", "\n Repair Experiment Observations"))

        fracs = sorted({r.damage_fraction for r in results})
        for frac in fracs:
            subset = [r for r in results if r.damage_fraction == frac]
            strats = sorted({r.strategy_name for r in subset})

            print(f"\n  Damage {frac:.0%}  (n={len(subset)} trials across {len(strats)} strategies)")
            for strat in strats:
                s = [r for r in subset if r.strategy_name == strat]
                mean_rec = sum(r.recovery_rate for r in s) / len(s)
                mean_reach_loss = sum(r.reachability_loss for r in s) / len(s)
                mean_reach_rest = sum(r.reachability_restored for r in s) / len(s)

                rec_col = "green" if mean_rec > 0.7 else ("yellow" if mean_rec > 0.3 else "red")
                short = strat.replace("strategy_", "")[:30]
                print(
                    f"    {short:<32} "
                    f"recovery={self._c(rec_col, f'{mean_rec:.0%}'):<20} "
                    f"reach_loss={mean_reach_loss:+.2f}  "
                    f"reach_restored={mean_reach_rest:+.2f}"
                )


# ---------------------------------------------------------------------------
# Matplotlib renderer (optional)
# ---------------------------------------------------------------------------

class PlotRenderer:
    """
    Matplotlib-based renderer for admissibility geometry.
    Requires matplotlib (pip install matplotlib).
    """

    def __init__(self) -> None:
        try:
            import matplotlib.pyplot as plt
            import matplotlib.cm as cm
            self.plt = plt
            self.cm = cm
            self.available = True
        except ImportError:
            self.available = False
            print("PlotRenderer: matplotlib not available. Install with: pip install matplotlib")

    def _require(self) -> bool:
        if not self.available:
            print("matplotlib required. pip install matplotlib")
            return False
        return True

    def plot_fan_out(
        self,
        graph: AdmissibilityGraph,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ) -> None:
        if not self._require():
            return
        plt = self.plt

        fan = graph.fan_out_map()
        states = sorted(graph.states, key=lambda s: fan.get(s.id, 0))
        labels = [s.label or s.id[:6] for s in states]
        values = [fan.get(s.id, 0) for s in states]
        colors = ["#cc3333" if v == 0 else "#cc9900" if v == 1 else "#33aa55" for v in values]

        fig, ax = plt.subplots(figsize=(max(8, len(states) * 0.4), 5))
        ax.barh(labels, values, color=colors, edgecolor="none")
        ax.set_xlabel("Fan-out (admissible continuations)")
        ax.set_title(title or f"Fan-out profile: {graph.label or 'graph'}")
        ax.axvline(x=1, color="orange", linestyle="--", alpha=0.5, label="bottleneck threshold")
        ax.legend()
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=120)
            print(f"Saved: {save_path}")
        else:
            plt.show()

    def plot_trajectory_navigability(
        self,
        traj: Trajectory,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ) -> None:
        if not self._require():
            return
        plt = self.plt

        sizes = traj.admissibility_sizes
        steps = list(range(len(sizes)))
        bottlenecks = traj.bottleneck_indices
        sinks = traj.sink_indices

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(steps, sizes, color="#33aa55", linewidth=1.5, label="fan-out")
        ax.fill_between(steps, sizes, alpha=0.15, color="#33aa55")

        for b in bottlenecks:
            ax.axvline(x=b, color="orange", alpha=0.5, linewidth=1)
        for s in sinks:
            ax.axvline(x=s, color="red", alpha=0.7, linewidth=1.5)

        ax.set_xlabel("Trajectory step")
        ax.set_ylabel("Admissibility set size (fan-out)")
        ax.set_title(title or f"Navigability profile: {traj.label or 'trajectory'}")
        ax.legend()
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=120)
            print(f"Saved: {save_path}")
        else:
            plt.show()

    def plot_repair_recovery(
        self,
        results: List[RepairResult],
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ) -> None:
        if not self._require():
            return
        plt = self.plt
        import numpy as np

        fracs = sorted({r.damage_fraction for r in results})
        strategies = sorted({r.strategy_name for r in results})
        colors = ["#3366cc", "#cc3300", "#33aa55", "#cc9900", "#993399"]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        for i, strat in enumerate(strategies):
            rec_means = []
            reach_means = []
            color = colors[i % len(colors)]
            short = strat.replace("strategy_", "")

            for frac in fracs:
                subset = [r for r in results if r.damage_fraction == frac and r.strategy_name == strat]
                if subset:
                    rec_means.append(sum(r.recovery_rate for r in subset) / len(subset))
                    reach_means.append(sum(r.reachability_restored for r in subset) / len(subset))
                else:
                    rec_means.append(0)
                    reach_means.append(0)

            axes[0].plot([f * 100 for f in fracs], [r * 100 for r in rec_means],
                        marker="o", label=short, color=color)
            axes[1].plot([f * 100 for f in fracs], reach_means,
                        marker="o", label=short, color=color)

        axes[0].set_xlabel("Damage fraction (%)")
        axes[0].set_ylabel("Recovery rate (%)")
        axes[0].set_title("Recovery rate by strategy")
        axes[0].legend(fontsize=8)

        axes[1].set_xlabel("Damage fraction (%)")
        axes[1].set_ylabel("Reachability restored")
        axes[1].set_title("Reachability restoration by strategy")
        axes[1].legend(fontsize=8)

        fig.suptitle(title or "Repair Experiment Results")
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=120)
            print(f"Saved: {save_path}")
        else:
            plt.show()

    def plot_graph_structure(
        self,
        graph: AdmissibilityGraph,
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ) -> None:
        """Force-directed layout of the admissibility graph. Requires networkx."""
        if not self._require():
            return
        try:
            import networkx as nx
        except ImportError:
            print("plot_graph_structure requires networkx: pip install networkx")
            return

        plt = self.plt
        G = nx.DiGraph()
        fan = graph.fan_out_map()

        for state in graph.states:
            G.add_node(state.id, label=state.label or state.id[:6])

        for cont in graph.continuations:
            G.add_edge(cont.source.id, cont.target.id, weight=cont.weight)

        pos = nx.spring_layout(G, seed=42)
        node_colors = []
        for nid in G.nodes():
            f = fan.get(nid, 0)
            if f == 0:
                node_colors.append("#cc3333")
            elif f == 1:
                node_colors.append("#cc9900")
            elif f >= 3:
                node_colors.append("#33aa55")
            else:
                node_colors.append("#6699cc")

        labels = {nid: G.nodes[nid]["label"] for nid in G.nodes()}

        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw_networkx(G, pos, ax=ax, labels=labels,
                        node_color=node_colors, node_size=400,
                        arrows=True, font_size=7, edge_color="#888888",
                        width=0.8, alpha=0.9)
        ax.set_title(title or f"Admissibility graph: {graph.label or 'unnamed'}")
        ax.axis("off")
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=120)
            print(f"Saved: {save_path}")
        else:
            plt.show()
