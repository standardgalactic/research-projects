import bpy
import argparse
import os

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
parser.add_argument('--steps', type=int, default=80)
    parser.add_argument('--eta0', type=float, default=0.1)
    parser.add_argument('--eta1', type=float, default=0.08)
    parser.add_argument('--eta2', type=float, default=0.05)
    parser.add_argument('--eta3', type=float, default=0.02)
    return parser.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)
    print("CLIO single agent levels:", vars(args))

    # TODO: insert theory-specific simulation / geometry here.
    # This template only sets up argument parsing and saving.

    # Save .blend file as a marker that the script ran.
    bpy.ops.wm.save_mainfile(filepath=os.path.join(args.output, "scene.blend"))

if __name__ == "__main__":
    main()
