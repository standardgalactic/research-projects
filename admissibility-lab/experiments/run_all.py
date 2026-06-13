"""
Run all experiments in sequence.
Usage: python -m experiments.run_all
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from experiments import (
    exp01_repair_corridor,
    exp02_sink_formation,
    exp03_trajectory_archaeology,
    exp04_archaeology,
    exp05_generator,
    exp06_metrics_series,
)

if __name__ == "__main__":
    print("\n" + "▓" * 70)
    print("ADM-LAB EXPERIMENT SUITE")
    print("▓" * 70)

    experiments = [
        ("[1/6] Repair Corridor Discovery",          exp01_repair_corridor),
        ("[2/6] Sink Formation Under Constraints",   exp02_sink_formation),
        ("[3/6] Trajectory Archaeology (basic)",     exp03_trajectory_archaeology),
        ("[4/6] Trajectory Archaeology (fidelity)",  exp04_archaeology),
        ("[5/6] Generative Compression",             exp05_generator),
        ("[6/6] Metrics Series",                     exp06_metrics_series),
    ]

    for label, mod in experiments:
        print(f"\n{'▒'*70}")
        print(label)
        print('▒'*70)
        mod.run()

    print("\n" + "▓" * 70)
    print("All experiments complete.")
    print("▓" * 70)
