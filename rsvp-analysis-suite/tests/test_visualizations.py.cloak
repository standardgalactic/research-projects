"""
Test Visualizations

Confirms that field plots and phase diagrams render without errors.
"""

import numpy as np
import matplotlib.pyplot as plt
from simulation.lattice_solver import run_lattice_solver


def test_field_plots():
    lattice_size = 16
    Phi = np.random.rand(lattice_size, lattice_size)
    V = np.random.rand(lattice_size, lattice_size, 2)
    S = np.random.rand(lattice_size, lattice_size)

    # Simple plot check
    try:
        plt.figure()
        plt.imshow(Phi, cmap='viridis')
        plt.colorbar()
        plt.close()

        plt.figure()
        plt.imshow(S, cmap='plasma')
        plt.colorbar()
        plt.close()
    except Exception as e:
        assert False, f"Visualization failed: {e}"


def test_phase_diagram():
    # Generate dummy 3D phase data
    phi = np.linspace(0,1,5)
    s = np.linspace(0,1,5)
    lam = np.linspace(0.1,1,5)
    Phi_grid, S_grid, Lambda_grid = np.meshgrid(phi, s, lam)

    try:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(Phi_grid.ravel(), S_grid.ravel(), Lambda_grid.ravel(), c=Phi_grid.ravel())
        plt.close()
    except Exception as e:
        assert False, f"Phase diagram visualization failed: {e}"


if __name__ == '__main__':
    test_field_plots()
    test_phase_diagram()
    print('All visualization tests passed.')

