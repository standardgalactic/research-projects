import os
import random
import math
import itertools
import bpy
from mathutils import Vector
from scene_utils import ensure_collection, add_camera_and_light


def build_history_rsvp_flow(scene, anim_dir: str):

    random.seed(5)

    col = ensure_collection("HistoryRSVPFlow")

    add_camera_and_light(camera_loc=(12, -12, 10), look_at=(3.5, 0, 1.5))

    # ------------------------------------------------------------
    # Lattice: nodes are subsets of events, directed edges are extensions
    # ------------------------------------------------------------

    events = ["a", "b", "c", "d"]

    nodes = []
    for k in range(len(events) + 1):
        for subset in itertools.combinations(events, k):
            nodes.append(subset)

    node_set = set(nodes)

    def pos(subset):
        k = len(subset)
        x = k * 1.9
        y = (hash(subset) % 11 - 5) * 0.42
        z = (hash(subset[::-1]) % 7 - 3) * 0.35
        return Vector((x, y, z))

    node_pos = {s: pos(s) for s in nodes}

    # Directed extension edges: s -> t if t = s ∪ {e}
    edges = []
    out_edges = {s: [] for s in nodes}
    in_edges = {s: [] for s in nodes}

    for s in nodes:
        for e in events:
            if e in s:
                continue
            t = tuple(sorted(s + (e,)))
            if t in node_set:
                edges.append((s, t))
                out_edges[s].append((s, t))
                in_edges[t].append((s, t))

    # Undirected adjacency for graph diffusion of entropy
    adj = {s: set() for s in nodes}
    for (s, t) in edges:
        adj[s].add(t)
        adj[t].add(s)

    # ------------------------------------------------------------
    # Create node objects (spheres) and edge objects (cylinders)
    # ------------------------------------------------------------

    objs = {}
    for s in nodes:
        p = node_pos[s]
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=p)
        obj = bpy.context.object
        label = "".join(s) if s else "∅"
        obj.name = f"H_{label}"
        objs[s] = obj
        col.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

    edge_obj = {}
    for (s, t) in edges:
        p0 = node_pos[s]
        p1 = node_pos[t]
        mid = (p0 + p1) / 2.0
        vec = p1 - p0
        length = vec.length
        if length < 1e-6:
            continue

        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=length, location=mid)
        obj = bpy.context.object
        obj.name = f"E_{objs[s].name}_to_{objs[t].name}"

        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = vec.to_track_quat('Z', 'Y')

        col.objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

        edge_obj[(s, t)] = obj

    # ------------------------------------------------------------
    # RSVP-like discrete fields on nodes and flux on edges
    # ------------------------------------------------------------

    Phi = {}
    S = {}
    for s in nodes:
        k = len(s)
        Phi[s] = 0.8 + 0.18 * k + random.uniform(-0.06, 0.06)
        S[s] = 0.35 + 0.12 * k + random.uniform(-0.06, 0.06)

    # Flux f_{s->t} on each directed extension edge
    F = {}
    for (s, t) in edges:
        F[(s, t)] = random.uniform(-0.05, 0.05)

    # ------------------------------------------------------------
    # Parameters (tuned to look stable at 120 frames)
    # ------------------------------------------------------------

    frames = 120
    dt = 0.15

    lam = 1.1          # pressure-gradient drive: pushes flux down Phi gradient
    nu = 0.55          # flux damping
    sigma = 0.10       # coupling from entropy to Phi (optional; small)
    u0 = 0.05          # weak stabilizing potential pull strength
    phi_target = 1.0   # anchor point for the weak potential

    DS = 0.35          # graph diffusion for entropy
    mu = 0.05          # coupling from Phi into entropy sink/source
    chi = 0.20         # entropy production from flow intensity
    ent_noise = 0.06   # Evo: noise injected into entropy

    flux_noise = 0.06  # Evo: noise injected into flux (edge exploration)

    phi_cap = (0.0, 3.0)
    S_cap = (0.0, 3.0)

    collapse_threshold = 1.55

    # Edge thickness scale from flux magnitude
    edge_radius_base = 0.018
    edge_radius_gain = 0.08

    scene.frame_start = 1
    scene.frame_end = frames

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def set_node_color(obj, phi, entropy):
        r = min(1.0, 0.25 + 0.60 * entropy)
        g = min(1.0, 0.15 + 0.55 * phi)
        b = 0.45
        obj.color = (r, g, b, 1.0)

    def set_edge_color(obj, flux):
        # encode sign in color bias; magnitude via brightness
        m = min(1.0, abs(flux) * 1.2)
        if flux >= 0:
            obj.color = (0.2 + 0.8 * m, 0.25 + 0.55 * m, 0.35, 1.0)
        else:
            obj.color = (0.35, 0.25 + 0.55 * m, 0.2 + 0.8 * m, 1.0)

    # ------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------

    for f in range(1, frames + 1):

        # -----------------------------
        # Flux update (vector field proxy on edges)
        # dF/dt = -lam*(Phi_t - Phi_s) - nu*F + noise
        # -----------------------------

        newF = {}
        for (s, t) in edges:
            grad_phi = (Phi[t] - Phi[s])
            dF = (-lam * grad_phi) - (nu * F[(s, t)])
            dF += random.uniform(-flux_noise, flux_noise)
            newF[(s, t)] = F[(s, t)] + dt * dF
        F = newF

        # -----------------------------
        # Phi update (continuity-like)
        # dPhi/dt = -div(F) + sigma*S - u0*(Phi - phi_target)
        # where div(F)(s) = sum_out F(s->*) - sum_in F(*->s)
        # -----------------------------

        div = {}
        for s in nodes:
            out_sum = sum(F[e] for e in out_edges[s]) if out_edges[s] else 0.0
            in_sum = sum(F[e] for e in in_edges[s]) if in_edges[s] else 0.0
            div[s] = out_sum - in_sum

        newPhi = {}
        for s in nodes:
            dPhi = -div[s] + sigma * S[s] - u0 * (Phi[s] - phi_target)
            newPhi[s] = Phi[s] + dt * dPhi

        for s in nodes:
            newPhi[s] = clamp(newPhi[s], phi_cap[0], phi_cap[1])
        Phi = newPhi

        # -----------------------------
        # Entropy update on graph
        # dS/dt = DS * graphLaplacian(S) - mu*Phi + chi*(flow_intensity) + noise
        # -----------------------------

        newS = {}
        for s in nodes:
            deg = len(adj[s])
            if deg == 0:
                lap = 0.0
            else:
                lap = sum(S[nbr] - S[s] for nbr in adj[s])  # unnormalized Laplacian

            flow_intensity = 0.0
            if out_edges[s]:
                flow_intensity += sum(abs(F[e]) for e in out_edges[s])
            if in_edges[s]:
                flow_intensity += sum(abs(F[e]) for e in in_edges[s])

            dS = DS * lap - mu * Phi[s] + chi * flow_intensity
            dS += random.uniform(-ent_noise, ent_noise)
            newS[s] = S[s] + dt * dS

        for s in nodes:
            newS[s] = clamp(newS[s], S_cap[0], S_cap[1])
        S = newS

        # -----------------------------
        # Visual update: nodes scale/color, edges radius/color, pruning by entropy
        # -----------------------------

        for s in nodes:
            obj = objs[s]

            phi = Phi[s]
            ent = S[s]

            scale = 0.14 + 0.12 * phi
            obj.scale = (scale, scale, scale)

            if ent > collapse_threshold:
                obj.hide_viewport = True
                obj.hide_render = True
            else:
                obj.hide_viewport = False
                obj.hide_render = False

            set_node_color(obj, phi, ent)

            obj.keyframe_insert(data_path="scale", frame=f)
            obj.keyframe_insert(data_path="color", frame=f)
            obj.keyframe_insert(data_path="hide_viewport", frame=f)
            obj.keyframe_insert(data_path="hide_render", frame=f)

        for (s, t) in edges:
            obj = edge_obj.get((s, t))
            if obj is None:
                continue

            flux = F[(s, t)]

            # The cylinder was built with some initial radius; scale X/Y to change radius.
            r = edge_radius_base + edge_radius_gain * min(1.0, abs(flux))
            obj.scale = (r / 0.03, r / 0.03, 1.0)  # because cylinder radius was 0.03

            set_edge_color(obj, flux)

            obj.keyframe_insert(data_path="scale", frame=f)
            obj.keyframe_insert(data_path="color", frame=f)

    # ------------------------------------------------------------
    # Render
    # ------------------------------------------------------------

    os.makedirs(anim_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = os.path.join(anim_dir, "frame_")
    bpy.ops.render.render(animation=True, write_still=True)