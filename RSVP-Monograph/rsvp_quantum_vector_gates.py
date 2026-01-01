#!/usr/bin/env python3
"""
rsvp_quantum_vector_gates.py
----------------------------
Map flow vector v -> RX/RY angles, while scalar theta stays on RZ.
Optional circuit constructor (requires Qiskit).
"""

import numpy as np

try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None

def normalize_v(vx, vy, v_scale=1.0, eps=1e-12):
    """
    Normalize v to roughly [-1,1] scale (user chooses v_scale).
    """
    return vx / (v_scale + eps), vy / (v_scale + eps)

def angles_from_v_linear(vx, vy, alpha=np.pi):
    """
    Simple linear mapping:
        ax = alpha*vx
        ay = alpha*vy
    Assumes vx,vy already normalized to ~[-1,1].
    """
    return float(alpha * vx), float(alpha * vy)

def angles_from_v_polar(vx, vy, alpha=np.pi):
    """
    Polar mapping:
        r = |v|, phi = atan2(vy,vx)
        ax = alpha*r*cos(phi), ay = alpha*r*sin(phi)
    Which reduces to alpha*vx, alpha*vy if r small, but keeps interpretation explicit.
    """
    r = float(np.sqrt(vx*vx + vy*vy))
    if r == 0.0:
        return 0.0, 0.0
    phi = float(np.arctan2(vy, vx))
    return float(alpha * r * np.cos(phi)), float(alpha * r * np.sin(phi))

def build_hybrid_circuit(theta_z, theta_x, theta_y):
    """
    GHZ-like + imprint:
      - RZ(theta_z) = scalar holonomy
      - RX(theta_x), RY(theta_y) = vector encoding
    """
    if QuantumCircuit is None:
        raise RuntimeError("Qiskit not installed.")

    qc = QuantumCircuit(3)

    qc.h(2)
    qc.cx(2, 0)
    qc.cx(2, 1)

    # scalar holonomy
    qc.rz(theta_z, 0)
    qc.rz(theta_z, 1)

    # vector encoding
    qc.rx(theta_x, 0)
    qc.ry(theta_y, 1)

    qc.barrier()
    return qc