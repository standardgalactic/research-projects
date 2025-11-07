"""
derived_geometry.py

Utilities and lightweight helpers for experimenting with derived-style
constructions, shifted symplectic placeholders, and symbolic helpers suitable
for integrating with RSVP Analysis Suite (RAS).

Goals for this starter module:
- Provide small data structures mimicking derived fiber products and mapping stacks
  at a discrete / algebraic level for experiments.
- Helpers to construct 2-shifted and (-1)-shifted symplectic forms symbolically
  (using sympy) for toy finite-dimensional models.
- Utilities to discretize forms and test nondegeneracy on small grids.

This is intentionally a prototype meant to be extended into your more
rigorous derived geometry pipeline when you discretize fields or connect
with the BV module.
"""
from __future__ import annotations
from typing import Any, Dict, Tuple, Sequence

try:
    import sympy as sp
except Exception as e:
    raise ImportError("sympy is required for derived_geometry.py — please install sympy") from e

try:
    import numpy as np
except Exception as e:
    raise ImportError("numpy is required for derived_geometry.py — please install numpy") from e


# ----------------------------- Simple derived fiber product -----------------------------

def derived_fiber_product(A: Dict[str, Any], B: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    """A tiny, algebraic 'derived' fiber product for dictionaries representing schemes/objects.

    This is only a metaphorical playground: each input is a dict of generators -> relations
    (e.g. polynomial algebra descriptors). The function returns the naive pullback object
    by merging generators and adding relations that identify the shared base `over`.

    Example:
      A = {'gens': {'x': 'R'}, 'rels': ['x**2 - 1']}
      B = {'gens': {'y': 'R'}, 'rels': ['y - x']}
      over = {'gens': {'x': 'R'}, 'rels': []}
    """
    gens = {}
    rels = []
    # collect gens
    for src in (A, B):
        for k, v in src.get('gens', {}).items():
            if k in gens and gens[k] != v:
                # name collision with different types — append suffix
                newk = k + "_dup"
                gens[newk] = v
            else:
                gens[k] = v
        rels.extend(src.get('rels', []))

    # identify generators from `over` by adding relations
    for k in over.get('gens', {}).keys():
        if k in gens:
            rels.append(f"IDENTIFY_{k}")

    return {'gens': gens, 'rels': rels}


# ----------------------------- Shifted symplectic forms (toy) -----------------------------

def shifted_symplectic_form(symbols: Sequence[sp.Symbol], shift: int = -1) -> sp.Expr:
    """Construct a toy canonical 2-form for pairs of symbols.

    For shift = -1 (common in BV/AKSZ contexts) we return a bilinear pairing
    
    Example: symbols = [x1, x2, p1, p2] -> returns x1*p1 + x2*p2 (up to sign)
    """
    if len(symbols) % 2 != 0:
        raise ValueError("need even number of symbols to build a simple symplectic pairing")
    half = len(symbols) // 2
    s = 0
    for a, b in zip(symbols[:half], symbols[half:]):
        s += a * b
    # annotate with shift via a symbol comment (purely symbolic)
    return sp.simplify(s)


def is_nondegenerate(pairing: sp.Expr, symbols: Sequence[sp.Symbol]) -> bool:
    """Check nondegeneracy by building and testing the matrix of second derivatives (toy).

    This computes the Hessian matrix of `pairing` wrt `symbols` and checks if det != 0.
    Note: for a true 2-form one should anti-symmetrize; this is a simplified heuristic.
    """
    M = sp.Matrix([[sp.diff(pairing, si, sj) for sj in symbols] for si in symbols])
    det = sp.simplify(M.det())
    return det != 0


# ----------------------------- Discretize forms on small grids -----------------------------

def discretize_form_on_grid(form_fn, grid_shape: Tuple[int, int] = (8, 8)) -> np.ndarray:
    """Sample a scalar form-generating function across a grid to create a matrix.

    `form_fn` should accept two floats (x, y) and return a scalar. Returns a 2D numpy array.
    """
    nx, ny = grid_shape
    xs = np.linspace(0, 1, nx)
    ys = np.linspace(0, 1, ny)
    out = np.zeros((nx, ny), dtype=float)
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            out[i, j] = float(form_fn(x, y))
    return out


# ----------------------------- Small demo utilities -----------------------------

def demo_shifted_pairing():
    x1, x2, p1, p2 = sp.symbols('x1 x2 p1 p2')
    pairing = shifted_symplectic_form((x1, x2, p1, p2), shift=-1)
    print('Pairing =', pairing)
    print('Nondegenerate?', is_nondegenerate(pairing, (x1, x2, p1, p2)))


def demo_discretize():
    # simple form function: sin(2*pi*x)*cos(2*pi*y)
    import math
    fn = lambda x, y: math.sin(2 * math.pi * x) * math.cos(2 * math.pi * y)
    M = discretize_form_on_grid(fn, grid_shape=(16, 16))
    print('Sample matrix shape:', M.shape, 'mean abs val:', np.mean(np.abs(M)))


if __name__ == "__main__":
    print("Derived geometry demo — toy shifted pairing and discretization")
    demo_shifted_pairing()
    demo_discretize()

