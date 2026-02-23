#!/usr/bin/env bash

set -e

PROJECT_DIR="rsvp_blender_lab"

echo "Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR/experiments"

############################################
# core_engine.py
############################################
cat > "$PROJECT_DIR/core_engine.py" << 'EOF'
import bpy
import bmesh
import math
import random

# ============================================================
# Core Engine: GridFieldSimulation
# ============================================================

class GridFieldSimulation:

    def __init__(self, N=64, size=6.0, seed=0):
        self.N = N
        self.size = size
        self.seed = seed
        random.seed(seed)
        self.phi = [0.0] * (N * N)
        for i in range(N * N):
            self.phi[i] = 0.02 * (random.random() - 0.5)
        self.obj = None

    def idx(self, i, j):
        return i * self.N + j

    def laplacian(self, phi):
        N = self.N
        out = [0.0] * (N * N)
        for i in range(N):
            ip, im = (i + 1) % N, (i - 1) % N
            for j in range(N):
                jp, jm = (j + 1) % N, (j - 1) % N
                c = phi[self.idx(i, j)]
                out[self.idx(i, j)] = (
                    phi[self.idx(ip, j)] +
                    phi[self.idx(im, j)] +
                    phi[self.idx(i, jp)] +
                    phi[self.idx(i, jm)] -
                    4.0 * c
                )
        return out

    def create_plane(self, name="FieldPlane"):
        mesh = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)

        bm = bmesh.new()
        bmesh.ops.create_grid(
            bm,
            x_segments=self.N - 1,
            y_segments=self.N - 1,
            size=self.size / 2.0
        )
        bm.to_mesh(mesh)
        bm.free()

        self.obj = obj
        return obj

    def apply_height(self, zscale=0.5):
        for v in self.obj.data.vertices:
            v.co.z = zscale * self.phi[v.index]

    def step(self, rule_function, dt):
        self.phi = rule_function(self, self.phi, dt)

# ============================================================
# Scene Utilities
# ============================================================

def reset_scene(frame_end=240):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = frame_end
    return scene

def add_basic_camera_and_light():
    scene = bpy.context.scene
    bpy.ops.object.camera_add(
        location=(0, -10, 6),
        rotation=(math.radians(65), 0, 0)
    )
    scene.camera = bpy.context.active_object
    bpy.ops.object.light_add(type='SUN', location=(4, -4, 10))
    bpy.context.active_object.data.energy = 2.5
EOF

############################################
# Experiment 1: Regulated Instability
############################################
cat > "$PROJECT_DIR/experiments/regulated_instability.py" << 'EOF'
import bpy
from core_engine import GridFieldSimulation, reset_scene, add_basic_camera_and_light

scene = reset_scene(240)
sim = GridFieldSimulation(N=80, size=6.0, seed=1)
sim.create_plane("RegulatedField")
add_basic_camera_and_light()

dt = 0.08
Deff_on = -0.55
Deff_off = 0.3
kappa = 0.2
nonlinear = 0.85
t_on, t_off = 40, 160

def rule(sim, phi, dt):
    L1 = sim.laplacian(phi)
    L2 = sim.laplacian(L1)
    new_phi = []
    frame = bpy.context.scene.frame_current
    Deff = Deff_on if (t_on <= frame <= t_off) else Deff_off
    for k in range(len(phi)):
        p = phi[k]
        dp = Deff * L1[k] - kappa * L2[k] - nonlinear * (p ** 3)
        new_phi.append(p + dt * dp)
    return new_phi

def handler(scene):
    sim.step(rule, dt)
    sim.apply_height(0.6)

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(handler)
scene.frame_set(scene.frame_start)
EOF

############################################
# Experiment 2: Pure Smoothing
############################################
cat > "$PROJECT_DIR/experiments/smoothing.py" << 'EOF'
import bpy
from core_engine import GridFieldSimulation, reset_scene, add_basic_camera_and_light

scene = reset_scene(200)
sim = GridFieldSimulation(N=80, size=6.0, seed=2)
sim.create_plane("SmoothingField")
add_basic_camera_and_light()

dt = 0.15
alpha = 0.4

def rule(sim, phi, dt):
    L = sim.laplacian(phi)
    return [phi[k] + dt * alpha * L[k] for k in range(len(phi))]

def handler(scene):
    sim.step(rule, dt)
    sim.apply_height(0.6)

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(handler)
scene.frame_set(scene.frame_start)
EOF

############################################
# Experiment 3: Double-Well Phase Separation
############################################
cat > "$PROJECT_DIR/experiments/phase_separation.py" << 'EOF'
import bpy
from core_engine import GridFieldSimulation, reset_scene, add_basic_camera_and_light

scene = reset_scene(240)
sim = GridFieldSimulation(N=80, size=6.0, seed=3)
sim.create_plane("PhaseField")
add_basic_camera_and_light()

dt = 0.07
kappa = 0.18
t_on, t_off = 30, 150

def rule(sim, phi, dt):
    L = sim.laplacian(phi)
    frame = bpy.context.scene.frame_current
    double_well = (t_on <= frame <= t_off)

    mu = []
    for k in range(len(phi)):
        p = phi[k]
        if double_well:
            fp = p * (p*p - 1.0)
        else:
            fp = p
        mu.append(fp - kappa * L[k])

    Lmu = sim.laplacian(mu)
    return [phi[k] + dt * Lmu[k] for k in range(len(phi))]

def handler(scene):
    sim.step(rule, dt)
    sim.apply_height(0.6)

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(handler)
scene.frame_set(scene.frame_start)
EOF

############################################
# README
############################################
cat > "$PROJECT_DIR/README.txt" << 'EOF'
RSVP Blender Lab

Structure:

core_engine.py
    Shared grid simulation engine and scene utilities.

experiments/
    regulated_instability.py
    smoothing.py
    phase_separation.py

How to use in Blender:

1. Open Blender.
2. Go to Scripting workspace.
3. Open one of the experiment files.
4. Ensure the folder containing core_engine.py is in the same directory.
5. Run the experiment script.
6. Press Play.

To extend:
    Define a new rule(sim, phi, dt) function
    Create a new experiment file importing core_engine
EOF

echo "Library-style Blender lab generated in: $PROJECT_DIR"
