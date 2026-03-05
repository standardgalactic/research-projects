import itertools
from mathutils import Vector
from scene_utils import ensure_collection, make_material, add_sphere, add_cylinder_edge, add_camera_and_light

def build_history_lattice(scene):
    col = ensure_collection("HistoryLattice")

    add_camera_and_light(camera_loc=(10, -10, 8), look_at=(3.5, 0, 1.5))

    mat_node = make_material("lat_node", rgba=(0.95, 0.95, 0.95, 1.0), emission=0.25)
    mat_edge = make_material("lat_edge", rgba=(0.2, 0.2, 0.25, 1.0), emission=0.0)

    events = ["a", "b", "c", "d"]
    nodes = []
    for k in range(len(events) + 1):
        for subset in itertools.combinations(events, k):
            nodes.append(subset)

    def pos(subset):
        k = len(subset)
        x = k * 1.6
        y = (hash(subset) % 11 - 5) * 0.35
        z = (hash(subset[::-1]) % 7 - 3) * 0.25
        return Vector((x, y, z))

    node_pos = {}
    for s in nodes:
        p = pos(s)
        node_pos[s] = p
        add_sphere(p, radius=0.16, name=f"H_{''.join(s) if s else '∅'}", material=mat_node, collection=col)

    for s in nodes:
        for e in events:
            if e in s:
                continue
            t = tuple(sorted(s + (e,)))
            if t in node_pos:
                add_cylinder_edge(node_pos[s], node_pos[t], radius=0.035, material=mat_edge, collection=col)

    scene.frame_start = 1
    scene.frame_end = 1
