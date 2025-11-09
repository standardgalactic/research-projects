from typing import Dict, List
import numpy as np
from ontology import ONTOLOGY

def tag_from_embedding(embedding: List[float]) -> Dict[str,float]:
    """
    Placeholder: map embedding to ontology dimensions.
    Replace with trained regressors mapping embedding -> score [0,1].
    """
    dims = [d["name"] for d in ONTOLOGY["dimensions"]]
    # Simple deterministic projection for demo
    rng = np.random.RandomState(sum(int(255*x) for x in embedding[:3]) if len(embedding)>=3 else 0)
    return {name: float(rng.rand()) for name in dims}

def project_to_persona(scores: Dict[str,float]) -> Dict[str,float]:
    personas = ONTOLOGY["persona_projection"]
    out = {}
    for p, dims in personas.items():
        out[p] = float(sum(scores.get(d,0) for d in dims)/len(dims))
    return out
