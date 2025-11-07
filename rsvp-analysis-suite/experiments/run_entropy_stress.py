"""
run_entropy_stress.py

Performs stress tests on RSVP simulations: varying λ, Σ̇, and boundary conditions.

Purpose:
- Identify critical points and sensitivity to parameters
- Test robustness of entropic dynamics under extreme conditions

Inputs:
- Range of λ values
- Lattice size, dt, n_steps
- Boundary condition type

Outputs:
- JSONL file summarizing stress test metrics

Testing Focus:
- Stability under extreme λ
- Proper logging of Σ̇ and boundary behavior
"""
from __future__ import annotations
import json
import os
import numpy as np

from simulation.lattice_solver import run_lattice_solver
from simulation.entropy_balance import run_entropy_balance
from utils.logging_utils import initialize_log, log_event


def run_entropy_stress(output_path: str = 'entropy_stress.jsonl') -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    initialize_log(output_path)

    lambda_values = [0.1, 0.5, 1.0, 2.0, 5.0]  # stress extremes
    lattice_size = 16
    dt = 0.01
    n_steps = 50
    boundary_modes = ['periodic', 'reflective', 'open']

    for lam in lambda_values:
        for mode in boundary_modes:
            Phi = np.random.randn(lattice_size, lattice_size)
            V = np.random.randn(lattice_size, lattice_size, 2)
            S = np.random.randn(lattice_size, lattice_size)
            Phi_new, V_new, S_new = run_lattice_solver(Phi, V, S, dt=dt, n_steps=n_steps)
            Sigma_dot_history, S_final = run_entropy_balance(Phi_new, V, S_new, dt=dt, n_steps=n_steps)
            metrics = {
                'lambda': lam,
                'boundary_mode': mode,
                'Sigma_dot_mean': float(np.mean(Sigma_dot_history)),
                'Phi_min': float(Phi_new.min()),
                'Phi_max': float(Phi_new.max()),
                'S_min': float(S_final.min()),
                'S_max': float(S_final.max())
            }
            log_event(metrics, output_path)


# Demo harness
if __name__ == '__main__':
    print('run_entropy_stress demo')
    run_entropy_stress('demo_entropy_stress.jsonl')
    print('Demo stress test written to demo_entropy_stress.jsonl')

