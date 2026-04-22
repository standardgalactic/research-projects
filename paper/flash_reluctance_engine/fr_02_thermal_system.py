"""
Flash-Reluctance Engine — Script 2: Thermal Chamber System
===========================================================
Run AFTER fr_01_rotor_geometry.py (adds to the FR_Engine collection).

Generates:
  - Central heat manifold (burner core)
  - Per-chamber hot-wall segments (arc sections between vanes)
  - Injection nozzle stubs (one per chamber)
  - Cold manifold ring (condenser/exhaust)
  - Coolant pipe stubs

Design rationale encoded in geometry:
  - Hot wall arc = PULSE_WIDTH_DEG of each chamber's angular span
  - Nozzle injection angle is tangential + slight inward rake
  - Cold manifold is axially offset (below disc plane) to reflect
    the real heat-flow direction: heat inward, cold outward/below
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ──────────────────────────────────────────────
# PARAMETERS  (keep in sync with script 01)
# ──────────────────────────────────────────────

R_ROTOR         = 0.15
R_HUB           = 0.04
N_CHAMBERS      = 6
PULSE_WIDTH_DEG = 40.0
FLYWHEEL_THICK  = 0.025
VANE_HEIGHT     = 0.040

# Thermal geometry specifics
R_BURNER_CORE   = R_HUB * 0.85          # m  — inner heat manifold radius
BURNER_HEIGHT   = VANE_HEIGHT * 1.4     # m  — taller than rotor for heat wrap
HOT_WALL_R      = R_HUB + (R_ROTOR - R_HUB) * 0.55  # mid-radius for hot wall arc
HOT_WALL_THICK  = 0.005                 # m
NOZZLE_R        = 0.004                 # m  — injection tube radius
NOZZLE_LEN      = 0.028                 # m
COLD_MANIFOLD_R = R_ROTOR + 0.045       # m  — outside stators
COLD_PIPE_R     = 0.006                 # m
COLD_PIPE_LEN   = 0.04                  # m
COLD_Z_OFFSET   = -(FLYWHEEL_THICK/2 + 0.018)  # below disc

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def get_collection(name="FR_Engine"):
    if name not in bpy.data.collections:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return bpy.data.collections[name]

def link(col, obj):
    if obj.name not in col.objects:
        col.objects.link(obj)

    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def make_material(name, base_color, metallic=0.8, roughness=0.3,
                  emission=None, emission_strength=1.5):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def add_cylinder(name, radius, depth, location=(0,0,0), rotation=(0,0,0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=verts,
        radius=radius,
        depth=depth,
        location=location,
        rotation=rotation
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def arc_mesh(name, r_inner, r_outer, height, angle_start, angle_end,
             segments=24, z=0.0):
    """
    Build a radial arc section (like a pie-slice annulus).
    Used for hot-wall chamber liners.
    """
    mesh = bpy.data.meshes.new(name + "_mesh")
    bm = bmesh.new()

    half_h = height / 2
    a_range = angle_end - angle_start

    verts_bot_inner = []
    verts_bot_outer = []
    verts_top_inner = []
    verts_top_outer = []

    for s in range(segments + 1):
        a = angle_start + (a_range * s / segments)
        ca, sa = math.cos(a), math.sin(a)
        verts_bot_inner.append(bm.verts.new((r_inner*ca, r_inner*sa, z - half_h)))
        verts_bot_outer.append(bm.verts.new((r_outer*ca, r_outer*sa, z - half_h)))
        verts_top_inner.append(bm.verts.new((r_inner*ca, r_inner*sa, z + half_h)))
        verts_top_outer.append(bm.verts.new((r_outer*ca, r_outer*sa, z + half_h)))

    for s in range(segments):
        # outer face
        bm.faces.new([verts_bot_outer[s], verts_bot_outer[s+1],
                      verts_top_outer[s+1], verts_top_outer[s]])
        # inner face
        bm.faces.new([verts_bot_inner[s+1], verts_bot_inner[s],
                      verts_top_inner[s], verts_top_inner[s+1]])
        # top face
        bm.faces.new([verts_top_inner[s], verts_top_outer[s],
                      verts_top_outer[s+1], verts_top_inner[s+1]])
        # bottom face
        bm.faces.new([verts_bot_inner[s+1], verts_bot_outer[s+1],
                      verts_bot_outer[s], verts_bot_inner[s]])

    # Side caps
    bm.faces.new([verts_bot_inner[0], verts_bot_outer[0],
                  verts_top_outer[0], verts_top_inner[0]])
    bm.faces.new([verts_bot_outer[-1], verts_bot_inner[-1],
                  verts_top_inner[-1], verts_top_outer[-1]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    return bpy.data.objects.new(name, mesh)


# ──────────────────────────────────────────────
# BUILD
# ──────────────────────────────────────────────

col = get_collection("FR_Engine")

mat_burner   = make_material("FR_Burner",   (0.90, 0.25, 0.02),
                              metallic=0.6, roughness=0.4,
                              emission=(1.0, 0.35, 0.0), emission_strength=3.0)
mat_hotwall  = make_material("FR_HotWall",  (0.65, 0.20, 0.05),
                              metallic=0.85, roughness=0.3,
                              emission=(0.8, 0.15, 0.0), emission_strength=0.8)
mat_nozzle   = make_material("FR_Nozzle",   (0.30, 0.55, 0.70),
                              metallic=0.95, roughness=0.15)
mat_cold     = make_material("FR_ColdManifold", (0.15, 0.40, 0.65),
                              metallic=0.80, roughness=0.25,
                              emission=(0.0, 0.5, 1.0), emission_strength=0.4)
mat_pipe     = make_material("FR_CoolantPipe",  (0.20, 0.50, 0.80),
                              metallic=0.90, roughness=0.15)


# ── 1. Central burner core ──────────────────────────────────────────────────
burner = add_cylinder("FR_BurnerCore", R_BURNER_CORE, BURNER_HEIGHT, (0, 0, 0))
burner.data.materials.append(mat_burner)
link(col, burner)

# Inner heat channel (annular gap — subtract a smaller cylinder visually)
# We just add a second smaller slightly recessed cylinder to suggest the channel
inner_glow = add_cylinder("FR_BurnerInnerGlow",
                           R_BURNER_CORE * 0.6,
                           BURNER_HEIGHT * 0.95,
                           (0, 0, 0), verts=32)
inner_glow.data.materials.append(mat_burner)
link(col, inner_glow)


# ── 2. Hot-wall arc liners — one per chamber ────────────────────────────────
#
# Each arc occupies the "expansion zone" of a chamber, from the trailing edge
# of one vane to PULSE_WIDTH_DEG forward.  The gap between arc end and the
# next vane is the exhaust/reset zone.

spacing_rad = 2 * math.pi / N_CHAMBERS
pw_rad      = PULSE_WIDTH_DEG * math.pi / 180.0

for i in range(N_CHAMBERS):
    base_angle  = spacing_rad * i
    arc_start   = base_angle + 0.02        # small clearance from vane edge
    arc_end     = base_angle + pw_rad - 0.02

    arc_obj = arc_mesh(
        f"FR_HotWall_{i:02d}",
        r_inner = HOT_WALL_R - HOT_WALL_THICK,
        r_outer = HOT_WALL_R + HOT_WALL_THICK,
        height  = VANE_HEIGHT * 0.85,
        angle_start = arc_start,
        angle_end   = arc_end,
        segments    = 18,
        z = 0.0
    )
    arc_obj.data.materials.append(mat_hotwall)
    link(col, arc_obj)


# ── 3. Injection nozzles ─────────────────────────────────────────────────────
#
# Each nozzle is placed at R_HUB * 1.2, aimed tangentially inward toward the
# hot wall arc.  The injection angle is perpendicular to the rotor radius +
# a slight inward rake (15°) to maximize contact with the hot wall.

INJECTION_ANGLE_RAKE = 15.0  # degrees inward from tangent

for i in range(N_CHAMBERS):
    # Nozzle fires at chamber midpoint
    mid_angle = spacing_rad * i + pw_rad * 0.5

    # Position: slightly inside R_HUB, at the chamber mid-arc
    r_pos = HOT_WALL_R - HOT_WALL_THICK - NOZZLE_LEN * 0.4
    nx = r_pos * math.cos(mid_angle)
    ny = r_pos * math.sin(mid_angle)

    # Nozzle points tangentially + rake inward
    # Tangent direction at mid_angle: (-sin, cos, 0)
    # Rake toward center
    tang_angle = mid_angle + math.pi/2   # tangent direction angle
    rake_rad   = INJECTION_ANGLE_RAKE * math.pi / 180.0

    # Cylinder rotation: align Z axis along nozzle direction
    rot_z = tang_angle
    rot_y = math.pi/2 - rake_rad   # tilt from vertical

    nozzle = add_cylinder(
        f"FR_Nozzle_{i:02d}",
        NOZZLE_R,
        NOZZLE_LEN,
        (nx, ny, 0.0),
        rotation=(math.pi/2 - rake_rad, 0, tang_angle)
    )
    nozzle.data.materials.append(mat_nozzle)
    link(col, nozzle)

    # Nozzle tip — slightly larger cone-like cap
    tip_x = (r_pos + NOZZLE_LEN * 0.4) * math.cos(mid_angle)
    tip_y = (r_pos + NOZZLE_LEN * 0.4) * math.sin(mid_angle)
    bpy.ops.mesh.primitive_cone_add(
        vertices=16,
        radius1=NOZZLE_R * 1.6,
        radius2=NOZZLE_R * 0.3,
        depth=NOZZLE_R * 2.5,
        location=(tip_x, tip_y, 0.0),
        rotation=(math.pi/2 - rake_rad, 0, tang_angle)
    )
    tip = bpy.context.active_object
    tip.name = f"FR_NozzleTip_{i:02d}"
    tip.data.materials.append(mat_nozzle)
    link(col, tip)


# ── 4. Cold manifold ring (condenser) ───────────────────────────────────────
bpy.ops.mesh.primitive_torus_add(
    major_radius=COLD_MANIFOLD_R,
    minor_radius=COLD_PIPE_R * 1.4,
    major_segments=80,
    minor_segments=16,
    location=(0, 0, COLD_Z_OFFSET)
)
cold_ring = bpy.context.active_object
cold_ring.name = "FR_ColdManifold"
cold_ring.data.materials.append(mat_cold)
link(col, cold_ring)


# ── 5. Coolant inlet/outlet pipe stubs ──────────────────────────────────────
# Two pipes: inlet (bottom) and outlet (top), 180° apart on the cold ring

for angle, label in [(0, "Inlet"), (math.pi, "Outlet")]:
    px = COLD_MANIFOLD_R * math.cos(angle)
    py = COLD_MANIFOLD_R * math.sin(angle)
    pz = COLD_Z_OFFSET - COLD_PIPE_LEN / 2

    pipe = add_cylinder(
        f"FR_Coolant{label}",
        COLD_PIPE_R,
        COLD_PIPE_LEN,
        (px, py, pz),
        rotation=(0, 0, 0)   # vertical pipes
    )
    pipe.data.materials.append(mat_pipe)
    link(col, pipe)

    # Flange
    flange = add_cylinder(
        f"FR_Coolant{label}Flange",
        COLD_PIPE_R * 2.2,
        0.005,
        (px, py, COLD_Z_OFFSET - COLD_PIPE_LEN)
    )
    flange.data.materials.append(mat_pipe)
    link(col, flange)


# ── 6. Steam exhaust channels ────────────────────────────────────────────────
# Small rectangular exhaust slots at the end of each active arc (at R_ROTOR edge)
# Modeled as thin flat boxes placed at rotor rim

for i in range(N_CHAMBERS):
    exhaust_angle = spacing_rad * i + pw_rad   # end of expansion zone

    ex = (R_ROTOR + 0.003) * math.cos(exhaust_angle)
    ey = (R_ROTOR + 0.003) * math.sin(exhaust_angle)

    bpy.ops.mesh.primitive_cube_add(location=(ex, ey, 0))
    exh = bpy.context.active_object
    exh.name = f"FR_Exhaust_{i:02d}"
    exh.scale = (0.004, 0.012, VANE_HEIGHT * 0.6)
    exh.rotation_euler.z = exhaust_angle
    bpy.ops.object.transform_apply(scale=True, rotation=False)
    exh.data.materials.append(mat_cold)
    link(col, exh)


# ──────────────────────────────────────────────
print("=" * 60)
print("FR Engine — Thermal System: BUILT")
print(f"  Hot wall arcs  : {N_CHAMBERS}")
print(f"  Injection nozzles: {N_CHAMBERS}")
print(f"  Burner core R  : {R_BURNER_CORE*1000:.1f} mm")
print(f"  Cold manifold R: {COLD_MANIFOLD_R*1000:.1f} mm")
print(f"  Cold Z offset  : {COLD_Z_OFFSET*1000:.1f} mm")
print("Collection  : FR_Engine")
print("=" * 60)
