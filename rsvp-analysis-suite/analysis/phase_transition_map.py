"""
phase_transition_map.py

Generates 2D/3D bifurcation plots over (Phi, S, lambda) for RSVP Analysis Suite (RAS).

Purpose:
- Visualize phase transitions and critical points in the parameter space.
- Supports 2D slices or full 3D plots.

Inputs:
- lambda_values: array of lambda values
- Phi_list: list of Phi arrays corresponding to lambda_values
- S_list: list of S arrays corresponding to lambda_values

Outputs:
- Plots (matplotlib 2D/3D)
- Optional data array for further analysis

Testing Focus:
- Correct mapping of observables to lambda
- Visual verification of bifurcations and critical transitions
"""
from __future__ import annotations
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def compute_phase_metric(Phi: np.ndarray, S: np.ndarray) -> float:
    """Toy metric for phase transition: mean S times std Phi."""
    return np.mean(S) * np.std(Phi)


def generate_phase_map(lambda_values: List[float], Phi_list: List[np.ndarray], S_list: List[np.ndarray], plot_3d: bool = True):
    metrics = [compute_phase_metric(Phi, S) for Phi, S in zip(Phi_list, S_list)]
    
    if plot_3d:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        # Use lambda_values as x, mean(Phi) as y, metric as z
        mean_Phi = [np.mean(Phi) for Phi in Phi_list]
        ax.plot(lambda_values, mean_Phi, metrics, marker='o')
        ax.set_xlabel('Lambda')
        ax.set_ylabel('Mean Phi')
        ax.set_zlabel('Phase Metric')
        ax.set_title('Phase Transition Map (3D)')
        plt.show()
    else:
        plt.figure()
        plt.plot(lambda_values, metrics, marker='o')
        plt.xlabel('Lambda')
        plt.ylabel('Phase Metric')
        plt.title('Phase Transition Map (2D)')
        plt.show()
    
    return metrics


# Demo harness
if __name__ == '__main__':
    print('phase_transition_map demo')
    lambda_values = np.linspace(0.1, 2.0, 5)
    Phi_list = [np.random.randn(16,16) for _ in lambda_values]
    S_list = [np.random.randn(16,16) for _ in lambda_values]
    metrics = generate_phase_map(lambda_values, Phi_list, S_list)

