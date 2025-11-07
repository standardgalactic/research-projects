"""
coupling_scan.py

Performs parameter sweeps over coupling constant λ to identify critical λ₍c₎
and phase transitions in RSVP Analysis Suite (RAS).

Purpose:
- Scan λ parameter space for given Phi, V, S fields.
- Record observables and identify phase transitions.

Inputs:
- Phi, V, S arrays (numpy)
- lam_range: list/array of λ values
- n_steps: number of Lamphron steps per λ
- dt: time step

Outputs:
- Dictionary of λ → observables (e.g., mean S, torsion, topological charge)
- Critical λ₍c₎ estimate

Testing Focus:
- Reproducibility of phase transition detection
- Correct aggregation of observables
"""
from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np

from rsvp_analysis_suite.core import lamphron_solver, torsion_spectrum


def scan_lambda(Phi: np.ndarray, V: np.ndarray, S: np.ndarray, lam_range: List[float], dt: float = 0.01, n_steps: int = 100) -> Tuple[Dict[float, Dict[str,float]], float]:
    """Scan over λ values, return observables and estimated critical λ₍c₎."""
    results: Dict[float, Dict[str,float]] = {}
    critical_lambda: float = lam_range[0]
    prev_obs = None

    for lam in lam_range:
        Phi_new, V_new, S_new = lamphron_solver.run_lamphron(Phi, V, S, dt=dt, n_steps=n_steps, lam=lam)
        torsion_map = torsion_spectrum.torsion_map(Phi_new, V_new, S_new)
        Q = torsion_spectrum.topological_charge(torsion_map)
        mean_S = np.mean(S_new)
        results[lam] = {'mean_S': mean_S, 'topological_charge': Q}

        # crude critical lambda detection: abrupt change in mean_S
        if prev_obs is not None and np.abs(mean_S - prev_obs) > 0.1:  # threshold can be adjusted
            critical_lambda = lam
        prev_obs = mean_S

    return results, critical_lambda


# Demo harness
if __name__ == '__main__':
    print('coupling_scan demo')
    shape = (16,16)
    Phi, V, S = np.random.randn(*shape), np.random.randn(*shape,2), np.random.randn(*shape)
    lam_range = np.linspace(0.1, 2.0, 10)
    results, lam_c = scan_lambda(Phi, V, S, lam_range, dt=0.01, n_steps=50)
    print('Results:', results)
    print('Estimated critical lambda:', lam_c)

