import numpy as np

def laplacian_2d(f, dx, dy):
    f_ip = np.roll(f, -1, axis=1)
    f_im = np.roll(f,  1, axis=1)
    f_jp = np.roll(f, -1, axis=0)
    f_jm = np.roll(f,  1, axis=0)
    return ((f_ip - 2 * f + f_im) / (dx * dx)
            + (f_jp - 2 * f + f_jm) / (dy * dy))

def rsvp_phi_2d_step(phi, S, dx, dy, dt, kappa=0.02, lam=0.2):
    dPhi = kappa * laplacian_2d(phi, dx, dy) + lam * S
    return phi + dt * dPhi
