import random
import math
import bpy
from mathutils import Vector
from scene_utils import ensure_collection, make_material, add_sphere, add_cylinder_edge, add_camera_and_light


def build_history_dag_dynamics(scene):

    random.seed(7)

    col = ensure_collection("HistoryDAG")

    mat_node = make_material("event_node", rgba=(0.85, 0.9, 1.0, 1.0), emission=0.3)
    mat_edge = make_material("event_edge", rgba=(0.2, 0.2, 0.25, 1.0), emission=0.0)

    add_camera_and_light(camera_loc=(10, -10, 7), look_at=(5, 0, 1))

    layers = 10
    width = 6
    frames = 120

    nodes = []
    objs = {}
    parents = {}

    # create nodes
    for t in range(layers):

        layer_nodes = []

        for i in range(width):

            if random.random() < 0.55:
                continue

            y = (i - (width - 1) / 2) * 0.7 + random.uniform(-0.15, 0.15)
            z = random.uniform(-0.4, 0.4)
            x = t * 1.0

            pos = Vector((x, y, z))

            obj = add_sphere(
                pos,
                radius=0.14,
                name=f"e_{t}_{i}",
                material=mat_node,
                collection=col
            )

            layer_nodes.append((pos, obj))
            objs[obj] = (t, i)
            parents[obj] = []

        nodes.append(layer_nodes)

    # edges
    for t in range(1, layers):

        prev = nodes[t - 1]
        curr = nodes[t]

        if not prev or not curr:
            continue

        for (p_pos, p_obj) in curr:

            for (q_pos, q_obj) in random.sample(prev, k=min(len(prev), random.randint(1, 3))):

                if q_pos.x < p_pos.x:

                    add_cylinder_edge(q_pos, p_pos, radius=0.04, name="edge", material=mat_edge, collection=col)

                    parents[p_obj].append(q_obj)

    # RSVP state
    Phi = {obj: random.uniform(0.4, 0.6) for obj in parents}
    S = {obj: random.uniform(0.2, 0.4) for obj in parents}

    scene.frame_start = 1
    scene.frame_end = frames

    for f in range(1, frames + 1):

        new_phi = {}
        new_S = {}

        for obj in parents:

            ps = parents[obj]

            if not ps:

                new_phi[obj] = Phi[obj]
                new_S[obj] = S[obj] * 0.95
                continue

            avg_phi = sum(Phi[p] for p in ps) / len(ps)
            avg_S = sum(S[p] for p in ps) / len(ps)

            new_phi[obj] = 0.7 * Phi[obj] + 0.3 * avg_phi + random.uniform(-0.02, 0.02)
            new_S[obj] = 0.7 * S[obj] + 0.3 * avg_S + random.uniform(-0.03, 0.03)

        Phi = new_phi
        S = new_S

        for obj in parents:

            phi = Phi[obj]
            entropy = S[obj]

            scale = 0.12 + 0.18 * phi
            obj.scale = (scale, scale, scale)

            r = min(1.0, entropy)
            g = min(1.0, phi)

            obj.color = (r, g, 0.5, 1.0)

            obj.keyframe_insert(data_path="scale", frame=f)
            obj.keyframe_insert(data_path="color", frame=f)