#!/usr/bin/env python3
"""prune_daemon.py
Runs pruning policy daily (or via cron). Moves pruned memories to archives/ directory.
"""
import os, json, shutil
from pathlib import Path
from datetime import datetime, timedelta

MEM_DIR = Path(os.getenv('MEM_DIR', 'to_process/memories'))
ARCHIVE_DIR = MEM_DIR.parent / 'archives'
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

def load_mem(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except:
        return None

def should_prune(data, months_unused_threshold=12):
    # Simple heuristic: if state is 'candidate' and not used and older than threshold
    if not data: return False
    state = data.get('state_machine',{}).get('state','candidate')
    created = data.get('created_at')
    if not created: return False
    created_dt = datetime.fromisoformat(created.replace('Z',''))
    if state in ('pruned','archived'):
        return False
    age_months = (datetime.utcnow() - created_dt).days / 30.0
    if state == 'candidate' and age_months > months_unused_threshold:
        return True
    # additional heuristics: low weights across personas
    weights = data.get('curator',{}).get('weights',{})
    if weights and max(weights.values()) < 0.15 and age_months > 6:
        return True
    return False

def prune_all():
    for p in MEM_DIR.glob('*.memory'):
        d = load_mem(p)
        if should_prune(d):
            dest = ARCHIVE_DIR / p.name
            shutil.move(str(p), str(dest))
            # move vector if exists
            v = p.with_suffix('.vector')
            if v.exists():
                shutil.move(str(v), str(ARCHIVE_DIR / v.name))
            print('Pruned', p.name)

if __name__ == '__main__':
    prune_all()
