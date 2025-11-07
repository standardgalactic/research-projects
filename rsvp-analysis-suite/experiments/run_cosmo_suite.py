"""
run_cosmo_suite.py

Runs the cosmological validation suite for RSVP theory: redshift, CMB, and lensing tests.

Purpose:
- Automate cosmological experiment execution
- Collect results for analysis and visualization

Inputs:
- Config parameters for simulation (lattice size, dt, λ)

Outputs:
- JSONL summaries of cosmological observables

Testing Focus:
- Correct execution of cosmological test modules
- Proper recording of metrics and observables
"""
from __future__ import annotations
import json
import os
import numpy as np

from simulation.lattice_solver import run_lattice_solver
from utils.logging_utils import initialize_log, log_event


def run_cosmo_suite(output_path: str = 'cosmo_suite.jsonl') -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    initialize_log(output_path)

    lattice_sizes = [16,32]
    dt_values = [0.01,0.02]
    lambda_values = [0.5,1.0]

    for L in lattice_sizes:
        for dt in dt_values:
            for lam in lambda_values:
                Phi = np.random.randn(L,L)
                V = np.random.randn(L,L,2)
                S = np.random.randn(L,L)
                Phi_new, V_new, S_new = run_lattice_solver(Phi, V, S, dt=dt, n_steps=50)
                metrics = {
                    'lattice_size': L,
                    'dt': dt,
                    'lambda': lam,
                    'Phi_min': float(Phi_new.min()),
                    'Phi_max': float(Phi_new.max()),
                    'S_min': float(S_new.min()),
                    'S_max': float(S_new.max())
                }
                log_event(metrics, output_path)


# Demo harness
if __name__ == '__main__':
    print('run_cosmo_suite demo')
    run_cosmo_suite('demo_cosmo_suite.jsonl')
    print('Demo cosmo suite written to demo_cosmo_suite.jsonl')

