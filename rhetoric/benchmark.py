#!/usr/bin/env python3
"""Exact reference benchmark for the Repair Theory conformance slice."""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

State = tuple[int, int, int, int]
Observation = tuple[Optional[int], Optional[int], Optional[int], Optional[int]]
Word = tuple[str, ...]

ACTIONS = ("flip_p", "flip_q", "swap_pq", "flip_mode")
STATES: tuple[State, ...] = tuple(itertools.product((0, 1), repeat=4))
HORIZON = 3
EPSILON_P = 0.05
EPSILON_U = 0.0


def valid(x: State) -> bool:
    p, q, r, _ = x
    return r == (p ^ q)


TEST_STATES: tuple[State, ...] = tuple(x for x in STATES if valid(x))


def step(x: State, action: str) -> State:
    p, q, r, m = x
    if action == "flip_p":
        return (1 - p, q, 1 - r, m)
    if action == "flip_q":
        return (p, 1 - q, 1 - r, m)
    if action == "swap_pq":
        return (q, p, r, m)
    if action == "flip_mode":
        return (p, q, r, 1 - m)
    raise ValueError(action)


def run(x: State, word: Word) -> State:
    for action in word:
        x = step(x, action)
    return x


def observable(x: State) -> tuple[int, int, int]:
    """Task output deliberately omits the causally inert mode coordinate."""
    p, q, r, _ = x
    return (p, q, r)


WORDS_BY_K: dict[int, tuple[Word, ...]] = {
    k: tuple(itertools.product(ACTIONS, repeat=k)) for k in range(HORIZON + 1)
}
WORDS: tuple[Word, ...] = tuple(w for group in WORDS_BY_K.values() for w in group)


def signature(x: State) -> tuple[tuple[int, int, int], ...]:
    return tuple(observable(run(x, w)) for w in WORDS)


def consistent(z: Observation, x: State) -> bool:
    return all(v is None or v == actual for v, actual in zip(z, x))


def info_class(damage_name: str, z: Observation) -> frozenset[State]:
    """Preimage of z under the preregistered, known damage operator."""
    damage = DAMAGES[damage_name]
    return frozenset(x for x in STATES if damage(x) == z)


def delete_parity(x: State) -> Observation:
    p, q, _, _ = x
    return (p, q, None, None)


def corrupt_parity(x: State) -> Observation:
    p, q, r, m = x
    return (p, q, 1 - r, m)


def aggregate_qr(x: State) -> Observation:
    p, _, _, m = x
    return (p, None, None, m)


DAMAGES: dict[str, Callable[[State], Observation]] = {
    "deletion": delete_parity,
    "corruption": corrupt_parity,
    "aggregation": aggregate_qr,
}


@dataclass(frozen=True)
class Claim:
    candidates: frozenset[State]
    executable: Optional[State]
    changed_components: int


def embed(z: Observation) -> State:
    return tuple(0 if v is None else v for v in z)  # type: ignore[return-value]


def hamming_observation(z: Observation, x: State) -> int:
    return sum(v is not None and v != actual for v, actual in zip(z, x))


def identity(damage_name: str, z: Observation) -> Claim:
    x = embed(z)
    return Claim(frozenset((x,)), x, sum(v is None for v in z))


def nearest_valid(damage_name: str, z: Observation) -> Claim:
    candidates = [x for x in STATES if valid(x)]
    x = min(candidates, key=lambda s: (hamming_observation(z, s), s))
    return Claim(frozenset((x,)), x, hamming_observation(z, x))


def erase(damage_name: str, z: Observation) -> Claim:
    return Claim(info_class(damage_name, z), None, 0)


def constraint_repair(damage_name: str, z: Observation) -> Claim:
    candidates = frozenset(x for x in info_class(damage_name, z) if valid(x))
    sigs = {signature(x) for x in candidates}
    executable = min(candidates) if len(sigs) == 1 and candidates else None
    changes = 0 if executable is None else hamming_observation(z, executable)
    return Claim(candidates, executable, changes)


METHODS: dict[str, Callable[[str, Observation], Claim]] = {
    "identity": identity,
    "nearest_valid": nearest_valid,
    "erase": erase,
    "constraint_repair": constraint_repair,
}


def entailed(candidates: Iterable[State], word: Word):
    values = {observable(run(x, word)) for x in candidates}
    return next(iter(values)) if len(values) == 1 else None


def reachable(x: State) -> frozenset[tuple[Word, tuple[int, int, int]]]:
    # Action-labelled reachability; an unlabelled reachable set is transitive here
    # and would erase the very intervention-conditioned distinctions under test.
    return frozenset((w, observable(run(x, w))) for w in WORDS)


def jaccard(a: frozenset, b: frozenset) -> float:
    return len(a & b) / len(a | b) if a or b else 1.0


def claim_signature(claim: Claim):
    return tuple(entailed(claim.candidates, w) for w in WORDS)


def evaluate(damage_name: str, method_name: str) -> dict:
    damage = DAMAGES[damage_name]
    method = METHODS[method_name]
    claims = {x: method(damage_name, damage(x)) for x in TEST_STATES}

    defined = sound = unsupported = empty = entailed_total = entailed_kept = 0
    behavior_by_horizon: dict[str, float] = {}
    for x in TEST_STATES:
        truth_class = info_class(damage_name, damage(x))
        claim = claims[x]
        for w in WORDS:
            truth_entailment = entailed(truth_class, w)
            answer = entailed(claim.candidates, w) if claim.candidates else None
            if truth_entailment is not None:
                entailed_total += 1
                if answer == truth_entailment:
                    entailed_kept += 1
            if not claim.candidates:
                empty += 1
            elif answer is not None:
                defined += 1
                if answer == observable(run(x, w)):
                    sound += 1
                else:
                    unsupported += 1

    for k, words in WORDS_BY_K.items():
        correct = 0
        total = len(TEST_STATES) * len(words)
        for x in TEST_STATES:
            e = claims[x].executable
            if e is not None:
                correct += sum(observable(run(e, w)) == observable(run(x, w)) for w in words)
        behavior_by_horizon[str(k)] = correct / total

    pair_den = pair_num = 0
    for i, x in enumerate(TEST_STATES):
        for xp in TEST_STATES[i + 1 :]:
            if damage(x) != damage(xp) and signature(x) != signature(xp):
                pair_den += 1
                pair_num += claim_signature(claims[x]) != claim_signature(claims[xp])

    reachability = []
    for x in TEST_STATES:
        e = claims[x].executable
        reachability.append(0.0 if e is None else jaccard(reachable(x), reachable(e)))

    execs = [c.executable for c in claims.values()]
    valid_rate = sum(e is not None and valid(e) for e in execs) / len(execs)
    baseline_valid = sum(valid(embed(damage(x))) for x in TEST_STATES) / len(TEST_STATES)
    total_queries = len(TEST_STATES) * len(WORDS)
    raw_singletons = [
        x for x in TEST_STATES if len(info_class(damage_name, damage(x))) == 1
    ]
    constrained_singletons = [
        x
        for x in TEST_STATES
        if len(frozenset(s for s in info_class(damage_name, damage(x)) if valid(s))) == 1
    ]

    def conditional_identity_accuracy(eligible: list[State]):
        if not eligible:
            return None
        return sum(claims[x].executable == x for x in eligible) / len(eligible)

    return {
        "damage": damage_name,
        "method": method_name,
        "claim_coverage": defined / total_queries,
        "claim_soundness": sound / defined if defined else 1.0,
        "unsupported_claim_rate": unsupported / defined if defined else 0.0,
        "empty_claim_rate": empty / total_queries,
        "common_behavior_completeness": entailed_kept / entailed_total if entailed_total else 1.0,
        "evidence_supported_query_rate": entailed_total / total_queries,
        "executable_coverage": sum(e is not None for e in execs) / len(execs),
        "behavior_by_horizon": behavior_by_horizon,
        "mean_behavior": sum(behavior_by_horizon.values()) / len(behavior_by_horizon),
        "distinction_retention": pair_num / pair_den if pair_den else 1.0,
        "reachability_recovery": sum(reachability) / len(reachability),
        "validity_recovery": valid_rate - baseline_valid,
        "mean_changed_components": sum(c.changed_components for c in claims.values()) / len(claims),
        "full_state_accuracy": sum(claims[x].executable == x for x in TEST_STATES) / len(TEST_STATES),
        "raw_evidence_identity": {
            "eligible_cases": len(raw_singletons),
            "accuracy": conditional_identity_accuracy(raw_singletons),
        },
        "constraint_informed_identity": {
            "eligible_cases": len(constrained_singletons),
            "accuracy": conditional_identity_accuracy(constrained_singletons),
        },
    }


def classify(rows: list[dict]) -> list[dict]:
    indexed = {(r["damage"], r["method"]): r for r in rows}
    decisions = []
    for damage in DAMAGES:
        base = indexed[(damage, "identity")]
        erase_row = indexed[(damage, "erase")]
        for method in METHODS:
            r = indexed[(damage, method)]
            repair_like = (
                r["mean_behavior"] > base["mean_behavior"]
                and r["reachability_recovery"] > base["reachability_recovery"]
                and r["distinction_retention"] >= base["distinction_retention"] - EPSILON_P
                and r["unsupported_claim_rate"] <= EPSILON_U
                and r["common_behavior_completeness"] >= erase_row["common_behavior_completeness"]
            )
            smoothing_like = (
                r["validity_recovery"] > base["validity_recovery"]
                and r["distinction_retention"] < base["distinction_retention"] - EPSILON_P
            )
            erasure_like = (
                r["evidence_supported_query_rate"] > 0
                and r["executable_coverage"] < base["executable_coverage"]
                and r["reachability_recovery"] <= base["reachability_recovery"]
            )
            ambiguity_preserving = (
                r["evidence_supported_query_rate"] == 0
                and r["unsupported_claim_rate"] == 0
                and r["executable_coverage"] == 0
            )
            decisions.append({"damage": damage, "method": method, "repair_like": repair_like, "smoothing_like": smoothing_like, "erasure_like": erasure_like, "ambiguity_preserving": ambiguity_preserving})
    return decisions


def prediction_verdicts(rows: list[dict]) -> dict:
    indexed = {(r["damage"], r["method"]): r for r in rows}
    repair_labels = {
        d["damage"]: d["repair_like"]
        for d in classify(rows)
        if d["method"] == "constraint_repair"
    }
    benefit_keys = (
        "mean_behavior",
        "distinction_retention",
        "reachability_recovery",
        "executable_coverage",
    )

    def no_worse(control: dict, repair: dict) -> bool:
        benefits_hold = all(control[k] >= repair[k] for k in benefit_keys)
        support_holds = control["unsupported_claim_rate"] <= repair["unsupported_claim_rate"]
        cost_holds = control["mean_changed_components"] <= repair["mean_changed_components"]
        return benefits_hold and support_holds and cost_holds

    general_counterexamples = []
    for damage in DAMAGES:
        if not repair_labels[damage]:
            continue
        repair = indexed[(damage, "constraint_repair")]
        for control_name in ("nearest_valid", "erase"):
            if no_worse(indexed[(damage, control_name)], repair):
                general_counterexamples.append({"damage": damage, "control": control_name})

    same_distinction_and_curves = all(
        indexed[(damage, "nearest_valid")]["distinction_retention"]
        == indexed[(damage, "constraint_repair")]["distinction_retention"]
        and indexed[(damage, "nearest_valid")]["behavior_by_horizon"]
        == indexed[(damage, "constraint_repair")]["behavior_by_horizon"]
        for damage in DAMAGES
    )

    # Identity credit is emitted only on explicitly counted singleton classes.
    epistemic_violations = []
    for r in rows:
        for field in ("raw_evidence_identity", "constraint_informed_identity"):
            identity = r[field]
            if identity["eligible_cases"] == 0 and identity["accuracy"] is not None:
                epistemic_violations.append({"damage": r["damage"], "method": r["method"], "field": field})

    erasure_counterexamples = []
    for damage in DAMAGES:
        erase_row = indexed[(damage, "erase")]
        repair = indexed[(damage, "constraint_repair")]
        base = indexed[(damage, "identity")]
        if (
            erase_row["mean_behavior"] == repair["mean_behavior"]
            and erase_row["reachability_recovery"] == repair["reachability_recovery"]
            and (erase_row["mean_behavior"] > base["mean_behavior"] or erase_row["reachability_recovery"] > base["reachability_recovery"])
        ):
            erasure_counterexamples.append({"damage": damage})

    return {
        "general_prediction": {"verdict": "failed" if general_counterexamples else "held", "counterexamples": general_counterexamples},
        "distinction_retention_prediction": {"verdict": "failed" if same_distinction_and_curves else "held"},
        "epistemic_boundary_prediction": {"verdict": "failed" if epistemic_violations else "held", "violations": epistemic_violations},
        "erasure_diagnosis": {"verdict": "failed" if erasure_counterexamples else "held", "counterexamples": erasure_counterexamples},
    }


def self_check(rows: list[dict]) -> None:
    assert len(STATES) == 16
    assert len(WORDS) == 1 + 4 + 16 + 64
    assert all(valid(step(x, a)) for x in STATES if valid(x) for a in ACTIONS)
    assert all(info_class(d, DAMAGES[d](x)) for d in DAMAGES for x in STATES)
    for x in TEST_STATES:
        deletion_candidates = frozenset(
            s for s in info_class("deletion", delete_parity(x)) if valid(s)
        )
        assert len(deletion_candidates) == 2
        assert len({signature(s) for s in deletion_candidates}) == 1
    for row in rows:
        for key, value in row.items():
            if key in {"damage", "method", "behavior_by_horizon", "mean_changed_components", "validity_recovery", "raw_evidence_identity", "constraint_informed_identity"}:
                continue
            assert 0.0 <= value <= 1.0, (key, value)
        assert -1.0 <= row["validity_recovery"] <= 1.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    rows = [evaluate(d, m) for d in DAMAGES for m in METHODS]
    self_check(rows)
    report = {
        "benchmark": "repair-theory-conformance-v1",
        "horizon": HORIZON,
        "state_count": len(STATES),
        "valid_test_state_count": len(TEST_STATES),
        "query_count_per_state": len(WORDS),
        "parameters": {"epsilon_P": EPSILON_P, "epsilon_U": EPSILON_U},
        "metrics": rows,
        "decisions": classify(rows),
        "prediction_verdicts": prediction_verdicts(rows),
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for r in rows:
        print(f"{r['damage']:11} {r['method']:18} B={r['mean_behavior']:.3f} P={r['distinction_retention']:.3f} Q={r['reachability_recovery']:.3f} U={r['unsupported_claim_rate']:.3f} K={r['executable_coverage']:.3f}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
