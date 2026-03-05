import bpy
import os
import sys
import importlib
import inspect


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)


def discover_scenes():

    scenes = {}

    base_dir = os.path.dirname(__file__)

    for fname in os.listdir(base_dir):

        if not fname.startswith("scenes_") or not fname.endswith(".py"):
            continue

        module_name = fname[:-3]

        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module):

            if inspect.isfunction(obj) and name.startswith("build_"):
                key = name.replace("build_", "")
                scenes[key] = obj

    return scenes


def parse_args():

    argv = sys.argv

    if "--" not in argv:
        return None

    argv = argv[argv.index("--") + 1:]

    if len(argv) == 0:
        return None

    return argv[0]


def run_scene(scene_name, anim_dir="./renders"):

    scene = bpy.context.scene

    clear_scene()

    scenes = discover_scenes()

    if scene_name not in scenes:
        raise ValueError(
            f"Scene '{scene_name}' not found. Available: {list(scenes.keys())}"
        )

    builder = scenes[scene_name]

    try:
        builder(scene, os.path.join(anim_dir, scene_name))
    except TypeError:
        builder(scene)


def main():

    scene_name = parse_args()

    scenes = discover_scenes()

    # If a scene is specified, run only that
    if scene_name is not None:
        run_scene(scene_name)
        return

    # Otherwise run all scenes
    print("No scene specified — rendering all scenes\n")

    for name in scenes:
        print(f"Running {name}")
        run_scene(name)


if __name__ == "__main__":
    main()