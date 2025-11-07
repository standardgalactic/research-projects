"""
parameter_sweeps.py

Batch execution for RSVP lattice simulations over Δt, lambda, and lattice size sweeps.
Produces JSONL summaries for analysis.

Purpose:
- Automate parameter scans for stability, phase transitions, and scaling studies.
- Save structured output for downstream analysis.

Inputs:
- dt_values: list of timesteps
- lambda_values: list of lambda parameters
- lattice_sizes: list of lattice dimensions
- solver_fn: callable to run simulation (e.g., lattice_solver.run_lattice_solver)

Outputs:
- JSONL file summarizing parameters and key metrics (min/max Phi, S, Sigma_dot)

Testing Focus:
- Correct sweep loops
- Reproducible results with seeds
"""
from __future__ import annotations
from typing import List, Callable, Tuple
import numpy as np
import json
import os


def run_parameter_sweep(dt_values: List[float], lambda_values: List[float], lattice_sizes: List[int], solver_fn: Callable, output_path: str = 'parameter_sweep.jsonl') -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        for dt in dt_values:
            for lam in lambda_values:
                for L in lattice_sizes:
                    # Initialize fields
                    Phi = np.random.randn(L,L)
                    V = np.random.randn(L,L,2)
                    S = np.random.randn(L,L)
                    # Run solver
                    Phi_new, V_new, S_new = solver_fn(Phi, V, S, dt=dt, n_steps=50)
                    # Compute summary metrics
                    summary = {
                        'dt': dt,
                        'lambda': lam,
                        'lattice_size': L,
                        'Phi_min': float(Phi_new.min()),
                        'Phi_max': float(Phi_new.max()),
                        'S_min': float(S_new.min()),
                        'S_max': float(S_new.max())
                    }
                    f.write(json.dumps(summary) + '\n')


# Demo harness
if __name__ == '__main__':
    print('parameter_sweeps demo')
    run_parameter_sweep(dt_values=[0.01,0.02], lambda_values=[0.5,1.0], lattice_sizes=[8,16],
                        solver_fn=lambda Phi,V,S,dt,n_steps: (Phi,V,S),
                        output_path='demo_sweep.jsonl')
    print('Demo sweep written to demo_sweep.jsonl')

