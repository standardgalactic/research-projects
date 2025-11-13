
"""Run all labs 30–40 to regenerate frame_000.json in data/labXX/.

Usage:
    python run_all.py
"""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).parent
PYDIR = ROOT / "python"
DATADIR = ROOT / "data"

def main():
    sys.path.insert(0, str(PYDIR))
    labs = list(range(30, 41))
    for num in labs:
        name = f"lab{num}"
        try:
            mod = importlib.import_module(name)
        except Exception as e:
            print(f"[!] Could not import {name}: {e}")
            continue
        out_dir = DATADIR / name
        out_dir.mkdir(parents=True, exist_ok=True)
        try:
            # most labs expose run(output_dir=None, steps=None)
            print(f"[+] Running {name} ...")
            mod.run(output_dir=str(out_dir))
        except TypeError:
            # fallback: maybe run(output_dir)
            try:
                mod.run(str(out_dir))
            except Exception as e:
                print(f"[!] Error running {name}: {e}")
        except Exception as e:
            print(f"[!] Error running {name}: {e}")

if __name__ == "__main__":
    main()
