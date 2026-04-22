"""
Flash-Reluctance Engine — Script 4: Analysis & Parameter Sweep
===============================================================
Run this in Blender's Scripting workspace OR as a plain Python script
outside Blender (no bpy required — pure math + matplotlib).

Produces four plots:
  1. Torque waveform over one revolution (thermal / EM / friction / net)
  2. Angular velocity vs time for three operating points
  3. EM phase offset sweep — how net torque changes with offset angle
  4. Chamber count sweep — torque ripple vs N_chambers

Saves figures to /tmp/fr_analysis_*.png
"""

import math
import os

# Try matplotlib — graceful fail if not installed in Blender's Python
try:
    import matplotlib
    matplotlib.use('Agg')   # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("matplotlib not available — printing numeric output only")

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
EM_PHASE_DEG    = 15.0

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0

H_VAP   = 2257e3
C_WATER = 4186.0
T_COLD  = 20.0
VOL_CH  = 5e-4


# ──────────────────────────────────────────────
# PHYSICS CORE
# ──────────────────────────────────────────────

def flash_pressure(m_inj, T_wall):
    Q = m_inj * (C_WATER * (T_wall - T_COLD) + H_VAP)
    return min((Q * 0.25) / VOL_CH, 8e6)


def thermal_torque_at(theta, N, pw_deg, P_peak):
    spacing = TWO_PI / N
    pw = pw_deg * DEG2RAD
    tau = 0.0
    for c in range(N):
        d = (theta - c * spacing) % TWO_PI
        if d < pw:
            t = d / pw
            tau += P_peak * (4*t*(1-t)*math.exp(-2*t)) * A_VANE * R_ROTOR
    return tau


def em_torque_at(theta, N, pw_deg, tau_em_pk, em_phase_deg):
    if tau_em_pk <= 0:
        return 0.0
    spacing = TWO_PI / N
    pw = pw_deg * DEG2RAD * 0.6
    offset = em_phase_deg * DEG2RAD
    tau = 0.0
    for c in range(N):
        d = (theta - (c * spacing + offset)) % TWO_PI
        if d < pw:
            tau += tau_em_pk * math.sin(math.pi * d / pw)
    return tau


def friction_at(omega):
    return K_DRAG * omega**2 * (1 if omega >= 0 else -1) + K_BEARING * omega


def simulate(T_wall=T_WALL, N=N_CHAMBERS, pw_deg=PULSE_WIDTH_DEG,
             tau_em=TAU_EM_PEAK, em_phase=EM_PHASE_DEG,
             duration=5.0, dt=0.001, omega0=0.1):
    """Run full Euler integration. Returns time, omega arrays."""
    P_peak = flash_pressure(M_INJ, T_wall)
    theta = 0.0
    omega = omega0
    steps = int(duration / dt)
    record_every = 10   # downsample for memory
    times, omegas = [], []
    for s in range(steps):
        tau_th = thermal_torque_at(theta, N, pw_deg, P_peak)
        tau_em_ = em_torque_at(theta, N, pw_deg, tau_em, em_phase)
        tau_fr = friction_at(omega)
        alpha = (tau_th + tau_em_ - tau_fr) / I_ROTOR
        omega = max(omega + alpha * dt, 0.0)
        theta = (theta + omega * dt) % TWO_PI
        if s % record_every == 0:
            times.append(s * dt)
            omegas.append(omega)
    return times, omegas


# ──────────────────────────────────────────────
# PLOT 1: Torque waveform — one revolution
# ──────────────────────────────────────────────

def compute_torque_waveform(N=N_CHAMBERS, pw_deg=PULSE_WIDTH_DEG,
                             T_wall=T_WALL, tau_em=TAU_EM_PEAK,
                             em_phase=EM_PHASE_DEG, omega_ref=20.0,
                             steps=720):
    P_peak = flash_pressure(M_INJ, T_wall)
    angles = [s * TWO_PI / steps for s in range(steps)]
    th_arr, em_arr, fr_arr, net_arr = [], [], [], []
    for a in angles:
        t = thermal_torque_at(a, N, pw_deg, P_peak)
        e = em_torque_at(a, N, pw_deg, tau_em, em_phase)
        f = friction_at(omega_ref)
        th_arr.append(t); em_arr.append(e)
        fr_arr.append(f); net_arr.append(t + e - f)
    return angles, th_arr, em_arr, fr_arr, net_arr

# ──────────────────────────────────────────────
# NUMERIC SUMMARY (always printed)
# ──────────────────────────────────────────────

angles, th, em, fr, net = compute_torque_waveform()

avg_th  = sum(th) / len(th)
avg_em  = sum(em) / len(em)
avg_fr  = sum(fr) / len(fr)
avg_net = sum(net) / len(net)
max_net = max(net)
min_net = min(net)
ripple  = (max_net - min_net) / (avg_net if avg_net > 0 else 1)

print("=" * 60)
print("FR ENGINE — TORQUE ANALYSIS")
print(f"  N_chambers      : {N_CHAMBERS}")
print(f"  T_wall          : {T_WALL} °C")
print(f"  P_peak (flash)  : {flash_pressure(M_INJ, T_WALL)/1e6:.2f} MPa")
print(f"  τ_thermal avg   : {avg_th:.1f} N·m")
print(f"  τ_EM avg        : {avg_em:.1f} N·m")
print(f"  τ_friction      : {avg_fr:.1f} N·m")
print(f"  τ_net avg       : {avg_net:.1f} N·m")
print(f"  τ_net max       : {max_net:.1f} N·m")
print(f"  τ_net min       : {min_net:.1f} N·m")
print(f"  Torque ripple   : {ripple*100:.1f}%")
print()

# Simulate three operating points
print("  Operating point sweeps:")
for T in [250, 400, 600]:
    t_arr, w_arr = simulate(T_wall=T, duration=5.0)
    final_rpm = w_arr[-1] * 60 / TWO_PI
    print(f"    T={T}°C  →  terminal ω={w_arr[-1]:.1f} rad/s  ({final_rpm:.0f} RPM)")

# EM phase sweep
print()
print("  EM phase offset sweep (avg net torque):")
for ph in range(-20, 61, 10):
    _, th_, em_, fr_, net_ = compute_torque_waveform(em_phase=ph)
    avg_n = sum(net_) / len(net_)
    print(f"    phase={ph:+3d}°  →  τ_net avg = {avg_n:.2f} N·m")

print("=" * 60)

# ──────────────────────────────────────────────
# MATPLOTLIB PLOTS
# ──────────────────────────────────────────────

if not HAS_MPL:
    print("Install matplotlib to generate plots:")
    print("  (in Blender terminal)  import subprocess; subprocess.run(['pip','install','matplotlib'])")
else:
    STYLE = {
        "figure.facecolor":  "#080c10",
        "axes.facecolor":    "#0d1520",
        "axes.edgecolor":    "#1a3050",
        "axes.labelcolor":   "#c8d8e8",
        "axes.titlecolor":   "#ffffff",
        "xtick.color":       "#5a7a9a",
        "ytick.color":       "#5a7a9a",
        "grid.color":        "#1a3050",
        "grid.linestyle":    "--",
        "grid.linewidth":    0.5,
        "text.color":        "#c8d8e8",
        "font.family":       "monospace",
        "lines.linewidth":   1.8,
    }

    THERMAL_C = "#ff6b35"
    EM_C      = "#00d4ff"
    FRIC_C    = "#ff3e6c"
    NET_C     = "#a8ff3e"
    OMEGA_C   = "#f0e060"

    with plt.rc_context(STYLE):

        # ── Figure 1: Torque waveform ────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#080c10")

        deg_x = [a * 180 / math.pi for a in angles]
        ax.plot(deg_x, th,  color=THERMAL_C, label="τ_thermal", linewidth=2)
        ax.plot(deg_x, em,  color=EM_C,      label="τ_EM",      linewidth=1.5, linestyle="--")
        ax.plot(deg_x, fr,  color=FRIC_C,    label="τ_friction",linewidth=1, linestyle=":")
        ax.plot(deg_x, net, color=NET_C,     label="τ_net",     linewidth=2.5)
        ax.axhline(0, color="#2a4060", linewidth=1)
        ax.axhline(avg_net, color=NET_C, linewidth=1, alpha=0.4, linestyle="-.")

        ax.set_xlabel("Rotor angle (degrees)")
        ax.set_ylabel("Torque (N·m)")
        ax.set_title(f"FLASH-RELUCTANCE ENGINE — Torque Waveform\n"
                     f"N={N_CHAMBERS} chambers, T_wall={T_WALL}°C, τ_EM_peak={TAU_EM_PEAK} N·m",
                     pad=12)
        ax.set_xlim(0, 360)
        ax.legend(loc="upper right", framealpha=0.2, edgecolor="#1a3050")
        ax.grid(True)
        ax.text(2, avg_net + 0.5, f"avg τ_net = {avg_net:.1f} N·m", color=NET_C, fontsize=8)

        out1 = "/tmp/fr_analysis_torque.png"
        fig.savefig(out1, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  Saved: {out1}")

        # ── Figure 2: ω vs time, three operating points ───────────────────────
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#080c10")

        colors_op = ["#ff6b35", "#a8ff3e", "#00d4ff"]
        for color, T in zip(colors_op, [250, 400, 600]):
            t_arr, w_arr = simulate(T_wall=T, duration=5.0)
            rpm_arr = [w * 60 / TWO_PI for w in w_arr]
            ax.plot(t_arr, rpm_arr, color=color, label=f"T_wall = {T}°C")

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Angular velocity (RPM)")
        ax.set_title("FLASH-RELUCTANCE ENGINE — Speed Ramp-Up\nEuler integration, dt = 1ms")
        ax.legend(loc="lower right", framealpha=0.2, edgecolor="#1a3050")
        ax.grid(True)
        ax.set_xlim(0, 5)

        out2 = "/tmp/fr_analysis_omega.png"
        fig.savefig(out2, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  Saved: {out2}")

        # ── Figure 3: EM phase sweep ───────────────────────────────────────────
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor("#080c10")

        phases = list(range(-30, 70, 2))
        avg_nets = []
        for ph in phases:
            _, th_, em_, fr_, net_ = compute_torque_waveform(em_phase=ph)
            avg_nets.append(sum(net_) / len(net_))

        best_ph = phases[avg_nets.index(max(avg_nets))]
        ax.plot(phases, avg_nets, color=EM_C, linewidth=2)
        ax.axvline(best_ph, color=NET_C, linewidth=1, linestyle="--",
                   label=f"Optimal offset = {best_ph}°")
        ax.axvline(EM_PHASE_DEG, color=THERMAL_C, linewidth=1, linestyle=":",
                   label=f"Current = {EM_PHASE_DEG}°")

        ax.set_xlabel("EM phase offset (degrees)")
        ax.set_ylabel("Average net torque (N·m)")
        ax.set_title("EM PHASE SWEEP — Optimal Coupling Angle")
        ax.legend(framealpha=0.2, edgecolor="#1a3050")
        ax.grid(True)

        out3 = "/tmp/fr_analysis_phase_sweep.png"
        fig.savefig(out3, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  Saved: {out3}")

        # ── Figure 4: Chamber count sweep ─────────────────────────────────────
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        fig.patch.set_facecolor("#080c10")

        chamber_counts = list(range(2, 13))
        avg_net_by_N   = []
        ripple_by_N    = []

        for N in chamber_counts:
            _, th_, em_, fr_, net_ = compute_torque_waveform(N=N)
            avg_n = sum(net_) / len(net_)
            rip = (max(net_) - min(net_)) / (avg_n if avg_n > 0 else 1)
            avg_net_by_N.append(avg_n)
            ripple_by_N.append(rip * 100)

        ax1.plot(chamber_counts, avg_net_by_N, color=NET_C, marker="o", markersize=5)
        ax1.axvline(N_CHAMBERS, color=THERMAL_C, linewidth=1, linestyle="--",
                    label=f"Current N={N_CHAMBERS}")
        ax1.set_xlabel("Number of chambers")
        ax1.set_ylabel("Average net torque (N·m)")
        ax1.set_title("CHAMBER COUNT vs AVG TORQUE")
        ax1.legend(framealpha=0.2, edgecolor="#1a3050")
        ax1.grid(True)

        ax2.plot(chamber_counts, ripple_by_N, color=FRIC_C, marker="o", markersize=5)
        ax2.axvline(N_CHAMBERS, color=THERMAL_C, linewidth=1, linestyle="--",
                    label=f"Current N={N_CHAMBERS}")
        ax2.set_xlabel("Number of chambers")
        ax2.set_ylabel("Torque ripple (%)")
        ax2.set_title("CHAMBER COUNT vs TORQUE RIPPLE")
        ax2.legend(framealpha=0.2, edgecolor="#1a3050")
        ax2.grid(True)

        out4 = "/tmp/fr_analysis_chamber_sweep.png"
        fig.savefig(out4, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        print(f"  Saved: {out4}")

    print()
    print("All plots saved to /tmp/")
    print("Open from Blender: Image Editor → Open → /tmp/fr_analysis_*.png")
