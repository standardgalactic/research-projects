import numpy as np
import matplotlib.pyplot as plt

def rsvp_ode_rhs(state, params):
    Phi, V, S = state
    kP  = params["kappa_Phi"]
    lam = params["lambda_S"]
    aP  = params["alpha_Phi"]
    nu  = params["nu_v"]
    bVS = params["beta_vS"]
    gE  = params["gamma_err"]
    Phi_star = params["Phi_star"]
    dS  = params["delta_S"]

    dPhi = -kP * Phi - V * Phi + lam * S
    dV   = -S + aP * Phi - nu * V - V * V
    dSdt = -bVS * V * S - gE * (Phi - Phi_star) - dS * S
    return np.array([dPhi, dV, dSdt])

def rk4_step(f, state, dt, params):
    k1 = f(state, params)
    k2 = f(state + 0.5 * dt * k1, params)
    k3 = f(state + 0.5 * dt * k2, params)
    k4 = f(state + dt * k3, params)
    return state + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)

def integrate_ode(f, state0, t_max, dt, params):
    n_steps = int(t_max / dt)
    traj = np.zeros((n_steps + 1, len(state0)))
    traj[0] = state0
    state = state0.copy()
    for i in range(1, n_steps + 1):
        state = rk4_step(f, state, dt, params)
        traj[i] = state
    return traj

if __name__ == "__main__":
    base_params = {
        "kappa_Phi": 0.5,
        "lambda_S": 0.8,
        "alpha_Phi": 0.3,
        "nu_v": 0.7,
        "beta_vS": 0.2,
        "gamma_err": 1.0,
        "Phi_star": 1.0,
        "delta_S": 0.2,
    }

    Phi_vals = np.linspace(-2.0, 2.0, 10)
    S_vals   = np.linspace(-2.0, 2.0, 10)

    t_max = 20.0
    dt    = 0.01

    fig, ax = plt.subplots()
    ax.set_xlabel("Phi")
    ax.set_ylabel("S")
    ax.set_title("Phase Portraits")

    for Phi0 in Phi_vals:
        for S0 in S_vals:
            V0 = 0.0
            traj = integrate_ode(rsvp_ode_rhs, np.array([Phi0, V0, S0]),
                                 t_max, dt, base_params)
            ax.plot(traj[:, 0], traj[:, 2])

    plt.tight_layout()
    fig.savefig("phase_portraits.png")
