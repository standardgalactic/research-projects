#!/usr/bin/env python3
"""
RSVP irreversible history field chi(x,t)
----------------------------------------
Chi accumulates entropy and feeds back
into Phi and entropy dynamics.
"""

import numpy as np

def roll(a, s, ax): return np.roll(a, s, axis=ax)

def grad_x(f, dx): return (roll(f,-1,1) - roll(f,1,1)) / (2*dx)
def grad_y(f, dy): return (roll(f,-1,0) - roll(f,1,0)) / (2*dy)

def laplacian(f, dx, dy):
    return ((roll(f,-1,1)-2*f+roll(f,1,1))/(dx*dx)
          + (roll(f,-1,0)-2*f+roll(f,1,0))/(dy*dy))

def advect(f, vx, vy, dx, dy):
    fx = np.where(vx>=0, (f-roll(f,1,1))/dx,
                          (roll(f,-1,1)-f)/dx)
    fy = np.where(vy>=0, (f-roll(f,1,0))/dy,
                          (roll(f,-1,0)-f)/dy)
    return -(vx*fx + vy*fy)

# ---------- chi evolution ----------

def step_chi(chi, S, vx, vy, dx, dy, p):
    """
    chi_t = accumulation - decay + diffusion + advection
    """
    dchi = (
        advect(chi, vx, vy, dx, dy)
        + p["a"] * S
        - p["b"] * chi
        + p["kchi"] * laplacian(chi, dx, dy)
    )
    return chi + p["dt"] * dchi

# ---------- feedback modifiers ----------

def phi_modifier(chi, p):
    """Slows Phi relaxation as history accumulates"""
    return 1.0 / (1.0 + p["alpha"] * chi)

def entropy_sink_modifier(chi, p):
    """Strengthens entropy sink with accumulated history"""
    return 1.0 + p["beta"] * chi