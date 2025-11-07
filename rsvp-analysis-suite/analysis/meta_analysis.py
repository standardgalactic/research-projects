"""
meta_analysis.py

Cross-experiment meta-analysis module for RSVP Analysis Suite (RAS).
Provides:
- aggregation of experiment results
- statistical summaries across multiple runs
- correlation and covariance analysis between fields, entropy, and phi_RSVP
- lightweight visualization of experiment trends
"""
from __future__ import annotations
from typing import List, Dict

import numpy as np
try:
    import pandas as pd
except ImportError:
    pd = None

from rsvp_analysis_suite.utils import io_utils, data_viz


def aggregate_experiments(exp_paths: List[str], key: str = 'state.npz') -> Dict[str, List[np.ndarray]]:
    """Load a given key (numpy state) from multiple experiments and aggregate."""
    aggregated: Dict[str, List[np.ndarray]] = {}
    for path in exp_paths:
        data = io_utils.load_numpy_state(f'{path}/{key}')
        for k, v in data.items():
            if k not in aggregated:
                aggregated[k] = []
            aggregated[k].append(v)
    return aggregated


def compute_statistics(aggregated: Dict[str, List[np.ndarray]]) -> Dict[str, Dict[str, float]]:
    """Compute mean and std for each variable across experiments."""
    stats: Dict[str, Dict[str, float]] = {}
    for k, arr_list in aggregated.items():
        stacked = np.stack(arr_list)
        stats[k] = {'mean': float(np.mean(stacked)), 'std': float(np.std(stacked))}
    return stats


def correlation_matrix(aggregated: Dict[str, List[np.ndarray]]) -> Dict[str, np.ndarray]:
    """Compute correlation matrices between variables across experiments."""
    corr_matrices: Dict[str, np.ndarray] = {}
    keys = list(aggregated.keys())
    for i, ki in enumerate(keys):
        for j, kj in enumerate(keys):
            stacked_i = np.stack(aggregated[ki]).ravel()
            stacked_j = np.stack(aggregated[kj]).ravel()
            corr = np.corrcoef(stacked_i, stacked_j)[0,1]
            corr_matrices[f'{ki}-{kj}'] = corr
    return corr_matrices


def plot_experiment_trends(aggregated: Dict[str, List[np.ndarray]]):
    """Plot mean trend for each variable across experiments."""
    for k, arr_list in aggregated.items():
        means = [np.mean(a) for a in arr_list]
        data_viz.plot_time_series(np.arange(len(means)), np.array(means), label=k, title=f'Trend of {k}')


if __name__ == "__main__":
    print('meta_analysis demo')
    # demo with synthetic experiment folders
    exp_paths = ['experiments/demo1', 'experiments/demo2']
    # create dummy npz for demo
    for p in exp_paths:
        io_utils.ensure_root()
        io_utils.save_numpy_state(f'{p}/state.npz', Phi=np.random.randn(4,4), S=np.random.randn(4,4))
    aggregated = aggregate_experiments(exp_paths)
    stats = compute_statistics(aggregated)
    print('Aggregated statistics:', stats)
    corrs = correlation_matrix(aggregated)
    print('Correlation matrices:', corrs)
    plot_experiment_trends(aggregated)

