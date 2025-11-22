import numpy as np
import matplotlib.pyplot as plt
from ode_phase_portrait import rsvp_ode_rhs, integrate_ode

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

t_max = 20.0
dt    = 0.01

gamma_values = np.linspace(0.1, 3.0, 40)
final_Phi = []
final_S   = []

for gE in gamma_values:
    params = base_params.copy()
    params["gamma_err"] = gE
    state0 = np.array([0.5, 0.0, 0.5])
    traj = integrate_ode(rsvp_ode_rhs, state0, t_max, dt, params)
    final_Phi.append(traj[-1, 0])
    final_S.append(traj[-1, 2])

plt.figure()
plt.plot(gamma_values, final_Phi)
plt.xlabel("gamma_err")
plt.ylabel("Final Phi")
plt.title("Bifurcation Scan: Final Phi")
plt.savefig("bifurcation_phi.png")

plt.figure()
plt.plot(gamma_values, final_S)
plt.xlabel("gamma_err")
plt.ylabel("Final S")
plt.title("Bifurcation Scan: Final S")
plt.savefig("bifurcation_s.png")
