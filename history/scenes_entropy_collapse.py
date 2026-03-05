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

    relaxation = 0.07      # descent rate
    noise_amp = 0.03       # small thermal jitter


    def generate_targets():

        targets = []

        for g in range(groups):
            targets.append(
                Vector(
                    (
                        g * 1.6,
                        random.uniform(-1.2, 1.2),
                        random.uniform(-0.6, 0.6),
                    )
                )
            )

        return targets


    def create_coarse_nodes(targets):

        coarse_objs = []

        for g, t in enumerate(targets):

            obj = add_sphere(
                t,
                radius=0.22,
                name=f"R_{g}",
                material=mat_coarse,
                collection=col,
            )

            coarse_objs.append(obj)

        return coarse_objs


    def create_fine_nodes(targets):

        particles = []

        for g, target in enumerate(targets):

            for i in range(per_group):

                start = target + Vector(
                    (
                        random.uniform(-2.0, -0.5),
                        random.uniform(-1.3, 1.3),
                        random.uniform(-1.0, 1.0),
                    )
                )

                obj = add_sphere(
                    start,
                    radius=0.11,
                    name=f"h_{g}_{i}",
                    material=mat_fine,
                    collection=col,
                )

                particles.append(
                    {
                        "obj": obj,
                        "pos": start.copy(),
                        "target": target.copy(),
                    }
                )

        return particles


    def simulate_relaxation(particles):

        for p in particles:
            p["obj"].location = p["pos"]
            p["obj"].keyframe_insert("location", frame=1)

        for frame in range(2, frames + 1):

            for p in particles:

                pos = p["pos"]
                target = p["target"]

                # gradient descent step
                step = (target - pos) * relaxation

                # small stochastic jitter
                noise = Vector(
                    (
                        random.uniform(-noise_amp, noise_amp),
                        random.uniform(-noise_amp, noise_amp),
                        random.uniform(-noise_amp, noise_amp),
                    )
                )

                pos += step + noise

                p["pos"] = pos

                obj = p["obj"]
                obj.location = pos
                obj.keyframe_insert("location", frame=frame)


    targets = generate_targets()

    create_coarse_nodes(targets)

    particles = create_fine_nodes(targets)

    scene.frame_start = 1
    scene.frame_end = frames

    simulate_relaxation(particles)


    if anim_dir:

        os.makedirs(anim_dir, exist_ok=True)

        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = os.path.join(anim_dir, "frame_")

        bpy.ops.render.render(animation=True, write_still=True)