"""
io_utils.py

I/O utilities for the RSVP Analysis Suite (RAS).
Provides:
- experiment logging and JSON metadata storage
- simple experiment registry using a local directory structure
- wrappers for saving/loading numpy states and pandas DataFrames
- reproducible RNG state capture and restore helpers
- lightweight JSONL experiment logger for streaming experiment records

This module favors transparency (plain files, readable metadata) and is
intended to be replaced with CRDT / distributed logs for larger experiments.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

import os
import json
import numpy as np

try:
    import pandas as pd
except Exception:
    pd = None


ROOT = 'experiments'


def ensure_root():
    os.makedirs(ROOT, exist_ok=True)


def new_experiment(name: str, metadata: Dict[str, Any] | None = None) -> str:
    """Create a new experiment folder and write metadata.json. Returns path."""
    ensure_root()
    path = os.path.join(ROOT, name)
    os.makedirs(path, exist_ok=True)
    meta = metadata or {}
    with open(os.path.join(path, 'metadata.json'), 'w') as f:
        json.dump(meta, f, indent=2)
    return path


def save_numpy_state(path: str, **arrays) -> None:
    """Save named numpy arrays to a .npz file at path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    np.savez(path, **arrays)


def load_numpy_state(path: str) -> Dict[str, np.ndarray]:
    """Load a .npz saved with save_numpy_state and return a dict of arrays."""
    data = np.load(path, allow_pickle=True)
    return {k: data[k] for k in data.files}


def save_dataframe(path: str, df) -> None:
    """Save pandas DataFrame if pandas available, else raise."""
    if pd is None:
        raise ImportError('pandas is required to use save_dataframe')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def load_dataframe(path: str):
    if pd is None:
        raise ImportError('pandas is required to use load_dataframe')
    return pd.read_csv(path)


def capture_rng_state(rng: np.random.Generator) -> Dict[str, Any]:
    """Capture numpy RNG state for reproducibility."""
    return {'bit_generator': type(rng.bit_generator).__name__, 'state': rng.bit_generator.state}


def restore_rng_state(rng: np.random.Generator, state: Dict[str, Any]) -> None:
    """Restore RNG state captured by capture_rng_state."""
    rng.bit_generator.state = state['state']


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    """Append a JSON record to a JSONL file (newline-delimited JSON)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(record) + '\n')


if __name__ == "__main__":
    print('io_utils demo — creating experiment folder and saving a state')
    p = new_experiment('test_run', {'desc': 'demo run'})
    save_numpy_state(p + '/state.npz', a=np.arange(10), b=np.random.randn(5))
    print('Saved example state to', p)

