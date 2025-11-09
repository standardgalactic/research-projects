"""
plenumhub.core
Expanded reference runtime for the PlenumHub Sphere / Rule / Interpreter model.
- Sphere: multimodal typed object with entropy and provenance
- Rule: typed operator with entropy budget and deterministic implementation
- Interpreter: executes rule-chains (pop), merge with entropy guard, Media-Quine closure (simplified)
- Proofs: simple Merkle-style fingerprinting of provenance for a proof-carrying trace
This is a compact, reference-grade implementation intended for prototyping and tests.
"""

from __future__ import annotations
import json, hashlib, time, copy
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Optional

# ---------------------- Exceptions ----------------------
class PlenumError(Exception):
    pass

class TypeErrorPlenum(PlenumError):
    pass

class EntropyError(PlenumError):
    pass

class MergeError(PlenumError):
    pass

# ---------------------- Utilities ----------------------
def fingerprint(obj: Any) -> str:
    """Deterministic fingerprint for small objects (JSON canonicalization + sha256)."""
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---------------------- Core data types ----------------------
@dataclass
class ProvenanceNode:
    """A node in the provenance DAG: records the rule applied, input sphere ids, timestamp, and fingerprint"""
    rule_id: str
    inputs: List[str]
    output_id: str
    timestamp: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        return fingerprint({
            "rule_id": self.rule_id,
            "inputs": sorted(self.inputs),
            "output_id": self.output_id,
            "timestamp": round(self.timestamp, 6),
            "meta": self.meta,
        })

@dataclass
class Sphere:
    id: str
    types: List[str]                 # required modalities keys, e.g. ["text","audio","code"]
    content: Dict[str, Any]          # modality -> value
    entropy: float = 0.0             # semantic entropy (nonnegative)
    provenance: List[ProvenanceNode] = field(default_factory=list)

    def is_well_typed(self) -> bool:
        return all(k in self.content and self.content[k] is not None for k in self.types)

    def fingerprint(self) -> str:
        # include identity, types, content keys, entropy and provenance fingerprints
        prov_fps = [p.fingerprint() for p in self.provenance]
        return fingerprint({
            "id": self.id,
            "types": sorted(self.types),
            "content_keys": sorted(list(self.content.keys())),
            "entropy": round(self.entropy, 9),
            "prov": prov_fps
        })

    def copy(self) -> "Sphere":
        return copy.deepcopy(self)

# ---------------------- Rule registry ----------------------
class Rule:
    def __init__(self, id: str, src: str, dst: str, entropy_budget: float, impl):
        """
        impl: a callable impl(value, ctx) -> (new_value, delta_entropy, meta)
        src/dst are modality keys (e.g., 'text' -> 'audio')
        """
        self.id = id
        self.src = src
        self.dst = dst
        self.entropy_budget = float(entropy_budget)
        self.impl = impl

    def apply(self, sphere: Sphere, ctx: Optional[Dict]=None) -> Tuple[Sphere, ProvenanceNode]:
        if ctx is None: ctx = {}
        if self.src not in sphere.content or sphere.content[self.src] is None:
            raise TypeErrorPlenum(f"Rule {self.id} expects modality '{self.src}' present on sphere {sphere.id}")
        src_val = sphere.content[self.src]
        new_val, delta_e, meta = self.impl(src_val, ctx)
        if delta_e > self.entropy_budget + 1e-12:
            raise EntropyError(f"Rule {self.id} would increase entropy by {delta_e} > budget {self.entropy_budget}")
        new_sphere = sphere.copy()
        new_sphere.content[self.dst] = new_val
        new_sphere.entropy = max(0.0, new_sphere.entropy + delta_e)
        # provenance node
        node = ProvenanceNode(rule_id=self.id, inputs=[sphere.id], output_id=new_sphere.id, meta=meta)
        new_sphere.provenance.append(node)
        return new_sphere, node

class RuleRegistry:
    def __init__(self):
        self._rules = {}

    def register(self, rule: Rule):
        if rule.id in self._rules:
            raise PlenumError(f"Rule {rule.id} already registered")
        self._rules[rule.id] = rule

    def get(self, rule_id: str) -> Rule:
        if rule_id not in self._rules:
            raise PlenumError(f"Unknown rule {rule_id}")
        return self._rules[rule_id]

# ---------------------- Interpreter ----------------------
class Interpreter:
    def __init__(self, registry: RuleRegistry, merge_merge_eps: float=0.05):
        self.registry = registry
        self.spheres: Dict[str, Sphere] = {}
        self.merge_eps = float(merge_merge_eps)

    def add_sphere(self, s: Sphere):
        if s.id in self.spheres:
            raise PlenumError(f"Sphere {s.id} already exists")
        self.spheres[s.id] = s.copy()

    def get(self, sid: str) -> Sphere:
        if sid not in self.spheres:
            raise PlenumError(f"Sphere {sid} not found")
        return self.spheres[sid].copy()

    def pop(self, source_id: str, target_id: str, rule_chain: List[str]) -> Sphere:
        """
        Apply a sequence of rules starting from source sphere, writing into the target sphere.
        This implements the big-step judgment: source ↓_R result
        Each rule must type-match (src -> dst) with available modalities.
        Entropy budgets checked per-rule and overall via provenance.
        """
        src = self.get(source_id)
        tgt = self.get(target_id)
        curr = src.copy()
        for rid in rule_chain:
            rule = self.registry.get(rid)
            # ensure modality availability
            if rule.src not in curr.content or curr.content[rule.src] is None:
                raise TypeErrorPlenum(f"Rule {rid} requires modality {rule.src} present in intermediate sphere")
            curr, node = rule.apply(curr, ctx={"target": target_id})
        # After chain, merge produced modalities into target (entropy-guarded merge)
        merged = self._merge_spheres(curr, tgt, allow_overwrite=True)
        # store merged result as new sphere in interpreter
        self.spheres[merged.id] = merged.copy()
        return merged

    def _merge_spheres(self, a: Sphere, b: Sphere, allow_overwrite: bool=False) -> Sphere:
        """
        Entropy-bounded merge: result's entropy must be <= max(entropies) + merge_eps.
        If overwrite allowed, modalities from `a` replace `b` when present.
        """
        max_e = max(a.entropy, b.entropy)
        # naive merged entropy estimate: max + small delta for combining content differences
        # In a prototype we compute content-key mismatch penalty
        mismatch_penalty = 0.0
        keys = set(a.content.keys()) | set(b.content.keys())
        for k in keys:
            va = a.content.get(k)
            vb = b.content.get(k)
            if va is None and vb is None: continue
            if va is None or vb is None:
                mismatch_penalty += 0.01
            elif fingerprint(va) != fingerprint(vb):
                mismatch_penalty += 0.02
        e_m = max_e + mismatch_penalty
        if e_m > max_e + self.merge_eps + 1e-12:
            raise MergeError(f"Merge would exceed entropy allowance: {e_m:.4f} > {max_e + self.merge_eps:.4f}")
        # construct merged sphere
        out = b.copy()
        # canonical id is b.id to preserve target identity
        out.entropy = e_m
        # copy/overwrite content
        for k, v in a.content.items():
            if allow_overwrite or k not in out.content or out.content[k] is None:
                out.content[k] = v
        # append provenance nodes (fingerprint them)
        out.provenance.extend(a.provenance)
        return out

    def merge(self, a_id: str, b_id: str, out_id: Optional[str]=None) -> Sphere:
        a = self.get(a_id)
        b = self.get(b_id)
        merged = self._merge_spheres(a, b, allow_overwrite=False)
        # set canonical id
        if out_id:
            merged.id = out_id
        else:
            merged.id = b.id
        self.spheres[merged.id] = merged.copy()
        return merged

    def close_media_quine(self, sid: str, permitted_transducers: Dict[Tuple[str,str], str]) -> Sphere:
        """
        Attempt to synthesize missing modalities using permitted_transducers mapping (src,dst)->rule_id.
        This is a simplified closure operator: it applies available transducers greedily.
        """
        s = self.get(sid)
        changed = True
        while changed:
            changed = False
            for req in s.types:
                if req not in s.content or s.content[req] is None:
                    # find a transducer that can produce req from an existing modality
                    for (src,dst), rid in permitted_transducers.items():
                        if dst != req: continue
                        if src in s.content and s.content[src] is not None:
                            rule = self.registry.get(rid)
                            s, node = rule.apply(s, ctx={"closure": True})
                            changed = True
                            break
                    if changed: break
        # update stored sphere
        self.spheres[s.id] = s.copy()
        return s

    def emit_proof_log(self, sid: str) -> Dict[str, Any]:
        s = self.get(sid)
        return {
            "sphere_id": s.id,
            "fingerprint": s.fingerprint(),
            "provenance": [ {"rule": p.rule_id, "inputs": p.inputs, "output": p.output_id, "fp": p.fingerprint()} for p in s.provenance ]
        }
