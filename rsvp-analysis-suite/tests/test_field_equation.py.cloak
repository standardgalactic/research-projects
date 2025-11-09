"""
Test Field Equations

Checks numerical conservation of energy-momentum (∂_μ T^{μν} = 0) and entropy continuity equations for RSVP fields.
"""

import numpy as np
from core.rsvp_fields import compute_energy_momentum_tensor


def test_energy_momentum_conservation():
    lattice_size = 16
    Phi = np.random.rand(lattice_size, lattice_size)
    V = np.random.rand(lattice_size, lattice_size, 2)
    S = np.random.rand(lattice_size, lattice_size)

    T = compute_energy_momentum_tensor(Phi, V, S)
    div_T = np.gradient(T, axis=(0,1))  # simple finite difference divergence

    max_div = np.max(np.abs(div_T))
    assert max_div < 1e-5, f"Energy-momentum not conserved, max divergence={max_div}"


def test_entropy_continuity():
    # ∂t S + ∇·(Phi * V) ≈ 0
    lattice_size = 16
    Phi = np.random.rand(lattice_size, lattice_size)
    V = np.random.rand(lattice_size, lattice_size, 2)
    S = np.random.rand(lattice_size, lattice_size)

    dS_dt = np.gradient(S, axis=0)
    div_flux = np.gradient(Phi*V[:,:,0], axis=0) + np.gradient(Phi*V[:,:,1], axis=1)
    continuity_residual = dS_dt + div_flux

    max_residual = np.max(np.abs(continuity_residual))
    assert max_residual < 1e-5, f"Entropy continuity violated, max residual={max_residual}"


if __name__ == '__main__':
    test_energy_momentum_conservation()
    test_entropy_continuity()
    print('All field equations tests passed.')

