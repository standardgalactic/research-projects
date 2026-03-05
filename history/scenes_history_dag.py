import random
from mathutils import Vector
from scene_utils import ensure_collection, make_material, add_sphere, add_cylinder_edge, add_camera_and_light

def build_history_dag(scene):
    random.seed(7)
    col = ensure_collection("HistoryDAG")

    mat_node = make_material("event_node", rgba=(0.85, 0.9, 1.0, 1.0), emission=0.3)
    mat_edge = make_material("event_edge", rgba=(0.2, 0.2, 0.25, 1.0), emission=0.0)

    add_camera_and_light(camera_loc=(10, -10, 7), look_at=(5, 0, 1))

    layers = 10
    width = 6

    nodes = []
    for t in range(layers):
        layer_nodes = []
        for i in range(width):
            if random.random() < 0.55:
                continue
            y = (i - (width - 1) / 2) * 0.7 + random.uniform(-0.15, 0.15)
            z = random.uniform(-0.4, 0.4)
            x = t * 1.0
            obj = add_sphere((x, y, z), radius=0.14, name=f"e_{t}_{i}", material=mat_node, collection=col)
            layer_nodes.append((Vector((x, y, z)), obj))
        nodes.append(layer_nodes)

    for t in range(1, layers):
        prev = nodes[t-1]
        curr = nodes[t]
        if not prev or not curr:
            continue
        for (p, _) in curr:
            for (q, _) in random.sample(prev, k=min(len(prev), random.randint(1, 3))):
                if q.x < p.x:
                    add_cylinder_edge(q, p, radius=0.04, name="edge", material=mat_edge, collection=col)

    scene.frame_start = 1
    scene.frame_end = 1
