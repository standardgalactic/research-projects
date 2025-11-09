# PlenumHub — Stage 3 Roadmap (Immediate Next Development Phase)

**Goal (Stage 3):** produce a runnable reference implementation of the SpherePOP interpreter,
a deterministic proof-carrying reduction pipeline, automated CI for builds/tests, and an executable
minimal end-to-end demo (create sphere -> pop -> close -> merge).

## Priorities (M1..M4)
- **M1 (Core runtime):**
  - Implement `Sphere`, `Rule`, and `Interpreter` classes in `src/plenumhub`.
  - Canonical big-step reduction (`pop`) + small-step hooks.
  - Proof object emission (Merkle-like proof stubs).

- **M2 (Validation & Entropy):**
  - Entropy model: entropy score functions and per-rule budgets.
  - Type-checker for rule-chains.
  - Merge operator with mediation stub.

- **M3 (Tooling & CI):**
  - Unit tests for core behaviors.
  - GitHub Actions for linting and tests.
  - Makefile targets: `make build`, `make test`, `make paper`.

- **M4 (Research artifacts):**
  - Integrate full LaTeX manuscript in `paper/`.
  - Add Lean formalization stubs in `lean/`.
  - Provide TikZ architecture diagram in `docs/diagram.tex`.

## Stage 3 Sprint Plan (4 weeks)
- Week 1: Core runtime (M1) — API, basic interpreter, readme examples.
- Week 2: Entropy & type-checking (M2) — implement budgets, simple merge.
- Week 3: Tests, CI, demo (M3) — unit tests and GitHub Actions.
- Week 4: Documentation, paper integration, Lean expansion (M4) — finish manuscript integration and Lean seeds.

## Milestones & Deliverables
- `plenumhub_stage3.zip` containing the repo skeleton and working unit tests.
- Minimal demo: `examples/demo.py` (create -> pop -> close -> merge).
- CI passing on main branch.

