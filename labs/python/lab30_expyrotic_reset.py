"""RSVP Lab 30 — Expyrotic Reset

This is a scaffold module. Intended pattern:

- define `default_params` dict
- define `init(params)` -> state
- define `step(state, params, dt)` -> new_state
- define `serialize(state)` -> JSON-serializable frame

Then call `run()` to write frames into data/lab30_expyrotic_reset/.

Replace the placeholder print with real simulation logic.
"""

from pathlib import Path
import json

def run(output_dir: str = f"data/lab30_expyrotic_reset", n_steps: int = 100) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    # TODO: replace with actual simulation loop
    dummy = {
        "lab": 30,
        "title": "Expyrotic Reset",
        "note": "placeholder frame; implement simulation to populate this structure"
    }
    with open(out / "frame_000.json", "w") as f:
        json.dump(dummy, f)
    print(f"Lab 30 placeholder frame written to {out / 'frame_000.json'}")

if __name__ == "__main__":
    run()
