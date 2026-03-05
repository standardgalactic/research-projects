import os
import bpy
import sys
import argparse
import os

sys.path.append(os.path.dirname(__file__))

from scenes_history_dag import build_history_dag
from scenes_crdt_convergence import build_crdt_convergence
from scenes_history_lattice import build_history_lattice
from scenes_entropy_collapse import build_entropy_collapse
from scenes_ising_descent import build_ising_descent

def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--")+1:]

    p = argparse.ArgumentParser()
    p.add_argument("--scene", required=True)
    p.add_argument("--blend", required=True)
    p.add_argument("--png", required=True)

    return p.parse_args(argv)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def render_image(path):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = path
    scene.render.resolution_x = 2000
    scene.render.resolution_y = 1200

    bpy.ops.render.render(write_still=True)

args = parse_args()

reset()

scene = bpy.context.scene

if args.scene == "history_dag":
    build_history_dag(scene)

elif args.scene == "crdt_convergence":
    build_crdt_convergence(scene, None)

elif args.scene == "history_lattice":
    build_history_lattice(scene)

elif args.scene == "entropy_collapse":
    build_entropy_collapse(scene, None)

elif args.scene == "ising_descent":
    build_ising_descent(scene, None)

# save .blend
bpy.ops.wm.save_as_mainfile(filepath=args.blend)

# render image
render_image(args.png)
