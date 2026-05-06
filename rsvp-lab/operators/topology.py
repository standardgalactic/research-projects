# ============================================================
# operators/topology.py
# ------------------------------------------------------------
# Topological and sheaf-theoretic metrics for RSVP fields.
#
# Included
# --------
#   gluing_obstruction      — global sheaf cocycle error
#   local_gluing_map        — per-patch obstruction grid
#   connected_components    — level-set component counting
#   euler_characteristic    — discrete Euler number
#   persistence_diagram     — crude 0-D sublevel persistence
#   tartan_tiles            — TARTAN coarse-grained tile stats
#   tartan_hierarchy        — recursive multi-scale tiling
#   pca_embedding           — low-D state-space trajectory
#   synchrony               — Pearson correlation of two fields
#   gini                    — Gini coefficient
#
# Author: Flyxion
# ============================================================

import numpy as np
from scipy.ndimage import label as nd_label, gaussian_filter


# ============================================================
# Sheaf / gluing metrics
# ============================================================

def gluing_obstruction(field, patch=32, overlap=8):
    """
    Global sheaf gluing obstruction.

    Partitions the domain into overlapping patches and
    computes the mean L² mismatch between adjacent patch
    restrictions:

        Ω = (1/|E|) Σ_{(i,j)∈E} ||φ_i|_{ij} − φ_j|_{ij}||²

    A compatible global section has Ω = 0.

    Returns
    -------
    float — mean gluing error
    """
    H_, W_ = field.shape
    stride = patch - overlap
    errors = []

    for y in range(0, H_ - patch + 1, stride):
        for x in range(0, W_ - patch + 1, stride):
            # Right neighbour
            xr = x + stride
            if xr + patch <= W_:
                a = field[y:y+patch,  x:x+patch][:, -overlap:]
                b = field[y:y+patch, xr:xr+patch][:,  :overlap]
                errors.append(np.mean((a - b)**2))
            # Bottom neighbour
            yb = y + stride
            if yb + patch <= H_:
                a = field[y:y+patch,   x:x+patch][-overlap:, :]
                b = field[yb:yb+patch, x:x+patch][ :overlap, :]
                errors.append(np.mean((a - b)**2))

    return float(np.mean(errors)) if errors else 0.0


def local_gluing_map(field, patch=32, overlap=8):
    """
    Return a coarse grid of per-patch gluing errors.

    Shape is approximately (H//stride, W//stride).
    Useful for visualising spatial obstruction structure.
    """
    H_, W_ = field.shape
    stride = patch - overlap
    grid_h = max(1, (H_ - overlap) // stride)
    grid_w = max(1, (W_ - overlap) // stride)
    grid   = np.zeros((grid_h, grid_w))

    for y in range(0, H_ - patch + 1, stride):
        for x in range(0, W_ - patch + 1, stride):
            gy = y // stride
            gx = x // stride
            if gy >= grid_h or gx >= grid_w:
                continue
            err = 0.0; count = 0

            xr = x + stride
            if xr + patch <= W_:
                a = field[y:y+patch,  x:x+patch][:, -overlap:]
                b = field[y:y+patch, xr:xr+patch][:,  :overlap]
                err += np.mean((a - b)**2); count += 1

            yb = y + stride
            if yb + patch <= H_:
                a = field[y:y+patch,   x:x+patch][-overlap:, :]
                b = field[yb:yb+patch, x:x+patch][ :overlap, :]
                err += np.mean((a - b)**2); count += 1

            grid[gy, gx] = err / max(count, 1)

    return grid


# ============================================================
# Level-set topology
# ============================================================

def connected_components(field, level=0.5):
    """
    Count connected components of the super-level set
    {x : field(x) > level} using 4-connectivity.

    Returns
    -------
    int — number of connected components
    """
    binary        = (field > level).astype(np.uint8)
    _, n_comps    = nd_label(binary)
    return int(n_comps)


def euler_characteristic(field, level=0.5):
    """
    Discrete Euler characteristic of the super-level set.

    Uses the standard formula  χ = V − E + F  on the
    2-D pixel complex (vertices, edges, faces).

    This is a coarse topological invariant; for a richer
    picture use persistent homology.
    """
    binary = (field > level).astype(int)

    # Vertices (cells above threshold)
    V = int(binary.sum())

    # Horizontal edges: adjacent pairs both above threshold
    E_h = int((binary[:, :-1] * binary[:, 1:]).sum())
    # Vertical edges
    E_v = int((binary[:-1, :] * binary[1:, :]).sum())
    E   = E_h + E_v

    # Faces (2×2 squares all above threshold)
    F   = int((binary[:-1, :-1] * binary[:-1, 1:]
              * binary[1:, :-1] * binary[1:,  1:]).sum())

    return V - E + F


def persistence_diagram(field, n_levels=20):
    """
    Crude 0-D sublevel-set persistence diagram.

    Sweeps thresholds from min to max of field.  At each
    threshold, counts connected components of {field < t}.
    Birth/death pairs are approximated as consecutive
    threshold levels where the component count changes.

    Returns
    -------
    list of (birth, death) tuples (in field units)
    """
    lo, hi   = float(field.min()), float(field.max())
    levels   = np.linspace(lo, hi, n_levels)
    counts   = []
    for t in levels:
        binary = (field < t).astype(np.uint8)
        _, n   = nd_label(binary)
        counts.append(n)

    pairs = []
    prev  = 0
    births = {}
    for i, (t, c) in enumerate(zip(levels, counts)):
        if c > prev:
            for _ in range(c - prev):
                births[len(births)] = t
        elif c < prev:
            for _ in range(prev - c):
                k = max(births, key=births.get)
                pairs.append((births.pop(k), t))
        prev = c

    # Close surviving components at hi
    for k, b in births.items():
        pairs.append((b, hi))

    return pairs


# ============================================================
# TARTAN tiling
# ============================================================

def tartan_tiles(field, tile_size=16):
    """
    Partition field into non-overlapping tiles and return
    per-tile summary statistics.

    Returns
    -------
    list of dicts with keys: x, y, mean, variance, skew, max_grad
    """
    from operators.rsvp import gradient
    gx, gy = gradient(field)
    grad_mag = np.sqrt(gx**2 + gy**2)

    H_, W_ = field.shape
    tiles  = []
    for y in range(0, H_, tile_size):
        for x in range(0, W_, tile_size):
            tile = field[y:y+tile_size, x:x+tile_size]
            gm   = grad_mag[y:y+tile_size, x:x+tile_size]
            mean = float(np.mean(tile))
            var  = float(np.var(tile))
            # Normalised skewness
            std  = float(np.std(tile))
            skew = float(np.mean((tile - mean)**3) / (std**3 + 1e-9))
            tiles.append({
                "x": x, "y": y,
                "mean": mean, "variance": var,
                "skew": skew,
                "max_grad": float(np.max(gm)),
            })
    return tiles


def tartan_hierarchy(field, levels=3, base_tile=8):
    """
    Recursive multi-scale TARTAN tiling.

    At each level, tile_size doubles.  Returns a dict keyed
    by level index with the corresponding tile list.
    """
    result = {}
    for lvl in range(levels):
        tile_size       = base_tile * (2 ** lvl)
        result[lvl]     = tartan_tiles(field, tile_size=tile_size)
    return result


# ============================================================
# State-space embedding
# ============================================================

def pca_embedding(frames, n_components=2):
    """
    Project a sequence of field snapshots into a low-D space
    via PCA (SVD method).

    Parameters
    ----------
    frames       : list of (H, W) arrays
    n_components : int — number of principal components

    Returns
    -------
    coords     : (n_frames, n_components) array
    explained  : (n_components,) fraction of variance explained
    """
    X    = np.stack([f.flatten() for f in frames])
    X_c  = X - X.mean(axis=0, keepdims=True)
    _, s, Vt = np.linalg.svd(X_c, full_matrices=False)

    coords   = X_c @ Vt[:n_components].T
    total_var = float(np.var(X_c, axis=0).sum())
    explained = np.var(coords, axis=0) / (total_var + 1e-12)
    return coords, explained


# ============================================================
# Synchrony and statistics
# ============================================================

def synchrony(phi1, phi2):
    """
    Pearson correlation coefficient between two fields.
    Ranges from −1 (anti-correlated) to +1 (synchronised).
    """
    s1, s2 = np.std(phi1), np.std(phi2)
    if s1 < 1e-9 or s2 < 1e-9:
        return 0.0
    return float(
        np.mean((phi1 - phi1.mean()) * (phi2 - phi2.mean())) / (s1 * s2)
    )


def gini(field):
    """
    Gini coefficient of a non-negative field.
    0 = perfect equality, 1 = maximal concentration.
    """
    flat = np.sort(np.abs(field.flatten()))
    n    = len(flat)
    if n == 0 or flat.sum() == 0:
        return 0.0
    idx = np.arange(1, n + 1)
    return float((2 * np.sum(idx * flat) / (n * flat.sum())) - (n + 1) / n)


def structure_function(field, max_lag=32):
    """
    Second-order structure function:

        D(r) = <(Φ(x+r) − Φ(x))²>

    evaluated for integer lags r = 1 … max_lag in the x direction.
    A power-law D(r) ~ r^ζ indicates scale-invariant fluctuations.

    Returns
    -------
    lags   : 1-D int array
    D      : 1-D float array
    """
    lags = np.arange(1, max_lag + 1)
    D    = np.array([
        float(np.mean((np.roll(field, -r, axis=1) - field)**2))
        for r in lags
    ])
    return lags, D
