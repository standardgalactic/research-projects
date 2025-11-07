"""
synthetic_experiments.py

Generates controlled toy experiments for RSVP Analysis Suite (RAS).

Purpose:
- Create synthetic Phi, V, S fields for calibration and Monte Carlo validation.
- Supports reproducibility with deterministic seeds.

Inputs:
- shape: tuple, size of generated lattice
- seed: random seed for reproducibility
- pattern_type: 'random', 'gradient', 'sinusoidal'

Outputs:
- Phi, V, S numpy arrays

Testing Focus:
- Field generation reproducibility
- Controlled parameter variations for benchmarking
"""
from __future__ import annotations
from typing import Tuple
import numpy as np


def generate_synthetic_field(shape: Tuple[int,int]=(16,16), seed: int = 42, pattern_type: str = 'random') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    np.random.seed(seed)
    if pattern_type == 'random':
        Phi = np.random.randn(*shape)
        V = np.random.randn(*shape,2)
        S = np.random.randn(*shape)

    elif pattern_type == 'gradient':
        x = np.linspace(0,1,shape[0])
        y = np.linspace(0,1,shape[1])
        X, Y = np.meshgrid(x,y,indexing='ij')
        Phi = X+Y
        V = np.stack([X,Y],axis=-1)
        S = X-Y

    elif pattern_type == 'sinusoidal':
        x = np.linspace(0,2*np.pi,shape[0])
        y = np.linspace(0,2*np.pi,shape[1])
        X, Y = np.meshgrid(x,y,indexing='ij')
        Phi = np.sin(X)*np.cos(Y)
        V = np.stack([np.sin(Y), np.cos(X)],axis=-1)
        S = np.sin(X+Y)

    else:
        raise ValueError(f'Unknown pattern_type: {pattern_type}')

    return Phi, V, S


# Demo harness
if __name__ == '__main__':
    print('synthetic_experiments demo')
    Phi, V, S = generate_synthetic_field(shape=(16,16), seed=123, pattern_type='sinusoidal')
    print('Phi min/max:', Phi.min(), Phi.max())
    print('S min/max:', S.min(), S.max())

