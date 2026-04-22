"""
Flash-Reluctance Engine — Script 3 (v2): Closed-Loop Animation
===============================================================
Upgrades from v1:
  - Open-loop phase EM → PD torque controller
  - Phase-driven coil emission → torque-magnitude emission
  - Per-chamber spatial coil activation (not global τ_em)
  - Nozzle glow tied to dτ_thermal/dt (real injection spike)
  - Energy accounting: Joules in vs rotational KE out

Run AFTER fr_01_rotor_geometry.py and fr_02_thermal_system.py.
"""

import bpy
import math
import csv

# ──────────────────────────────────────────────
# PARAMETERS
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
FLYWHEEL_THICK  = 0.025

# Thermal physics
T_WALL          = 400.0
M_INJ           = 0.002
I_ROTOR         = 0.80
K_DRAG          = 0.04
K_BEARING       = 0.02
A_VANE          = 0.020

# EM hardware limits
TAU_EM_PEAK     = 12.0      # N·m  absolute cap (coil saturation limit)

# ── PD Torque Controller ──────────────────────
USE_TORQUE_CONTROL = True
TAU_TARGET      = 25.0      # N·m  desired net torque
KP_EM           = 0.8       # proportional gain
KD_EM           = 0.2       # derivative damping

# Integration
DT              = 0.001
SIM_DURATION    = 5.0
FPS             = 24
FRAMES_TOTAL    = int(SIM_DURATION * FPS)
ANIM_START      = 1
ANIM_END        = ANIM_START + FRAMES_TOTAL - 1

# ──────────────────────────────────────────────
# PHYSICS
# ──────────────────────────────────────────────

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0

H_VAP   = 2257e3
C_WATER = 4186.0
T_COLD  = 20.0
VOL_CH  = 5e-4


def flash_pressure(m_inj, T_wall):
    Q = m_inj * (C_WATER * (T_wall - T_COLD) + H_VAP)
    return min((Q * 0.25) / VOL_CH, 8e6)


def thermal_torque_total(theta, P_peak):
    """Aggregate thermal torque across all chambers."""
    spacing = TWO_PI / N_CHAMBERS
    pw = PULSE_WIDTH_DEG * DEG2RAD
    tau = 0.0
    for c in range(N_CHAMBERS):
        d = (theta - c * spacing) % TWO_PI
        if d < pw:
            t = d / pw
            tau += P_peak * (4*t*(1-t)*math.exp(-2*t)) * A_VANE * R_ROTOR
    return tau


def thermal_torque_per_chamber(theta, P_peak):
    """Return list of per-chamber thermal torque contributions."""
    spacing = TWO_PI / N_CHAMBERS
    pw = PULSE_WIDTH_DEG * DEG2RAD
    contributions = []
    for c in range(N_CHAMBERS):
        d = (theta - c * spacing) % TWO_PI
        if d < pw:
            t = d / pw
            tau_c = P_peak * (4*t*(1-t)*math.exp(-2*t)) * A_VANE * R_ROTOR
        else:
            tau_c = 0.0
        contributions.append(tau_c)
    return contributions


def friction_torque(omega):
    return K_DRAG * omega**2 * (1 if omega >= 0 else -1) + K_BEARING * omega


# PD controller — global state persists across integration steps
_prev_tau_base = 0.0

def em_torque_control(tau_th, tau_fr):
    """
    PD controller: computes required EM torque to approach TAU_TARGET.
    Only assists (never opposes). Capped at TAU_EM_PEAK.
    """
    global _prev_tau_base

    if not USE_TORQUE_CONTROL or TAU_EM_PEAK <= 0:
        return 0.0

    tau_base = tau_th - tau_fr
    error    = TAU_TARGET - tau_base
    d_tau    = tau_base - _prev_tau_base
    _prev_tau_base = tau_base

    tau_em = KP_EM * error - KD_EM * d_tau
    return min(max(tau_em, 0.0), TAU_EM_PEAK)


def em_torque_per_chamber(tau_em_total, tau_th_per_chamber, tau_th_total):
    """
    Distribute total EM torque spatially across chambers,
    weighted by each chamber's thermal contribution.
    Chambers with higher thermal load get proportionally more EM assist.
    """
    if tau_th_total < 1e-6:
        # Uniform distribution if no thermal signal
        return [tau_em_total / N_CHAMBERS] * N_CHAMBERS
    return [(t / tau_th_total) * tau_em_total for t in tau_th_per_chamber]


# ──────────────────────────────────────────────
# RUN SIMULATION
# ──────────────────────────────────────────────

print("Running closed-loop physics simulation ...")

global _prev_tau_base
_prev_tau_base = 0.0

P_peak = flash_pressure(M_INJ, T_WALL)
theta  = 0.0
omega  = 0.1
sim_t  = 0.0

steps_per_frame = max(1, int((1.0 / FPS) / DT))

# Energy accounting
E_thermal_total = 0.0    # Joules delivered by flash expansion
E_em_total      = 0.0    # Joules delivered by EM coils
E_friction_loss = 0.0    # Joules lost to friction

frame_states = []

for frame in range(FRAMES_TOTAL):
    # Snapshot at frame start
    tau_th_total   = thermal_torque_total(theta, P_peak)
    tau_th_per_ch  = thermal_torque_per_chamber(theta, P_peak)
    tau_fr         = friction_torque(omega)
    tau_em         = em_torque_control(tau_th_total, tau_fr)
    tau_em_per_ch  = em_torque_per_chamber(tau_em, tau_th_per_ch, tau_th_total)
    tau_net        = tau_th_total + tau_em - tau_fr

    frame_states.append({
        "frame":        frame + ANIM_START,
        "theta":        theta,
        "omega":        omega,
        "tau_th":       tau_th_total,
        "tau_th_ch":    list(tau_th_per_ch),   # per-chamber list
        "tau_em":       tau_em,
        "tau_em_ch":    list(tau_em_per_ch),    # per-chamber list
        "tau_fr":       tau_fr,
        "tau_net":      tau_net,
        "E_th_cum":     E_thermal_total,
        "E_em_cum":     E_em_total,
        "E_fr_cum":     E_friction_loss,
        "KE":           0.5 * I_ROTOR * omega**2,
    })

    # Micro-integration
    for _ in range(steps_per_frame):
        tau_th_i  = thermal_torque_total(theta, P_peak)
        tau_fr_i  = friction_torque(omega)
        tau_em_i  = em_torque_control(tau_th_i, tau_fr_i)
        tau_net_i = tau_th_i + tau_em_i - tau_fr_i

        alpha  = tau_net_i / I_ROTOR
        omega  = max(omega + alpha * DT, 0.0)
        dtheta = omega * DT
        theta  = (theta + dtheta) % TWO_PI

        # Accumulate energy (work = torque × angular displacement)
        E_thermal_total += tau_th_i  * dtheta
        E_em_total      += tau_em_i  * dtheta
        E_friction_loss += tau_fr_i  * dtheta

        sim_t += DT

final_omega = frame_states[-1]["omega"]
final_rpm   = final_omega * 60 / TWO_PI
final_KE    = 0.5 * I_ROTOR * final_omega**2

print(f"  Terminal ω    = {final_omega:.2f} rad/s  ({final_rpm:.0f} RPM)")
print(f"  Final KE      = {final_KE:.1f} J")
print(f"  E_thermal in  = {E_thermal_total:.1f} J")
print(f"  E_EM in       = {E_em_total:.1f} J")
print(f"  E_friction    = {E_friction_loss:.1f} J")
efficiency = final_KE / max(E_thermal_total + E_em_total, 1e-6) * 100
print(f"  System eff    = {efficiency:.1f}%")

# ──────────────────────────────────────────────
# CSV EXPORT
# ──────────────────────────────────────────────

csv_path = "/tmp/fr_torque_log_v2.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame","theta","omega","tau_th","tau_em","tau_fr","tau_net",
                     "E_th_cum","E_em_cum","E_fr_cum","KE"])
    for s in frame_states:
        writer.writerow([s["frame"], f"{s['theta']:.4f}", f"{s['omega']:.4f}",
                         f"{s['tau_th']:.3f}", f"{s['tau_em']:.3f}",
                         f"{s['tau_fr']:.3f}", f"{s['tau_net']:.3f}",
                         f"{s['E_th_cum']:.2f}", f"{s['E_em_cum']:.2f}",
                         f"{s['E_fr_cum']:.2f}", f"{s['KE']:.2f}"])
print(f"  CSV written: {csv_path}")

# ──────────────────────────────────────────────
# BLENDER SETUP
# ──────────────────────────────────────────────

bpy.context.scene.frame_start = ANIM_START
bpy.context.scene.frame_end   = ANIM_END
bpy.context.scene.render.fps  = FPS

# Gather objects
rotor_names = (["FR_Flywheel", "FR_Hub", "FR_ShaftCollar", "FR_Shaft"] +
               [f"FR_Vane_{i:02d}" for i in range(N_CHAMBERS)])
rotor_objects = [bpy.data.objects[n] for n in rotor_names if n in bpy.data.objects]

stator_coils = [(i, bpy.data.objects[f"FR_StatorCoil_{i:02d}"])
                for i in range(N_CHAMBERS)
                if f"FR_StatorCoil_{i:02d}" in bpy.data.objects]

nozzles = [(i, bpy.data.objects[f"FR_Nozzle_{i:02d}"])
           for i in range(N_CHAMBERS)
           if f"FR_Nozzle_{i:02d}" in bpy.data.objects]

for obj in rotor_objects:
    obj.animation_data_clear()


def set_emission(mat, strength, frame):
    nodes = mat.node_tree.nodes
    bsdf  = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Emission Strength"].keyframe_insert(
            data_path='default_value', frame=frame)


def set_emission_color(mat, r, g, b, frame):
    nodes = mat.node_tree.nodes
    bsdf  = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (r, g, b, 1.0)
        bsdf.inputs["Emission Color"].keyframe_insert(
            data_path='default_value', frame=frame)


# ──────────────────────────────────────────────
# NORMALIZATION SCALES
# ──────────────────────────────────────────────

max_tau_th = max(s["tau_th"] for s in frame_states) + 1e-6
max_tau_em = max(s["tau_em"] for s in frame_states) + 1e-6
max_d_tau  = 1e-6   # will grow below

# Pre-compute thermal derivatives for nozzle flash
d_taus = [0.0]
for i in range(1, len(frame_states)):
    d = frame_states[i]["tau_th"] - frame_states[i-1]["tau_th"]
    d_taus.append(max(d, 0.0))
    if d > max_d_tau:
        max_d_tau = d

print(f"\n  max τ_thermal = {max_tau_th:.1f} N·m")
print(f"  max τ_EM      = {max_tau_em:.1f} N·m")
print(f"  max dτ/dt     = {max_d_tau:.2f} N·m/frame")

# ──────────────────────────────────────────────
# ROTOR ROTATION KEYFRAMES
# ──────────────────────────────────────────────

print("\n  Keying rotor rotation ...")

cumulative_theta = 0.0
prev_theta = frame_states[0]["theta"]

for state in frame_states:
    dt_theta = state["theta"] - prev_theta
    if dt_theta < -math.pi:   dt_theta += TWO_PI
    elif dt_theta > math.pi:  dt_theta -= TWO_PI
    cumulative_theta += dt_theta
    prev_theta = state["theta"]

    for obj in rotor_objects:
        obj.rotation_euler.z = cumulative_theta
        obj.keyframe_insert(data_path="rotation_euler", index=2,
                            frame=state["frame"])

for obj in rotor_objects:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

print("  Rotor keyframes: done")

# ──────────────────────────────────────────────
# STATOR COIL EMISSION — PER-CHAMBER TORQUE-DRIVEN
# ──────────────────────────────────────────────
#
# Each coil i responds to:
#   - tau_em_ch[i]  → blue brightness (EM demand)
#   - tau_th_ch[i]  → orange tint (thermal activity in that chamber)
#
# Color blend: orange (thermal) ← → blue (EM)
# Brightness: sum of both contributions, normalized

print("  Keying stator coil emission (per-chamber, torque-driven) ...")

# Per-chamber normalization
max_tau_th_ch = [max(s["tau_th_ch"][i] for s in frame_states) + 1e-6
                 for i in range(N_CHAMBERS)]
max_tau_em_ch = [max(s["tau_em_ch"][i] for s in frame_states) + 1e-6
                 for i in range(N_CHAMBERS)]

for state in frame_states:
    frame_num = state["frame"]

    for chamber_idx, coil_obj in stator_coils:
        if not coil_obj.data.materials:
            continue

        mat = coil_obj.data.materials[0]
        mat.use_nodes = True

        th_raw = state["tau_th_ch"][chamber_idx]
        em_raw = state["tau_em_ch"][chamber_idx]

        th_norm = th_raw / max_tau_th_ch[chamber_idx]
        em_norm = em_raw / max_tau_em_ch[chamber_idx]

        # Color: R = orange contribution, B = EM contribution
        # G blends between them
        r = th_norm * 0.9 + em_norm * 0.05
        g = th_norm * 0.35 + em_norm * 0.55
        b = em_norm * 0.95 + th_norm * 0.05

        # Brightness: EM is primary visual signal; thermal adds warmth
        strength = em_norm * 8.0 + th_norm * 3.0

        # At idle (both low) → very dim cool blue ambient
        if strength < 0.1:
            r, g, b = 0.0, 0.15, 0.4
            strength = 0.15

        set_emission_color(mat, r, g, b, frame_num)
        set_emission(mat, strength, frame_num)

print("  Stator coil keyframes: done")

# ──────────────────────────────────────────────
# NOZZLE FLASH — THERMAL DERIVATIVE (dτ/dt)
# ──────────────────────────────────────────────
#
# Nozzle glows when thermal torque is *rising* — i.e., at the moment
# of flash-steam injection, not throughout the expansion arc.

print("  Keying nozzle flash (dτ_thermal/dt) ...")

for idx, state in enumerate(frame_states):
    frame_num = state["frame"]
    d_tau_norm = d_taus[idx] / max_d_tau

    for chamber_idx, nozzle_obj in nozzles:
        if not nozzle_obj.data.materials:
            continue

        mat = nozzle_obj.data.materials[0]
        mat.use_nodes = True

        # Only the chamber whose thermal torque is rising fires its nozzle
        # Approximate: use global d_tau but gate by chamber activity
        th_ch = state["tau_th_ch"][chamber_idx]
        active = th_ch / max_tau_th_ch[chamber_idx] > 0.1

        if active and d_taus[idx] > 0:
            # Sharp cold-blue flash — water injection aesthetic
            strength = d_tau_norm * 6.0
            set_emission_color(mat, 0.4, 0.8, 1.0, frame_num)
        else:
            strength = 0.0
            set_emission_color(mat, 0.0, 0.2, 0.5, frame_num)

        set_emission(mat, strength, frame_num)

print("  Nozzle keyframes: done")

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────

print("\n" + "=" * 60)
print("FR Engine v2 — Closed-Loop Animation: COMPLETE")
print(f"  Frames          : {ANIM_START} → {ANIM_END}  ({FPS} fps, {SIM_DURATION}s)")
print(f"  Terminal RPM    : {final_rpm:.0f}")
print(f"  TAU_TARGET      : {TAU_TARGET} N·m")
print(f"  KP={KP_EM}  KD={KD_EM}")
print(f"  Thermal energy  : {E_thermal_total:.1f} J")
print(f"  EM energy       : {E_em_total:.1f} J")
print(f"  Friction loss   : {E_friction_loss:.1f} J")
print(f"  Final KE        : {final_KE:.1f} J")
print(f"  System eff      : {efficiency:.1f}%")
print(f"  CSV             : {csv_path}")
print()
print("  Coils  : per-chamber torque-driven (orange=thermal / blue=EM)")
print("  Nozzles: flash at dτ_thermal/dt spike (injection moment only)")
print()
print("  Press SPACE to play. Render with Cycles + Bloom for glow.")
print("=" * 60)
