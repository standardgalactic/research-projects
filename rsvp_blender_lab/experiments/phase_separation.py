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
