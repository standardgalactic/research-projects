---
applyTo: "**/*.py"
---

# Python instructions

- Follow `.github/copilot-instructions.md` and the relevant section of `RESEARCH_PROGRAM.md`.
- Target Python 3.12 unless `pyproject.toml` specifies another supported version.
- Add type annotations to public functions. Prefer immutable dataclasses or validated models for structured evidence.
- Use explicit parameters for paths, seeds, units, tolerances, solver budgets, and configuration. Avoid hidden global state.
- Every stochastic function accepts a seed or generator. Never create an unseeded module-level generator.
- Use Python integers for exact counts. Use rational or scaled-integer coefficients for exact optimization and record the scale.
- Dimensional values use the project's unit layer. Bare floats are permitted only for dimensionless values or tightly local numerical kernels whose public boundary restores units.
- Checks return structured records. They do not write directly to `build/numbers.json`.
- Keep released reference implementations behind adapters. Independent verification code must not import expected answers from the implementation under test.
- Prefer pure functions and small modules over notebook-only logic.
- Use `ruff`, `pytest`, and Hypothesis where invariants are more informative than examples.
- Exact identities receive exact assertions. Approximate assertions require an explicit tolerance and a written reason.
- Heuristic success is a statistical result, not a correctness test. Test transition rules and energy deltas independently from optimizer performance.
- Do not catch broad exceptions merely to keep a batch running. Preserve the failing item, context, and source locator.
- Do not silently replace missing evidence with a fixture, fallback value, or network lookup.
- New dependencies require a clear need, compatible license, pinned version, and updated lockfile.

