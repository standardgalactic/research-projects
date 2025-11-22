import bpy
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
parser.add_argument('--steps', type=int, default=120)
    parser.add_argument('--baseline_affect', type=float, default=0.5)
    parser.add_argument('--gain', type=float, default=1.3)
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    print("CLIO affective modulation:", vars(args))

    # TODO: insert theory-specific simulation / geometry here.
    # This template only sets up argument parsing and saving.

    # Save .blend file as a marker that the script ran.
    bpy.ops.wm.save_mainfile(filepath=os.path.join(args.output, "scene.blend"))

if __name__ == "__main__":
    main()
