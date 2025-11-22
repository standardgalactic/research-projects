import bpy, argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
parser.add_argument('--depth', type=int, default=4)
parser.add_argument('--tiles', type=int, default=8)
args = parser.parse_args()
os.makedirs(args.output, exist_ok=True)
print("TARTAN recursive tiling:", args)
bpy.ops.wm.save_mainfile(filepath=os.path.join(args.output, "scene.blend"))
