"""
Flash-Reluctance Engine — Script 3: Physics-Driven Animation
=============================================================
Run AFTER scripts 01 and 02.

This script:
  1. Re-runs the same Euler integrator from the HTML simulator in Python
  2. Converts the omega/theta time-series into Blender keyframes
  3. Animates the rotor (FR_Flywheel + FR_Hub + all vanes)
  4. Drives stator coil emission intensity from the thermal/EM phase state
  5. Outputs a per-frame torque CSV to /tmp/fr_torque_log.csv

The animation physically encodes your design:
  - Rotor accelerates from rest, reaches terminal omega
  - Coils flash orange (thermal) and blue (EM) in phase sequence
  - You can scrub the timeline and see exactly which chamber is active

PARAMETERS — keep in sync with scripts 01 and 02
"""

import bpy
import math
import csv
import os

# ──────────────────────────────────────────────
# SIMULATION PARAMETERS
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
FLYWHEEL_THICK  = 0.025

# Physics
T_WALL          = 400.0     # °C  wall temperature
M_INJ           = 0.002     # kg  water per injection
I_ROTOR         = 0.80      # kg·m²  moment of inertia
K_DRAG          = 0.04      # viscous drag coefficient
K_BEARING       = 0.02      # bearing friction coefficient
A_VANE          = 0.020     # m²  vane effective area
TAU_EM_PEAK     = 12.0      # N·m  peak EM torque (set 0 to disable)
EM_PHASE_DEG    = 15.0      # °  EM phase offset ahead of injection

# Integration
DT              = 0.001     # s  time step
SIM_DURATION    = 4.0       # s  total simulation time
FPS             = 24        # Blender frame rate
FRAMES_TOTAL    = int(SIM_DURATION * FPS)

# Animation output
ANIM_START      = 1
ANIM_END        = ANIM_START + FRAMES_TOTAL - 1

# ──────────────────────────────────────────────
# PHYSICS FUNCTIONS  (identical to HTML sim)
# ──────────────────────────────────────────────

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0

H_VAP   = 2257e3    # J/kg
C_WATER = 4186.0    # J/(kg·K)
T_COLD  = 20.0      # °C
VOL_CH  = 5e-4      # m³


def flash_pressure(m_inj, T_wall):
    Q = m_inj * (C_WATER * (T_wall - T_COLD) + H_VAP)
    eff = 0.25
    P = (Q * eff) / VOL_CH
    return min(P, 8e6)


def thermal_torque(theta, P_peak):
    spacing = TWO_PI / N_CHAMBERS
    pw = PULSE_WIDTH_DEG * DEG2RAD
    tau = 0.0
    for c in range(N_CHAMBERS):
        inj_angle = c * spacing
        delta = (theta - inj_angle) % TWO_PI
        if delta < pw:
            t = delta / pw
            shape = 4 * t * (1 - t) * math.exp(-2 * t)
            tau += P_peak * shape * A_VANE * R_ROTOR
    return tau


def em_torque(theta):
    if TAU_EM_PEAK <= 0:
        return 0.0
    spacing = TWO_PI / N_CHAMBERS
    pw = PULSE_WIDTH_DEG * DEG2RAD * 0.6
    offset = EM_PHASE_DEG * DEG2RAD
    tau = 0.0
    for c in range(N_CHAMBERS):
        trigger = c * spacing + offset
        delta = (theta - trigger) % TWO_PI
        if delta < pw:
            tau += TAU_EM_PEAK * math.sin(math.pi * delta / pw)
    return tau


def friction_torque(omega):
    return K_DRAG * omega * omega * (1 if omega >= 0 else -1) + K_BEARING * omega


# ──────────────────────────────────────────────
# RUN SIMULATION — build per-frame state table
# ──────────────────────────────────────────────

print("Running physics simulation ...")

theta = 0.0
omega = 0.1     # seed
sim_t = 0.0

# We want one state snapshot per Blender frame
steps_per_frame = int((1.0 / FPS) / DT)   # e.g. 24fps, 1ms dt → 41 steps/frame

P_peak = flash_pressure(M_INJ, T_WALL)

frame_states = []   # list of (frame, theta, omega, tau_th, tau_em, tau_fr, tau_net)

for frame in range(FRAMES_TOTAL):
    # Record state at start of frame
    tau_th = thermal_torque(theta, P_peak)
    tau_em = em_torque(theta)
    tau_fr = friction_torque(omega)
    tau_net = tau_th + tau_em - tau_fr
    frame_states.append({
        "frame":   frame + ANIM_START,
        "theta":   theta,
        "omega":   omega,
        "tau_th":  tau_th,
        "tau_em":  tau_em,
        "tau_fr":  tau_fr,
        "tau_net": tau_net,
    })

    # Integrate steps_per_frame micro-steps
    for _ in range(steps_per_frame):
        tau_th_i  = thermal_torque(theta, P_peak)
        tau_em_i  = em_torque(theta)
        tau_fr_i  = friction_torque(omega)
        tau_net_i = tau_th_i + tau_em_i - tau_fr_i
        alpha = tau_net_i / I_ROTOR
        omega = max(omega + alpha * DT, 0.0)
        theta = (theta + omega * DT) % TWO_PI
        sim_t += DT

final_rpm = frame_states[-1]["omega"] * 60 / TWO_PI
print(f"  Simulation done. Terminal omega = {frame_states[-1]['omega']:.2f} rad/s  ({final_rpm:.0f} RPM)")


# ──────────────────────────────────────────────
# EXPORT CSV LOG
# ──────────────────────────────────────────────

csv_path = "/tmp/fr_torque_log.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["frame","theta","omega","tau_th","tau_em","tau_fr","tau_net"])
    writer.writeheader()
    writer.writerows(frame_states)
print(f"  Torque log written: {csv_path}")


# ──────────────────────────────────────────────
# APPLY KEYFRAMES TO BLENDER OBJECTS
# ──────────────────────────────────────────────

bpy.context.scene.frame_start = ANIM_START
bpy.context.scene.frame_end   = ANIM_END
bpy.context.scene.render.fps  = FPS

# Collect rotor objects (everything that rotates with the disc)
rotor_names = ["FR_Flywheel", "FR_Hub", "FR_ShaftCollar"]
rotor_names += [f"FR_Vane_{i:02d}" for i in range(N_CHAMBERS)]

rotor_objects = []
for name in rotor_names:
    if name in bpy.data.objects:
        rotor_objects.append(bpy.data.objects[name])

# Shaft rotates too
if "FR_Shaft" in bpy.data.objects:
    rotor_objects.append(bpy.data.objects["FR_Shaft"])

# Stator coil objects for emission animation
stator_coils = []
for i in range(N_CHAMBERS):
    name = f"FR_StatorCoil_{i:02d}"
    if name in bpy.data.objects:
        stator_coils.append((i, bpy.data.objects[name]))

# Nozzles for blue flash
nozzles = []
for i in range(N_CHAMBERS):
    name = f"FR_Nozzle_{i:02d}"
    if name in bpy.data.objects:
        nozzles.append((i, bpy.data.objects[name]))

print(f"  Animating {len(rotor_objects)} rotor objects ...")
print(f"  Animating {len(stator_coils)} stator coils ...")

# Clear existing animation data on rotor objects
for obj in rotor_objects:
    obj.animation_data_clear()

for _, obj in stator_coils + nozzles:
    # Ensure material has emission node we can keyframe
    if obj.data.materials:
        mat = obj.data.materials[0]
        mat.use_nodes = True


def set_emission(mat, strength, frame):
    """Keyframe the emission strength on a material's Principled BSDF."""
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Emission Strength"].keyframe_insert(
        data_path='default_value', frame=frame
    )


# Determine active chamber for each frame
def active_chambers_at(theta):
    """Return dict: chamber_index -> (thermal_frac, em_frac)"""
    spacing  = TWO_PI / N_CHAMBERS
    pw_th    = PULSE_WIDTH_DEG * DEG2RAD
    pw_em    = pw_th * 0.6
    em_off   = EM_PHASE_DEG * DEG2RAD
    result   = {}
    for c in range(N_CHAMBERS):
        th_delta = (theta - c * spacing) % TWO_PI
        em_delta = (theta - (c * spacing + em_off)) % TWO_PI
        th_frac = (1 - th_delta / pw_th) if th_delta < pw_th else 0.0
        em_frac = math.sin(math.pi * em_delta / pw_em) if em_delta < pw_em else 0.0
        if th_frac > 0 or em_frac > 0:
            result[c] = (th_frac, max(em_frac, 0))
    return result


# ── Keyframe rotor rotation (Z axis) ────────────────────────────────────────
# We accumulate total angle (not wrapped) for clean rotation keyframing
cumulative_theta = 0.0
prev_theta = frame_states[0]["theta"]

for state in frame_states:
    frame_num = state["frame"]

    # Unwrap theta to avoid jumps at 2π boundary
    dt_theta = state["theta"] - prev_theta
    if dt_theta < -math.pi:
        dt_theta += TWO_PI
    elif dt_theta > math.pi:
        dt_theta -= TWO_PI
    cumulative_theta += dt_theta
    prev_theta = state["theta"]

    for obj in rotor_objects:
        obj.rotation_euler.z = cumulative_theta
        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame_num)

print("  Rotor rotation keyframes: done")

# ── Keyframe stator coil emission ────────────────────────────────────────────
# Thermal active = orange glow; EM active = blue glow; both = white

for state in frame_states:
    frame_num = state["frame"]
    active = active_chambers_at(state["theta"])

    for chamber_idx, coil_obj in stator_coils:
        if not coil_obj.data.materials:
            continue
        mat = coil_obj.data.materials[0]
        if chamber_idx in active:
            th_f, em_f = active[chamber_idx]
            # Emission strength: thermal drives orange, EM drives blue
            strength = max(th_f, em_f) * 6.0
            # Modulate base color toward orange if thermal dominant
            nodes = mat.node_tree.nodes
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                if th_f > em_f:
                    bsdf.inputs["Emission Color"].default_value = (1.0, 0.35, 0.0, 1.0)
                else:
                    bsdf.inputs["Emission Color"].default_value = (0.0, 0.6, 1.0, 1.0)
                bsdf.inputs["Emission Color"].keyframe_insert(
                    data_path='default_value', frame=frame_num)
            set_emission(mat, strength, frame_num)
        else:
            set_emission(mat, 0.2, frame_num)

print("  Stator emission keyframes: done")

# ── Keyframe nozzle flash ─────────────────────────────────────────────────────
# Nozzle glows briefly at injection moment (peak of thermal pulse)

for state in frame_states:
    frame_num = state["frame"]
    active = active_chambers_at(state["theta"])

    for chamber_idx, nozzle_obj in nozzles:
        if not nozzle_obj.data.materials:
            continue
        mat = nozzle_obj.data.materials[0]
        if chamber_idx in active:
            th_f, _ = active[chamber_idx]
            # Nozzle glows at injection peak (early in pulse)
            inj_strength = max(0, 4.0 * th_f * (1 - th_f) * math.exp(-2 * th_f)) * 5.0
            set_emission(mat, inj_strength, frame_num)
        else:
            set_emission(mat, 0.0, frame_num)

print("  Nozzle flash keyframes: done")

# ── Set interpolation to LINEAR for physics realism ─────────────────────────
# Default Blender keyframes use BEZIER which gives incorrect easing
for obj in rotor_objects:
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'LINEAR'

print("  Interpolation set to LINEAR")

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────
print("=" * 60)
print("FR Engine — Animation: COMPLETE")
print(f"  Frames       : {ANIM_START} → {ANIM_END}  ({FPS} fps)")
print(f"  Duration     : {SIM_DURATION:.1f} s")
print(f"  Terminal RPM : {final_rpm:.0f}")
print(f"  Steps/frame  : {steps_per_frame}")
print(f"  CSV log      : {csv_path}")
print()
print("  Press SPACE in Blender to play the animation.")
print("  Scrub the timeline to inspect individual frames.")
print("  Adjust T_WALL / TAU_EM_PEAK above and re-run")
print("  to compare different operating points.")
print("=" * 60)
