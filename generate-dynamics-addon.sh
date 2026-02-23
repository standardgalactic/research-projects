#!/usr/bin/env bash
set -e

ADDON_DIR="rsvp_research_lab"
mkdir -p "$ADDON_DIR"

echo "Generating advanced RSVP research add-on..."

########################################################
# __init__.py
########################################################
cat > "$ADDON_DIR/__init__.py" << 'EOF'
bl_info = {
    "name": "RSVP Research Lab",
    "author": "Flyxion",
    "version": (0, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > RSVP Research",
    "description": "Advanced scalar-field research platform",
    "category": "Object",
}

import bpy
from . import engine
from . import diagnostics
from . import controller
from . import ui

def register():
    engine.register()
    diagnostics.register()
    controller.register()
    ui.register()

def unregister():
    ui.unregister()
    controller.unregister()
    diagnostics.unregister()
    engine.unregister()
EOF

########################################################
# engine.py
########################################################
cat > "$ADDON_DIR/engine.py" << 'EOF'
import bpy
import bmesh
import random
import numpy as np

_sim = None

class SimulationState:

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
            np.roll(arr, 1, axis=0) +
            np.roll(arr, -1, axis=0) +
            np.roll(arr, 1, axis=1) +
            np.roll(arr, -1, axis=1) -
            4 * arr
        )

def create_plane(sim):
    mesh = bpy.data.meshes.new("RSVP_Field")
    obj = bpy.data.objects.new("RSVP_Field", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bmesh.ops.create_grid(
        bm,
        x_segments=sim.N - 1,
        y_segments=sim.N - 1,
        size=sim.size / 2
    )
    bm.to_mesh(mesh)
    bm.free()

    sim.obj = obj

def apply_height(sim, scale=0.6):
    flat = sim.phi.flatten()
    for v in sim.obj.data.vertices:
        v.co.z = scale * flat[v.index]

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
    grad2 = (
        np.roll(phi,1,0) - phi
    )**2 + (
        np.roll(phi,1,1) - phi
    )**2
    bulk = 0.25*(phi**2 - 1)**2
    return np.sum(bulk + 0.5*kappa*grad2)

def l2_norm(phi):
    return np.sqrt(np.sum(phi**2))

def dominant_wavenumber(phi):
    fft = np.fft.fft2(phi)
    power = np.abs(fft)**2
    k_index = np.unravel_index(np.argmax(power), power.shape)
    return k_index

def register():
    pass

def unregister():
    pass
EOF

########################################################
# controller.py
########################################################
cat > "$ADDON_DIR/controller.py" << 'EOF'
import bpy
import numpy as np
import json
import os
from .engine import SimulationState, create_plane, apply_height
from .diagnostics import free_energy, l2_norm, dominant_wavenumber

_sim = None
_log = []

class RSVPSettings(bpy.types.PropertyGroup):
    N: bpy.props.IntProperty(default=96, min=16, max=256)
    size: bpy.props.FloatProperty(default=6.0)
    dt: bpy.props.FloatProperty(default=0.08)
    Deff: bpy.props.FloatProperty(default=-0.5)
    kappa: bpy.props.FloatProperty(default=0.2)
    nonlinear: bpy.props.FloatProperty(default=0.8)
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
    global _sim, _log
    s = context.scene.rsvp_research
    scene = reset_scene()
    _sim = SimulationState(s.N, s.size)
    create_plane(_sim)
    _log = []

    bpy.ops.object.camera_add(location=(0,-10,6),
                              rotation=(1.13,0,0))
    scene.camera = bpy.context.active_object

def step(context):
    global _sim, _log
    s = context.scene.rsvp_research

    L1 = _sim.laplacian(_sim.phi)
    L2 = _sim.laplacian(L1)

    nonlinear_term = s.nonlinear * (_sim.phi**3)
    vector_term = s.vector_coupling * np.sin(_sim.phi)

    _sim.phi += s.dt * (
        s.Deff * L1
        - s.kappa * L2
        - nonlinear_term
        + vector_term
    )

    apply_height(_sim)

    if s.track_energy:
        E = free_energy(_sim.phi, s.kappa)
        L2n = l2_norm(_sim.phi)
        kdom = dominant_wavenumber(_sim.phi)
        _log.append({
            "frame": bpy.context.scene.frame_current,
            "energy": float(E),
            "L2": float(L2n),
            "k_dom": kdom
        })

    if s.export_json and bpy.context.scene.frame_current == bpy.context.scene.frame_end:
        path = os.path.join(bpy.app.tempdir, "rsvp_research_log.json")
        with open(path,"w") as f:
            json.dump(_log,f)

def frame_handler(scene):
    step(bpy.context)

class RSVP_OT_Run(bpy.types.Operator):
    bl_idname = "rsvp_research.run"
    bl_label = "Run Research Simulation"
    def execute(self, context):
        initialize(context)
        bpy.app.handlers.frame_change_pre.clear()
        bpy.app.handlers.frame_change_pre.append(frame_handler)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(RSVPSettings)
    bpy.types.Scene.rsvp_research = bpy.props.PointerProperty(type=RSVPSettings)
    bpy.utils.register_class(RSVP_OT_Run)

def unregister():
    bpy.utils.unregister_class(RSVP_OT_Run)
    del bpy.types.Scene.rsvp_research
    bpy.utils.unregister_class(RSVPSettings)
EOF

########################################################
# ui.py
########################################################
cat > "$ADDON_DIR/ui.py" << 'EOF'
import bpy

class RSVP_PT_ResearchPanel(bpy.types.Panel):
    bl_label = "RSVP Research Lab"
    bl_idname = "RSVP_PT_research"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "RSVP Research"

    def draw(self, context):
        layout = self.layout
        s = context.scene.rsvp_research

        layout.prop(s,"N")
        layout.prop(s,"size")
        layout.prop(s,"dt")
        layout.prop(s,"Deff")
        layout.prop(s,"kappa")
        layout.prop(s,"nonlinear")
        layout.prop(s,"vector_coupling")
        layout.prop(s,"track_energy")
        layout.prop(s,"export_json")
        layout.operator("rsvp_research.run", icon="PLAY")

def register():
    bpy.utils.register_class(RSVP_PT_ResearchPanel)

def unregister():
    bpy.utils.unregister_class(RSVP_PT_ResearchPanel)
EOF

echo "Advanced add-on created."
echo "Zip the rsvp_research_lab folder and install in Blender."
