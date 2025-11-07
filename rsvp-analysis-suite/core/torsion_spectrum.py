"""
torsion_spectrum.py

Computes torsion, topological charge, helicity spectra, and vorticity suppression metrics
for RSVP Analysis Suite (RAS).

Purpose:
- Analyze topological features of vector fields (V) and scalar Φ/S fields.
- Compute helicity spectra and vorticity suppression.

Inputs:
- Phi: scalar field array
- V: vector field array
- S: scalar field array
- optional k-space resolution for spectra

Outputs:
- torsion maps
- helicity spectrum
- topological charge scalar
- vorticity suppression metrics

Testing Focus:
- Correct computation of helicity spectrum
- Preservation of global topological invariants
"""
from __future__ import annotations
from typing import Tuple, Optional
import numpy as np


def compute_vorticity(V: np.ndarray) -> np.ndarray:
    """Compute 2D vorticity (curl) of a 2-component vector field V(x,y)."""
    vx, vy = V[...,0], V[...,1]
    dvy_dx = np.gradient(vy, axis=0)
    dvx_dy = np.gradient(vx, axis=1)
    return dvy_dx - dvx_dy


def torsion_map(Phi: np.ndarray, V: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Compute a toy torsion map combining gradients and vorticity."""
    grad_phi_x, grad_phi_y = np.gradient(Phi)
    vorticity = compute_vorticity(V)
    torsion = grad_phi_x*V[...,0] + grad_phi_y*V[...,1] + vorticity + S
    return torsion


def topological_charge(torsion: np.ndarray) -> float:
    """Compute a scalar topological charge (sum over torsion map)."""
    return np.sum(torsion)


def helicity_spectrum(V: np.ndarray) -> np.ndarray:
    """Compute 2D Fourier-domain helicity spectrum (toy placeholder)."""
    vx_hat = np.fft.fft2(V[...,0])
    vy_hat = np.fft.fft2(V[...,1])
    # magnitude squared as toy helicity
    spectrum = np.abs(vx_hat*vy_hat.conjugate())
    spectrum = np.fft.fftshift(spectrum)
    return np.real(spectrum)


def vorticity_suppression(V: np.ndarray) -> float:
    """Compute suppression metric: fraction of vorticity below threshold."""
    vort = np.abs(compute_vorticity(V))
    threshold = np.mean(vort)
    return np.sum(vort < threshold)/vort.size


# Demo harness
if __name__ == '__main__':
    print('torsion_spectrum demo')
    shape = (16,16)
    Phi = np.random.randn(*shape)
    V = np.random.randn(*shape,2)
    S = np.random.randn(*shape)
    torsion = torsion_map(Phi, V, S)
    Q = topological_charge(torsion)
    spectrum = helicity_spectrum(V)
    suppression = vorticity_suppression(V)
    print('Topological charge:', Q)
    print('Helicity spectrum shape:', spectrum.shape)
    print('Vorticity suppression fraction:', suppression)

