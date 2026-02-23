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
