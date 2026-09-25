# Repository Instructions for GitHub Copilot

## Project purpose

This repository supports the Hardware-Claim Series, a public research program about how hardware results become claims. It contains reproducible checks, experimental tools, source records, generated figures and tables, and seven related LaTeX essays:

1. *The Spin Count*
2. *The Comparison Table*
3. *The Location of Chance*
4. *Chips That Route Chips*
5. *Certified Chance*
6. *Replottable, Not Rerunnable*
7. *The Easy Phase*

The repository examines capacity, coupling, benchmark construction, system boundaries, tool lineage, randomness, endurance, reproducibility, and instance difficulty in Ising-machine research. Its purpose is careful reconstruction and independent verification, not adversarial fault-finding. Preserve useful results while locating exactly what the available evidence establishes.

The detailed research plan lives in `RESEARCH_PROGRAM.md`. Consult the relevant section before implementing an essay-specific task. Do not treat that document as evidence for an empirical claim.

## Governing rule

A generated number is not thereby a verified number. Keep transcription, reconstruction, reproduction, certification, extrapolation, projection, and physical replication distinct in code, records, tests, and prose.

## Scope and task discipline

- Implement only the requested issue or prompt. Do not silently expand a task into adjacent essays, refactors, new dependencies, external communication, or physical experiments.
- Inspect the relevant source files, tests, schemas, and pinned external commit before changing code.
- Preserve existing findings unless the task explicitly requires recalculation. If new evidence conflicts with a stored result, stop and report the conflict instead of overwriting it.
- Do not alter pinned external repositories, source data, or imported research artifacts. Treat them as immutable evidence.
- Do not send emails, open issues in external repositories, submit forms, contact authors, operate laboratory hardware, run destructive endurance tests, or perform human-subject experiments.
- Never claim that a task has reproduced a physical experiment when it has only recomputed released data or simulated a device.

## Evidence vocabulary

Every empirical value must be represented by a structured record. Do not collapse provenance into one confidence ranking. Record these dimensions separately:

- `origin`: `reported`, `independently_reproduced`, or `independently_measured`
- `transformation`: `direct`, `derived`, `fitted`, `extrapolated`, or `projected`
- `certification`: `uncertified`, `consistency_checked`, or `independently_certified`
- `boundary`: `device`, `subsystem`, `system`, `infrastructure`, or `not_applicable`
- `source`: a stable source identifier
- `source_locator`: page, figure, table, cell, equation, notebook cell, file and line, or equivalent precise locator
- `unit`: an explicit machine-readable unit when the value is dimensional
- `assumptions`: all conditions required for the value or derivation

Do not infer `independently_reproduced` from successful replotting. Do not infer `independently_certified` from agreement with a released notebook. A value copied from a paper and passed through a script remains `origin: reported`.

Use the following terms consistently:

- **Replot**: regenerate a figure from released result records.
- **Verify**: independently check a stated relation or calculation using available artifacts.
- **Rerun**: regenerate result records by executing the released experimental or computational process.
- **Rebuild comparison**: reconstruct all material rows, metrics, boundaries, and transformations in a comparative claim.
- **Certify**: establish a result through an exact method, proof, certificate, or independently checkable exhaustive computation.

When none of these classifications can be established, record `unknown`. Never guess a stronger classification.

## Quantitative claims and the number pipeline

- Every empirical or derived quantitative claim in an essay must enter through the number pipeline. Ordinary mathematical constants, equation indices, section numbers, years in citations, quoted text, and non-empirical definitions are exempt.
- Checks must emit isolated records under `build/records/`. They must not write directly to a shared `build/numbers.json`.
- The merge step must sort records deterministically, reject duplicate keys, reject incompatible units, detect conflicting sources, and fail on missing required metadata.
- The merge step generates `build/numbers.json`, `build/numbers.tex`, and a human-readable provenance ledger.
- Essays use `\claimnum{key}` or generated semantic macros. Do not redefine or appropriate `\num`, which belongs to `siunitx`.
- Never type a derived result directly into an essay to make a build pass. Add or repair the check that owns the result.
- Golden tests must pin source inputs and state an explicit exactness rule or tolerance. Do not update a golden value merely because current output differs.
- Generated records must include the repository commit, dependency-lock hash, and pinned external commit hashes. Exclude volatile timestamps from byte-reproducibility comparisons.

## Units, boundaries, and composition

- Use a unit library for dimensional values. Do not compare or combine bare floating-point values whose units are implicit.
- Boundary tags describe what has been counted, not the presumed quality of the measurement.
- Silent boundary mixing is forbidden. A deliberate mixed-boundary reconstruction is allowed only through an explicit API that records the operation, all input boundaries, the calling check, and a written rationale.
- Reconstructing a published mixed-boundary metric does not endorse it. Label the result as a reconstruction.
- Distinguish energy per device event, energy per spin update, energy per iteration, average power, facility power, and time to solution.
- Before computing a ratio across machines, verify that numerator and denominator refer to compatible tasks, solution criteria, instance distributions, operating points, and system boundaries.

## Claims about papers and releases

- Phrase findings conditionally on the material checked. Prefer: “Under the released notebook's instance, Hamiltonian, and validity conditions...”
- Do not write “the paper is wrong,” “the authors fabricated,” “fraud,” or equivalent accusations.
- Clearly distinguish what a paper reports, what its release computes, what this repository reconstructs, and what this repository independently proves.
- A minimum observed within one run is a run minimum, not a ground state, unless an exact certificate or proof establishes global optimality.
- “Best known,” “optimal,” “ground state,” “success,” “gap,” and “time to solution” are semantic labels that require explicit definitions and provenance.
- Do not silently reinterpret a label to make it technically defensible. Report the released computation and then classify it.
- Preserve version distinctions among preprints, accepted manuscripts, published articles, supplementary files, repositories, and later corrections.
- When comparing versions, cite each version separately and report whether data, formulas, captions, or operating conditions changed.
- Include favorable and limiting evidence. A criticism of a composed claim must not erase a genuine device-level result.

## Independent verification

- Verification code must not import expected answers from the artifact being tested.
- When reproducing a released function verbatim for comparison, isolate it as a reference adapter, retain its license and source locator, and test independent code against it.
- Exact certificates should be serializable and independently checkable. For routing, include the edge set, coordinates, decoded variables, every penalty term, objective term, total energy, and solver status.
- For Ising and QUBO models, retain sign conventions, factor-of-two conventions, diagonal treatment, symmetry assumptions, and additive offsets.
- Energy-order preservation is more important than matching one convention's absolute value. Report affine mappings and residuals explicitly.
- For counting problems, state whether counts identify complementary partitions, globally inverted spin states, permutations, degeneracies, or assignments as distinct.
- Treat a failed verification as a result to diagnose, not as permission to weaken the test.

## Software standards

- Target Python 3.12 unless the project configuration states otherwise.
- Use type annotations for public functions and dataclasses for structured records.
- Use `ruff` for formatting and linting, `pytest` for tests, and Hypothesis for algebraic or invariant-based tests where appropriate.
- Use Python integers for exact counts. Do not pass large exact counts through floating point merely for formatting.
- Use rational or explicitly scaled integer coefficients in exact solvers. Record the scaling factor and prove that it preserves the relevant ordering or optimum.
- Avoid hidden global state. Pass configuration, seeds, paths, and tolerances explicitly.
- Every stochastic function takes a seed or generator argument. Do not use an unseeded global random-number generator.
- Set deterministic solver options where available, including worker count. If a dependency cannot guarantee cross-platform determinism, document the reproducibility scope.
- Prefer small pure functions and independently testable transformations over notebook-only logic.
- Do not add a dependency when a short, auditable implementation using existing dependencies is sufficient.
- Update the dependency lock whenever dependencies change. Do not rely on an unpinned transitive dependency for a claimed result.
- Preserve third-party license notices. Original project work may be CC0-1.0, but external repositories and incorporated components retain their own licenses.

## Test design

- Test exact identities exactly. Use tolerances only for quantities that are genuinely approximate.
- Every tolerance must have a reason stated in the test or adjacent documentation.
- Do not use “enough iterations,” “approximately correct,” or “usually passes” as an acceptance criterion.
- Do not require a stochastic heuristic to find every optimum as proof of implementation correctness. Test energy deltas, state transitions, seed reproducibility, and fixed-budget success statistics separately.
- Statistical tests must declare the instance set, sample count, seed policy, estimator, uncertainty interval, and decision threshold before inspecting results.
- Tests must fail if required source files, external commits, metadata, or generated keys are absent. Do not replace missing evidence with fixtures that contain the expected conclusion.
- Keep fast deterministic unit tests separate from long experiments and hardware protocols.

## Reproducibility tiers

Use these targets and do not blur their meanings:

- `make verify`: fast deterministic checks suitable for continuous integration
- `make papers`: generate PDFs from available certified records
- `make extended`: long simulations, exact solvers, and optional external test suites
- `make protocols`: render protocols for manual, physical, destructive, or human-operated experiments without executing them

`make all` may combine computational targets, but it must not claim to reproduce manual or physical observations. Hardware measurements enter the repository only through reviewed manifests containing the protocol version, apparatus, operator, date, calibration information, environment, and raw-data hashes.

## External repositories and source artifacts

- External repositories must be pinned to exact commits. Report those commits in generated manifests and essays.
- Never edit submodule contents to make a check pass.
- A clean computational reproduction must state whether it requires `git clone --recurse-submodules`, Git LFS, proprietary software, credentials, licensed data, or unavailable hardware.
- Store hashes for source artifacts used in checks. A matching filename is not sufficient identity.
- Do not download or substitute a newer external artifact without an explicit task and a recorded source-version change.
- Keep raw source artifacts separate from normalized or generated data.

## Notebook and figure audits

- Notebook execution order is evidence. Do not assume visual cell order equals execution order.
- Classify semantic annotations as `certified`, `empirical_run_statistic`, `external_reference`, `constant`, or `unknown`.
- Static analysis of notebooks is allowed to return `unknown`. Never manufacture a dependency trace across dynamic execution, hidden state, imports, or reassigned variables.
- Begin with explicit adapters for known notebooks before generalizing an audit engine.
- Audit outputs must cite notebook path, cell identifier, relevant code, upstream data, classification, and unresolved dependencies.

## Benchmark reconstruction

- Preserve the original metric before evaluating alternatives.
- Reverse-engineered formulas must be dimensionally valid and accompanied by residual, expression complexity, and search-space description.
- Do not treat a discovered formula as intentional merely because it reproduces a column.
- Separate measured, estimated, projected, and extrapolated table entries without imposing a total quality ordering on them.
- Report how rankings change under alternative boundaries and evaluative rules. Do not choose only the rule that produces the most dramatic reversal.
- Include elementary baselines such as random guessing, greedy methods, and exact small-instance solutions when they are relevant to interpreting difficulty.
- Never transfer iteration counts, success probabilities, or time-to-solution values across platforms without stating the required kernel, schedule, instance, and solution-quality equivalence assumptions.

## Essay standards

- Essay prose avoids em dashes and first-person narration.
- Use precise academic language without inflating certainty.
- Use `\claimnum{key}` for empirical and derived quantitative claims.
- Cite bibliography keys from `bib/series.bib`; do not place raw URLs in essay prose.
- Do not invent bibliographic metadata. Mark unresolved fields explicitly for verification.
- Keep quotations short and necessary. Preserve exact wording when the terminology itself is under analysis.
- Attribute reused formulations to earlier essays in the series. In particular, attribute “Valuation is digital; chance is magnetic” to *The Shape of Search*.
- Distinguish theorem, proposition, reconstruction, empirical observation, interpretation, conjecture, and analogy.
- Page targets are planning guides, not requirements to pad an argument.
- Every figure caption states whether the figure is reported, replotted, reconstructed, simulated, or schematic.

## Manual, destructive, and human-operated experiments

- Copilot may write protocols, simulators, data schemas, and analysis code for these experiments, but must not claim to execute them.
- Mark destructive experiments conspicuously. Never run storage wear, device endurance, electrical stress, or irreversible filesystem operations automatically.
- Include safety precautions for glass abrasion, electrical hardware, lasers, magnetic devices, radiation sources, and other relevant apparatus.
- Human-operated demonstrations require informed participation, minimal data collection, anonymization, and an explicit statement that they are demonstrations rather than population studies.
- External correspondence requires human review and sending. Do not automate author requests or represent silence as refusal.

## Absurd experiments

Deliberately absurd experiments are legitimate analytical instruments in this repository. Treat them with the same quantitative and provenance standards as serious experiments.

- State the category error or hidden assumption the experiment isolates.
- Keep the absurd premise distinct from the measured result.
- Do not falsify a specification, result, quotation, or source for comic effect.
- Do not let humor substitute for a baseline or uncertainty analysis.
- Make names and captions playful only after the underlying calculation is correct.

## Required workflow for a new check

1. Read the relevant essay plan, source artifact, existing adapters, and nearby tests.
2. State the exact claim the check can establish and the stronger claims it cannot establish.
3. Identify inputs by path, source, version, commit, and hash where available.
4. Implement the smallest independent calculation that tests the claim.
5. Emit isolated structured records with complete evidence metadata.
6. Add exact, invariant-based, or explicitly tolerated tests as appropriate.
7. Add a concise entry to `checks/README.md` describing the check and its evidential scope.
8. Run the narrow tests, then the relevant repository target.
9. Report unresolved assumptions, unknown classifications, unavailable dependencies, and deviations from the issue.

## Required workflow for an essay change

1. Identify the claim record or source supporting every new empirical statement.
2. Add missing checks before adding generated numbers to prose.
3. Preserve conditional wording and system boundaries.
4. Add or verify bibliography entries without inventing missing fields.
5. Build the changed essay and run the numeric-claim lint.
6. Check that captions and surrounding prose identify the evidential status of every figure and table.

## Completion standard

A task is complete only when its stated acceptance criteria pass, generated records contain complete provenance, tests exercise the actual claim, documentation states the evidential scope, and no unrelated files have been changed. If an acceptance criterion cannot be met from the available artifacts, report the blocker and leave the criterion unmet. Do not simulate success.
