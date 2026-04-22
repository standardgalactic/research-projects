"""
Flash-Reluctance Engine — Script 1: Rotor Geometry
====================================================
Run this in Blender's Scripting workspace (Text Editor → Run Script).
Tested on Blender 3.x / 4.x.

Generates the full rotor assembly:
  - Flywheel disc
  - Radial vanes (expansion chambers)
  - Central hub with keyway
  - Output shaft stub
  - Stator coil mounts (outer ring)

Parameters at the top mirror the HTML simulator exactly.
Change them here, re-run, and the geometry updates.

Collection created: "FR_Engine"
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# ──────────────────────────────────────────────
# ENGINE PARAMETERS  (mirror the simulator)
# ──────────────────────────────────────────────

R_ROTOR         = 0.15      # m  — rotor radius (vane tip)
R_HUB           = 0.04      # m  — central hub radius
R_SHAFT         = 0.015     # m  — output shaft radius
N_CHAMBERS      = 6         # —   number of vanes / chambers
PULSE_WIDTH_DEG = 40.0      # °  — angular width of each chamber opening
FLYWHEEL_THICK  = 0.025     # m  — disc thickness
VANE_THICK      = 0.008     # m  — vane radial thickness
VANE_HEIGHT     = 0.040     # m  — vane axial height (same as disc)
SHAFT_LENGTH    = 0.12      # m  — stub shaft length
R_STATOR        = R_ROTOR + 0.025   # m  — stator coil ring radius
STATOR_COIL_R   = 0.010     # m  — coil cylinder radius
STATOR_COIL_H   = 0.030     # m  — coil cylinder height

# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def clear_collection(name):
    """Remove existing collection with this name, create fresh one."""
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

def link(col, obj):
    if obj.name not in col.objects:
        col.objects.link(obj)

    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def make_material(name, base_color, metallic=0.9, roughness=0.25, emission=None):
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
        bsdf.inputs["Emission Strength"].default_value = 2.0
    return mat


def add_cylinder(name, radius, depth, location=(0,0,0), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def add_mesh_obj(name, verts, edges, faces):
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, edges, faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    return obj

# ──────────────────────────────────────────────
# BUILD
# ──────────────────────────────────────────────

col = clear_collection("FR_Engine")

# Materials
mat_steel   = make_material("FR_Steel",   (0.55, 0.57, 0.60), metallic=0.95, roughness=0.20)
mat_hub     = make_material("FR_Hub",     (0.30, 0.33, 0.38), metallic=0.98, roughness=0.10)
mat_vane    = make_material("FR_Vane",    (0.70, 0.40, 0.10), metallic=0.80, roughness=0.35)  # orange-ish (thermal)
mat_shaft   = make_material("FR_Shaft",   (0.40, 0.42, 0.45), metallic=0.99, roughness=0.05)
mat_coil    = make_material("FR_Coil",    (0.05, 0.40, 0.90), metallic=0.30, roughness=0.60,
                             emission=(0.0, 0.6, 1.0))  # blue glow — EM coils
mat_housing = make_material("FR_Housing", (0.18, 0.20, 0.22), metallic=0.70, roughness=0.50)


# ── 1. Flywheel disc ────────────────────────────────────────────────────────
disc = add_cylinder("FR_Flywheel", R_ROTOR, FLYWHEEL_THICK, (0, 0, 0))
disc.data.materials.append(mat_steel)
link(col, disc)

# Boolean: cut hub hole — cutter must survive until AFTER modifier_apply
bpy.ops.mesh.primitive_cylinder_add(radius=R_HUB * 0.95, depth=FLYWHEEL_THICK * 2, location=(0,0,0))
hub_cutter = bpy.context.active_object
hub_cutter.name = "FR_HubCutter"
bool_mod = disc.modifiers.new("HubBool", "BOOLEAN")
bool_mod.operation = "DIFFERENCE"
bool_mod.object = hub_cutter
# Apply modifier first (cutter must still exist at this point)
bpy.ops.object.select_all(action='DESELECT')
disc.select_set(True)
bpy.context.view_layer.objects.active = disc
bpy.ops.object.modifier_apply(modifier="HubBool")
# Now safe to delete the cutter
bpy.ops.object.select_all(action='DESELECT')
hub_cutter.select_set(True)
bpy.context.view_layer.objects.active = hub_cutter
bpy.ops.object.delete()


# ── 2. Radial vanes ─────────────────────────────────────────────────────────
#
# Each vane is a tapered box placed at R_HUB + margin, extending toward R_ROTOR.
# The pulse_width_deg defines how wide (in angle) the chamber opening is —
# vane thickness at tip is set from that arc length.

vane_length = R_ROTOR - R_HUB - 0.005   # radial span
tip_arc     = 2 * math.pi * R_ROTOR * (PULSE_WIDTH_DEG / 360.0)
vane_width  = tip_arc * 0.15             # vane is 15% of arc width (wall, not gap)

for i in range(N_CHAMBERS):
    angle = (2 * math.pi / N_CHAMBERS) * i

    # Build vane as a box in edit mode via bmesh
    mesh = bpy.data.meshes.new(f"FR_Vane_{i:02d}_mesh")
    bm = bmesh.new()

    # Vane local coords: X = radial, Y = tangential, Z = axial
    half_y = vane_width / 2
    half_z = VANE_HEIGHT / 2
    x0 = R_HUB + 0.003
    x1 = R_ROTOR - 0.002

    # Slight taper: wider at root, narrower at tip
    bmesh.ops.create_cube(bm, size=1)
    bm.free()

    # Manually create tapered vane
    bm = bmesh.new()
    verts_coords = [
        (x0,  half_y * 1.3, -half_z),
        (x0, -half_y * 1.3, -half_z),
        (x1, -half_y,       -half_z),
        (x1,  half_y,       -half_z),
        (x0,  half_y * 1.3,  half_z),
        (x0, -half_y * 1.3,  half_z),
        (x1, -half_y,        half_z),
        (x1,  half_y,        half_z),
    ]
    bverts = [bm.verts.new(v) for v in verts_coords]
    bm.faces.new([bverts[0], bverts[1], bverts[2], bverts[3]])  # bottom
    bm.faces.new([bverts[4], bverts[7], bverts[6], bverts[5]])  # top
    bm.faces.new([bverts[0], bverts[4], bverts[5], bverts[1]])  # side A
    bm.faces.new([bverts[2], bverts[6], bverts[7], bverts[3]])  # side B
    bm.faces.new([bverts[0], bverts[3], bverts[7], bverts[4]])  # tip face
    bm.faces.new([bverts[1], bverts[5], bverts[6], bverts[2]])  # root face
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()

    vane_obj = bpy.data.objects.new(f"FR_Vane_{i:02d}", mesh)
    vane_obj.rotation_euler.z = angle
    vane_obj.data.materials.append(mat_vane)
    link(col, vane_obj)


# ── 3. Central hub ──────────────────────────────────────────────────────────
hub = add_cylinder("FR_Hub", R_HUB, VANE_HEIGHT + 0.002, (0, 0, 0))
hub.data.materials.append(mat_hub)
link(col, hub)

# Keyway slot (simple rectangular notch via boolean)
bpy.ops.mesh.primitive_cube_add(
    size=1,
    location=(R_HUB * 0.6, 0, 0)
)
keyway_cut = bpy.context.active_object
keyway_cut.name = "FR_KeywayCutter"
keyway_cut.scale = (R_HUB * 0.5, R_HUB * 0.25, VANE_HEIGHT)
bpy.ops.object.transform_apply(scale=True)

bool_k = hub.modifiers.new("KeywayBool", "BOOLEAN")
bool_k.operation = "DIFFERENCE"
bool_k.object = keyway_cut
bpy.context.view_layer.objects.active = hub
hub.select_set(True)
bpy.ops.object.modifier_apply(modifier="KeywayBool")
bpy.ops.object.select_all(action='DESELECT')
keyway_cut.select_set(True)
bpy.context.view_layer.objects.active = keyway_cut
bpy.ops.object.delete()


# ── 4. Output shaft stub ────────────────────────────────────────────────────
shaft_z = -(FLYWHEEL_THICK / 2 + SHAFT_LENGTH / 2)
shaft = add_cylinder("FR_Shaft", R_SHAFT, SHAFT_LENGTH, (0, 0, shaft_z))
shaft.data.materials.append(mat_shaft)
link(col, shaft)

# Shaft collar at disc face
collar = add_cylinder("FR_ShaftCollar", R_SHAFT * 1.8, 0.008, (0, 0, -FLYWHEEL_THICK/2 - 0.004))
collar.data.materials.append(mat_hub)
link(col, collar)


# ── 5. Stator coil ring ─────────────────────────────────────────────────────
# One coil per chamber, positioned at R_STATOR, equally spaced
# EM phase offset is baked into the angular position label only (visual)

for i in range(N_CHAMBERS):
    angle = (2 * math.pi / N_CHAMBERS) * i
    cx = R_STATOR * math.cos(angle)
    cy = R_STATOR * math.sin(angle)
    coil = add_cylinder(f"FR_StatorCoil_{i:02d}", STATOR_COIL_R, STATOR_COIL_H, (cx, cy, 0))
    coil.data.materials.append(mat_coil)
    link(col, coil)


# ── 6. Outer housing ring (partial — open for visibility) ───────────────────
bpy.ops.mesh.primitive_torus_add(
    major_radius=R_STATOR + STATOR_COIL_R + 0.008,
    minor_radius=0.006,
    major_segments=64,
    minor_segments=12,
    location=(0, 0, 0)
)
ring = bpy.context.active_object
ring.name = "FR_HousingRing"
ring.data.materials.append(mat_housing)
link(col, ring)

# Second ring (axially offset — top of stator)
bpy.ops.mesh.primitive_torus_add(
    major_radius=R_STATOR + STATOR_COIL_R + 0.008,
    minor_radius=0.006,
    major_segments=64,
    minor_segments=12,
    location=(0, 0, STATOR_COIL_H / 2 + 0.005)
)
ring2 = bpy.context.active_object
ring2.name = "FR_HousingRing_Top"
ring2.data.materials.append(mat_housing)
link(col, ring2)


# ── 7. Camera & lights for quick render ─────────────────────────────────────
# Only adds if not already present
if "FR_Cam" not in bpy.data.objects:
    bpy.ops.object.camera_add(location=(0.5, -0.5, 0.35))
    cam = bpy.context.active_object
    cam.name = "FR_Cam"
    cam.rotation_euler = (math.radians(65), 0, math.radians(45))
    bpy.context.scene.camera = cam

if "FR_KeyLight" not in bpy.data.objects:
    bpy.ops.object.light_add(type='AREA', location=(0.4, -0.3, 0.5))
    key = bpy.context.active_object
    key.name = "FR_KeyLight"
    key.data.energy = 200
    key.data.size = 0.3

if "FR_RimLight" not in bpy.data.objects:
    bpy.ops.object.light_add(type='SPOT', location=(-0.3, 0.3, 0.2))
    rim = bpy.context.active_object
    rim.name = "FR_RimLight"
    rim.data.energy = 80
    rim.data.color = (0.3, 0.7, 1.0)  # blue tint — EM aesthetic


# ── Done ────────────────────────────────────────────────────────────────────
# Select all in collection for user convenience
bpy.ops.object.select_all(action='DESELECT')
for obj in col.objects:
    obj.select_set(True)
bpy.context.view_layer.objects.active = disc

print("=" * 60)
print("FR Engine — Rotor Geometry: BUILT")
print(f"  Chambers  : {N_CHAMBERS}")
print(f"  R_rotor   : {R_ROTOR*1000:.1f} mm")
print(f"  R_stator  : {R_STATOR*1000:.1f} mm")
print(f"  Vane arc  : {2*math.pi*R_ROTOR*(PULSE_WIDTH_DEG/360)*1000:.1f} mm")
print(f"  Objects   : {len(list(col.objects))}")
print("Collection  : FR_Engine")
print("=" * 60)
