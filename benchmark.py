from curator import route_memory
from random import choice
failures = ["hoarding","brittleness","never_converging","myopia","over_coordination"]
templates = {
"hoarding":"Note from 1998: {idea} might be useful someday. Context: {story}.",
"brittleness":"Proof: {deriv}. Assume axioms A,B,C. Result follows. No examples.",
"never_converging":"Idea: {A} + {B} = ? What if {ext}? Keep exploring.",
"myopia":"Tactic: Do X to get funding. Ignore theory. Works 60% of time.",
"over_coordination":"Meta: Should we route this to A or B? Log routing debate. Re-evaluate in 3 months."
}
def gen(mode):
    return templates[mode].format(
        idea=choice(["flux capacitors","neural lace","quantum spoons"]),
        story="lorem ipsum "*10,
        deriv="∀x ∈ ℝ ...",
        A=choice(["AI","blockchain","CRISPR"]),
        B=choice(["poetry","dance","medieval history"]),
        ext=choice(["in 12D","with emotions","on Mars"])
    )

if __name__ == '__main__':
    results={}
    for m in failures:
        mem = gen(m)
        routed = route_memory(mem, phase="discovery")
        results[m]=routed["routing"]["primary_owner"]
    print(results)
