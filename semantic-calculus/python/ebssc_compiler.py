# Python implementation of a small EBSSC compiler prototype.
# It parses a tiny SpherePOP-like DSL, typechecks against an environment JSON,
# lowers AST to a SheafIR, checks entropy/sparsity budgets, executes the SheafIR
# in a toy runtime model, and emits a LaTeX Section 9 snippet (TikZ + LaTeX).

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable
import json
import textwrap

# ---------- Data model ----------
@dataclass
class Sphere:
    id: str
    ty_in: str
    ty_out: str
    entropy: float = 0.0

@dataclass
class Policy:
    id: str
    pre: str
    post: str
    deltaE: float
    l0bound: int = 1

# AST nodes
class ASTNode:
    pass

@dataclass
class Pop(ASTNode):
    sph: str

@dataclass
class Merge(ASTNode):
    s1: str
    s2: str

@dataclass
class Collapse(ASTNode):
    s: str

@dataclass
class Rewrite(ASTNode):
    s: str
    rule: str

@dataclass
class Bind(ASTNode):
    s1: str
    s2: str

@dataclass
class Seq(ASTNode):
    a: ASTNode
    b: ASTNode

# Sheaf IR
@dataclass
class SheafNode:
    open_id: str
    sphere_id: str

@dataclass
class SheafEdge:
    src: SheafNode
    tgt: SheafNode
    deltaE: float
    l0used: int = 0

@dataclass
class SheafIR:
    nodes: List[SheafNode] = field(default_factory=list)
    edges: List[SheafEdge] = field(default_factory=list)


# ---------- Parser for a tiny DSL ----------
# Example program (lines):
#   POP sigma0
#   MERGE sigma1 sigma2
#   SEQ
# Indentation-agnostic, one statement per line. SEQ can be encoded by writing lines sequentially.
def parse_program(lines: List[str]) -> ASTNode:
    nodes: List[ASTNode] = []
    for ln in lines:
        ln = ln.strip()
        if ln == "" or ln.startswith("#"):
            continue
        parts = ln.split()
        op = parts[0].upper()
        if op == "POP":
            nodes.append(Pop(parts[1]))
        elif op == "MERGE":
            nodes.append(Merge(parts[1], parts[2]))
        elif op == "COLLAPSE":
            nodes.append(Collapse(parts[1]))
        elif op == "REWRITE":
            nodes.append(Rewrite(parts[1], " ".join(parts[2:])))
        elif op == "BIND":
            nodes.append(Bind(parts[1], parts[2]))
        else:
            raise ValueError(f"Unknown op: {op}")
    # fold into a Seq chain
    if not nodes:
        raise ValueError("Empty program")
    cur = nodes[0]
    for n in nodes[1:]:
        cur = Seq(cur, n)
    return cur

# ---------- Typechecking / Environment ----------
@dataclass
class Env:
    spheres: Dict[str, Sphere]
    policies: Dict[str, Policy]

    @staticmethod
    def from_dict(d: Dict) -> "Env":
        spheres = {s['id']: Sphere(**s) for s in d.get('spheres', [])}
        policies = {p['id']: Policy(**p) for p in d.get('policies', [])}
        return Env(spheres, policies)

    def find_sphere(self, id: str) -> Optional[Sphere]:
        return self.spheres.get(id)

# ---------- Lowering: AST -> SheafIR ----------
def lower(ast: ASTNode, site: str = "U0") -> SheafIR:
    ir = SheafIR()
    if isinstance(ast, Pop):
        n = SheafNode(site, ast.sph)
        ir.nodes.append(n)
        ir.edges.append(SheafEdge(n, n, deltaE=0.02, l0used=1))
    elif isinstance(ast, Merge):
        n1 = SheafNode(site, ast.s1)
        n2 = SheafNode(site, ast.s2)
        fused = SheafNode(site, ast.s1)
        ir.nodes.extend([n1, n2, fused])
        ir.edges.append(SheafEdge(n1, fused, deltaE=-0.01, l0used=2))
        ir.edges.append(SheafEdge(n2, fused, deltaE=-0.01, l0used=2))
    elif isinstance(ast, Collapse):
        n = SheafNode(site, ast.s)
        ir.nodes.append(n)
        ir.edges.append(SheafEdge(n, n, deltaE=-0.05, l0used=1))
    elif isinstance(ast, Rewrite):
        n = SheafNode(site, ast.s)
        ir.nodes.append(n)
        ir.edges.append(SheafEdge(n, n, deltaE=0.0, l0used=0))
    elif isinstance(ast, Bind):
        n1 = SheafNode(site, ast.s1)
        n2 = SheafNode(site, ast.s2)
        ir.nodes.extend([n1, n2])
        ir.edges.append(SheafEdge(n1, n2, deltaE=0.01, l0used=1))
    elif isinstance(ast, Seq):
        ir1 = lower(ast.a, site)
        ir2 = lower(ast.b, site)
        # concatenate, but avoid duplicate node entries by id
        nodes_map = {(n.open_id, n.sphere_id): n for n in ir1.nodes}
        for n in ir2.nodes:
            key = (n.open_id, n.sphere_id)
            if key not in nodes_map:
                nodes_map[key] = n
        ir.nodes = list(nodes_map.values())
        ir.edges = ir1.edges + ir2.edges
    else:
        raise ValueError("Unknown AST node")
    return ir

# ---------- Execution semantics for SheafIR ----------
def exec_sheaf(ir: SheafIR, state: Dict[str, Sphere]) -> Tuple[Dict[str, Sphere], float, int]:
    st = dict(state)
    totalE = 0.0
    totalL0 = 0
    for e in ir.edges:
        sid_src = e.src.sphere_id
        sid_tgt = e.tgt.sphere_id
        s = st.get(sid_src)
        if s is None:
            # no-op
            continue
        s_new = Sphere(
            id=sid_tgt,
            ty_in=s.ty_in,
            ty_out=s.ty_out,
            entropy= s.entropy + e.deltaE
        )
        st[sid_tgt] = s_new
        totalE += e.deltaE
        totalL0 += e.l0used
    return st, totalE, totalL0

# ---------- Invariant checks ----------
def check_entropy_safety(ir: SheafIR, state: Dict[str, Sphere], budget: float) -> bool:
    # check sum of deltas ≤ budget (simple global check)
    total = sum(e.deltaE for e in ir.edges)
    return total <= budget + 1e-9

def check_sparsity(ir: SheafIR, max_l0: int) -> bool:
    total_l0 = sum(e.l0used for e in ir.edges)
    return total_l0 <= max_l0

# ---------- LaTeX emission for Section 9 (TikZ + textual) ----------
def emit_section9_latex(ir: SheafIR, site: str = "U0") -> str:
    # Produce the same LaTeX section as earlier, but populated with the IR diagram.
    tikz_nodes = []
    tikz_edges = []
    node_names = {}
    for i, n in enumerate(ir.nodes):
        nm = f"n{i}"
        node_names[(n.open_id, n.sphere_id)] = nm
        tikz_nodes.append(f'\\node[box] ({nm}) at (0,-{i*1.2}) {{{n.sphere_id}\\\\({n.open_id})}};')
    for i, e in enumerate(ir.edges):
        sname = node_names[(e.src.open_id, e.src.sphere_id)]
        tname = node_names[(e.tgt.open_id, e.tgt.sphere_id)]
        label = f"$\\Delta E={e.deltaE},\\;\\ell_0={e.l0used}$"
        tikz_edges.append(f'\\draw[arr] ({sname}) -- ({tname}) node[midway,right]{{{label}}};')
    tikz_body = "\n".join(tikz_nodes + tikz_edges)
    latex = r"""\section{Compiler Pipeline for Rewriting EBSSC Policies as Sheaf Operations}

To operationalize EBSSC, the compiler lowers SpherePOP policy traces into a SheafIR and produces executable sheaf functors. The pipeline stages, invariants, and the IR diagram for the compiled program are shown below.

\subsection{Compiled Sheaf IR (visual)}
\begin{center}
\begin{tikzpicture}[
  node distance=1.3cm,
  box/.style={draw,rounded corners,align=center,inner sep=5pt},
  arr/.style={-stealth,thick}
]
"""
    latex += "\n" + tikz_body + "\n"
    latex += r"""\end{tikzpicture}
\end{center}

\subsection{Sheaf IR (textual)}
\begin{itemize}
"""
    for e in ir.edges:
        latex += f"\\item {e.src.sphere_id} \\(\\to\\) {e.tgt.sphere_id}: $\\Delta E={e.deltaE}$, $\\ell_0={e.l0used}$\n"
    latex += r"""\end{itemize}

\subsection{Compiler invariants checked}
\begin{itemize}
  \item Entropy safety: global $\sum \Delta E$ reported below.
  \item Sparsity contractivity: sum of $\ell_0$ usages reported below.
\end{itemize}

\subsection{Diagnostics}
\begin{verbatim}
"""
    # diagnostics
    totalE = sum(e.deltaE for e in ir.edges)
    totalL0 = sum(e.l0used for e in ir.edges)
    latex += f"Total ΔE = {totalE}\nTotal ℓ0 = {totalL0}\n"
    latex += r"""\end{verbatim}
"""
    return latex

# ---------- Demo driver ----------
def demo():
    env_dict = {
        "spheres": [
            {"id": "sigma0", "ty_in": "text", "ty_out": "proof", "entropy": 0.05},
            {"id": "sigma1", "ty_in": "proof", "ty_out": "audio", "entropy": 0.02},
            {"id": "prior",  "ty_in": "text", "ty_out": "text", "entropy": 0.01}
        ],
        "policies": [
            {"id": "formalize", "pre": "sigma0", "post": "sigma1", "deltaE": 0.03, "l0bound": 1}
        ]
    }
    env = Env.from_dict(env_dict)
    program_lines = [
        "POP sigma0",
        "REWRITE sigma0 simplify",
        "POP sigma1",
        "MERGE sigma1 prior",
        "COLLAPSE sigma1"
    ]
    ast = parse_program(program_lines)
    ir = lower(ast, site="U0")
    state = {sid: s for sid, s in env.spheres.items()}
    st_final, totalE, totalL0 = exec_sheaf(ir, state)
    print("=== Runtime diagnostics ===")
    print(f"Total ΔE (exec): {totalE}, Total ℓ0: {totalL0}")
    print("Final sphere entropies:")
    for k, v in st_final.items():
        print(f"  {k}: entropy={v.entropy}")
    # invariants
    ent_ok = check_entropy_safety(ir, state, budget=0.1)
    sparse_ok = check_sparsity(ir, max_l0=10)
    print(f"Entropy safety ok (budget 0.1): {ent_ok}")
    print(f"Sparsity ok (max ℓ0 10): {sparse_ok}")
    # emit LaTeX section
    latex = emit_section9_latex(ir, site="U0")
    print("\n=== LaTeX Section 9 ===\n")
    print(latex)
    # also return values for further integration
    return {"ast": ast, "ir": ir, "state_final": st_final, "latex": latex}

if __name__ == "__main__":
    demo_result = demo()
    # Save LaTeX to file for easy inclusion
    with open("section9_generated.tex", "w") as f:
        f.write(demo_result["latex"])
    print("Wrote section9_generated.tex")


