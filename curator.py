from typing import Dict, Any
import uuid
from datetime import datetime
import numpy as np
from jsonschema import validate
import json
SCHEMA_PATH = "memory_routing_schema.json"

# Simple softmax
def softmax(vec):
    e = np.exp(vec - np.max(vec))
    return (e / e.sum()).tolist()

def score_for_personas(content: str, phase: str="discovery") -> Dict[str,float]:
    # Heuristic scoring (replace with LLM or trained classifier)
    scores = {"archivist":0.1,"formalist":0.1,"synthesist":0.1,"strategist":0.1}
    lc = content.lower()
    if any(k in lc for k in ["dismissed","may be relevant","archive","old paper","forgotten"]):
        scores["archivist"] += 0.6
    if any(k in lc for k in ["theorem","prove","lemma","derive","proof"]):
        scores["formalist"] += 0.7
    if any(k in lc for k in ["what if","reframe","combine","synthesize","hybrid"]):
        scores["synthesist"] += 0.7
    if any(k in lc for k in ["%","scale","deploy","implement","fund","adoption","traction"]):
        scores["strategist"] += 0.7
    # phase bias
    phase_bias = {"discovery":{"synthesist":0.2}, "preservation":{"archivist":0.2},
                  "distillation":{"formalist":0.2}, "deployment":{"strategist":0.2}}
    for p,b in phase_bias.get(phase,{}).items():
        scores[p] = min(1.0, scores.get(p,0)+b)
    weights = softmax(list(scores.values()))
    persona_keys = list(scores.keys())
    weights_dict = dict(zip(persona_keys, [round(float(w),3) for w in weights]))
    primary = max(weights_dict, key=lambda k: weights_dict[k])
    return weights_dict, primary

def route_memory(content: str, phase: str="discovery") -> Dict[str,Any]:
    weights, primary = score_for_personas(content, phase)
    record = {
        "memory_id": str(uuid.uuid4()),
        "content": content,
        "metadata": {"source":"user", "timestamp": datetime.utcnow().isoformat(), "project_phase": phase},
        "routing": {
            "primary_owner": primary,
            "weights": weights,
            "lifecycle": {
                "review_in_months": 6 if primary in ["synthesist","archivist"] else 3,
                "prune_if_unused_after_months": 12
            },
            "tags": [primary, phase]
        },
        "curator_meta": {"drift_score":0.0, "last_rebalance": datetime.utcnow().isoformat(), "alerts":[]}
    }
    # Validate against schema if available
    try:
        with open(SCHEMA_PATH) as f:
            schema = json.load(f)
            validate(instance=record, schema=schema)
    except Exception:
        # skip validation in this environment if jsonschema not available
        pass
    return record

if __name__ == "__main__":
    example = "12% decoherence reduction → enables 1000-qubit scale-up by 2027."
    print(json.dumps(route_memory(example, phase="deployment"), indent=2))
