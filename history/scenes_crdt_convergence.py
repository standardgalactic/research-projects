import os
import random
import bpy
from mathutils import Vector
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

    ops_pool = list(range(ops_total))
    random.shuffle(ops_pool)

    op_sets = [set() for _ in range(replicas)]

    for r in range(replicas):
        for _ in range(4):
            op_sets[r].add(ops_pool.pop())

    op_objs = [[None] * ops_total for _ in range(replicas)]

    def op_position(replica, op_id):

        x = replica * 3.0
        y = (op_id - (ops_total - 1) / 2) * 0.22
        z = 0.0

        return Vector((x, y, z))

    def create_operation_objects():

        for r in range(replicas):
            for op_id in range(ops_total):

                pos = op_position(r, op_id)

                obj = add_sphere(
                    pos,
                    radius=0.11,
                    name=f"op_{r}_{op_id}",
                    material=mat_ops[r],
                    collection=col,
                )

                obj.hide_render = True
                obj.hide_viewport = True

                op_objs[r][op_id] = obj

    def reveal_operations(frame):

        for r in range(replicas):

            for op_id in op_sets[r]:

                obj = op_objs[r][op_id]

                obj.hide_render = False
                obj.hide_viewport = False

                obj.keyframe_insert("hide_render", frame=frame)
                obj.keyframe_insert("hide_viewport", frame=frame)

    def merge(a, b):

        before = set(op_sets[b])

        op_sets[b] |= op_sets[a]

        return before != op_sets[b]

    def inject_operation():

        if not ops_pool:
            return

        r = random.randrange(replicas)
        op_sets[r].add(ops_pool.pop())

    def converged():

        base = op_sets[0]

        for r in range(1, replicas):
            if op_sets[r] != base:
                return False

        return not ops_pool

    create_operation_objects()

    scene.frame_start = 1
    scene.frame_end = steps

    reveal_operations(1)

    for frame in range(2, steps + 1):

        if random.random() < 0.55:

            a, b = random.sample(range(replicas), 2)

            if merge(a, b):

                add_cylinder_edge(
                    (a * 3.0, 0, 0.4),
                    (b * 3.0, 0, 0.4),
                    radius=0.03,
                    material=mat_edge,
                    collection=col,
                )

        if random.random() < 0.25:
            inject_operation()

        reveal_operations(frame)

        if converged():
            scene.frame_end = frame
            break

    if anim_dir:

        os.makedirs(anim_dir, exist_ok=True)

        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = os.path.join(anim_dir, "frame_")

        bpy.ops.render.render(animation=True, write_still=True)