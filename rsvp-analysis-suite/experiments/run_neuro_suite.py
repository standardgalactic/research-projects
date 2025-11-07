"""
run_neuro_suite.py

Executes neural validation experiments for RSVP theory: EEG/fMRI entropy coupling.

Purpose:
- Automate neural experiment execution
- Collect field-neural correlations for analysis

Inputs:
- EEG/fMRI data arrays
- Simulation parameters (lattice size, dt, λ)

Outputs:
- JSONL summaries of neural coupling metrics

Testing Focus:
- Correct calculation of Phi-S correlations
- Proper logging and reproducibility
"""
from __future__ import annotations
import json
import os
import numpy as np

from simulation.lattice_solver import run_lattice_solver
from simulation.entropy_balance import run_entropy_balance
from utils.logging_utils import initialize_log, log_event
from utils.stats_utils import spatial_coherence


def run_neuro_suite(output_path: str = 'neuro_suite.jsonl') -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    initialize_log(output_path)

    lattice_sizes = [16]
    dt_values = [0.01]
    lambda_values = [0.5]

    # Placeholder: simulate EEG/fMRI data as random fields
    eeg_data = np.random.randn(16,16)
    fmri_data = np.random.randn(16,16)

    for L in lattice_sizes:
        for dt in dt_values:
            for lam in lambda_values:
                Phi = np.random.randn(L,L)
                V = np.random.randn(L,L,2)
                S = np.random.randn(L,L)
                Phi_new, V_new, S_new = run_lattice_solver(Phi, V, S, dt=dt, n_steps=50)
                Sigma_dot_history, S_final = run_entropy_balance(Phi_new, V, S_new, dt=dt, n_steps=50)
                coherence_metric = spatial_coherence(Phi_new, S_final)
                metrics = {
                    'lattice_size': L,
                    'dt': dt,
                    'lambda': lam,
                    'coherence_metric': float(coherence_metric),
                    'Sigma_dot_mean': float(np.mean(Sigma_dot_history))
                }
                log_event(metrics, output_path)


# Demo harness
if __name__ == '__main__':
    print('run_neuro_suite demo')
    run_neuro_suite('demo_neuro_suite.jsonl')
    print('Demo neuro suite written to demo_neuro_suite.jsonl')

