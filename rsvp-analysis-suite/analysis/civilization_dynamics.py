"""
civilization_dynamics.py

Simulates RSVP civilization/tech tree dynamics coupled to entropy production metrics.

Purpose:
- Model simplified growth/decay of civilization states as function of entropy production.
- Track tech tree development and collapse probabilities.

Inputs:
- n_nodes: number of tech tree nodes
- Sigma_dot: entropy production rate array or scalar
- dt: time step
- n_steps: number of simulation steps

Outputs:
- Tech tree state evolution
- Entropy coupling metrics

Testing Focus:
- Correct propagation of tech tree states
- Coupling between Σ̇ and node activity
"""
from __future__ import annotations
from typing import Tuple
import numpy as np


def initialize_tech_tree(n_nodes: int, seed: int = 42) -> np.ndarray:
    np.random.seed(seed)
    # Binary state: 0=inactive, 1=active
    return np.random.choice([0,1], size=n_nodes)


def evolve_tech_tree(tree_state: np.ndarray, Sigma_dot: float, dt: float = 0.1) -> np.ndarray:
    # Simple update: probability of activation proportional to Sigma_dot
    prob = np.clip(Sigma_dot*dt, 0, 1)
    new_state = tree_state.copy()
    for i in range(len(tree_state)):
        if tree_state[i] == 0 and np.random.rand() < prob:
            new_state[i] = 1
        elif tree_state[i] == 1 and np.random.rand() < 0.01:  # small chance of decay
            new_state[i] = 0
    return new_state


def run_civilization_sim(n_nodes: int = 16, Sigma_dot: float = 0.5, dt: float = 0.1, n_steps: int = 50, seed: int = 42) -> np.ndarray:
    tree_state = initialize_tech_tree(n_nodes, seed=seed)
    history = np.zeros((n_steps, n_nodes), dtype=int)
    for step in range(n_steps):
        tree_state = evolve_tech_tree(tree_state, Sigma_dot, dt=dt)
        history[step] = tree_state
    return history


# Demo harness
if __name__ == '__main__':
    print('civilization_dynamics demo')
    history = run_civilization_sim(n_nodes=10, Sigma_dot=0.3, dt=0.1, n_steps=20)
    print('Tech tree history shape:', history.shape)
    print('Final state:', history[-1])

