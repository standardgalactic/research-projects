"""
examples/damaged_maze.py — The Flagship Communication Artifact

Damage removes possibilities.
Repair restores reachability.
A repair is valid when it increases admissible continuations.

This example makes the distinction immediately visible:
  - Repair does not restore the original maze
  - Repair finds a new corridor that restores path access

No monograph required.

Usage: python examples/damaged_maze.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from adm_core import State, Continuation, Constraint
from adm_graph import AdmissibilityGraph
from adm_metrics import AdmissibilityMetrics, MetricsDelta
from adm_visual import TerminalRenderer


MAZE = """
┌───────────────────────────┐
│ S . . # . . . . . . . . E │
│ . # . # . # # # # # . # . │
│ . # . . . . . . . # . # . │
│ . # # # # # # . . # . . . │
│ . . . . . . # . # # # # . │
│ # # # # . . # . . . . # . │
│ . . . . . # . . # . . . . │
└───────────────────────────┘
S = Start   E = End   # = Wall   . = Open
"""

def build_maze_graph() -> tuple[AdmissibilityGraph, State, State]:
    """
    Build a grid graph representing the maze above.
    Walls are represented as missing edges, not as constraints.
    This makes damage (removing edges) and repair (adding edges) natural.
    """
    rows, cols = 7, 13
    walls = {
        # Row 0
        (0, 3),
        # Row 1
        (1, 1), (1, 3), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 11),
        # Row 2
        (2, 1), (2, 9), (2, 11),
        # Row 3
        (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 9),
        # Row 4
        (4, 6), (4, 8), (4, 9), (4, 10), (4, 11),
        # Row 5
        (5, 0), (5, 1), (5, 2), (5, 3), (5, 6), (5, 11),
        # Row 6
        (6, 4), (6, 6), (6, 8),
    }

    g = AdmissibilityGraph(label="maze")
    states: dict[tuple, State] = {}

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in walls:
                s = State(label=f"r{r}c{c}")
                states[(r, c)] = s

    # Add edges between adjacent non-wall cells
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in states:
                continue
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in states:
                    g.add_continuation(Continuation(states[(r, c)], states[(nr, nc)]))

    start = states.get((0, 0)) or list(g.states)[0]
    end = states.get((0, 12)) or list(g.states)[-1]

    return g, start, end


def find_path(g: AdmissibilityGraph, source: State, target: State) -> list[State]:
    """BFS to find a path from source to target under current constraints."""
    from collections import deque
    visited = {source.id}
    queue = deque([(source, [source])])

    while queue:
        current, path = queue.popleft()
        if current.id == target.id:
            return path
        adm = g.admissibility_set(current)
        for cont in adm:
            if cont.target.id not in visited:
                visited.add(cont.target.id)
                queue.append((cont.target, path + [cont.target]))
    return []


def print_path_on_maze(path: list[State], label: str) -> None:
    path_labels = {s.label for s in path}

    rows, cols = 7, 13
    walls = {
        (0, 3), (1, 1), (1, 3), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 11),
        (2, 1), (2, 9), (2, 11), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6),
        (3, 9), (4, 6), (4, 8), (4, 9), (4, 10), (4, 11), (5, 0), (5, 1), (5, 2),
        (5, 3), (5, 6), (5, 11), (6, 4), (6, 6), (6, 8),
    }

    print(f"\n  {label}")
    print("  ┌" + "──" * cols + "┐")
    for r in range(rows):
        row_str = "  │"
        for c in range(cols):
            lbl = f"r{r}c{c}"
            if (r, c) in walls:
                row_str += "█ "
            elif r == 0 and c == 0:
                row_str += "S "
            elif r == 0 and c == cols - 1:
                row_str += "E "
            elif lbl in path_labels:
                row_str += "\033[92m* \033[0m"
            else:
                row_str += "· "
        row_str += "│"
        print(row_str)
    print("  └" + "──" * cols + "┘")


def run():
    renderer = TerminalRenderer()

    print("=" * 70)
    print("DAMAGED MAZE — Admissibility Repair Demo")
    print("=" * 70)
    print(MAZE)
    print("""
CORE CLAIM:
  Repair does not restore the original maze.
  Repair finds new corridors that restore reachability.

  A repair is valid when it increases admissible continuations.
  The original path is not required — any path to E suffices.
""")

    g, start, end = build_maze_graph()
    pre_metrics = AdmissibilityMetrics.from_graph(g, "pre_damage")

    # Find original path
    original_path = find_path(g, start, end)
    print_path_on_maze(original_path, f"ORIGINAL PATH ({len(original_path)} steps)")
    print(f"  Reachable volume: {pre_metrics.reachable_volume}")
    print(f"  Path length: {len(original_path)} steps")

    # ── DAMAGE ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("DAMAGE: Removing a corridor through the maze...")
    print("─" * 70)

    # Damage the middle section of the path
    if len(original_path) > 6:
        damaged_segment = original_path[3:7]
        edge_ids = set()
        for i in range(len(damaged_segment) - 1):
            s, t = damaged_segment[i], damaged_segment[i+1]
            edge_ids.add((s.id, t.id))
            edge_ids.add((t.id, s.id))  # bidirectional
        record = g.damage_edges(edge_ids)
    else:
        record = g.damage_random(fraction=0.3, rng_seed=42)

    post_damage_metrics = AdmissibilityMetrics.from_graph(g, "post_damage")
    damaged_path = find_path(g, start, end)

    if damaged_path:
        print_path_on_maze(damaged_path, f"PATH AFTER DAMAGE (still exists, {len(damaged_path)} steps)")
    else:
        print_path_on_maze([], "PATH AFTER DAMAGE: NO PATH EXISTS")

    print(f"  Reachable volume: {post_damage_metrics.reachable_volume} "
          f"(was {pre_metrics.reachable_volume})")
    delta = pre_metrics.delta(post_damage_metrics)
    print(f"  Volume change: {delta.volume_change:+d} ({delta.volume_change_pct:+.1%})")
    print(f"  New sinks created: {delta.sink_density_change:+.1%} of states")

    # ── REPAIR ──────────────────────────────────────────────────────────────
    print("\n" + "─" * 70)
    print("REPAIR: Restoring admissible continuations...")
    print("─" * 70)
    print("""
  The repair does not rebuild the original corridor.
  It restores enough edges that a path to E exists again.
  The new path may be completely different from the original.
""")

    # Try hub-first repair — restore edges connected to well-connected states
    from adm_repair import strategy_hub_first, strategy_sink_rescue
    ops1 = strategy_hub_first(g, record)

    post_repair_metrics = AdmissibilityMetrics.from_graph(g, "post_repair")
    repaired_path = find_path(g, start, end)

    if repaired_path:
        print_path_on_maze(repaired_path, f"PATH AFTER REPAIR ({len(repaired_path)} steps)")
        same_as_original = (
            len(repaired_path) == len(original_path) and
            all(a.id == b.id for a, b in zip(repaired_path, original_path))
        )
        print(f"  Same as original path: {same_as_original}")
        if not same_as_original:
            print("  → Repair found a new corridor. Original path not restored.")
            print("    This is the key distinction from error-correction.")
    else:
        print("  Repair did not restore path connectivity.")
        print("  (Hub-first repair may need more operations — try full restore)")
        record.restore()
        full_path = find_path(g, start, end)
        if full_path:
            print_path_on_maze(full_path, f"PATH AFTER FULL RESTORE ({len(full_path)} steps)")

    print(f"\n  Reachable volume: {post_repair_metrics.reachable_volume} "
          f"(damaged: {post_damage_metrics.reachable_volume}, "
          f"original: {pre_metrics.reachable_volume})")

    repair_delta = post_damage_metrics.delta(post_repair_metrics)
    print(f"  Volume recovered: {repair_delta.volume_change:+d} ({repair_delta.volume_change_pct:+.1%})")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"""
  Pre-damage reachable volume:    {pre_metrics.reachable_volume}
  Post-damage reachable volume:   {post_damage_metrics.reachable_volume}
  Post-repair reachable volume:   {post_repair_metrics.reachable_volume}

  Repair success = |R(repaired)| > |R(damaged)|
                 = {post_repair_metrics.reachable_volume} > {post_damage_metrics.reachable_volume}
                 = {post_repair_metrics.reachable_volume > post_damage_metrics.reachable_volume}

  Repair is not restoration of a prior state.
  Repair is restoration of admissible continuation.
""")


if __name__ == "__main__":
    run()
