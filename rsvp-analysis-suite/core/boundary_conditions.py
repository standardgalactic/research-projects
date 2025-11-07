"""
boundary_conditions.py

Implements boundary handling for RSVP fields (Phi, V, S) on 2D/3D lattices.

Purpose:
- Supports reflective, periodic, and open boundary conditions.
- Ensures consistent evolution for core solvers and simulations.

Inputs:
- Field array (Phi, V, or S)
- bc_type: 'reflective', 'periodic', or 'open'

Outputs:
- Field array with boundary conditions applied

Testing Focus:
- Correct mirroring for reflective BC
- Wrap-around for periodic BC
- Zero-padding for open BC
"""
from __future__ import annotations
import numpy as np


def apply_boundary(field: np.ndarray, bc_type: str = 'periodic') -> np.ndarray:
    """Apply boundary conditions to a field array."""
    field_bc = field.copy()

    if bc_type == 'reflective':
        # Mirror edges
        field_bc[0,:] = field_bc[1,:]
        field_bc[-1,:] = field_bc[-2,:]
        field_bc[:,0] = field_bc[:,1]
        field_bc[:,-1] = field_bc[:,-2]

    elif bc_type == 'periodic':
        # Wrap-around edges
        field_bc[0,:] = field_bc[-2,:]
        field_bc[-1,:] = field_bc[1,:]
        field_bc[:,0] = field_bc[:,-2]
        field_bc[:,-1] = field_bc[:,1]

    elif bc_type == 'open':
        # Zero padding
        field_bc[0,:] = 0
        field_bc[-1,:] = 0
        field_bc[:,0] = 0
        field_bc[:,-1] = 0

    else:
        raise ValueError(f'Unknown boundary condition type: {bc_type}')

    return field_bc


# Demo harness
if __name__ == '__main__':
    print('boundary_conditions demo')
    shape = (8,8)
    Phi = np.random.randn(*shape)
    print('Original Phi[0,:]:', Phi[0,:])
    Phi_reflect = apply_boundary(Phi, bc_type='reflective')
    print('Reflective Phi[0,:]:', Phi_reflect[0,:])
    Phi_periodic = apply_boundary(Phi, bc_type='periodic')
    print('Periodic Phi[0,:]:', Phi_periodic[0,:])
    Phi_open = apply_boundary(Phi, bc_type='open')
    print('Open Phi[0,:]:', Phi_open[0,:])

