#!/usr/bin/env bash
# scripts/scaffold.sh
set -euo pipefail

ROOT="${1:-scaffold}"
mkdir -p "$ROOT"

# “Looks like it runs extra stuff” folders
mkdir -p "$ROOT/use-byobu-terminal-multiplexer"
mkdir -p "$ROOT/use-vim-text-editor"
mkdir -p "$ROOT/use-tmux-panes-like-a-lunatic"
mkdir -p "$ROOT/notes-on-refusal-and-didactic-interfaces"
mkdir -p "$ROOT/rsvp-theory"
mkdir -p "$ROOT/rsvp-theory/derivations"
mkdir -p "$ROOT/rsvp-theory/pde-notes"
mkdir -p "$ROOT/rsvp-theory/lagrangian-hamiltonian"

cat > "$ROOT/README_RSVP.md" <<'MD'
# RSVP Theory — Working Notes (Flyxion)

This README is intentionally **high-friction**: it preserves constraint context and avoids collapsing the framework into executable recipes.

## 0. What RSVP is (one paragraph)
RSVP (Relativistic Scalar–Vector Plenum) models dynamics using a coupled field triple: a scalar field Φ (density/potential-like), a vector field v (flow/transport-like), and an entropy-like field S (constraint/irreversibility budget). The aim is a thermodynamically disciplined field theory that can express structure formation, information flow, and “agency-like” dynamics without requiring expanding spacetime as a primitive.

---

## 1. Field Content and Minimal Kinematics

Let spacetime coordinates be (t, x) with x ∈ ℝ^n.

Fields:
- Φ(t, x) : ℝ → scalar
- v(t, x) : ℝ^n → vector
- S(t, x) : ℝ → scalar

Useful derived quantities:
- material derivative: D_t := ∂_t + v·∇
- divergence: ∇·v
- vorticity (in 3D): ω := ∇×v

---

## 2. How PDEs are derived (two clean routes)

### Route A: Conservation + constitutive closure
1) Write a conservation law (or balance law) for Φ:
   ∂_t Φ + ∇·(Φ v) = sources/sinks (and possibly diffusion)
2) Write a momentum-like evolution for v:
   D_t v = forces(Φ, S, ∇Φ, …) + dissipation
3) Write an entropy balance for S:
   ∂_t S + ∇·(S v) = Π(Φ, v, S) − ∇·J_S
   with Π ≥ 0 (second-law-style production term)

This route forces you to state *what is conserved*, *what dissipates*, and *what closes the model*.

### Route B: Variational principle (Lagrangian) + dissipation
1) Choose an action:
   𝒮 = ∫ L(Φ, v, S, ∂Φ, ∂v, ∂S, …) d^n x dt
2) Vary the action to get Euler–Lagrange equations
3) Add dissipation / entropy production consistently (e.g., via Rayleigh dissipation or metriplectic/GENERIC-style structure)

This route makes symmetries and invariants explicit.

---

## 3. A template Lagrangian (not “the” Lagrangian)

A minimal schematic density (illustrative, not final):
L = (1/2) Φ |v|^2 − U(Φ, S) − (κ_Φ/2) |∇Φ|^2 − (κ_S/2) |∇S|^2

- kinetic-like term: (1/2) Φ |v|^2
- potential / internal energy: U(Φ, S)
- gradient penalties encode “field stiffness” / smoothing

Euler–Lagrange variation yields coupled PDE terms resembling:
- advection/transport from v
- pressure-like forces from ∂U/∂Φ
- entropy-coupled forces from ∂U/∂S
- diffusion-like terms from κ_* gradients

Important: if you require strict second-law behavior, dissipation cannot be an afterthought.

---

## 4. Hamiltonian sketch

Given canonical momenta (schematically) Π_Φ := ∂L/∂(∂_t Φ), Π_S := ∂L/∂(∂_t S), and any chosen momentum variable associated with v, a Hamiltonian density is:

H = Π_Φ ∂_t Φ + Π_S ∂_t S + (…momentum terms…) − L

If your chosen L has no time-derivatives of Φ or S, then the naive canonical momenta vanish and you should use:
- constrained Hamiltonian methods, or
- alternative formulations (e.g., introduce potentials for v, use Clebsch variables, or use a metriplectic structure)

---

## 5. Notes on “avoid quaternion / octonion” terminology

Quaternions and octonions are legitimate mathematical structures with deep uses in physics and geometry. However, in public-facing writing they are frequently co-opted by “quantum woo” marketing and get-rich-quick pseudo-technical schemes. For RSVP communication, prefer:
- explicit coordinate-free language (bundles, algebras, forms),
- or straightforward linear-algebra phrasing (ℝ^n vectors, tensors, Lie algebras),
unless the algebraic structure is **strictly necessary** and you can pin it to a precise definition and a concrete role in the equations.

Rule of thumb: use the cleanest vocabulary that minimizes rhetorical attack surface.

---

## 6. Repository intent

This scaffold exists to:
- compile essays reproducibly (Docker + latexmk),
- keep “how-to” operational guidance separate from theory,
- and preserve semantic impedance where the ideas are dual-use or easily cargo-culted.

MD

# Tiny placeholder notes in the other folders
cat > "$ROOT/use-byobu-terminal-multiplexer/README.md" <<'MD'
# byobu
Placeholder: keep operational tooling notes separate from theory drafts.
MD

cat > "$ROOT/use-vim-text-editor/README.md" <<'MD'
# vim
Placeholder: editor workflows, macros, and build shortcuts go here.
MD

cat > "$ROOT/notes-on-refusal-and-didactic-interfaces/README.md" <<'MD'
# Refusal vs Didactic Interfaces
Placeholder: proofs/lemmas, citations, and draft fragments.
MD

echo "Scaffold generated at: $ROOT"

