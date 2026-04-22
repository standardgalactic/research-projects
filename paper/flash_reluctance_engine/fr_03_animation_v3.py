"""
Flash-Reluctance Engine — Script 3 (v3): Thermodynamic Machine
===============================================================
Upgrades from v2:
  - Dynamic per-chamber wall temperature (T_wall_ch evolves each step)
  - Shared thermal core (chambers compete for heat from same reservoir)
  - ω-governed control (torque + speed objective, machine now regulates)
  - Load torque model (constant + proportional — machine does work)
  - Slope-based per-chamber EM distribution (predictive, not reactive)
  - Per-chamber nozzle derivative (true injection spike per chamber)
  - Energy accounting: thermal / EM / friction / load / KE
  - Conditional injection (skip cold chambers below threshold)

Run AFTER fr_01_rotor_geometry.py and fr_02_thermal_system.py.
"""

import bpy
import math
import csv
import os

# ──────────────────────────────────────────────
# GEOMETRY PARAMETERS
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
FLYWHEEL_THICK  = 0.025
A_VANE          = 0.020

# ──────────────────────────────────────────────
# MECHANICAL PARAMETERS
# ──────────────────────────────────────────────

I_ROTOR         = 0.80      # kg·m²
K_DRAG          = 0.04      # viscous drag
K_BEARING       = 0.02      # bearing friction

# Load model: τ_load = CONST_LOAD + K_LOAD × ω
CONST_LOAD      = 2.0       # N·m  constant resistance
K_LOAD          = 0.08      # N·m/(rad/s)  generator-like load

# ──────────────────────────────────────────────
# THERMAL PARAMETERS
# ──────────────────────────────────────────────

T_SOURCE        = 500.0     # °C  burner / central core temperature
T_AMBIENT       = 25.0      # °C
T_INJECT        = 20.0      # °C  injected water temperature
T_INJECT_MIN    = 200.0     # °C  minimum wall temp to allow injection

K_HEAT          = 200.0     # W/°C  heating rate (core → wall)
K_COOL          = 20.0      # W/°C  cooling rate (wall → ambient)
C_WALL          = 500.0     # J/°C  heat capacity per chamber wall

M_INJ           = 0.002     # kg/injection
H_VAP           = 2257e3    # J/kg
C_WATER         = 4186.0    # J/(kg·K)
VOL_CH          = 5e-4      # m³

# Shared core: total burner power is limited
# Each chamber draws from a shared reservoir
T_CORE_INIT     = 500.0     # °C  initial core temperature
C_CORE          = 8000.0    # J/°C  core heat capacity (large = slow depletion)
K_CORE_INPUT    = 400.0     # W/°C  external heat input to core (fuel/solar)
K_CORE_TO_WALL  = 200.0     # W/°C  conduction core→each wall

# ──────────────────────────────────────────────
# EM / CONTROL PARAMETERS
# ──────────────────────────────────────────────

TAU_EM_PEAK     = 12.0      # N·m  coil saturation limit
USE_TORQUE_CONTROL = True
TAU_TARGET      = 20.0      # N·m  desired net torque
OMEGA_TARGET    = 25.0      # rad/s  (~239 RPM) speed setpoint
KP_EM           = 0.8       # torque proportional gain
KD_EM           = 0.2       # torque derivative damping
K_OMEGA         = 0.5       # speed gain

# ──────────────────────────────────────────────
# INTEGRATION
# ──────────────────────────────────────────────

DT              = 0.001     # s
SIM_DURATION    = 8.0       # s  (longer — need time to reach thermal steady state)
FPS             = 24
FRAMES_TOTAL    = int(SIM_DURATION * FPS)
ANIM_START      = 1
ANIM_END        = ANIM_START + FRAMES_TOTAL - 1

# ──────────────────────────────────────────────
# DERIVED CONSTANTS
# ──────────────────────────────────────────────

TWO_PI  = 2 * math.pi
DEG2RAD = math.pi / 180.0
SPACING = TWO_PI / N_CHAMBERS
PW_RAD  = PULSE_WIDTH_DEG * DEG2RAD


# ──────────────────────────────────────────────
# PHYSICS FUNCTIONS
# ──────────────────────────────────────────────

def chamber_in_injection_phase(chamber_idx, theta):
    """True if rotor angle is in this chamber's expansion arc."""
    d = (theta - chamber_idx * SPACING) % TWO_PI
    return d < PW_RAD


def flash_pressure(m_inj, T_wall):
    """Pressure from flash-steam expansion at current wall temperature."""
    if T_wall <= T_INJECT:
        return 0.0
    Q = m_inj * (C_WATER * (T_wall - T_INJECT) + H_VAP)
    return min((Q * 0.25) / VOL_CH, 8e6)


def thermal_torque_per_chamber(theta, T_wall_ch):
    """Per-chamber thermal torque using individual wall temperatures."""
    contributions = []
    for c in range(N_CHAMBERS):
        d = (theta - c * SPACING) % TWO_PI
        if d < PW_RAD and T_wall_ch[c] > T_INJECT_MIN:
            t = d / PW_RAD
            shape = 4 * t * (1 - t) * math.exp(-2 * t)
            P = flash_pressure(M_INJ, T_wall_ch[c])
            contributions.append(P * shape * A_VANE * R_ROTOR)
        else:
            contributions.append(0.0)
    return contributions


def friction_torque(omega):
    return K_DRAG * omega**2 * (1 if omega >= 0 else -1) + K_BEARING * omega


def load_torque(omega):
    """Generator-like load: constant resistance + speed-proportional."""
    return CONST_LOAD + K_LOAD * omega


def injection_energy(T_wall):
    """
    Energy extracted from wall in one discrete injection event (Joules).
    Only called once per arc-entry, not every timestep.
    """
    if T_wall <= T_INJECT_MIN:
        return 0.0
    return M_INJ * (C_WATER * (T_wall - T_INJECT) + H_VAP)


def update_thermal_state(T_wall_ch, T_core, theta, prev_theta, dt):
    """
    Evolve per-chamber temperatures and shared core temperature.
    Injection heat extraction is a discrete event fired once per arc-entry,
    not a continuous power term — this preserves dimensional consistency.
    Returns (new_T_wall_ch, new_T_core).
    """
    new_walls = list(T_wall_ch)

    # Core heating from external source (fuel/solar)
    Q_core_in = K_CORE_INPUT * (T_SOURCE - T_core) * dt

    # Core loses heat to each wall (power terms, correctly scaled by dt)
    Q_core_to_walls = 0.0
    wall_Q_in = []
    for c in range(N_CHAMBERS):
        q = K_CORE_TO_WALL * (T_core - T_wall_ch[c]) * dt
        q = max(q, 0.0)
        wall_Q_in.append(q)
        Q_core_to_walls += q

    # Update core
    dT_core = (Q_core_in - Q_core_to_walls) / C_CORE
    new_T_core = T_core + dT_core

    # Update each wall
    for c in range(N_CHAMBERS):
        T = T_wall_ch[c]
        Q_in   = wall_Q_in[c]
        Q_cool = K_COOL * (T - T_AMBIENT) * dt

        # Discrete injection event: fires once when rotor crosses arc entry
        # Detection: previous angle was outside arc, current angle is inside
        prev_d = (prev_theta - c * SPACING) % TWO_PI
        curr_d = (theta      - c * SPACING) % TWO_PI
        arc_entry = (prev_d >= PW_RAD or prev_d > curr_d) and curr_d < PW_RAD
        Q_inj = injection_energy(T) if arc_entry else 0.0

        dQ = Q_in - Q_cool - Q_inj
        new_walls[c] = T + dQ / C_WALL

    return new_walls, new_T_core


# ──────────────────────────────────────────────
# EM CONTROLLER — ω-governed PD
# ──────────────────────────────────────────────

_prev_tau_base = 0.0

def em_torque_control(tau_th, tau_fr, tau_load, omega):
    """
    PD controller with speed objective:
      τ_em = Kp·e_τ + Kω·e_ω − Kd·dτ/dt
    Only assists. Capped at TAU_EM_PEAK.
    """
    global _prev_tau_base

    if not USE_TORQUE_CONTROL or TAU_EM_PEAK <= 0:
        return 0.0

    tau_base = tau_th - tau_fr - tau_load
    e_tau    = TAU_TARGET - tau_base
    e_omega  = OMEGA_TARGET - omega
    d_tau    = tau_base - _prev_tau_base
    _prev_tau_base = tau_base

    tau_em = KP_EM * e_tau + K_OMEGA * e_omega - KD_EM * d_tau
    return min(max(tau_em, 0.0), TAU_EM_PEAK)


# ──────────────────────────────────────────────
# SLOPE-BASED PER-CHAMBER EM DISTRIBUTION
# ──────────────────────────────────────────────

_prev_tau_th_ch = [0.0] * N_CHAMBERS

def em_per_chamber_slope(tau_em_total, tau_th_ch):
    """
    Distribute EM torque to chambers where thermal torque is decaying fastest.
    Predictive: supports chambers losing energy, not just those currently active.
    Falls back to magnitude-proportional if no decay exists.
    """
    global _prev_tau_th_ch

    d_tau = [tau_th_ch[c] - _prev_tau_th_ch[c] for c in range(N_CHAMBERS)]
    _prev_tau_th_ch = list(tau_th_ch)

    # Weight by negative slope (decay)
    weights = [max(-d, 0.0) for d in d_tau]
    total_w = sum(weights)

    if total_w < 1e-6:
        # Fallback: proportional to magnitude
        total_m = sum(tau_th_ch)
        if total_m < 1e-6:
            return [tau_em_total / N_CHAMBERS] * N_CHAMBERS
        return [(t / total_m) * tau_em_total for t in tau_th_ch]

    return [(w / total_w) * tau_em_total for w in weights]


# ──────────────────────────────────────────────
# RUN SIMULATION
# ──────────────────────────────────────────────

print("Running thermodynamic simulation (v3) ...")
print(f"  Duration: {SIM_DURATION}s  dt={DT}s  FPS={FPS}")
print(f"  OMEGA_TARGET={OMEGA_TARGET} rad/s  TAU_TARGET={TAU_TARGET} N·m")
print(f"  T_SOURCE={T_SOURCE}°C  LOAD={CONST_LOAD}+{K_LOAD}ω N·m")

# Reset controller state
_prev_tau_base = 0.0
_prev_tau_th_ch = [0.0] * N_CHAMBERS

# Initial state
T_wall_ch  = [T_SOURCE * 0.8] * N_CHAMBERS   # start slightly below source
T_core     = T_CORE_INIT
theta      = 0.0
omega      = 0.1

# Energy accounting
E_th = E_em = E_fr = E_load = 0.0
steps_per_frame = max(1, int((1.0 / FPS) / DT))

frame_states = []

for frame in range(FRAMES_TOTAL):
    # Snapshot
    tau_th_ch  = thermal_torque_per_chamber(theta, T_wall_ch)
    tau_th     = sum(tau_th_ch)
    tau_fr     = friction_torque(omega)
    tau_load   = load_torque(omega)
    tau_em     = em_torque_control(tau_th, tau_fr, tau_load, omega)
    tau_em_ch  = em_per_chamber_slope(tau_em, tau_th_ch)
    tau_net    = tau_th + tau_em - tau_fr - tau_load

    frame_states.append({
        "frame":     frame + ANIM_START,
        "theta":     theta,
        "omega":     omega,
        "tau_th":    tau_th,
        "tau_th_ch": list(tau_th_ch),
        "tau_em":    tau_em,
        "tau_em_ch": list(tau_em_ch),
        "tau_fr":    tau_fr,
        "tau_load":  tau_load,
        "tau_net":   tau_net,
        "T_wall_ch": list(T_wall_ch),
        "T_core":    T_core,
        "KE":        0.5 * I_ROTOR * omega**2,
        "E_th":      E_th,
        "E_em":      E_em,
        "E_fr":      E_fr,
        "E_load":    E_load,
    })

    # Micro-integration
    for _ in range(steps_per_frame):
        tau_th_ch_i = thermal_torque_per_chamber(theta, T_wall_ch)
        tau_th_i    = sum(tau_th_ch_i)
        tau_fr_i    = friction_torque(omega)
        tau_load_i  = load_torque(omega)
        tau_em_i    = em_torque_control(tau_th_i, tau_fr_i, tau_load_i, omega)
        tau_net_i   = tau_th_i + tau_em_i - tau_fr_i - tau_load_i

        alpha      = tau_net_i / I_ROTOR
        omega      = max(omega + alpha * DT, 0.0)
        dtheta     = omega * DT
        prev_theta = theta
        theta      = (theta + dtheta) % TWO_PI

        # Energy integrals
        E_th   += tau_th_i   * dtheta
        E_em   += tau_em_i   * dtheta
        E_fr   += tau_fr_i   * dtheta
        E_load += tau_load_i * dtheta

        # Thermal state evolution — pass prev_theta for discrete arc-entry detection
        T_wall_ch, T_core = update_thermal_state(T_wall_ch, T_core, theta, prev_theta, DT)

# Final state
final_omega  = frame_states[-1]["omega"]
final_rpm    = final_omega * 60 / TWO_PI
final_KE     = 0.5 * I_ROTOR * final_omega**2
final_T_core = frame_states[-1]["T_core"]
final_T_wall = frame_states[-1]["T_wall_ch"]
E_in         = E_th + E_em
eff          = final_KE / max(E_in, 1e-6) * 100
em_frac      = E_em / max(E_in, 1e-6) * 100

print(f"\n  Terminal ω      = {final_omega:.2f} rad/s  ({final_rpm:.0f} RPM)")
print(f"  Target ω        = {OMEGA_TARGET} rad/s  ({OMEGA_TARGET*60/TWO_PI:.0f} RPM)")
print(f"  Speed error     = {abs(final_omega - OMEGA_TARGET):.2f} rad/s")
print(f"  Final KE        = {final_KE:.1f} J")
print(f"  E_thermal in    = {E_th:.1f} J  ({100-em_frac:.1f}%)")
print(f"  E_EM in         = {E_em:.1f} J  ({em_frac:.1f}%)")
print(f"  E_friction      = {E_fr:.1f} J")
print(f"  E_load (work)   = {E_load:.1f} J")
print(f"  System eff      = {eff:.1f}%")
print(f"  Core temp final = {final_T_core:.1f}°C")
print(f"  Wall temps      = {[f'{t:.0f}' for t in final_T_wall]}")

if em_frac > 40:
    print(f"\n  ⚠  EM carrying {em_frac:.0f}% of load — thermal side under-performing.")
    print(f"     Consider: T_SOURCE↑, M_INJ↑, K_HEAT↑, or OMEGA_TARGET↓")
else:
    print(f"\n  ✓  Thermal side dominant ({100-em_frac:.0f}%). EM assisting correctly.")

# ──────────────────────────────────────────────
# CSV EXPORT
# ──────────────────────────────────────────────
os.makedirs("output", exist_ok=True)

csv_path = "output/fr_torque_log_v3.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["frame","theta","omega","tau_th","tau_em","tau_fr",
                     "tau_load","tau_net","T_core",
                     *[f"T_ch{i}" for i in range(N_CHAMBERS)],
                     "KE","E_th","E_em","E_load"])
    for s in frame_states:
        writer.writerow([
            s["frame"], f"{s['theta']:.4f}", f"{s['omega']:.4f}",
            f"{s['tau_th']:.3f}", f"{s['tau_em']:.3f}",
            f"{s['tau_fr']:.3f}", f"{s['tau_load']:.3f}", f"{s['tau_net']:.3f}",
            f"{s['T_core']:.2f}",
            *[f"{t:.2f}" for t in s["T_wall_ch"]],
            f"{s['KE']:.2f}", f"{s['E_th']:.2f}",
            f"{s['E_em']:.2f}", f"{s['E_load']:.2f}",
        ])
print(f"\n  CSV: {csv_path}")

# ──────────────────────────────────────────────
# BLENDER SETUP
# ──────────────────────────────────────────────

bpy.context.scene.frame_start = ANIM_START
bpy.context.scene.frame_end   = ANIM_END
bpy.context.scene.render.fps  = FPS

rotor_names = (["FR_Flywheel", "FR_Hub", "FR_ShaftCollar", "FR_Shaft"] +
               [f"FR_Vane_{i:02d}" for i in range(N_CHAMBERS)])
rotor_objects = [bpy.data.objects[n] for n in rotor_names if n in bpy.data.objects]

stator_coils = [(i, bpy.data.objects[f"FR_StatorCoil_{i:02d}"])
                for i in range(N_CHAMBERS)
                if f"FR_StatorCoil_{i:02d}" in bpy.data.objects]

nozzles = [(i, bpy.data.objects[f"FR_Nozzle_{i:02d}"])
           for i in range(N_CHAMBERS)
           if f"FR_Nozzle_{i:02d}" in bpy.data.objects]

burner = bpy.data.objects.get("FR_BurnerCore")

for obj in rotor_objects:
    obj.animation_data_clear()

# Clear material animation data to prevent accumulation across reruns
for obj_list in [stator_coils, nozzles]:
    for _, obj in obj_list:
        if obj.data.materials:
            for mat in obj.data.materials:
                if mat and mat.animation_data:
                    mat.animation_data_clear()
if burner and burner.data.materials:
    for mat in burner.data.materials:
        if mat and mat.animation_data:
            mat.animation_data_clear()


def set_bsdf(mat, attr, value, frame):
    nodes = mat.node_tree.nodes
    bsdf  = nodes.get("Principled BSDF")
    if bsdf and attr in bsdf.inputs:
        bsdf.inputs[attr].default_value = value
        bsdf.inputs[attr].keyframe_insert(data_path='default_value', frame=frame)


def set_emission(mat, strength, frame):
    set_bsdf(mat, "Emission Strength", strength, frame)


def set_color(mat, r, g, b, frame):
    set_bsdf(mat, "Emission Color", (r, g, b, 1.0), frame)


# ──────────────────────────────────────────────
# NORMALIZATION
# ──────────────────────────────────────────────

max_tau_th_ch = [max(s["tau_th_ch"][i] for s in frame_states) + 1e-6
                 for i in range(N_CHAMBERS)]
max_tau_em_ch = [max(s["tau_em_ch"][i] for s in frame_states) + 1e-6
                 for i in range(N_CHAMBERS)]

T_range = max(s["T_core"] for s in frame_states) - min(s["T_core"] for s in frame_states) + 1.0

# Per-chamber thermal derivatives for nozzle flash
prev_ch = [0.0] * N_CHAMBERS
d_tau_ch_series = []
max_d_ch = [1e-6] * N_CHAMBERS
for s in frame_states:
    row = []
    for c in range(N_CHAMBERS):
        d = max(s["tau_th_ch"][c] - prev_ch[c], 0.0)
        row.append(d)
        if d > max_d_ch[c]:
            max_d_ch[c] = d
        prev_ch[c] = s["tau_th_ch"][c]
    d_tau_ch_series.append(row)

print(f"\n  Animating {len(rotor_objects)} rotor objects + "
      f"{len(stator_coils)} coils + {len(nozzles)} nozzles ...")

# ──────────────────────────────────────────────
# ROTOR ROTATION
# ──────────────────────────────────────────────

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
        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=state["frame"])

for obj in rotor_objects:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

print("  Rotor: done")

# ──────────────────────────────────────────────
# STATOR COIL EMISSION — per-chamber torque-driven
# ──────────────────────────────────────────────
#
# Color encodes energy domain:
#   Orange component = thermal torque in this chamber
#   Blue component   = EM torque assigned to this chamber
#   Brightness       = total energy activity
#
# When thermal depletes (wall cools), orange fades → blue dominates
# At thermal steady state, orange returns → blue backs off
# Idle chambers: very dim cool blue

for idx, state in enumerate(frame_states):
    fn = state["frame"]
    for ci, coil_obj in stator_coils:
        if not coil_obj.data.materials:
            continue
        mat = coil_obj.data.materials[0]
        mat.use_nodes = True

        th_norm = state["tau_th_ch"][ci] / max_tau_th_ch[ci]
        em_norm = state["tau_em_ch"][ci] / max_tau_em_ch[ci]

        # Temperature-aware orange tint: hot wall = richer orange
        T_ch    = state["T_wall_ch"][ci]
        t_norm  = max(0.0, min(1.0, (T_ch - T_AMBIENT) / (T_SOURCE - T_AMBIENT)))

        r = th_norm * 0.9 * t_norm + em_norm * 0.05
        g = th_norm * 0.3 * t_norm + em_norm * 0.55
        b = em_norm * 0.95 + (1 - t_norm) * 0.1   # cold chambers get slight blue

        strength = em_norm * 8.0 + th_norm * 3.0 * t_norm
        if strength < 0.08:
            r, g, b, strength = 0.0, 0.1, 0.35, 0.1

        set_color(mat, r, g, b, fn)
        set_emission(mat, strength, fn)

print("  Stator coils: done")

# ──────────────────────────────────────────────
# NOZZLE FLASH — true per-chamber dτ_th/dt
# ──────────────────────────────────────────────
#
# Each nozzle fires only when its own chamber's thermal torque rises.
# Cold chambers (T_wall < T_INJECT_MIN) get no flash.

for idx, state in enumerate(frame_states):
    fn = state["frame"]
    for ci, nozzle_obj in nozzles:
        if not nozzle_obj.data.materials:
            continue
        mat = nozzle_obj.data.materials[0]
        mat.use_nodes = True

        d_norm = d_tau_ch_series[idx][ci] / max(max_d_ch[ci], 1e-6)
        T_ch   = state["T_wall_ch"][ci]
        hot_enough = T_ch > T_INJECT_MIN

        if d_norm > 0.05 and hot_enough:
            # Sharp cold-blue injection flash — brightness by injection intensity
            strength = d_norm * 7.0
            # Tint toward white at full flash (superheated steam)
            r = 0.3 + d_norm * 0.5
            g = 0.7 + d_norm * 0.2
            b = 1.0
        else:
            # Cold chamber or no injection
            t_norm = max(0.0, min(1.0, (T_ch - T_AMBIENT) / (T_SOURCE - T_AMBIENT)))
            strength = t_norm * 0.15   # faint thermal glow only
            r, g, b = t_norm * 0.3, t_norm * 0.1, 0.0

        set_color(mat, r, g, b, fn)
        set_emission(mat, strength, fn)

print("  Nozzles: done")

# ──────────────────────────────────────────────
# BURNER CORE — reflects T_core depletion/recovery
# ──────────────────────────────────────────────

if burner and burner.data.materials:
    mat = burner.data.materials[0]
    mat.use_nodes = True
    T_core_min = min(s["T_core"] for s in frame_states)
    T_core_max = max(s["T_core"] for s in frame_states)
    T_core_range = max(T_core_max - T_core_min, 1.0)

    for state in frame_states:
        fn = state["frame"]
        t_norm = (state["T_core"] - T_core_min) / T_core_range
        # Full strength at peak, dims as core depletes
        strength = 2.0 + t_norm * 4.0
        r = 1.0
        g = 0.2 + t_norm * 0.3
        b = 0.0
        set_color(mat, r, g, b, fn)
        set_emission(mat, strength, fn)

    print("  Burner core: done")

# ──────────────────────────────────────────────
# SUMMARY
# ──────────────────────────────────────────────

print("\n" + "=" * 60)
print("FR Engine v3 — Thermodynamic Machine: COMPLETE")
print(f"  Duration        : {SIM_DURATION}s  @{FPS}fps  ({FRAMES_TOTAL} frames)")
print(f"  Terminal RPM    : {final_rpm:.0f}  (target: {OMEGA_TARGET*60/TWO_PI:.0f})")
print(f"  Speed error     : {abs(final_omega-OMEGA_TARGET):.2f} rad/s")
print(f"  E_thermal       : {E_th:.0f} J  ({100-em_frac:.1f}%)")
print(f"  E_EM            : {E_em:.0f} J  ({em_frac:.1f}%)")
print(f"  E_load (work)   : {E_load:.0f} J")
print(f"  E_friction      : {E_fr:.0f} J")
print(f"  Final KE        : {final_KE:.1f} J")
print(f"  Core temp       : {final_T_core:.1f}°C")
print(f"  CSV             : {csv_path}")
print()
print("  Visual encoding:")
print("    Coils   orange → thermal active, blue → EM active")
print("    Coils   dim    → chamber thermally depleted")
print("    Nozzles flash  → injection spike (per-chamber dτ/dt)")
print("    Burner  dims   → core temperature depletion")
print("  Press SPACE to play. Render with Cycles + Bloom.")
print("=" * 60)
