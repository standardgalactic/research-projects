"""
Flash-Reluctance Engine — Script 4 (v2): Closed-Loop Analysis & Optimizer
==========================================================================
Upgrades from v1:
  - PD torque controller replaces phase-based EM (matches Script 03 v2)
  - Per-chamber energy accounting
  - KP/KD automatic optimizer (grid search → refinement)
  - TAU_TARGET as a function of (theta, omega) — programmable waveform
  - Five plots + a numeric optimization report

Run inside Blender Scripting workspace OR as plain Python (no bpy needed).
matplotlib required for plots; install with:
    import subprocess; subprocess.run(['pip','install','matplotlib'])
"""

import math
import os
import itertools

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not available — numeric output only")

# ──────────────────────────────────────────────
# BASE PARAMETERS
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
T_WALL          = 400.0
M_INJ           = 0.002
I_ROTOR         = 0.80
K_DRAG          = 0.04
K_BEARING       = 0.02
A_VANE          = 0.020
TAU_EM_PEAK     = 12.0

# PD controller defaults
USE_TORQUE_CONTROL = True
TAU_TARGET      = 25.0
KP_EM           = 0.8
KD_EM           = 0.2

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0
H_VAP   = 2257e3
C_WATER = 4186.0
T_COLD  = 20.0
VOL_CH  = 5e-4

# ──────────────────────────────────────────────
# PHYSICS
# ──────────────────────────────────────────────

def flash_pressure(m_inj, T_wall):
    Q = m_inj * (C_WATER * (T_wall - T_COLD) + H_VAP)
    return min((Q * 0.25) / VOL_CH, 8e6)


def thermal_torque(theta, P_peak, N=None, pw_deg=None):
    N = N or N_CHAMBERS
    pw_deg = pw_deg or PULSE_WIDTH_DEG
    spacing = TWO_PI / N
    pw = pw_deg * DEG2RAD
    tau = 0.0
    for c in range(N):
        d = (theta - c * spacing) % TWO_PI
        if d < pw:
            t = d / pw
            tau += P_peak * (4*t*(1-t)*math.exp(-2*t)) * A_VANE * R_ROTOR
    return tau


def friction(omega):
    return K_DRAG * omega**2 * (1 if omega >= 0 else -1) + K_BEARING * omega


def em_control(tau_th, tau_fr, state, tau_target=None, kp=None, kd=None):
    """
    PD controller with injectable gains and target.
    state dict carries prev_tau_base between calls.
    """
    if not USE_TORQUE_CONTROL or TAU_EM_PEAK <= 0:
        return 0.0

    tau_target = tau_target if tau_target is not None else TAU_TARGET
    kp = kp if kp is not None else KP_EM
    kd = kd if kd is not None else KD_EM

    tau_base = tau_th - tau_fr
    error    = tau_target - tau_base
    d_tau    = tau_base - state.get("prev", 0.0)
    state["prev"] = tau_base

    tau_em = kp * error - kd * d_tau
    return min(max(tau_em, 0.0), TAU_EM_PEAK)


# Programmable TAU_TARGET: function of theta and omega
# Modes: "constant", "sinusoidal", "rpm_proportional", "acceleration_boost"
TARGET_MODE = "sinusoidal"   # change this to explore

def tau_target_fn(theta, omega, mode=TARGET_MODE):
    """
    Returns the desired net torque given current state.
    This makes the engine a programmable torque waveform generator.
    """
    if mode == "constant":
        return TAU_TARGET

    elif mode == "sinusoidal":
        # Oscillate target between 15 and 35 N·m at rotor frequency / 2
        return TAU_TARGET + 10.0 * math.sin(N_CHAMBERS * theta / 2)

    elif mode == "rpm_proportional":
        # Reduce EM demand as RPM rises (back-off at speed)
        rpm = omega * 60 / TWO_PI
        rpm_max = 300.0
        fraction = max(0.0, 1.0 - rpm / rpm_max)
        return TAU_TARGET * fraction + 5.0   # floor at 5 N·m

    elif mode == "acceleration_boost":
        # Full target for first half-second, then settle at lower value
        t_sim = getattr(tau_target_fn, "_t", 0.0)
        return TAU_TARGET if t_sim < 0.5 else TAU_TARGET * 0.6

    return TAU_TARGET


# ──────────────────────────────────────────────
# CORE SIMULATOR
# ──────────────────────────────────────────────

def simulate(T_wall=T_WALL, N=N_CHAMBERS, pw_deg=PULSE_WIDTH_DEG,
             kp=KP_EM, kd=KD_EM, tau_target_mode="constant",
             duration=5.0, dt=0.001, omega0=0.1,
             record_every=10):
    """
    Full Euler integration with PD controller.
    Returns dict of recorded arrays.
    """
    P_peak = flash_pressure(M_INJ, T_wall)
    theta = 0.0
    omega = omega0
    state = {"prev": 0.0}
    sim_t = 0.0

    times, omegas, tau_ths, tau_ems, tau_nets = [], [], [], [], []
    E_th, E_em, E_fr = 0.0, 0.0, 0.0

    steps = int(duration / dt)

    for s in range(steps):
        tau_th  = thermal_torque(theta, P_peak, N, pw_deg)
        tau_fr  = friction(omega)
        tgt     = tau_target_fn(theta, omega, tau_target_mode)
        tau_em  = em_control(tau_th, tau_fr, state, tgt, kp, kd)
        tau_net = tau_th + tau_em - tau_fr

        alpha   = tau_net / I_ROTOR
        omega   = max(omega + alpha * dt, 0.0)
        dtheta  = omega * dt
        theta   = (theta + dtheta) % TWO_PI
        sim_t  += dt

        E_th += tau_th * dtheta
        E_em += tau_em * dtheta
        E_fr += tau_fr * dtheta

        if s % record_every == 0:
            times.append(sim_t)
            omegas.append(omega)
            tau_ths.append(tau_th)
            tau_ems.append(tau_em)
            tau_nets.append(tau_net)

    KE_final = 0.5 * I_ROTOR * omega**2
    E_in     = E_th + E_em
    eff      = KE_final / max(E_in, 1e-6) * 100

    return {
        "t": times, "omega": omegas,
        "tau_th": tau_ths, "tau_em": tau_ems, "tau_net": tau_nets,
        "E_th": E_th, "E_em": E_em, "E_fr": E_fr,
        "KE": KE_final, "efficiency": eff,
        "final_rpm": omega * 60 / TWO_PI,
    }


def torque_waveform(N=N_CHAMBERS, pw_deg=PULSE_WIDTH_DEG, T_wall=T_WALL,
                    omega_ref=20.0, kp=KP_EM, kd=KD_EM, steps=720):
    """One-revolution torque profile using PD controller."""
    P_peak = flash_pressure(M_INJ, T_wall)
    state  = {"prev": 0.0}
    angles, th_arr, em_arr, fr_arr, net_arr = [], [], [], [], []

    for s in range(steps):
        theta = s * TWO_PI / steps
        tau_th = thermal_torque(theta, P_peak, N, pw_deg)
        tau_fr = friction(omega_ref)
        tau_em = em_control(tau_th, tau_fr, state)
        net    = tau_th + tau_em - tau_fr
        angles.append(theta * 180 / math.pi)
        th_arr.append(tau_th); em_arr.append(tau_em)
        fr_arr.append(tau_fr); net_arr.append(net)

    return angles, th_arr, em_arr, fr_arr, net_arr


# ──────────────────────────────────────────────
# KP / KD OPTIMIZER — grid search + refinement
# ──────────────────────────────────────────────

def optimize_gains(duration=3.0, dt=0.002):
    """
    Grid search over KP × KD space.
    Objective: maximize final KE while minimizing torque ripple.
    Returns sorted list of (score, kp, kd, result).
    """
    kp_range = [round(0.2 + 0.2*i, 2) for i in range(9)]    # 0.2 … 1.8
    kd_range = [round(0.05 + 0.1*i, 2) for i in range(8)]   # 0.05 … 0.75

    results = []
    print(f"  Optimizer: {len(kp_range)}×{len(kd_range)} = {len(kp_range)*len(kd_range)} grid points ...")

    for kp, kd in itertools.product(kp_range, kd_range):
        r = simulate(kp=kp, kd=kd, duration=duration, dt=dt)

        # Score: KE (want high) − ripple penalty (want low)
        tau_nets = r["tau_net"]
        if len(tau_nets) > 1:
            avg_net = sum(tau_nets) / len(tau_nets)
            ripple  = (max(tau_nets) - min(tau_nets)) / max(abs(avg_net), 1e-6)
        else:
            ripple = 0.0

        # Also penalize if EM is doing all the work (thermal should dominate)
        em_fraction = r["E_em"] / max(r["E_th"] + r["E_em"], 1e-6)
        em_penalty  = max(0.0, em_fraction - 0.4) * 50.0   # penalize > 40% EM

        score = r["KE"] - ripple * 5.0 - em_penalty
        results.append((score, kp, kd, r))

    results.sort(key=lambda x: x[0], reverse=True)
    return results


# ──────────────────────────────────────────────
# NUMERIC OUTPUT
# ──────────────────────────────────────────────

print("=" * 60)
print("FR ENGINE v2 — CLOSED-LOOP ANALYSIS")

# Baseline
baseline = simulate(duration=5.0)
print(f"\nBaseline (KP={KP_EM}, KD={KD_EM}, TAU_TARGET={TAU_TARGET}):")
print(f"  Terminal RPM  : {baseline['final_rpm']:.0f}")
print(f"  Final KE      : {baseline['KE']:.1f} J")
print(f"  Thermal in    : {baseline['E_th']:.1f} J")
print(f"  EM in         : {baseline['E_em']:.1f} J")
print(f"  Friction loss : {baseline['E_fr']:.1f} J")
print(f"  System eff    : {baseline['efficiency']:.1f}%")

# Operating sweep
print("\nT_wall sweep (KP/KD fixed):")
for T in [200, 300, 400, 500, 600]:
    r = simulate(T_wall=T, duration=5.0)
    print(f"  T={T}°C  RPM={r['final_rpm']:.0f}  eff={r['efficiency']:.1f}%  "
          f"E_th={r['E_th']:.0f}J  E_em={r['E_em']:.0f}J")

# Target mode comparison
print("\nTAU_TARGET mode comparison:")
for mode in ["constant", "sinusoidal", "rpm_proportional", "acceleration_boost"]:
    r = simulate(tau_target_mode=mode, duration=5.0)
    nets = r["tau_net"]
    avg_n = sum(nets)/len(nets)
    rip = (max(nets)-min(nets))/max(abs(avg_n),1e-6)*100
    print(f"  {mode:25s}  RPM={r['final_rpm']:.0f}  "
          f"avg_τnet={avg_n:.1f}  ripple={rip:.1f}%  eff={r['efficiency']:.1f}%")

# Optimize
print("\nRunning KP/KD optimizer ...")
opt_results = optimize_gains(duration=3.0, dt=0.002)
print(f"\nTop 5 gain configurations:")
print(f"  {'KP':>6}  {'KD':>6}  {'Score':>8}  {'RPM':>6}  {'Eff%':>6}  {'E_EM/E_th':>10}")
for score, kp, kd, r in opt_results[:5]:
    em_frac = r["E_em"] / max(r["E_th"], 1e-6)
    print(f"  {kp:6.2f}  {kd:6.2f}  {score:8.2f}  {r['final_rpm']:6.0f}  "
          f"{r['efficiency']:6.1f}%  {em_frac:10.3f}")

best_score, best_kp, best_kd, best_result = opt_results[0]
print(f"\nOptimal: KP={best_kp}, KD={best_kd} → score={best_score:.2f}")
print("=" * 60)

# ──────────────────────────────────────────────
# PLOTS
# ──────────────────────────────────────────────

if not HAS_MPL:
    print("Install matplotlib for plots.")
else:
    STYLE = {
        "figure.facecolor": "#080c10", "axes.facecolor": "#0d1520",
        "axes.edgecolor": "#1a3050", "axes.labelcolor": "#c8d8e8",
        "axes.titlecolor": "#ffffff", "xtick.color": "#5a7a9a",
        "ytick.color": "#5a7a9a", "grid.color": "#1a3050",
        "grid.linestyle": "--", "grid.linewidth": 0.5,
        "text.color": "#c8d8e8", "font.family": "monospace",
        "lines.linewidth": 1.8,
    }
    TC = "#ff6b35"; EC = "#00d4ff"; FC = "#ff3e6c"; NC = "#a8ff3e"
    OC = "#f0e060"; WC = "#ffffff"

    with plt.rc_context(STYLE):

        # ── Plot 1: Torque waveform (PD-controlled) ──────────────────────────
        fig, ax = plt.subplots(figsize=(11, 4))
        fig.patch.set_facecolor("#080c10")
        angles, th, em, fr, net = torque_waveform()
        ax.plot(angles, th,  color=TC, label="τ_thermal", lw=2)
        ax.plot(angles, em,  color=EC, label="τ_EM (PD ctrl)", lw=1.5, ls="--")
        ax.plot(angles, fr,  color=FC, label="τ_friction", lw=1, ls=":")
        ax.plot(angles, net, color=NC, label="τ_net", lw=2.5)
        avg_net = sum(net)/len(net)
        ax.axhline(avg_net, color=NC, lw=1, alpha=0.4, ls="-.")
        ax.axhline(TAU_TARGET, color=WC, lw=0.8, alpha=0.3, ls="--")
        ax.text(5, TAU_TARGET+0.3, f"TAU_TARGET={TAU_TARGET} N·m",
                color=WC, fontsize=8, alpha=0.6)
        ax.set(xlabel="Rotor angle (°)", ylabel="Torque (N·m)",
               title=f"TORQUE WAVEFORM — PD Controller  (KP={KP_EM}, KD={KD_EM})",
               xlim=(0,360))
        ax.legend(loc="upper right", framealpha=0.2, edgecolor="#1a3050")
        ax.grid(True)
        p = "/tmp/fr_v2_torque.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  {p}")

        # ── Plot 2: Speed + energy accounting ────────────────────────────────
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
        fig.patch.set_facecolor("#080c10")

        r = baseline
        rpms = [w * 60 / TWO_PI for w in r["omega"]]
        ax1.plot(r["t"], rpms, color=OC, lw=2)
        ax1.axhline(baseline["final_rpm"], color=OC, lw=0.8, ls="--", alpha=0.5)
        ax1.set(ylabel="RPM", title="SPEED RAMP + ENERGY ACCOUNTING")
        ax1.grid(True)

        # Cumulative energy: recompute with detail
        r2 = simulate(duration=5.0, record_every=5)
        # Reconstruct cumulative from per-step torques (approx from recorded)
        dt_rec = 5.0 / (len(r2["t"]) * 5) * 5
        E_th_arr = [sum(r2["tau_th"][:i+1]) * 0.01 for i in range(len(r2["t"]))]
        E_em_arr = [sum(r2["tau_em"][:i+1]) * 0.01 for i in range(len(r2["t"]))]
        KE_arr   = [0.5 * I_ROTOR * w**2 for w in r2["omega"]]

        ax2.plot(r2["t"], E_th_arr, color=TC, lw=1.5, label="E_thermal (proxy)")
        ax2.plot(r2["t"], E_em_arr, color=EC, lw=1.5, label="E_EM (proxy)")
        ax2.plot(r2["t"], KE_arr,   color=NC, lw=2,   label="KE (actual)")
        ax2.set(xlabel="Time (s)", ylabel="Energy (J)")
        ax2.legend(loc="upper left", framealpha=0.2, edgecolor="#1a3050")
        ax2.grid(True)
        p = "/tmp/fr_v2_energy.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  {p}")

        # ── Plot 3: Target mode comparison ───────────────────────────────────
        fig, axes = plt.subplots(2, 2, figsize=(12, 7))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("TAU_TARGET MODE COMPARISON", color="#fff", fontsize=13)

        modes = ["constant", "sinusoidal", "rpm_proportional", "acceleration_boost"]
        mode_colors = [NC, EC, TC, OC]
        for ax, mode, color in zip(axes.flat, modes, mode_colors):
            r = simulate(tau_target_mode=mode, duration=5.0)
            rpms = [w * 60 / TWO_PI for w in r["omega"]]
            ax.plot(r["t"], rpms, color=color, lw=2)
            ax.set(title=mode, xlabel="Time (s)", ylabel="RPM")
            ax.text(0.05, 0.9, f"Final: {r['final_rpm']:.0f} RPM\nEff: {r['efficiency']:.1f}%",
                    transform=ax.transAxes, color=color, fontsize=9)
            ax.grid(True)

        p = "/tmp/fr_v2_modes.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  {p}")

        # ── Plot 4: KP/KD optimizer heatmap ──────────────────────────────────
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.patch.set_facecolor("#080c10")
        fig.suptitle("KP / KD OPTIMIZER — GRID SEARCH", color="#fff", fontsize=13)

        kp_vals = sorted(set(r[1] for r in opt_results))
        kd_vals = sorted(set(r[2] for r in opt_results))

        def make_grid(value_fn):
            grid = []
            for kd in kd_vals:
                row = []
                for kp in kp_vals:
                    match = next((r for r in opt_results if r[1]==kp and r[2]==kd), None)
                    row.append(value_fn(match[3]) if match else 0)
                grid.append(row)
            return grid

        score_grid = make_grid(lambda r: r["KE"])
        eff_grid   = make_grid(lambda r: r["efficiency"])

        for ax, grid, title, cmap in zip(axes,
                [score_grid, eff_grid],
                ["Final KE (J)", "Efficiency (%)"],
                ["YlOrRd", "GnBu"]):
            im = ax.imshow(grid, aspect="auto", origin="lower", cmap=cmap,
                           extent=[kp_vals[0], kp_vals[-1], kd_vals[0], kd_vals[-1]])
            plt.colorbar(im, ax=ax)
            ax.scatter([best_kp], [best_kd], c="white", s=80, marker="*", zorder=5)
            ax.set(xlabel="KP", ylabel="KD", title=title)

        p = "/tmp/fr_v2_optimizer.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  {p}")

        # ── Plot 5: Per-chamber torque share (at steady state) ────────────────
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#080c10")

        # Compute per-chamber thermal torque waveform
        P_peak_ref = flash_pressure(M_INJ, T_WALL)
        spacing_rad = TWO_PI / N_CHAMBERS
        pw_rad      = PULSE_WIDTH_DEG * DEG2RAD
        angle_steps = 360
        deg_ax = list(range(angle_steps))
        chamber_profiles = []
        for c in range(N_CHAMBERS):
            profile = []
            for s in range(angle_steps):
                theta = s * TWO_PI / angle_steps
                d = (theta - c * spacing_rad) % TWO_PI
                if d < pw_rad:
                    t = d / pw_rad
                    tau = P_peak_ref * (4*t*(1-t)*math.exp(-2*t)) * A_VANE * R_ROTOR
                else:
                    tau = 0.0
                profile.append(tau)
            chamber_profiles.append(profile)

        # Stacked area plot
        baseline_arr = [0.0] * angle_steps
        cmap_ch = plt.cm.plasma
        for c, profile in enumerate(chamber_profiles):
            top = [baseline_arr[i] + profile[i] for i in range(angle_steps)]
            ax.fill_between(deg_ax, baseline_arr, top,
                            alpha=0.7, label=f"Ch {c}",
                            color=cmap_ch(c / N_CHAMBERS))
            baseline_arr = top

        ax.set(xlabel="Rotor angle (°)", ylabel="Thermal torque (N·m)",
               title="PER-CHAMBER TORQUE SHARE — Stacked Profile",
               xlim=(0, 359))
        ax.legend(loc="upper right", framealpha=0.2, edgecolor="#1a3050",
                  ncol=3, fontsize=8)
        ax.grid(True)

        p = "/tmp/fr_v2_chambers.png"
        fig.savefig(p, dpi=140, bbox_inches="tight", facecolor="#080c10")
        plt.close(fig); print(f"  {p}")

    print("\nAll plots → /tmp/fr_v2_*.png")
    print("View in Blender: Image Editor → Open → /tmp/")
