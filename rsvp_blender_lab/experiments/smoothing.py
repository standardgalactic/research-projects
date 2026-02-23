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
