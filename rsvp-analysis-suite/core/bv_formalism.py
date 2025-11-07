"""
bv_formalism.py

Starter BV/BRST utilities for the RSVP Analysis Suite (RAS).
Provides:
- symbolic helpers (via sympy) to declare fields and antifields
- construction of a finite-dimensional BV phase space (fields <-> antifields)
- implementation of the canonical anti-bracket on the finite set
- `verify_master_equation(S, fields, antifields)` which returns the simplified {S, S}
- numeric lambdify helper to evaluate antibrackets on concrete configurations

This is intentionally lightweight and symbolic-first so you can extend to
field-theoretic functionals (e.g. by discretization) or hook into your
`rsvp_fields` grid objects for numerical checks.
"""
from __future__ import annotations
from typing import Sequence, Tuple, Dict, Any

try:
    import sympy as sp
except Exception as e:
    raise ImportError("sympy is required for bv_formalism.py — please install sympy") from e


Symbol = sp.Symbol
Expr = sp.Expr


def declare_bv_vars(names: Sequence[str]) -> Tuple[Sequence[Symbol], Sequence[Symbol]]:
    """Create pairs of (field symbols, antifield symbols) for each name.

    Example:
      fields, antifields = declare_bv_vars(['phi', 'psi'])
      # fields: (phi, psi)  antifields: (phi_star, psi_star)
    """
    fields = [Symbol(n) for n in names]
    antifields = [Symbol(f"{n}_star") for n in names]
    return tuple(fields), tuple(antifields)


def canonical_antibracket(F: Expr, G: Expr, fields: Sequence[Symbol], antifields: Sequence[Symbol]) -> Expr:
    """Compute the canonical BV anti-bracket {F, G} = \sum_i (dF/dphi_i dG/dphi^*_i - dF/dphi^*_i dG/dphi_i).

    Inputs
      F, G: sympy expressions
      fields, antifields: matching sequences of sympy Symbols
    """
    if len(fields) != len(antifields):
        raise ValueError("fields and antifields must have same length")
    s = 0
    for phi, phistar in zip(fields, antifields):
        dF_dphi = sp.diff(F, phi)
        dF_dphistar = sp.diff(F, phistar)
        dG_dphi = sp.diff(G, phi)
        dG_dphistar = sp.diff(G, phistar)
        s += dF_dphi * dG_dphistar - dF_dphistar * dG_dphi
    return sp.simplify(s)


def verify_master_equation(S: Expr, fields: Sequence[Symbol], antifields: Sequence[Symbol]) -> Expr:
    """Return the simplified antibracket {S, S}. The classical master equation holds if this is 0.

    Note: For large symbolic S this can be expensive; simplify with care.
    """
    bracket = canonical_antibracket(S, S, fields, antifields)
    return sp.simplify(bracket)


def numeric_antibracket(F: Expr, G: Expr, fields: Sequence[Symbol], antifields: Sequence[Symbol],
                        mapping: Dict[str, Any]) -> float:
    """Evaluate the antibracket {F, G} numerically given a dict mapping symbol names to values.

    mapping should include values for every symbol appearing in fields+antifields.
    Returns a float (or numpy array if values are arrays).
    """
    import numpy as np

    all_symbols = list(fields) + list(antifields)
    f_l = sp.lambdify(all_symbols, canonical_antibracket(F, G, fields, antifields), 'numpy')
    vals = [mapping[str(s)] for s in all_symbols]
    return f_l(*vals)


if __name__ == "__main__":
    # Quick demo / self-test
    print("BV formalism self-test — building a toy BV action and checking CME")

    # declare variables
    (phi,), (phi_star,) = declare_bv_vars(['phi'])

    # Toy action S = phi_star * R(phi)  where R(phi) = phi**2 / 2  (simple nonlinear gauge generator)
    R = phi ** 2 / 2
    S = phi_star * R

    print("S =", S)
    bracket = verify_master_equation(S, (phi,), (phi_star,))
    print("{S, S} simplified =", bracket)

    # Numeric check (should match symbolic): plug phi=1.0, phi_star=0.0
    mapping = {'phi': 1.0, 'phi_star': 0.0}
    val = numeric_antibracket(S, S, (phi,), (phi_star,), mapping)
    print("Numeric {S,S} at phi=1, phi_star=0 ->", val)

    # If you want a true solution of CME, try S=0 or pairwise cancellation examples.
    # For example S = 0 gives {S,S} = 0 by construction.
    print("Demo complete.")

