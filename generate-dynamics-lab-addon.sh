#!/usr/bin/env bash
set -e

ADDON_DIR="rsvp_field_dynamics_lab"
mkdir -p "$ADDON_DIR"

echo "Generating standalone RSVP Field Dynamics Lab add-on..."

########################################################
# __init__.py
########################################################
cat > "$ADDON_DIR/__init__.py" << 'EOF'
bl_info = {
    "name": "RSVP Field Dynamics Lab",
    "author": "Flyxion",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > RSVP Dynamics",
    "description": "Standalone scalar-field research instrument",
    "category": "Object",
}

import bpy
from . import core
from . import dynamics
from . import diagnostics
from . import ui

def register():
    core.register()
    dynamics.register()
    diagnostics.register()
    ui.register()

def unregister():
    ui.unregister()
    diagnostics.unregister()
    dynamics.unregister()
    core.unregister()
EOF

########################################################
# core.py
########################################################
cat > "$ADDON_DIR/core.py" << 'EOF'
import bpy
import bmesh
import numpy as np

_simulation = None

class FieldSimulation:
    def __init__(self, N, size):
        self.N = N
        self.size = size
        self.phi = np.zeros((N, N))
        self.obj = None
        self.initialize()

    def initialize(self):
        self.phi = 0.02 * (np.random.rand(self.N, self.N) - 0.5)

    def laplacian(self, arr):
        return (
            np.roll(arr,1,0) +
            np.roll(arr,-1,0) +
            np.roll(arr,1,1) +
            np.roll(arr,-1,1) -
            4*arr
        )

def create_mesh(sim):
    mesh = bpy.data.meshes.new("RSVP_Field")
    obj = bpy.data.objects.new("RSVP_Field", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_grid(
        bm,
        x_segments=sim.N-1,
        y_segments=sim.N-1,
        size=sim.size/2
    )
    bm.to_mesh(mesh)
    bm.free()

    sim.obj = obj

def apply_height(sim, scale=0.6):
    flat = sim.phi.flatten()
    for v in sim.obj.data.vertices:
        v.co.z = scale * flat[v.index]

def set_simulation(sim):
    global _simulation
    _simulation = sim

def get_simulation():
    return _simulation

def register():
    pass

def unregister():
    pass
EOF

########################################################
# diagnostics.py
########################################################
cat > "$ADDON_DIR/diagnostics.py" << 'EOF'
import numpy as np

def free_energy(phi, kappa):
    grad = (np.roll(phi,1,0)-phi)**2 + (np.roll(phi,1,1)-phi)**2
    bulk = 0.25*(phi**2 - 1)**2
    return float(np.sum(bulk + 0.5*kappa*grad))

def l2_norm(phi):
    return float(np.sqrt(np.sum(phi**2)))

def dominant_mode(phi):
    fft = np.fft.fft2(phi)
    power = np.abs(fft)**2
    idx = np.unravel_index(np.argmax(power), power.shape)
    return tuple(int(i) for i in idx)

def register():
    pass

def unregister():
    pass
EOF

########################################################
# dynamics.py
########################################################
cat > "$ADDON_DIR/dynamics.py" << 'EOF'
import bpy
import numpy as np
import json
import os
from .core import FieldSimulation, create_mesh, apply_height, set_simulation, get_simulation
from .diagnostics import free_energy, l2_norm, dominant_mode

_log = []

class RSVPFieldSettings(bpy.types.PropertyGroup):
    N: bpy.props.IntProperty(default=96, min=16, max=256)
    size: bpy.props.FloatProperty(default=6.0)
    dt: bpy.props.FloatProperty(default=0.08)
    Deff: bpy.props.FloatProperty(default=-0.5)
    kappa: bpy.props.FloatProperty(default=0.2)
    nonlinear: bpy.props.FloatProperty(default=0.8)
    conservative: bpy.props.BoolProperty(default=False)
    vector_coupling: bpy.props.FloatProperty(default=0.0)
    track_energy: bpy.props.BoolProperty(default=True)
    export_json: bpy.props.BoolProperty(default=False)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 240
    return scene

def initialize(context):
    global _log
    s = context.scene.rsvp_field
    scene = reset_scene()

    sim = FieldSimulation(s.N, s.size)
    create_mesh(sim)
    set_simulation(sim)

    bpy.ops.object.camera_add(location=(0,-10,6), rotation=(1.13,0,0))
    scene.camera = bpy.context.active_object

    _log = []

def evolve(context):
    global _log
    s = context.scene.rsvp_field
    sim = get_simulation()

    L1 = sim.laplacian(sim.phi)
    L2 = sim.laplacian(L1)

    if s.conservative:
        mu = sim.phi*(sim.phi**2 - 1) - s.kappa*L1
        sim.phi += s.dt * sim.laplacian(mu)
    else:
        sim.phi += s.dt * (
            s.Deff*L1
            - s.kappa*L2
            - s.nonlinear*(sim.phi**3)
            + s.vector_coupling*np.sin(sim.phi)
        )

    apply_height(sim)

    if s.track_energy:
        _log.append({
            "frame": bpy.context.scene.frame_current,
            "energy": free_energy(sim.phi, s.kappa),
            "L2": l2_norm(sim.phi),
            "k_dom": dominant_mode(sim.phi)
        })

    if s.export_json and bpy.context.scene.frame_current == bpy.context.scene.frame_end:
        path = os.path.join(bpy.app.tempdir, "rsvp_field_dynamics_log.json")
        with open(path,"w") as f:
            json.dump(_log,f)

def frame_handler(scene):
    evolve(bpy.context)

class RSVP_OT_RunField(bpy.types.Operator):
    bl_idname = "rsvp_field.run"
    bl_label = "Run Field Simulation"
    def execute(self, context):
        initialize(context)
        bpy.app.handlers.frame_change_pre.clear()
        bpy.app.handlers.frame_change_pre.append(frame_handler)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RSVPFieldSettings)
    bpy.types.Scene.rsvp_field = bpy.props.PointerProperty(type=RSVPFieldSettings)
    bpy.utils.register_class(RSVP_OT_RunField)

def unregister():
    bpy.utils.unregister_class(RSVP_OT_RunField)
    del bpy.types.Scene.rsvp_field
    bpy.utils.unregister_class(RSVPFieldSettings)
EOF

########################################################
# ui.py
########################################################
cat > "$ADDON_DIR/ui.py" << 'EOF'
import bpy

class RSVP_PT_FieldPanel(bpy.types.Panel):
    bl_label = "RSVP Field Dynamics"
    bl_idname = "RSVP_PT_field"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RSVP Dynamics"

    def draw(self, context):
        layout = self.layout
        s = context.scene.rsvp_field

        layout.prop(s,"N")
        layout.prop(s,"size")
        layout.prop(s,"dt")
        layout.prop(s,"Deff")
        layout.prop(s,"kappa")
        layout.prop(s,"nonlinear")
        layout.prop(s,"conservative")
        layout.prop(s,"vector_coupling")
        layout.prop(s,"track_energy")
        layout.prop(s,"export_json")
        layout.operator("rsvp_field.run", icon="PLAY")

def register():
    bpy.utils.register_class(RSVP_PT_FieldPanel)

def unregister():
    bpy.utils.unregister_class(RSVP_PT_FieldPanel)
EOF

echo "Standalone RSVP Field Dynamics Lab created."
echo "Zip the folder and install as a new add-on in Blender."
