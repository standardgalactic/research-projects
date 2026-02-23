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
