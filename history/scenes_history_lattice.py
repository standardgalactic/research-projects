import itertools
import random
import math
from mathutils import Vector
from scene_utils import (
    ensure_collection,
    make_material,
    add_sphere,
    add_cylinder_edge,
    add_camera_and_light,
)

def build_history_lattice(scene):

    col = ensure_collection("HistoryLattice")

    add_camera_and_light(
        camera_loc=(10, -10, 8),
        look_at=(3.5, 0, 1.5)
    )

    # ------------------------------------------------------------------
    # Materials
    # ------------------------------------------------------------------

    mat_node = make_material(
        "lat_node",
        rgba=(0.95, 0.95, 0.95, 1.0),
        emission=0.25
    )

    mat_edge_extension = make_material(
        "lat_edge_extension",
        rgba=(0.2, 0.2, 0.25, 1.0),
        emission=0.0
    )

    mat_edge_merge = make_material(
        "lat_edge_merge",
        rgba=(0.1, 0.35, 0.8, 1.0),
        emission=0.1
    )

    mat_edge_reduce = make_material(
        "lat_edge_reduce",
        rgba=(0.7, 0.3, 0.1, 1.0),
        emission=0.05
    )

    # RSVP visualization materials
    mat_phi = make_material(
        "rsvp_phi",
        rgba=(0.2, 0.9, 0.3, 1.0),
        emission=0.35
    )
    mat_entropy = make_material(
        "rsvp_entropy",
        rgba=(0.9, 0.2, 0.2, 1.0),
        emission=0.35
    )

    # ------------------------------------------------------------------
    # Event set
    # ------------------------------------------------------------------

    events = ["a", "b", "c", "d"]

    nodes = []
    for k in range(len(events) + 1):
        for subset in itertools.combinations(events, k):
            nodes.append(subset)

    # ------------------------------------------------------------------
    # Node positioning
    # ------------------------------------------------------------------

    def pos(subset):
        k = len(subset)
        x = k * 1.6
        y = (hash(subset) % 11 - 5) * 0.35
        z = (hash(subset[::-1]) % 7 - 3) * 0.25
        return Vector((x, y, z))

    # ------------------------------------------------------------------
    # Create nodes
    # ------------------------------------------------------------------

    node_pos = {}
    node_obj = {}      # optional: store returned sphere objects if scene_utils returns them
    node_label = {}

    for s in nodes:
        p = pos(s)
        node_pos[s] = p
        label = "".join(s) if s else "∅"
        node_label[s] = label
        obj = add_sphere(
            p,
            radius=0.16,
            name=f"H_{label}",
            material=mat_node,
            collection=col,
        )
        node_obj[s] = obj

    # ------------------------------------------------------------------
    # EXTENSION EDGES
    # ------------------------------------------------------------------

    ext_edges = []
    for s in nodes:
        for e in events:
            if e in s:
                continue
            t = tuple(sorted(s + (e,)))
            if t in node_pos:
                add_cylinder_edge(
                    node_pos[s],
                    node_pos[t],
                    radius=0.035,
                    material=mat_edge_extension,
                    collection=col,
                )
                ext_edges.append((s, t, e))

    # ------------------------------------------------------------------
    # MERGE EDGES
    # ------------------------------------------------------------------

    for s1 in nodes:
        for s2 in nodes:
            if s1 == s2:
                continue
            union = tuple(sorted(set(s1) | set(s2)))
            if union in node_pos and len(union) > max(len(s1), len(s2)):
                add_cylinder_edge(
                    node_pos[s1],
                    node_pos[union],
                    radius=0.02,
                    material=mat_edge_merge,
                    collection=col,
                )

    # ------------------------------------------------------------------
    # REDUCTION EDGES
    # ------------------------------------------------------------------

    for s in nodes:
        if len(s) < 2:
            continue
        for r in itertools.combinations(s, len(s) - 1):
            if r in node_pos:
                add_cylinder_edge(
                    node_pos[s],
                    node_pos[r],
                    radius=0.012,
                    material=mat_edge_reduce,
                    collection=col,
                )

    # ------------------------------------------------------------------
    # RSVP STATE PER NODE: (Phi, v, S)
    # In this lattice simulation, v is "flow along edges" rather than a spatial vector field.
    # We will store:
    #   Phi[s] = scalar potential / structure
    #   S[s]   = entropy / dispersion
    #   V[s]   = a scalar "throughput" proxy for flow magnitude
    # ------------------------------------------------------------------

    Phi = {}
    S = {}
    V = {}

    # Initialize: empty history has low entropy, some baseline Phi
    for s in nodes:
        k = len(s)
        Phi[s] = 0.3 + 0.15 * k + random.uniform(-0.05, 0.05)
        S[s] = 0.15 + 0.12 * k + random.uniform(-0.05, 0.05)
        V[s] = 0.0

    # ------------------------------------------------------------------
    # Evo-Devo operator parameters
    # ------------------------------------------------------------------

    # Evo: exploration injection (noise + novelty)
    evo_noise_S = 0.10
    evo_noise_Phi = 0.06
    evo_drive_from_events = 0.08

    # Devo: relaxation / smoothing / constraint pull
    devo_smooth = 0.35          # how strongly a node moves toward parent average
    devo_entropy_damp = 0.22    # entropy decay factor
    devo_phi_cap = (0.0, 2.0)   # clamp range
    devo_S_cap = (0.0, 2.0)

    # selection / pruning (visual collapse)
    prune_S_threshold = 1.25

    # animation length
    T = 120
    scene.frame_start = 1
    scene.frame_end = T

    # ------------------------------------------------------------------
    # Helpers: parents, children
    # ------------------------------------------------------------------

    parents = {s: [] for s in nodes}
    children = {s: [] for s in nodes}

    for s, t, e in ext_edges:
        parents[t].append(s)
        children[s].append(t)

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    # ------------------------------------------------------------------
    # Main simulation loop across frames
    # ------------------------------------------------------------------

    for frame in range(1, T + 1):

        # ----------------------------
        # EVO STEP
        # ----------------------------

        Phi_e = dict(Phi)
        S_e = dict(S)
        V_e = dict(V)

        for s in nodes:

            # random exploratory drift
            Phi_e[s] += random.uniform(-evo_noise_Phi, evo_noise_Phi)
            S_e[s] += random.uniform(-evo_noise_S, evo_noise_S)

            # "event novelty" grows with history length (proxy for branching pressure)
            k = len(s)
            S_e[s] += evo_drive_from_events * (k / max(1, len(events)))

            # flow proxy: if entropy is high, it drives "activity"
            V_e[s] = 0.5 * V_e[s] + 0.5 * abs(S_e[s] - S[s])

        # ----------------------------
        # DEVO STEP
        # ----------------------------

        Phi_d = dict(Phi_e)
        S_d = dict(S_e)
        V_d = dict(V_e)

        for s in nodes:

            if not parents[s]:
                # root: still relax entropy slightly
                S_d[s] = (1.0 - devo_entropy_damp) * S_d[s]
                continue

            # developmental attractor = average of parents (history-consistency)
            pavg_phi = sum(Phi_e[p] for p in parents[s]) / len(parents[s])
            pavg_S = sum(S_e[p] for p in parents[s]) / len(parents[s])

            Phi_d[s] = (1.0 - devo_smooth) * Phi_e[s] + devo_smooth * pavg_phi
            S_d[s] = (1.0 - devo_smooth) * S_e[s] + devo_smooth * pavg_S

            # damp entropy toward stability
            S_d[s] = (1.0 - devo_entropy_damp) * S_d[s]

        # clamp
        for s in nodes:
            Phi_d[s] = clamp(Phi_d[s], devo_phi_cap[0], devo_phi_cap[1])
            S_d[s] = clamp(S_d[s], devo_S_cap[0], devo_S_cap[1])

        Phi, S, V = Phi_d, S_d, V_d

        # ----------------------------
        # VISUALIZATION UPDATE
        # We cannot assume scene_utils returns bpy objects, but if it does,
        # we can animate scale + material emission as proxies.
        # If add_sphere returns None, this part can be adapted to lookup by name.
        # ----------------------------

        for s in nodes:

            obj = node_obj.get(s)

            # If scene_utils returns Blender objects, animate them directly.
            if obj is None:
                continue

            # Use Phi to drive scale (structure)
            scale = 0.12 + 0.10 * Phi[s]
            obj.scale = (scale, scale, scale)
            obj.keyframe_insert(data_path="scale", frame=frame)

            # Use S to drive visibility / collapse (pruning)
            if S[s] > prune_S_threshold:
                obj.hide_viewport = True
                obj.hide_render = True
            else:
                obj.hide_viewport = False
                obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=frame)
            obj.keyframe_insert(data_path="hide_render", frame=frame)