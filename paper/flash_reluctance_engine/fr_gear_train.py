import bpy
import math
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

FPS = 24
DURATION = 10

GEARS = [
    {"radius": 0.20, "teeth": 24},
    {"radius": 0.10, "teeth": 12},
    {"radius": 0.25, "teeth": 30},
]

TOOTH_DEPTH = 0.02
TOOTH_WIDTH_FACTOR = 0.6
GEAR_THICKNESS = 0.05

# RESET
bpy.ops.wm.read_factory_settings(use_empty=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = FPS * DURATION
scene.render.fps = FPS

def create_gear(name, radius, teeth, location):
    angle_step = 2 * math.pi / teeth

    verts = []
    faces = []

    inner_r = radius
    outer_r = radius + TOOTH_DEPTH

    for i in range(teeth):
        a0 = i * angle_step
        a1 = a0 + angle_step * TOOTH_WIDTH_FACTOR

        x0, y0 = inner_r * math.cos(a0), inner_r * math.sin(a0)
        x1, y1 = inner_r * math.cos(a1), inner_r * math.sin(a1)
        x2, y2 = outer_r * math.cos(a1), outer_r * math.sin(a1)
        x3, y3 = outer_r * math.cos(a0), outer_r * math.sin(a0)

        base = len(verts)

        verts.extend([
            (x0, y0, -GEAR_THICKNESS/2),
            (x1, y1, -GEAR_THICKNESS/2),
            (x2, y2, -GEAR_THICKNESS/2),
            (x3, y3, -GEAR_THICKNESS/2),
            (x0, y0,  GEAR_THICKNESS/2),
            (x1, y1,  GEAR_THICKNESS/2),
            (x2, y2,  GEAR_THICKNESS/2),
            (x3, y3,  GEAR_THICKNESS/2),
        ])

        faces.extend([
            (base, base+1, base+2, base+3),
            (base+4, base+5, base+6, base+7),
            (base, base+1, base+5, base+4),
            (base+1, base+2, base+6, base+5),
            (base+2, base+3, base+7, base+6),
            (base+3, base+0, base+4, base+7),
        ])

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location

    return obj

# BUILD GEARS
gears = []
x_pos = 0

for i, g in enumerate(GEARS):
    obj = create_gear(f"Gear_{i:02d}", g["radius"], g["teeth"], (x_pos, 0, 0))
    gears.append(obj)

    if i < len(GEARS) - 1:
        r1 = g["radius"]
        r2 = GEARS[i+1]["radius"]
        x_pos += r1 + r2

# Ensure animation data exists
for g in gears:
    g.animation_data_create()

# ANIMATION
base_speed = 2.0
omegas = [0.0] * len(gears)
omegas[0] = base_speed

for i in range(1, len(gears)):
    r1 = GEARS[i-1]["radius"]
    r2 = GEARS[i]["radius"]
    omegas[i] = -omegas[i-1] * (r1 / r2)

for frame in range(scene.frame_start, scene.frame_end + 1):
    t = (frame - 1) / FPS

    for i, gear in enumerate(gears):
        theta = omegas[i] * t
        gear.rotation_euler[2] = theta
        gear.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)

# Set interpolation
for g in gears:
    if g.animation_data and g.animation_data.action:
        action = g.animation_data.action
        if hasattr(action, "fcurves"):
            for fc in action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = 'LINEAR'

# SAVE
path = os.path.join(OUTPUT_DIR, "gear_train.blend")
bpy.ops.wm.save_as_mainfile(filepath=path)

print(f"Saved: {path}")
