import bpy, argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
parser.add_argument('--lattice', type=int, default=64)
parser.add_argument('--iterations', type=int, default=200)
args = parser.parse_args()
os.makedirs(args.output, exist_ok=True)
print("RSVP lattice sim:", args)
bpy.ops.wm.save_mainfile(filepath=os.path.join(args.output, "scene.blend"))
