import os
import random
from mathutils import Vector
import bpy
from scene_utils import ensure_collection, make_material, add_sphere, add_cylinder_edge, add_camera_and_light

def build_crdt_convergence(scene, anim_dir: str):
    random.seed(3)
    col = ensure_collection("CRDT")

    add_camera_and_light(camera_loc=(12, -12, 8), look_at=(6, 0, 1))

    mat_ops = [
        make_material("rep0", rgba=(1.0, 0.7, 0.7, 1.0), emission=0.25),
        make_material("rep1", rgba=(0.7, 1.0, 0.7, 1.0), emission=0.25),
        make_material("rep2", rgba=(0.7, 0.8, 1.0, 1.0), emission=0.25),
    ]
    mat_edge = make_material("merge_edge", rgba=(0.2, 0.2, 0.25, 1.0), emission=0.0)

    replicas = 3
    ops_total = 18
    steps = 90

    ops = list(range(ops_total))
    random.shuffle(ops)

    op_sets = [set() for _ in range(replicas)]
    for r in range(replicas):
        for _ in range(4):
            op_sets[r].add(ops.pop())

    op_objs = [[None]*ops_total for _ in range(replicas)]

    def op_position(r, op_id):
        x = r * 3.0
        y = (op_id - (ops_total-1)/2) * 0.22
        z = 0.0
        return Vector((x, y, z))

    for r in range(replicas):
        for op_id in range(ops_total):
            p = op_position(r, op_id)
            obj = add_sphere(p, radius=0.11, name=f"op_{r}_{op_id}", material=mat_ops[r], collection=col)
            obj.hide_render = True
            obj.hide_viewport = True
            op_objs[r][op_id] = obj

    def reveal_ops(frame):
        for r in range(replicas):
            for op_id in op_sets[r]:
                obj = op_objs[r][op_id]
                obj.hide_render = False
                obj.hide_viewport = False
                obj.keyframe_insert(data_path="hide_render", frame=frame)
                obj.keyframe_insert(data_path="hide_viewport", frame=frame)

    scene.frame_start = 1
    scene.frame_end = steps

    reveal_ops(1)

    for f in range(2, steps+1):
        if random.random() < 0.55:
            a, b = random.sample(range(replicas), 2)
            before = set(op_sets[b])
            op_sets[b] |= op_sets[a]
            if before != op_sets[b]:
                add_cylinder_edge((a*3.0, 0, 0.4), (b*3.0, 0, 0.4), radius=0.03, material=mat_edge, collection=col)

        if ops and random.random() < 0.25:
            r = random.randrange(replicas)
            op_sets[r].add(ops.pop())

        reveal_ops(f)

        if all(op_sets[0] == op_sets[r] for r in range(1, replicas)) and not ops:
            scene.frame_end = f
            break
        if anim_dir:
            os.makedirs(anim_dir, exist_ok=True)
    
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(anim_dir, "frame_")
    bpy.ops.render.render(animation=True, write_still=True)
