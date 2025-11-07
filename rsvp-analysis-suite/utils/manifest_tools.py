"""
manifest_tools.py

Generates SHA-256 manifests, timestamps, and reproducibility metadata for RSVP simulations.

Purpose:
- Verify integrity of input/output files
- Track reproducibility across runs

Inputs:
- File paths, metadata dicts

Outputs:
- Manifest dictionary
- Optional JSON file

Testing Focus:
- Correct hash generation
- Metadata completeness
"""
from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime


def compute_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_manifest(file_paths: list[str], metadata: dict = None) -> dict:
    manifest = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'files': {},
        'metadata': metadata or {}
    }
    for path in file_paths:
        if os.path.isfile(path):
            manifest['files'][path] = compute_sha256(path)
    return manifest


def save_manifest(manifest: dict, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)


# Demo harness
if __name__ == '__main__':
    print('manifest_tools demo')
    files = ['demo_log.jsonl']
    manifest = generate_manifest(files, metadata={'run_id': 1})
    save_manifest(manifest, 'demo_manifest.json')
    print('Manifest saved:', manifest)

