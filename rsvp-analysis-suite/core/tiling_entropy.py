"""
tiling_entropy.py

TARTAN / Gray-code tiling utilities and entropy-tiling diagnostics for the
RSVP Analysis Suite (RAS).

Features in this starter module:
- Gray-code sequence generators and index <-> 2D coordinate mappings
- Functions to partition a 2D grid into tiles following a Gray-code ordering
  (useful for recursive tilings and entropy-tiling experiments)
- Compute per-tile entropy and several diagnostics (mean, variance, Gini)
- Build a tile-adjacency graph (uses networkx if available) for graph-based analyses
- Small CLI/demo harness when executed as __main__

This module intentionally focuses on clarity and extendability rather than
high performance. Replace tiling strategies with more advanced L-systems or
CRDT-based tiling rules in later iterations.
"""
from __future__ import annotations
from typing import Tuple, List, Sequence, Dict, Any

import numpy as np

# optional networkx import for adjacency graphs
try:
    import networkx as nx
except Exception:
    nx = None


# ----------------------------- Gray code utilities -----------------------------

def int_to_gray(n: int) -> int:
    """Convert integer n to its binary-reflected Gray code equivalent."""
    return n ^ (n >> 1)


def gray_to_int(g: int) -> int:
    """Convert Gray code g back to integer using bitwise operations."""
    n = g
    shift = 1
    while (g >> shift) > 0:
        n ^= (g >> shift)
        shift += 1
    return n


def gray_sequence(nbits: int) -> List[int]:
    """Return the Gray code sequence (0..2**nbits - 1)."""
    N = 1 << nbits
    return [int_to_gray(i) for i in range(N)]


def hilbert_like_from_gray(idx: int, order: int) -> Tuple[int, int]:
    """Map a Gray-code index to a 2D coordinate for a 2^order x 2^order grid.

    This is a simple mapping that chops the index bits into x and y interleaved
    from least-significant bits. It is NOT a true Hilbert curve mapper, but it
    often produces locality-preserving layouts useful for tiling experiments.

    Inputs
      idx: integer index (should be < 2^(2*order))
      order: grid order so grid size is 2**order
    Returns (x, y) coordinates in [0, 2**order-1]
    """
    maxbits = 2 * order
    if idx >= (1 << maxbits):
        raise ValueError("idx too large for given order")
    x = 0
    y = 0
    for b in range(order):
        xi = (idx >> (2 * b)) & 1
        yi = (idx >> (2 * b + 1)) & 1
        x |= (xi << b)
        y |= (yi << b)
    return x, y


# ----------------------------- Tiling generators -----------------------------

def tartan_tiling_coords(order: int) -> List[Tuple[int, int]]:
    """Return a list of (x,y) coordinates covering a 2^order x 2^order grid
    in a Gray-code influenced ordering. Use this to map linear tile indices to
    spatial cells.
    """
    size = 1 << order
    N = size * size
    seq = []
    for idx in range(N):
        g = int_to_gray(idx)
        x, y = hilbert_like_from_gray(g, order)
        seq.append((x, y))
    return seq


def partition_grid_by_tiles(grid_shape: Tuple[int, int], tile_size: int) -> List[np.ndarray]:
    """Partition a rectangular grid (nx, ny) into non-overlapping square tiles of tile_size.
    Returns a list of boolean masks (nx, ny) where True indicates cells belonging to the tile.

    Note: If grid dimensions are not divisible by tile_size, the final tiles along the
    right/bottom edges will be smaller.
    """
    nx, ny = grid_shape
    tiles = []
    for i0 in range(0, nx, tile_size):
        for j0 in range(0, ny, tile_size):
            mask = np.zeros((nx, ny), dtype=bool)
            mask[i0:min(i0 + tile_size, nx), j0:min(j0 + tile_size, ny)] = True
            tiles.append(mask)
    return tiles


def tile_order_from_tartan(order: int, tile_size: int, grid_shape: Tuple[int, int] | None = None) -> List[int]:
    """Produce a linear ordering of tile indices following a tartan Gray-code inspired ordering.

    We map each tile's anchor coordinate to the nearest Gray-code coordinate and sort.
    Returns a list of tile indices (0..T-1) in the chosen order.
    """
    if grid_shape is None:
        size = 1 << order
        grid_shape = (size, size)
    nx, ny = grid_shape

    # form tile anchors
    anchors = []
    tiles = partition_grid_by_tiles(grid_shape, tile_size)
    for k, m in enumerate(tiles):
        # anchor is the top-left True cell
        idxs = np.argwhere(m)
        if idxs.shape[0] == 0:
            anchors.append(((0, 0), k))
        else:
            anchors.append(((int(idxs[0, 0]), int(idxs[0, 1])), k))

    # map anchor to Gray-like index by interleaving bits of anchor within grid order
    def anchor_to_idx(anchor):
        x, y = anchor
        # clamp to grid powers
        order_x = int(np.ceil(np.log2(max(1, nx))))
        order_y = int(np.ceil(np.log2(max(1, ny))))
        order_bits = max(order_x, order_y)
        # build an idx by interleaving bits (simple)
        idx = 0
        for b in range(order_bits):
            xi = (x >> b) & 1
            yi = (y >> b) & 1
            idx |= (xi << (2 * b))
            idx |= (yi << (2 * b + 1))
        return int_to_gray(idx)

    mapped = [(anchor_to_idx(a), k) for (a, k) in anchors]
    mapped.sort()
    return [k for (_g, k) in mapped]


# ----------------------------- Entropy tiling diagnostics -----------------------------

def compute_tile_entropies(S: np.ndarray, tiles: Sequence[np.ndarray], base: float = 2.0) -> np.ndarray:
    """Compute per-tile Shannon-like entropy (normalize each tile to a pmf then compute -sum p log_b p).
    Returns an array of entropies with length equal to number of tiles.
    """
    entropies = []
    for mask in tiles:
        vals = np.asarray(S)[mask]
        if vals.size == 0:
            entropies.append(0.0)
            continue
        p = np.abs(vals)
        if np.sum(p) == 0:
            entropies.append(0.0)
            continue
        p = p / np.sum(p)
        with np.errstate(divide='ignore', invalid='ignore'):
            e = -np.sum(p * np.log(p)) / np.log(base)
        entropies.append(float(np.nan_to_num(e)))
    return np.array(entropies)


def gini_coefficient(x: Sequence[float]) -> float:
    """Compute Gini coefficient of array x (inequality measure)."""
    arr = np.asarray(x, dtype=float)
    if arr.size == 0:
        return 0.0
    arr = arr.flatten()
    if np.all(arr == 0):
        return 0.0
    arr = arr - np.min(arr)
    n = arr.size
    cum = np.cumsum(np.sort(arr))
    sum_ = cum[-1]
    if sum_ == 0:
        return 0.0
    index = np.arange(1, n + 1)
    g = (2.0 * np.sum(index * np.sort(arr)) - (n + 1) * sum_) / (n * sum_)
    return float(g)


def tile_entropy_diagnostics(S: np.ndarray, tiles: Sequence[np.ndarray], base: float = 2.0) -> Dict[str, Any]:
    """Compute diagnostics over tile entropies: mean, var, gini, top-k concentration."""
    ent = compute_tile_entropies(S, tiles, base=base)
    diagnostics = {
        'n_tiles': int(ent.size),
        'mean_entropy': float(np.mean(ent)) if ent.size else 0.0,
        'var_entropy': float(np.var(ent)) if ent.size else 0.0,
        'gini_entropy': gini_coefficient(ent),
    }
    # fraction of total entropy in top-k tiles
    total = float(np.sum(ent)) if ent.size else 0.0
    for k in (1, 3, 5):
        if ent.size == 0 or total == 0:
            diagnostics[f'top_{k}_frac'] = 0.0
        else:
            topk = np.sort(ent)[-k:]
            diagnostics[f'top_{k}_frac'] = float(np.sum(topk) / total)
    return diagnostics


# ----------------------------- Adjacency graph -----------------------------

def build_tile_adjacency_graph(tiles: Sequence[np.ndarray]) -> Any:
    """Build a graph where nodes are tile indices and edges exist if two tiles touch.
    If networkx is present, returns an nx.Graph, otherwise returns adjacency dict.
    """
    T = len(tiles)
    adj = {i: set() for i in range(T)}
    # naive O(T^2) overlap check — fine for moderate T
    for i in range(T):
        for j in range(i + 1, T):
            # touching if any cell adjacent (4-neighborhood)
            A = tiles[i]
            B = tiles[j]
            # compute dilation of A by 1 and check intersection with B
            A_pad = np.pad(A.astype(int), pad_width=1, mode='constant', constant_values=0)
            # shift neighbors
            neigh = (
                A_pad[0:-2, 1:-1] | A_pad[2:, 1:-1] | A_pad[1:-1, 0:-2] | A_pad[1:-1, 2:]
            )
            if np.any(neigh & B):
                adj[i].add(j)
                adj[j].add(i)
    if nx is not None:
        G = nx.Graph()
        G.add_nodes_from(range(T))
        for i, nbrs in adj.items():
            for j in nbrs:
                G.add_edge(i, j)
        return G
    else:
        return adj


# ----------------------------- Demo / CLI harness -----------------------------

if __name__ == "__main__":
    print("Tiling / entropy demo: constructing tiles, computing entropies and diagnostics")
    order = 5  # grid size 32x32
    size = 1 << order
    # synth entropy field: mixture of Gaussians
    x = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, x, indexing='ij')
    S = np.exp(-((X - 0.3) ** 2 + (Y - 0.35) ** 2) / (2 * 0.02)) + 0.5 * np.exp(-((X - 0.7) ** 2 + (Y - 0.75) ** 2) / (2 * 0.01))

    tile_size = 4
    tiles = partition_grid_by_tiles((size, size), tile_size)
    ent = compute_tile_entropies(S, tiles)
    print('Computed', ent.size, 'tile entropies; mean=', np.mean(ent))
    diag = tile_entropy_diagnostics(S, tiles)
    print('Diagnostics:', diag)
    G = build_tile_adjacency_graph(tiles)
    if nx is not None:
        print('Adjacency graph: nodes=', G.number_of_nodes(), 'edges=', G.number_of_edges())
    else:
        print('Adjacency dict created with', len(G), 'nodes')

