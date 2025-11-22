import bpy
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
parser.add_argument('--grid', type=int, default=40)
    parser.add_argument('--steps', type=int, default=100)
    parser.add_argument('--boundary_type', type=str, default='periodic')
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    print("RSVP boundary conditions:", vars(args))

    # TODO: insert theory-specific simulation / geometry here.
    # This template only sets up argument parsing and saving.

    # Save .blend file as a marker that the script ran.
    bpy.ops.wm.save_mainfile(filepath=os.path.join(args.output, "scene.blend"))

if __name__ == "__main__":
    main()
