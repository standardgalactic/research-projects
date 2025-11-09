"""
Minimal demo for plenumhub.core
Creates two spheres, registers a TTS-like rule (text->audio),
applies a pop, attempts merge, and runs Media-Quine closure.
"""
from plenumhub.core import Sphere, Rule, RuleRegistry, Interpreter, ProvenanceNode

def tts_impl(text: str, ctx):
    # deterministic "audio" rendering: reverse string + simple entropy cost
    audio = f"<audio::{text[::-1]}>"
    # delta entropy is small if text not too short
    delta_e = 0.01 if len(text) > 5 else 0.02
    meta = {"len": len(text), "ctx": ctx}
    return audio, delta_e, meta

def summarize_impl(text: str, ctx):
    # trivial summary: first sentence or first 30 chars
    s = text.split(".")[0]
    s = s if len(s) > 0 else text[:30]
    delta_e = -0.005  # reduction in entropy by summarization
    meta = {"method": "trivial"}
    return s, delta_e, meta

def make_demo():
    reg = RuleRegistry()
    reg.register(Rule("tts", src="text", dst="audio", entropy_budget=0.02, impl=tts_impl))
    reg.register(Rule("summ", src="text", dst="text", entropy_budget=0.05, impl=summarize_impl))

    interp = Interpreter(registry=reg, merge_merge_eps=0.05)

    sA = Sphere(id="A", types=["text","audio"], content={"text": "Entropy bounds matter in collaborative systems."}, entropy=0.05)
    sB = Sphere(id="B", types=["text","audio"], content={"text": "Legacy doc without audio."}, entropy=0.04)

    interp.add_sphere(sA)
    interp.add_sphere(sB)

    print("Initial spheres:")
    print(interp.get("A").content, interp.get("A").entropy)
    print(interp.get("B").content, interp.get("B").entropy)

    # Apply pop: use tts on A and merge into B
    result = interp.pop(source_id="A", target_id="B", rule_chain=["tts"])
    print("\\nAfter pop (A -> B via tts):")
    print("B content:", interp.get("B").content)
    print("B entropy:", interp.get("B").entropy)

    # Attempt merge A and B (should be fine)
    merged = interp.merge("A", "B", out_id="M")
    print("\\nMerged sphere M content keys:", sorted(list(merged.content.keys())), "entropy:", merged.entropy)
    print("Proof log for M:", interp.emit_proof_log("M"))

    # Media-Quine closure: attempt to synthesize missing modalities using permitted transducers
    permitted = {("text","audio"): "tts"}
    closed = interp.close_media_quine("B", permitted_transducers=permitted)
    print("\\nAfter closure of B:", closed.content, closed.entropy)
    print("Closure proof:", interp.emit_proof_log("B"))

if __name__ == '__main__':
    make_demo()
