"""
Flash-Reluctance Engine — Script 4 (v3): Thermodynamic Analysis
================================================================
Upgrades from v2:
  - Dynamic per-chamber thermal state (matches Script 03 v3 exactly)
  - Shared thermal core model
  - ω-governed control
  - Load torque
  - Control effort integral vs tracking error (design frontier)
  - Regime detection: stall / steady / oscillation / thermal collapse
  - Six plots including temperature evolution and phase portrait

Run inside Blender OR as plain Python (no bpy needed).
"""

import math
import os
import itertools

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ──────────────────────────────────────────────
# PARAMETERS — must match Script 03 v3
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
A_VANE          = 0.020
I_ROTOR         = 0.80
K_DRAG          = 0.04
K_BEARING       = 0.02
CONST_LOAD      = 2.0
K_LOAD          = 0.08

T_SOURCE        = 500.0
T_AMBIENT       = 25.0
T_INJECT        = 20.0
T_INJECT_MIN    = 200.0
K_HEAT          = 200.0     # (legacy — now per wall via K_CORE_TO_WALL)
K_COOL          = 20.0
C_WALL          = 500.0
M_INJ           = 0.002
H_VAP           = 2257e3
C_WATER         = 4186.0
VOL_CH          = 5e-4

T_CORE_INIT     = 500.0
C_CORE          = 8000.0
K_CORE_INPUT    = 400.0
K_CORE_TO_WALL  = 200.0

TAU_EM_PEAK     = 12.0
USE_TORQUE_CONTROL = True
TAU_TARGET      = 20.0
OMEGA_TARGET    = 25.0
KP_EM           = 0.8
KD_EM           = 0.2
K_OMEGA         = 0.5

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0
SPACING = TWO_PI / N_CHAMBERS
PW_RAD  = PULSE_WIDTH_DEG * DEG2RAD


# ──────────────────────────────────────────────
# PHYSICS
# ──────────────────────────────────────────────

def chamber_active(c, theta):
    return (theta - c * SPACING) % TWO_PI < PW_RAD


def flash_pressure(m, T):
    if T <= T_INJECT:
        return 0.0
    Q = m * (C_WATER * (T - T_INJECT) + H_VAP)
    return min((Q * 0.25) / VOL_CH, 8e6)


def thermal_torque_ch(theta, T_wall_ch):
    result = []
    for c in range(N_CHAMBERS):
        d = (theta - c * SPACING) % TWO_PI
        if d < PW_RAD and T_wall_ch[c] > T_INJECT_MIN:
            t = d / PW_RAD
            shape = 4*t*(1-t)*math.exp(-2*t)
            result.append(flash_pressure(M_INJ, T_wall_ch[c]) * shape * A_VANE * R_ROTOR)
        else:
            result.append(0.0)
    return result


def friction(omega):
    return K_DRAG*omega**2*(1 if omega>=0 else -1) + K_BEARING*omega


def load(omega):
    return CONST_LOAD + K_LOAD * omega


def injection_energy(T_wall):
    """Energy extracted from wall in one discrete injection event (Joules)."""
    if T_wall <= T_INJECT_MIN:
        return 0.0
    return M_INJ * (C_WATER * (T_wall - T_INJECT) + H_VAP)


def update_thermal(T_wall_ch, T_core, theta, prev_theta, dt, T_source_local):
    """
    Evolve per-chamber and core temperatures.
    Injection is a discrete event fired once per arc-entry (dimensionally correct).
    T_source_local is passed explicitly so parameter sweeps work correctly.
    """
    Q_core_in = K_CORE_INPUT * (T_source_local - T_core) * dt
    wall_Q = []
    for c in range(N_CHAMBERS):
        q = max(K_CORE_TO_WALL * (T_core - T_wall_ch[c]) * dt, 0.0)
        wall_Q.append(q)
    new_core = T_core + (Q_core_in - sum(wall_Q)) / C_CORE

    new_walls = []
    for c in range(N_CHAMBERS):
        T     = T_wall_ch[c]
        Q_in  = wall_Q[c]
        Q_out = K_COOL * (T - T_AMBIENT) * dt
        # Discrete arc-entry detection: was outside arc, now inside
        prev_d = (prev_theta - c * SPACING) % TWO_PI
        curr_d = (theta      - c * SPACING) % TWO_PI
        arc_entry = (prev_d >= PW_RAD or prev_d > curr_d) and curr_d < PW_RAD
        Q_inj = injection_energy(T) if arc_entry else 0.0
        new_walls.append(T + (Q_in - Q_out - Q_inj) / C_WALL)
    return new_walls, new_core


def make_controller():
    """Returns a fresh controller closure with its own state."""
    state = {"prev": 0.0}
    def ctrl(tau_th, tau_fr, tau_ld, omega, kp=KP_EM, kd=KD_EM, kw=K_OMEGA,
             tau_tgt=TAU_TARGET, omega_tgt=OMEGA_TARGET):
        if not USE_TORQUE_CONTROL or TAU_EM_PEAK <= 0:
            return 0.0
        tau_base = tau_th - tau_fr - tau_ld
        e_tau    = tau_tgt - tau_base
        e_omega  = omega_tgt - omega
        d_tau    = tau_base - state["prev"]
        state["prev"] = tau_base
        return min(max(kp*e_tau + kw*e_omega - kd*d_tau, 0.0), TAU_EM_PEAK)
    return ctrl


def make_slope_dist():
    """Returns a fresh slope-based distribution closure."""
    prev = [0.0] * N_CHAMBERS
    def dist(tau_em, tau_th_ch):
        d = [tau_th_ch[c] - prev[c] for c in range(N_CHAMBERS)]
        for c in range(N_CHAMBERS):
            prev[c] = tau_th_ch[c]
        weights = [max(-x, 0.0) for x in d]
        total_w = sum(weights)
        if total_w < 1e-6:
            total_m = sum(tau_th_ch)
            if total_m < 1e-6:
                return [tau_em / N_CHAMBERS] * N_CHAMBERS
            return [(t/total_m)*tau_em for t in tau_th_ch]
        return [(w/total_w)*tau_em for w in weights]
    return dist


# ──────────────────────────────────────────────
# CORE SIMULATOR
# ──────────────────────────────────────────────

def simulate(duration=8.0, dt=0.001, omega0=0.1, record_every=20,
             T_source_override=None, kp=KP_EM, kd=KD_EM, kw=K_OMEGA,
             tau_tgt=TAU_TARGET, omega_tgt=OMEGA_TARGET,
             const_load=CONST_LOAD, k_load=K_LOAD):

    T_src = T_source_override if T_source_override is not None else T_SOURCE
    ctrl  = make_controller()
    # dist (slope distribution) is a visualization layer only — not wired into
    # the scalar equation of motion, so not instantiated here.

    T_wall = [T_src * 0.8] * N_CHAMBERS
    T_core = T_CORE_INIT
    theta  = 0.0
    prev_theta = 0.0
    omega  = omega0
    E_th = E_em = E_fr = E_ld = 0.0
    ctrl_effort = 0.0   # ∫|τ_em| dθ

    times, omegas, tau_ths, tau_ems, tau_nets = [], [], [], [], []
    T_core_arr, T_wall_avg_arr = [], []
    e_th_arr, e_em_arr, e_ld_arr = [], [], []

    steps = int(duration / dt)

    for s in range(steps):
        tau_th_ch = thermal_torque_ch(theta, T_wall)
        tau_th    = sum(tau_th_ch)
        tau_fr    = friction(omega)
        tau_ld    = const_load + k_load * omega
        tau_em    = ctrl(tau_th, tau_fr, tau_ld, omega, kp, kd, kw, tau_tgt, omega_tgt)
        tau_net   = tau_th + tau_em - tau_fr - tau_ld

        alpha      = tau_net / I_ROTOR
        omega      = max(omega + alpha * dt, 0.0)
        dtheta     = omega * dt
        prev_theta = theta
        theta      = (theta + dtheta) % TWO_PI

        E_th  += tau_th * dtheta
        E_em  += tau_em * dtheta
        E_fr  += tau_fr * dtheta
        E_ld  += tau_ld * dtheta
        ctrl_effort += tau_em * dtheta

        T_wall, T_core = update_thermal(T_wall, T_core, theta, prev_theta, dt, T_src)

        if s % record_every == 0:
            times.append(s * dt)
            omegas.append(omega)
            tau_ths.append(tau_th)
            tau_ems.append(tau_em)
            tau_nets.append(tau_net)
            T_core_arr.append(T_core)
            T_wall_avg_arr.append(sum(T_wall)/N_CHAMBERS)
            e_th_arr.append(E_th)
            e_em_arr.append(E_em)
            e_ld_arr.append(E_ld)

    final_rpm = omega * 60 / TWO_PI
    KE_final  = 0.5 * I_ROTOR * omega**2
    E_in      = E_th + E_em
    eff       = KE_final / max(E_in, 1e-6) * 100
    em_frac   = E_em / max(E_in, 1e-6) * 100

    # Regime detection
    if len(omegas) > 20:
        late = omegas[len(omegas)*3//4:]
        mean_late = sum(late)/len(late)
        var_late  = sum((x-mean_late)**2 for x in late)/len(late)
        std_late  = var_late**0.5
        if omega < 0.5:
            regime = "STALL"
        elif std_late / max(mean_late, 0.01) > 0.05:
            regime = "OSCILLATING"
        elif T_core < T_AMBIENT + 50:
            regime = "THERMAL COLLAPSE"
        else:
            regime = "STEADY"
    else:
        regime = "UNKNOWN"

    # Tracking error: RMS speed error in final quarter
    if len(omegas) > 20:
        late_err = [abs(w - omega_tgt) for w in late]
        rms_err  = (sum(x**2 for x in late_err)/len(late_err))**0.5
    else:
        rms_err = float('inf')

    return {
        "t": times, "omega": omegas,
        "tau_th": tau_ths, "tau_em": tau_ems, "tau_net": tau_nets,
        "T_core": T_core_arr, "T_wall_avg": T_wall_avg_arr,
        "E_th": e_th_arr, "E_em": e_em_arr, "E_ld": e_ld_arr,
        "final_rpm": final_rpm, "KE": KE_final,
        "E_th_total": E_th, "E_em_total": E_em,
        "E_fr_total": E_fr, "E_ld_total": E_ld,
        "efficiency": eff, "em_frac": em_frac,
        "ctrl_effort": ctrl_effort, "rms_err": rms_err,
        "regime": regime,
        "final_T_core": T_core,
        "final_omega": omega,
    }


# ──────────────────────────────────────────────
# NUMERIC OUTPUT
# ──────────────────────────────────────────────

print("=" * 60)
print("FR ENGINE v3 — THERMODYNAMIC ANALYSIS")

baseline = simulate(duration=8.0)
print(f"\nBaseline (KP={KP_EM}, KD={KD_EM}, Kω={K_OMEGA}):")
print(f"  Regime          : {baseline['regime']}")
print(f"  Terminal RPM    : {baseline['final_rpm']:.0f}  (target: {OMEGA_TARGET*60/TWO_PI:.0f})")
print(f"  RMS speed error : {baseline['rms_err']:.3f} rad/s")
print(f"  Control effort  : {baseline['ctrl_effort']:.1f} J")
print(f"  E_thermal       : {baseline['E_th_total']:.0f} J")
print(f"  E_EM            : {baseline['E_em_total']:.0f} J  ({baseline['em_frac']:.1f}%)")
print(f"  E_load (work)   : {baseline['E_ld_total']:.0f} J")
print(f"  System eff      : {baseline['efficiency']:.1f}%")
print(f"  Core temp final : {baseline['final_T_core']:.1f}°C")

# T_source sweep
print("\nT_source sweep:")
for Ts in [300, 400, 500, 600, 700]:
    r = simulate(duration=6.0, T_source_override=Ts)
    print(f"  T_src={Ts}°C  RPM={r['final_rpm']:.0f}  "
          f"regime={r['regime']:12s}  em_frac={r['em_frac']:.0f}%  "
          f"core={r['final_T_core']:.0f}°C")

# Load sweep
print("\nLoad sweep (CONST_LOAD):")
for cl in [0.5, 1.0, 2.0, 4.0, 6.0, 8.0]:
    r = simulate(duration=6.0, const_load=cl)
    print(f"  CONST={cl:.1f} N·m  RPM={r['final_rpm']:.0f}  "
          f"regime={r['regime']:12s}  eff={r['efficiency']:.1f}%")

# Control effort vs tracking error frontier
print("\nControl effort vs RMS error frontier (KP sweep):")
print(f"  {'KP':>5}  {'KD':>5}  {'effort(J)':>10}  {'rms_err':>8}  {'RPM':>6}  regime")
for kp in [0.2, 0.5, 0.8, 1.2, 1.6, 2.0]:
    for kd in [0.05, 0.2, 0.4]:
        r = simulate(duration=5.0, dt=0.002, kp=kp, kd=kd)
        print(f"  {kp:5.1f}  {kd:5.2f}  {r['ctrl_effort']:10.1f}  "
              f"{r['rms_err']:8.4f}  {r['final_rpm']:6.0f}  {r['regime']}")

print("=" * 60)

# ──────────────────────────────────────────────
# PLOTS
# ──────────────────────────────────────────────

if not HAS_MPL:
    print("Install matplotlib for plots.")
else:
    os.makedirs("output", exist_ok=True)
    STYLE = {
        "figure.facecolor": "#080c10", "axes.facecolor": "#0d1520",
        "axes.edgecolor": "#1a3050", "axes.labelcolor": "#c8d8e8",
        "axes.titlecolor": "#ffffff", "xtick.color": "#5a7a9a",
        "ytick.color": "#5a7a9a", "grid.color": "#1a3050",
        "grid.linestyle": "--", "grid.linewidth": 0.5,
        "text.color": "#c8d8e8", "font.family": "monospace",
    }
    TC="#ff6b35"; EC="#00d4ff"; FC="#ff3e6c"; NC="#a8ff3e"
    OC="#f0e060"; WC="#ffffff"; PC="#cc88ff"

    with plt.rc_context(STYLE):

        # ── Plot 1: Full system state — 4-panel dashboard ─────────────────────
        fig, axes = plt.subplots(2, 2, figsize=(13, 8))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("FR ENGINE v3 — THERMODYNAMIC MACHINE STATE", color="#fff", fontsize=13)
        r = baseline

        # RPM
        ax = axes[0,0]
        rpms = [w*60/TWO_PI for w in r["omega"]]
        ax.plot(r["t"], rpms, color=OC, lw=2)
        ax.axhline(OMEGA_TARGET*60/TWO_PI, color=WC, lw=0.8, ls="--", alpha=0.5,
                   label=f"target {OMEGA_TARGET*60/TWO_PI:.0f} RPM")
        ax.set(title="Angular Velocity", xlabel="Time (s)", ylabel="RPM")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)

        # Torques
        ax = axes[0,1]
        ax.plot(r["t"], r["tau_th"], color=TC, lw=1.5, label="τ_thermal")
        ax.plot(r["t"], r["tau_em"], color=EC, lw=1.5, label="τ_EM")
        ax.plot(r["t"], r["tau_net"], color=NC, lw=2, label="τ_net")
        ax.axhline(0, color="#2a4060", lw=0.8)
        ax.set(title="Torques", xlabel="Time (s)", ylabel="N·m")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)

        # Temperatures
        ax = axes[1,0]
        ax.plot(r["t"], r["T_core"], color=TC, lw=2, label="T_core")
        ax.plot(r["t"], r["T_wall_avg"], color=OC, lw=1.5, ls="--", label="T_wall avg")
        ax.axhline(T_INJECT_MIN, color=FC, lw=0.8, ls=":", alpha=0.7,
                   label=f"T_min inject ({T_INJECT_MIN}°C)")
        ax.set(title="Thermal State", xlabel="Time (s)", ylabel="°C")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)

        # Cumulative energy
        ax = axes[1,1]
        ax.plot(r["t"], r["E_th"], color=TC, lw=1.5, label="E_thermal")
        ax.plot(r["t"], r["E_em"], color=EC, lw=1.5, label="E_EM")
        ax.plot(r["t"], r["E_ld"], color=NC, lw=2, label="E_load (work)")
        ax.set(title="Cumulative Energy", xlabel="Time (s)", ylabel="J")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)

        p = "output/fr_v3_dashboard.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

        # ── Plot 2: Phase portrait ω vs τ_net ──────────────────────────────────
        fig, ax = plt.subplots(figsize=(7, 6))
        fig.patch.set_facecolor("#080c10")
        r = baseline
        sc = ax.scatter(r["tau_net"], r["omega"],
                        c=r["t"], cmap="plasma", s=3, alpha=0.7)
        plt.colorbar(sc, ax=ax, label="Time (s)")
        ax.axvline(0, color="#2a4060", lw=0.8)
        ax.axhline(OMEGA_TARGET, color=WC, lw=0.8, ls="--", alpha=0.4,
                   label=f"ω_target={OMEGA_TARGET}")
        ax.set(xlabel="τ_net (N·m)", ylabel="ω (rad/s)",
               title="PHASE PORTRAIT  τ_net vs ω\n(color = time, early→late)")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)
        p = "output/fr_v3_phase.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

        # ── Plot 3: T_source sweep — regime map ───────────────────────────────
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("T_SOURCE SWEEP — Thermal Sensitivity", color="#fff")

        Ts_vals = list(range(250, 750, 25))
        rpms_by_T, em_frac_by_T, T_core_fin = [], [], []
        regime_colors = []
        REGIME_C = {"STEADY": NC, "OSCILLATING": OC, "STALL": FC,
                    "THERMAL COLLAPSE": PC, "UNKNOWN": WC}

        for Ts in Ts_vals:
            r = simulate(duration=5.0, dt=0.002, T_source_override=Ts)
            rpms_by_T.append(r["final_rpm"])
            em_frac_by_T.append(r["em_frac"])
            T_core_fin.append(r["final_T_core"])
            regime_colors.append(REGIME_C.get(r["regime"], WC))

        ax1.scatter(Ts_vals, rpms_by_T, c=regime_colors, s=30, zorder=3)
        ax1.plot(Ts_vals, rpms_by_T, color="#3a5c7a", lw=1, zorder=2)
        ax1.axhline(OMEGA_TARGET*60/TWO_PI, color=WC, lw=0.8, ls="--", alpha=0.4)
        ax1.set(xlabel="T_source (°C)", ylabel="Terminal RPM", title="Speed vs Heat Source")
        ax1.grid(True)

        ax2.plot(Ts_vals, em_frac_by_T, color=EC, lw=2, label="EM fraction (%)")
        ax2.plot(Ts_vals, T_core_fin, color=TC, lw=1.5, ls="--", label="Core temp final (°C)")
        ax2.axhline(40, color=FC, lw=0.8, ls=":", alpha=0.7, label="40% EM threshold")
        ax2.set(xlabel="T_source (°C)", ylabel="Value", title="EM Dependence vs Core Temp")
        ax2.legend(fontsize=8, framealpha=0.2)
        ax2.grid(True)

        # Legend for regime colors
        for regime, color in REGIME_C.items():
            ax1.scatter([], [], c=color, label=regime, s=40)
        ax1.legend(fontsize=7, framealpha=0.2)

        p = "output/fr_v3_thermal_sweep.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

        # ── Plot 4: Control effort vs tracking error frontier ─────────────────
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("CONTROL FRONTIER: Effort vs Tracking Error", color="#fff")

        kp_vals = [0.2, 0.5, 0.8, 1.2, 1.6, 2.0]
        kd_vals = [0.05, 0.15, 0.3, 0.5]
        kw_vals = [0.2, 0.5, 0.8]

        frontier_pts = []
        for kp, kd in itertools.product(kp_vals, kd_vals):
            r = simulate(duration=4.0, dt=0.002, kp=kp, kd=kd)
            frontier_pts.append((r["ctrl_effort"], r["rms_err"], kp, kd, r["regime"]))

        efforts  = [p[0] for p in frontier_pts]
        errors   = [p[1] for p in frontier_pts]
        kp_color = [p[2] for p in frontier_pts]

        sc = ax.scatter(efforts, errors, c=kp_color, cmap="plasma",
                        s=50, alpha=0.8, zorder=3)
        plt.colorbar(sc, ax=ax, label="KP value")

        # Mark Pareto-efficient points (low effort AND low error)
        pareto = []
        for i, (eff_i, err_i, *_) in enumerate(frontier_pts):
            dominated = any(
                frontier_pts[j][0] <= eff_i and frontier_pts[j][1] <= err_i
                and (frontier_pts[j][0] < eff_i or frontier_pts[j][1] < err_i)
                for j in range(len(frontier_pts)) if j != i
            )
            if not dominated:
                pareto.append((eff_i, err_i, frontier_pts[i][2], frontier_pts[i][3]))

        if pareto:
            pareto.sort()
            ax.plot([p[0] for p in pareto], [p[1] for p in pareto],
                    color=NC, lw=2, label="Pareto frontier", zorder=4)
            # Label the best point
            best = min(pareto, key=lambda p: p[0]+p[1]*10)
            ax.annotate(f"KP={best[2]}\nKD={best[3]}",
                        (best[0], best[1]), color=NC, fontsize=8,
                        xytext=(10, 10), textcoords="offset points")

        ax.set(xlabel="Control effort ∫|τ_em|dθ (J)",
               ylabel="RMS speed error (rad/s)",
               title="Low left = optimal: cheap control, accurate tracking")
        ax.legend(fontsize=8, framealpha=0.2)
        ax.grid(True)

        p = "output/fr_v3_frontier.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

        # ── Plot 5: Load sweep — stall boundary ───────────────────────────────
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("LOAD SWEEP — Stall Boundary & Efficiency", color="#fff")

        load_vals = [round(0.5 + 0.5*i, 1) for i in range(18)]
        rpm_by_load, eff_by_load, em_by_load, regime_by_load = [], [], [], []
        for cl in load_vals:
            r = simulate(duration=5.0, dt=0.002, const_load=cl)
            rpm_by_load.append(r["final_rpm"])
            eff_by_load.append(r["efficiency"])
            em_by_load.append(r["em_frac"])
            regime_by_load.append(r["regime"])

        ax1, ax2 = axes
        colors_load = [REGIME_C.get(rg, WC) for rg in regime_by_load]

        ax1.scatter(load_vals, rpm_by_load, c=colors_load, s=40, zorder=3)
        ax1.plot(load_vals, rpm_by_load, color="#3a5c7a", lw=1)
        ax1.axhline(0, color=FC, lw=1, ls="--", alpha=0.5, label="Stall")
        ax1.set(xlabel="Constant load (N·m)", ylabel="Terminal RPM", title="Speed vs Load")
        ax1.legend(fontsize=8, framealpha=0.2)
        ax1.grid(True)
        for rg, color in REGIME_C.items():
            ax1.scatter([], [], c=color, label=rg, s=30)
        ax1.legend(fontsize=7, framealpha=0.2, ncol=2)

        ax2.plot(load_vals, eff_by_load, color=NC, lw=2, label="Efficiency (%)")
        ax2.plot(load_vals, em_by_load,  color=EC, lw=1.5, ls="--", label="EM fraction (%)")
        ax2.axhline(40, color=FC, lw=0.8, ls=":", alpha=0.6)
        ax2.set(xlabel="Constant load (N·m)", ylabel="%", title="Efficiency & EM Use vs Load")
        ax2.legend(fontsize=8, framealpha=0.2)
        ax2.grid(True)

        p = "output/fr_v3_load_sweep.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

        # ── Plot 6: Per-chamber temperature evolution ──────────────────────────
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#080c10")

        # Run a shorter sim tracking per-chamber temps
        ctrl_ch = make_controller()
        # dist_ch not needed — slope distribution is visualization only
        T_w = [T_SOURCE * 0.8] * N_CHAMBERS
        T_cr = T_CORE_INIT
        th, prev_th, om = 0.0, 0.0, 0.1
        ch_T_history = [[] for _ in range(N_CHAMBERS)]
        core_T_history = []
        t_history = []

        steps_ch = int(6.0 / 0.002)
        for s in range(steps_ch):
            tau_th_ch_v = thermal_torque_ch(th, T_w)
            tau_th_v    = sum(tau_th_ch_v)
            tau_fr_v    = friction(om)
            tau_ld_v    = CONST_LOAD + K_LOAD * om
            tau_em_v    = ctrl_ch(tau_th_v, tau_fr_v, tau_ld_v, om)
            tau_net_v   = tau_th_v + tau_em_v - tau_fr_v - tau_ld_v

            om     = max(om + (tau_net_v / I_ROTOR) * 0.002, 0.0)
            prev_th = th
            th     = (th + om * 0.002) % TWO_PI
            T_w, T_cr = update_thermal(T_w, T_cr, th, prev_th, 0.002, T_SOURCE)

            if s % 50 == 0:
                t_history.append(s * 0.002)
                for c in range(N_CHAMBERS):
                    ch_T_history[c].append(T_w[c])
                core_T_history.append(T_cr)

        cmap_ch = plt.cm.plasma
        for c in range(N_CHAMBERS):
            ax.plot(t_history, ch_T_history[c],
                    color=cmap_ch(c/N_CHAMBERS), lw=1.2, label=f"Ch {c}", alpha=0.85)
        ax.plot(t_history, core_T_history, color=TC, lw=2.5, ls="--", label="Core")
        ax.axhline(T_INJECT_MIN, color=FC, lw=1, ls=":", alpha=0.7,
                   label=f"T_min ({T_INJECT_MIN}°C)")
        ax.axhline(T_SOURCE, color=WC, lw=0.6, ls=":", alpha=0.3,
                   label=f"T_source ({T_SOURCE}°C)")
        ax.set(xlabel="Time (s)", ylabel="Temperature (°C)",
               title="PER-CHAMBER WALL TEMPERATURE EVOLUTION\n(phase-staggered depletion pattern)")
        ax.legend(fontsize=8, framealpha=0.2, ncol=4)
        ax.grid(True)

        p = "output/fr_v3_temperatures.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  Saved: {p}")

    print("\nAll plots → output/fr_v3_*.png")
    print("Open in Blender: Image Editor → Open → output/")
