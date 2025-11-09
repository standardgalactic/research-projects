#!/usr/bin/env python3
\"\"\"SpherePOP minimal interpreter demo
Run: python3 -m spherepop.cli demo
\"\"\"
import json, argparse, sys, uuid
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Sphere:
    id: str
    types: List[str]
    modalities: Dict[str, str]
    entropy: float = 0.0
    provenance: List[str] = field(default_factory=list)

class Rule:
    def __init__(self, name, input_mod, output_mod, budget, func):
        self.name = name
        self.input_mod = input_mod
        self.output_mod = output_mod
        self.budget = budget
        self.func = func

# simple in-memory store
SPHERES = {}
RULES = {}

def make_sphere(types, modalities):
    sid = str(uuid.uuid4())[:8]
    s = Sphere(id=sid, types=types, modalities=modalities, entropy=0.0, provenance=[])
    SPHERES[sid] = s
    return s

def register_rule(rule):
    RULES[rule.name] = rule

def pop(src_id, dst_id, rule_chain):
    src = SPHERES[src_id]
    dst = SPHERES[dst_id]
    current = src
    for rname in rule_chain:
        r = RULES[rname]
        if r.input_mod not in current.modalities:
            raise Exception(f"Missing modality {r.input_mod} for rule {rname}")
        out = r.func(current.modalities[r.input_mod])
        # simple entropy accounting
        new_entropy = dst.entropy + 0.01
        if new_entropy > dst.entropy + r.budget + 1e-9:
            raise Exception("Entropy budget exceeded")
        dst.modalities[r.output_mod] = out
        dst.entropy = new_entropy
        dst.provenance.append(f"{rname}@{current.id}")
    return dst

# demo rules
def tts(text):
    return f"<audio:{text[:32]}...>"

def summarize(text):
    return text.split('.')[0] + '.'

def create_demo():
    a = make_sphere(['text'], {'text': "Entropy bounds matter. PlenumHub demo."})
    b = make_sphere(['text','audio'], {'text': ""})
    register_rule(Rule('tts','text','audio',0.05,tts))
    register_rule(Rule('summ','text','text',0.02,summarize))
    return a,b

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['demo'])
    args = parser.parse_args()
    if args.command == 'demo':
        a,b = create_demo()
        print("Created spheres:", a.id, b.id)
        pop(a.id, b.id, ['summ'])
        pop(a.id, b.id, ['tts'])
        print("Result modalities:", b.modalities)
if __name__ == '__main__':
    cli()
