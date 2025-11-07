"""
Test Lattice Convergence

Performs grid-resolution convergence tests for lattice solver outputs.
"""

import numpy as np
from simulation.lattice_solver import run_lattice_solver


def test_convergence():
    lattice_sizes = [8, 16, 32]
    dt = 0.01
    n_steps = 20
    final_solutions = []

    for size in lattice_sizes:
        Phi = np.random.rand(size, size)
        V = np.random.rand(size, size, 2)
        S = np.random.rand(size, size)

        Phi_final, V_final, S_final = run_lattice_solver(Phi, V, S, dt=dt, n_steps=n_steps)
        final_solutions.append(Phi_final)

    # Simple convergence check: compare norms of Phi at successive resolutions
    for i in range(1, len(final_solutions)):
        diff = np.linalg.norm(final_solutions[i] - final_solutions[i-1].repeat(2, axis=0).repeat(2, axis=1))
        assert diff < 1e-1, f"Convergence failed between sizes {lattice_sizes[i-1]} and {lattice_sizes[i]}, diff={diff}"


if __name__ == '__main__':
    test_convergence()
    print('Lattice convergence test passed.')

