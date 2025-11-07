"""
governance_metrics.py

Computes collapse probability, critical lambda confidence, and stability scores for RSVP systems.

Purpose:
- Quantify system stability under varying λ and entropy conditions.
- Provides metrics for analysis of phase transitions and governance.

Inputs:
- observables: dict of λ → metrics (mean_S, topological_charge)
- lam_values: list or array of lambda values

Outputs:
- Collapse probability
- Critical lambda estimate and confidence interval
- Stability score

Testing Focus:
- Correct calculation of probabilities
- Confidence interval correctness
"""
from __future__ import annotations
from typing import Dict, List, Tuple
import numpy as np


def compute_collapse_probability(observables: Dict[float, Dict[str,float]], threshold: float = 0.5) -> float:
    collapse_count = sum(1 for obs in observables.values() if obs['mean_S'] < threshold)
    return collapse_count / len(observables)


def critical_lambda_confidence(observables: Dict[float, Dict[str,float]], lam_values: List[float]) -> Tuple[float,float]:
    # crude estimate: lambda where mean_S crosses median
    mean_S_vals = np.array([observables[lam]['mean_S'] for lam in lam_values])
    median_S = np.median(mean_S_vals)
    indices = np.where(mean_S_vals >= median_S)[0]
    if len(indices) == 0:
        lam_c = lam_values[0]
    else:
        lam_c = lam_values[indices[0]]
    # confidence interval: +/- one index as crude proxy
    idx = indices[0] if len(indices)>0 else 0
    lower = lam_values[max(0, idx-1)]
    upper = lam_values[min(len(lam_values)-1, idx+1)]
    return lam_c, (lower, upper)


def stability_score(observables: Dict[float, Dict[str,float]]) -> float:
    # simple metric: variance of topological_charge across lambda
    Q_vals = np.array([obs['topological_charge'] for obs in observables.values()])
    return 1.0 / (1.0 + np.var(Q_vals))


# Demo harness
if __name__ == '__main__':
    print('governance_metrics demo')
    lam_values = [0.1,0.5,1.0,1.5,2.0]
    observables = {lam: {'mean_S': np.random.rand(), 'topological_charge': np.random.randn()} for lam in lam_values}
    cp = compute_collapse_probability(observables)
    lam_c, ci = critical_lambda_confidence(observables, lam_values)
    score = stability_score(observables)
    print('Collapse probability:', cp)
    print('Critical lambda and CI:', lam_c, ci)
    print('Stability score:', score)

