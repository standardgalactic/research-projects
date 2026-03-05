import os
import random
import bpy
from mathutils import Vector
from scene_utils import ensure_collection, make_material, add_sphere, add_camera_and_light

def build_entropy_collapse(scene, anim_dir: str):
    random.seed(11)
    col = ensure_collection("EntropyCollapse")

    add_camera_and_light(camera_loc=(10, -12, 7), look_at=(4, 0, 0.5))

    mat_fine = make_material("fine", rgba=(0.9, 0.9, 1.0, 1.0), emission=0.2)
    mat_coarse = make_material("coarse", rgba=(1.0, 0.85, 0.6, 1.0), emission=0.35)

    groups = 5
    per_group = 24
    frames = 80

    targets = []
    for g in range(groups):
        targets.append(Vector((g * 1.6, random.uniform(-1.2, 1.2), random.uniform(-0.6, 0.6))))

    coarse_objs = []
    for g, t in enumerate(targets):
        obj = add_sphere(t, radius=0.22, name=f"R_{g}", material=mat_coarse, collection=col)
        coarse_objs.append(obj)

    fine_objs = []
    for g, t in enumerate(targets):
        for i in range(per_group):
            p = t + Vector((random.uniform(-2.0, -0.5), random.uniform(-1.3, 1.3), random.uniform(-1.0, 1.0)))
            obj = add_sphere(p, radius=0.11, name=f"h_{g}_{i}", material=mat_fine, collection=col)
            fine_objs.append((obj, p.copy(), t.copy()))

    scene.frame_start = 1
    scene.frame_end = frames

    for (obj, p0, pt) in fine_objs:
        obj.location = p0
        obj.keyframe_insert(data_path="location", frame=1)
        obj.location = pt
        obj.keyframe_insert(data_path="location", frame=frames)

    os.makedirs(anim_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(anim_dir, "frame_")
    bpy.ops.render.render(animation=True, write_still=True)
