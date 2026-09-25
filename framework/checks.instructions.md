---
applyTo: "checks/**/*.py"
---

# Reproducible check instructions

- Begin each check with a module docstring stating the exact claim it can establish and the stronger claims it cannot establish.
- Identify every input by path, source, version, commit, and hash where available.
- Checks must be runnable through the repository's standard runner from a clean computational environment.
- Emit isolated records under `build/records/`; never mutate a shared aggregate file directly.
- Use stable, namespaced keys beginning with the essay identifier, such as `e1.spincount.storage_mib`.
- Do not import an expected answer from the artifact being verified.
- Reproducing released behavior and independently verifying it must be separate operations with separate records.
- Exact claims require a proof, exhaustive computation, exact solver certificate, or independently checkable witness.
- Store witnesses when they are materially smaller than recomputation. A routing witness includes edges, coordinates, decoded variables, each penalty, objective, and total energy.
- A run minimum is recorded as a run minimum unless independently certified as global.
- Tests pin inputs as well as outputs. Golden-value updates require an explanation of the changed source or corrected method.
- Stochastic checks declare seeds, sample counts, budgets, estimators, uncertainty intervals, and decision thresholds.
- Add one concise entry to `checks/README.md` stating the check's evidential scope.
- If an input is unavailable or ambiguous, fail or emit `unknown`; do not construct a favorable substitute.

