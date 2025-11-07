"""
gpu_utils.py

Handles GPU backend selection and availability checks for RSVP simulations.

Purpose:
- Automatically detect if CuPy/Numba GPU acceleration is available.
- Provide unified interface for choosing CPU/GPU.

Outputs:
- GPU availability flag
- Recommended backend

Testing Focus:
- Detection logic across systems
"""
from __future__ import annotations

GPU_AVAILABLE = False
BACKEND = 'cpu'

try:
    import cupy as cp
    GPU_AVAILABLE = True
    BACKEND = 'gpu_cupy'
except ImportError:
    try:
        from numba import cuda
        GPU_AVAILABLE = cuda.is_available()
        BACKEND = 'gpu_numba' if GPU_AVAILABLE else 'cpu'
    except ImportError:
        GPU_AVAILABLE = False
        BACKEND = 'cpu'


def select_backend(prefer_gpu: bool = True) -> str:
    if prefer_gpu and GPU_AVAILABLE:
        return BACKEND
    return 'cpu'


def is_gpu_available() -> bool:
    return GPU_AVAILABLE


# Demo harness
if __name__ == '__main__':
    print('gpu_utils demo')
    print('GPU available:', is_gpu_available())
    print('Selected backend:', select_backend())

