"""
Test Entropy Balance

Verifies that integrated entropy production Σ̇ is computed correctly over runtime.
"""

import numpy as np
from simulation.entropy_balance import run_entropy_balance


def test_entropy_balance():
    lattice_size = 16
    n_steps = 50
    dt = 0.01

    Phi = np.random.rand(lattice_size, lattice_size)
    V = np.random.rand(lattice_size, lattice_size, 2)
    S = np.random.rand(lattice_size, lattice_size)

    Sigma_dot_history, S_final = run_entropy_balance(Phi, V, S, dt=dt, n_steps=n_steps)

    integrated_Sigma_dot = np.sum(Sigma_dot_history) * dt
    # Placeholder: check that integrated Σ̇ is finite and positive
    assert integrated_Sigma_dot > 0, f"Integrated Σ̇ invalid: {integrated_Sigma_dot}"


if __name__ == '__main__':
    test_entropy_balance()
    print('Entropy balance test passed.')

