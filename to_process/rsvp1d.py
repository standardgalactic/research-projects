import numpy as np

def laplacian_1d(f, dx):
    return (np.roll(f, -1) - 2 * f + np.roll(f, 1)) / (dx * dx)

def grad_1d(f, dx):
    return (np.roll(f, -1) - np.roll(f, 1)) / (2 * dx)

def advect_1d(f, v, dx):
    flux = f * v
    return -(np.roll(flux, -1) - np.roll(flux, 1)) / (2 * dx)

class RSVP1DParams:
    def __init__(self, kappa=0.02, lam=0.2, nu=0.05,
                 alpha=0.5, D_S=0.02, beta=0.3,
                 gamma=0.4, Phi_star=1.0):
        self.kappa = kappa
        self.lam = lam
        self.nu = nu
        self.alpha = alpha
        self.D_S = D_S
        self.beta = beta
        self.gamma = gamma
        self.Phi_star = Phi_star

def rsvp_rhs_1d(phi, v, S, dx, params):
    dPhi = params.kappa * laplacian_1d(phi, dx)            + advect_1d(phi, v, dx)            + params.lam * S

    dSdx = grad_1d(S, dx)
    dPhidx = grad_1d(phi, dx)
    dvdx = grad_1d(v, dx)

    dV = -dSdx + params.nu * laplacian_1d(v, dx)          + params.alpha * dPhidx - v * dvdx

    dS = params.D_S * laplacian_1d(S, dx)          - params.beta * v * dSdx          - params.gamma * (phi - params.Phi_star)

    return dPhi, dV, dS
