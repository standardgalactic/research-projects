"""
neuro_validation.py

Experimental neurobiological validation module for RSVP Analysis Suite (RAS).
Provides:
- utilities to load fMRI or neural imaging data
- field correlation with Phi/S fields
- computation of φ_RSVP metrics from neural data
- statistical testing of predicted vs observed field dynamics

Assumes data is either numpy arrays or pandas DataFrames (time x ROI).
"""
from __future__ import annotations
from typing import Optional

import numpy as np
try:
    import pandas as pd
except ImportError:
    pd = None

from rsvp_analysis_suite.core import rsvp_fields, semantic_phase
from rsvp_analysis_suite.utils import io_utils, data_viz


def load_neural_data(path: str) -> np.ndarray:
    """Load neural data; either npy/npz or pandas-compatible CSV."""
    if path.endswith('.npz') or path.endswith('.npy'):
        data = np.load(path)
        if isinstance(data, np.ndarray):
            return data
        elif hasattr(data, 'files'):
            return {k: data[k] for k in data.files}
    elif path.endswith('.csv'):
        if pd is None:
            raise ImportError('pandas required to load CSV')
        return pd.read_csv(path).values
    else:
        raise ValueError('Unsupported file format for neural data')


def correlate_with_phi(Phi: np.ndarray, neural_data: np.ndarray) -> float:
    """Compute correlation between flattened Phi field and neural data."""
    Phi_flat = Phi.ravel()
    neural_flat = neural_data.ravel()
    # align sizes
    min_len = min(Phi_flat.size, neural_flat.size)
    corr = np.corrcoef(Phi_flat[:min_len], neural_flat[:min_len])[0,1]
    return corr


def compute_phi_rsvp_from_neural(neural_data: np.ndarray) -> np.ndarray:
    """Compute φ_RSVP map from neural activity (toy placeholder)."""
    # normalize and map to 0..1
    normalized = (neural_data - np.min(neural_data)) / (np.max(neural_data) - np.min(neural_data) + 1e-12)
    return normalized


def plot_neural_phi(neural_phi: np.ndarray, title: Optional[str] = None):
    data_viz.plot_scalar_field(neural_phi, title=title)


if __name__ == "__main__":
    print('neuro_validation demo')
    # synthetic neural data demo
    neural_data = np.random.randn(32,32)
    Phi, _, _, _ = rsvp_fields.create_synthetic_field(shape=(32,32))
    corr = correlate_with_phi(Phi, neural_data)
    print('Correlation with Phi field:', corr)
    neural_phi = compute_phi_rsvp_from_neural(neural_data)
    plot_neural_phi(neural_phi, title='φ_RSVP from neural demo')

