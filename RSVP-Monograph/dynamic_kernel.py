#!/usr/bin/env python3
"""
Dynamical Equilibrium Kernel -> Phase Stream -> Optional Qiskit Circuit
"""

import numpy as np
from dataclasses import dataclass

try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None


@dataclass
class Params:
    T_env: float = 300.0

    # Temperature relaxation times
    tau_A: float = 8.0
    tau_B: float = 10.0

    # Couplings
    k_AB: float = 0.12
    k_phi: float = 0.8

    # Phi dynamics
    tau_phi: float = 20.0
    a_T: float = 0.004
    a_S: float = 0.06

    # Entropy dynamics
    sigma0: float = 0.02
    b_delta: float = 0.0005
    b_sink: float = 0.03

    # Chi dynamics (history / constraint accumulator)
    c_S: float = 0.9
    c_chi: float = 0.01


def Es_from_state(TA, TB, Phi, eps=1e-12):
    if abs(Phi) < eps:
        raise ValueError(f"Phi too close to zero: {Phi}")
    return (TA + TB) / (2.0 * Phi)


def theta_from_Es(Es):
    frac = Es % 1.0
    return float((2.0 * np.pi) * frac)


def rhs(state, p: Params):
    TA, TB, Phi, S, chi = state

    dTA = - (TA - p.T_env) / p.tau_A + p.k_AB * (TB - TA) + p.k_phi * (Phi - 1.0)
    dTB = - (TB - p.T_env) / p.tau_B + p.k_AB * (TA - TB) - p.k_phi * (Phi - 1.0)

    excitation = ((TA + TB) / 2.0) - p.T_env
    dPhi = - (Phi - 1.0) / p.tau_phi + p.a_T * excitation - p.a_S * S

    dS = p.sigma0 + p.b_delta * (TA - TB) ** 2 - p.b_sink * Phi * S

    dchi = p.c_S * S - p.c_chi * chi

    return np.array([dTA, dTB, dPhi, dS, dchi], dtype=float)


def rk4_step(state, dt, p: Params):
    k1 = rhs(state, p)
    k2 = rhs(state + 0.5 * dt * k1, p)
    k3 = rhs(state + 0.5 * dt * k2, p)
    k4 = rhs(state + dt * k3, p)
    return state + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


def build_phase_circuit(theta):
    """
    GHZ-like state + phase imprint.
    Optional 'phase readout' stage added so theta influences measurement statistics.
    """
    if QuantumCircuit is None:
        raise RuntimeError("Qiskit not installed.")

    qc = QuantumCircuit(3, 3)

    # GHZ-like preparation
    qc.h(2)
    qc.cx(2, 0)
    qc.cx(2, 1)

    # imprint phase
    qc.rz(theta, 0)
    qc.rz(theta, 1)

    # ---- phase readout trick ----
    # Convert relative phase into measurable parity signal:
    # undo GHZ and measure
    qc.cx(2, 1)
    qc.cx(2, 0)
    qc.h(2)

    qc.measure([0, 1, 2], [0, 1, 2])
    return qc


def simulate(
    T=100.0,
    dt=0.1,
    x0=(320.0, 285.0, 1.0, 0.1, 0.0),
    params=Params(),
    build_circuits=False,
):
    n = int(np.ceil(T / dt))
    t = np.linspace(0.0, n*dt, n+1)

    X = np.zeros((n+1, 5), dtype=float)
    Es = np.zeros(n+1, dtype=float)
    theta = np.zeros(n+1, dtype=float)
    circuits = [] if build_circuits else None

    X[0] = np.array(x0, dtype=float)

    for i in range(n+1):
        TA, TB, Phi, S, chi = X[i]
        Es[i] = Es_from_state(TA, TB, Phi)
        theta[i] = theta_from_Es(Es[i])

        if build_circuits:
            circuits.append(build_phase_circuit(theta[i]))

        if i < n:
            X[i+1] = rk4_step(X[i], dt, params)

            # Optional: keep Phi bounded positive-ish (a cheap “physicality” clamp)
            X[i+1, 2] = max(X[i+1, 2], 1e-6)
            X[i+1, 3] = max(X[i+1, 3], 0.0)  # S >= 0

    return t, X, Es, theta, circuits


if __name__ == "__main__":
    t, X, Es, th, _ = simulate(T=50.0, dt=0.2, build_circuits=False)
    print("final state:", X[-1])
    print("final Es:", Es[-1])
    print("final theta:", th[-1])