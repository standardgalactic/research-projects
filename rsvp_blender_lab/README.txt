RSVP Blender Lab

Structure:

core_engine.py
    Shared grid simulation engine and scene utilities.

experiments/
    regulated_instability.py
    smoothing.py
    phase_separation.py

How to use in Blender:

1. Open Blender.
2. Go to Scripting workspace.
3. Open one of the experiment files.
4. Ensure the folder containing core_engine.py is in the same directory.
5. Run the experiment script.
6. Press Play.

To extend:
    Define a new rule(sim, phi, dt) function
    Create a new experiment file importing core_engine
