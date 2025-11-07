"""
logging_utils.py

Structured logging for RSVP simulations.
Records per-step JSON events and overall run metadata.

Purpose:
- Ensure reproducibility and traceability of simulation runs.
- Produce machine-readable JSON logs.

Inputs:
- Event dicts, run metadata
- Output path

Outputs:
- JSONL log file

Testing Focus:
- Correct JSON formatting
- Per-step log consistency
"""
from __future__ import annotations
import json
import os


def initialize_log(output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('')  # clear existing file


def log_event(event: dict, output_path: str) -> None:
    with open(output_path, 'a') as f:
        f.write(json.dumps(event) + '\n')


def log_run_metadata(metadata: dict, output_path: str) -> None:
    event = {'type': 'metadata', 'data': metadata}
    log_event(event, output_path)


# Demo harness
if __name__ == '__main__':
    print('logging_utils demo')
    output_file = 'demo_log.jsonl'
    initialize_log(output_file)
    log_run_metadata({'run_id': 1, 'description': 'test run'}, output_file)
    log_event({'step': 0, 'Phi_min': 0.1, 'Phi_max': 1.2}, output_file)
    print('Demo log written to', output_file)

