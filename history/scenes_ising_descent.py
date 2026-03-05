import os
import random
import math
import bpy
from mathutils import Vector
from scene_utils import ensure_collection, add_camera_and_light

def build_ising_descent(scene, anim_dir: str):
    random.seed(5)
    col = ensure_collection("Ising")

    add_camera_and_light(camera_loc=(12, -12, 10), look_at=(4.5, 4.5, 0.0))

    n = 10
    frames = 120
    beta = 1.2
    J = 1.0

    spins = [[random.choice([-1, 1]) for _ in range(n)] for _ in range(n)]
    objs = [[None for _ in range(n)] for _ in range(n)]

    def neigh(i, j):
        return [((i-1) % n, j), ((i+1) % n, j), (i, (j-1) % n), (i, (j+1) % n)]

    def local_energy(i, j):
        s = spins[i][j]
        return -J * s * sum(spins[a][b] for (a,b) in neigh(i,j))

    def set_color(obj, spin):
        if spin == 1:
            obj.color = (1.0, 0.8, 0.7, 1.0)
        else:
            obj.color = (0.7, 0.85, 1.0, 1.0)

    for i in range(n):
        for j in range(n):
            bpy.ops.mesh.primitive_cube_add(size=0.85, location=(i, j, 0))
            obj = bpy.context.object
            obj.name = f"s_{i}_{j}"
            obj.data.materials.clear()
            obj.display_type = "SOLID"
            set_color(obj, spins[i][j])
            objs[i][j] = obj
            col.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)

    scene.frame_start = 1
    scene.frame_end = frames

    for f in range(1, frames + 1):
        for _ in range(n * n // 2):
            i = random.randrange(n)
            j = random.randrange(n)

            e0 = local_energy(i, j)
            spins[i][j] *= -1
            e1 = local_energy(i, j)
            dE = e1 - e0

            accept = (dE <= 0) or (random.random() < math.exp(-beta * dE))
            if not accept:
                spins[i][j] *= -1

        for i in range(n):
            for j in range(n):
                obj = objs[i][j]
                set_color(obj, spins[i][j])
                obj.keyframe_insert(data_path="color", frame=f)

    os.makedirs(anim_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(anim_dir, "frame_")
    bpy.ops.render.render(animation=True, write_still=True)
