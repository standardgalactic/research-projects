import bpy
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SCRIPTS = [
("fr_01_rotor_geometry.py", "fr_01_geometry.blend"),
("fr_02_thermal_system.py", "fr_02_thermal.blend"),
("fr_03_animation_v3.py", "fr_03_animation.blend"),
]

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def run_stage(script_path, blend_name):
    print(f"\n=== Running {script_path} ===")

    reset_scene()

    # Execute your script
    script_abs = os.path.abspath(script_path)

    with open(script_abs, "r") as f:
        code = compile(f.read(), script_abs, 'exec')
        exec(code, globals())

    # Save result
    output_path = os.path.join(OUTPUT_DIR, blend_name)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)

    print(f"Saved: {output_path}")

for script, blend in SCRIPTS:
    run_stage(script, blend)

print("\n=== All stages complete ===")
