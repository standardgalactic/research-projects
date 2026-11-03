# SPDX-License-Identifier: MIT
# Copyright (c) 2025-2026 Flyxion
"""Project-owned adaptation of Flyxion's vector-gate circuit, not Qiskit code."""
import json
import platform
from pathlib import Path
import numpy as np
import qiskit
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Pauli, partial_trace, purity


def angles(vx, vy, scale=1.0, alpha=np.pi, mapping='linear'):
    values = np.asarray([vx, vy, scale, alpha], dtype=float)
    if not np.isfinite(values).all() or scale <= 0:
        raise ValueError('finite inputs and positive scale required')
    x, y = vx / scale, vy / scale
    if mapping == 'linear':
        return alpha * x, alpha * y
    if mapping == 'polar':
        r, phi = np.hypot(x, y), np.arctan2(y, x)
        return alpha * r * np.cos(phi), alpha * r * np.sin(phi)
    raise ValueError('unknown mapping')


def circuit(z, x, y, order='z_then_vector', entangled=True):
    if order not in ('z_then_vector', 'vector_then_z'):
        raise ValueError('unknown order')
    qc = QuantumCircuit(3)
    qc.h(2)
    if entangled:
        qc.cx(2, 0)
        qc.cx(2, 1)
    def scalar():
        qc.rz(z, 0)
        qc.rz(z, 1)
    def vector():
        qc.rx(x, 0)
        qc.ry(y, 1)
    if order == 'z_then_vector':
        scalar(); vector()
    else:
        vector(); scalar()
    return qc


def state(qc):
    return Statevector.from_instruction(qc)


def expectation(s, label):
    # Qiskit labels and bitstrings run q2, q1, q0 from left to right.
    return float(np.real(s.expectation_value(Pauli(label))))


def infidelity(a, b):
    return float(np.clip(1 - abs(np.vdot(a.data, b.data))**2, 0, 1))


def tv(a, b):
    return float(np.abs(a - b).sum() / 2)


def write(name, rows, settings):
    out = Path(__file__).resolve().parent / 'results'
    out.mkdir(exist_ok=True)
    payload = dict(experiment=name, settings=settings, versions=dict(
        python=platform.python_version(), numpy=np.__version__, qiskit=qiskit.__version__), rows=rows)
    (out / (name + '.json')).write_text(json.dumps(payload, indent=2, allow_nan=False) + '\n')
    print(name + ': ' + json.dumps(rows[-1]))
