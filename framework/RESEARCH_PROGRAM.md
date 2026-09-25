# The Hardware-Claim Series

## Research program, experiments, and tool suites

This repository supports seven essays about how hardware results become claims. It combines textual analysis with independently checkable calculations, reconstructed benchmarks, exact certificates, simulations, release audits, and deliberately absurd experiments that expose hidden assumptions by exaggerating them.

The program has three commitments. Each essay should become a rigorous standalone study rather than an enlarged commentary. Every empirical or derived quantitative claim should be connected to a structured record and an executable check. Every distinction made in the prose should, where feasible, become an operation the repository can perform.

The governing equation for the series is

\[
\text{claim}
=
\text{device}
+
\text{instance}
+
\text{boundary}
+
\text{metric}
+
\text{baseline}
+
\text{released evidence}.
\]

Changing any one term can change the apparent capability without changing the underlying apparatus.

## Repository outcomes

The completed repository should contain seven LaTeX essays and a series preface; a typed Python library named `claimcheck`; one group of checks per essay; reproducible tables, figures, and numerical records; pinned external source repositories; protocols for manual and physical experiments; and a clear separation among replotting, verification, rerunning, comparison reconstruction, certification, and physical replication.

Computational work should be divided into four targets. `make verify` runs fast deterministic checks suitable for continuous integration. `make papers` generates PDFs from available records. `make extended` runs long simulations, exact solvers, and optional external test suites. `make protocols` renders procedures for experiments that require hardware, destruction, correspondence, or human participation. No automated target may claim to have performed a manual or physical experiment.

## Shared infrastructure

### Structured evidence records

Every empirical value should record its origin, transformation, certification status, system boundary, unit, source, source locator, and assumptions. These fields are orthogonal. A reported measurement remains reported even when a script reformats it. A replotted trajectory is not a rerun. Agreement with released code is not independent certification.

Checks emit isolated JSON records under `build/records/`. A deterministic merger rejects duplicate ownership, incompatible units, incomplete metadata, and conflicting sources before producing `build/numbers.json`, `build/numbers.tex`, and a human-readable evidence ledger. Essays refer to generated quantitative claims through `\claimnum{key}` or stable semantic macros.

### Typed values and boundary accounting

`claimcheck` should provide typed dimensional values using a unit library. Boundary mixing must be explicit. Reconstructing a published metric that multiplies device time by infrastructure power is permitted only through an auditable mixed-boundary operation with a rationale. Reconstructing a metric does not endorse it.

### Ising and QUBO conventions

The library should support common Ising conventions, including sums over `i < j` and sums over all ordered pairs, alternative signs, diagonal treatment, local fields, and additive offsets. It should provide energy, single-spin energy change, QUBO conversion, and convention fitting against an opaque reference function. Conversion tests should preserve energy ordering exactly on integral instances and report affine mappings and residuals when matching released notebooks.

### Solvers and baselines

The shared solver layer should include brute force for small systems, exact integer or rationalized optimization, a seeded simulated annealer, and random guessing. Essay-specific tools may add subset-sum dynamic programming, meet-in-the-middle counting, rectilinear Steiner solvers, Karmarkar-Karp differencing, and complete anytime search.

Heuristics are evaluated with declared budgets and uncertainty intervals. They are not certified merely because they match an exact solver on a sample. Exact solvers must emit independently checkable certificates when practical.

### External evidence

External repositories are pinned to exact commits and treated as immutable. Raw artifacts remain separate from normalized and generated data. Generated manifests should record repository commits, dependency-lock hashes, external commits, source hashes, and reproducibility scope. Original project work is intended for CC0-1.0; third-party material retains its own license.

## Essay 1: The Spin Count

### Thesis

The phrase “96,000-spin all-to-all” joins capacities that were demonstrated separately but not compositionally. The chip contains 96,000 spin elements, while the coupled demonstrations use at most 450 spins and the dense benchmark uses 60. Spin storage grows linearly with problem size, whereas arbitrary dense coupling grows quadratically.

### Argument to develop

The essay should distinguish component capacity, system capacity, and demonstrated compositional capacity. It should establish a representational lower bound for an arbitrary symmetric dense coupling matrix and a temporal-dynamical bound derived from controller bandwidth, update scheduling, and the paper's own flip-rate definition. The most charitable one-bit symmetric representation requires approximately 549 MiB before addressing, weights, runtime state, or operating-system use. The time analysis should state its execution model explicitly and should not assume that every architecture materializes the same matrix representation.

The essay should treat sparsity, procedural couplings, compression, and streaming as conditional alternatives. Each changes the capability being certified or relocates the resource obligation. A positive final section should specify the evidence required to demonstrate that two advertised capacities compose.

### Tool suite

`capacity-composer` accepts a machine description containing spin count, coupling model, precision, memory hierarchy, bandwidth, update time, flip rate, and schedule. It reports fit limits, bandwidth lower bounds, feasible flip-rate regions, assumptions, and whether claimed capability pairs are composed, separately demonstrated, unsupported, or infeasible under the stated model.

Board specifications belong in sourced YAML records under `data/boards/`. Primary manuals and data sheets are preferred.

### Experiments

The serious experiments are a sequential-sweep measurement on suitable Zynq hardware and a sparse frontier showing where representation cost gives way to bandwidth cost. Hardware execution remains a manual protocol unless the required board is explicitly available.

The absurd experiments are a 96,000-spin Raspberry Pi whose couplings live on slow storage, a floppy-disk coupling store with iteration time reported honestly, and a spin-count inflation script that renames ordinary storage devices as enormous Ising machines. Each must state the category error it exposes.

### Initial implementation tasks

Implement the PYNQ-Z2 model and reproduce the symmetric one-bit storage bound, the idealized column-fetch lower bound, and the bits transferable in one reported update interval. Add the sparse entropy model with explicit assumptions about support encoding and weight precision. Implement the spin-count inflation script as a deterministic comic baseline.

## Essay 2: The Comparison Table

### Thesis

A comparison table makes heterogeneous machines comparable by choosing metrics, system boundaries, operating points, and rules for filling unavailable cells. Those choices can determine the ranking.

### Argument to develop

Treat the preprint and published tables as a natural experiment. The machine remains fixed while the evaluative rule changes. Reconstruct every recoverable entry and separate measured, reported, fitted, estimated, extrapolated, and projected quantities without placing them on one confidence ladder.

The essay should distinguish device, system, and infrastructure boundaries; examine combinations such as device-level times with facility-level power; and test whether iteration counts can be transferred across platforms. A platform-independence assumption requires equivalence of instances, kernels, schedules, stopping rules, and solution-quality criteria. Evidence that randomness resolution changes success probability directly bears on that assumption.

### Tool suite

`tablecc` is a typed table compiler. Each cell carries units, evidence metadata, and boundaries. It reconstructs the original table before rendering alternatives under declared policies such as measured-only, device-boundary, system-boundary, or infrastructure-inclusive.

`reverse-metric` searches a bounded grammar of dimensionally valid expressions for formulas reproducing a target column. It reports the simplest expression, residual, complexity, and search space. Formula recovery is not evidence of authorial intention.

### Experiments

Encode both table versions and plot rank as a function of evaluative rule. Extend the reverse-metric audit to a declared sample of Ising-machine papers.

The absurd baselines are a coin, a solar calculator plus human operator, and boundary roulette. Human labor and omitted infrastructure must be recorded rather than treated as zero merely to improve the joke.

## Essay 3: The Location of Chance

### Thesis

The machine is named after where stochastic transition occurs while valuation, coupling, scheduling, and much of the energy and latency occur elsewhere. The name identifies the novel physics more reliably than the system capability.

### Argument to develop

Use “Valuation is digital; chance is magnetic,” attributed to *The Shape of Search*, as the architectural division. Analyze “on-chip,” “in situ,” and “all-to-all” as boundary-drawing operations rather than simple true-or-false labels.

Construct a per-iteration energy ledger and state an Amdahl-style ceiling for improving the named component alone. Provide bounds under each plausible update schedule rather than hiding ambiguity behind one preferred interpretation. Extend the analysis to photonic, measurement-feedback, memristive, and p-bit systems where sufficient data exist.

### Tool suite

`energy-ledger` consumes sourced component inventories and produces a boundary-aware ledger, component shares, unaccounted residuals, and Amdahl ceilings. Missing quantities remain unknown.

`rename` generates a playful alternative name based on the component dominating energy, time, or infrastructure cost. Its input ledger must be correct before humor is added.

### Experiments

Build ledgers for the spintronic and photonic systems, followed by a scoped field survey. The absurd experiments rename every machine in the comparison tables and replace a software random source with an artisanal physical source while keeping valuation digital.

## Essay 4: Chips That Route Chips

### Thesis

Self-reference has several distinct forms. A system may process its own description, solve a problem of its own kind, or participate in a lineage that produces its successors. The demonstrated chip establishes the second form, not literal self-design.

### Argument to develop

Reconstruct the released routing instance, its number of terminals and Steiner candidates, its 450-spin encoding, and an independently certified optimum. Place the instance within actual routing practice and avoid presenting a small proof-of-concept net as an industrial routing advance.

Formalize tool lineage with a check predicate. A lineage can improve or drift depending on whether one generation can pass its checks merely by agreeing with itself. Compare chip design, bootstrapping compilers, precision machine tools, model-generated training data, and later-generation design systems. Detection and correction must remain distinct.

### Tool suite

`rsmt-kit` provides Hanan-grid construction, exact small-net solvers, optional licensed wrappers, the released Ising/QUBO encoding, decoding, and certificate generation.

`lineage-sim` models inherited error under self-agreement, relational checks, and external references. It is an explanatory simulation, not empirical evidence about real industrial lineages.

### Experiments

Compare the demonstration net with a declared industrial benchmark distribution. Simulate lineage behavior under different checks. Manual or extended protocols may include a small FPGA design that solves extracted nets from its own synthesized design, Whitworth's three-plate method, and generational training on model-produced text. Each protocol must state what kind of self-reference it actually demonstrates.

## Essay 5: Certified Chance

### Thesis

“Random” names several separable properties certified by different evidence for different users. Optimization success does not by itself require unpredictability. The physical source may earn its place through cost, locality, or resolution rather than a superior metaphysical grade of chance.

### Argument to develop

Separate unpredictability, distributional conformity, probability resolution, calibration, device heterogeneity, energy cost, switching latency, and endurance. Treat disagreements between paper versions as version drift requiring explanation. Formalize lifetime as endurance divided by an assumed duty cycle, and state the duty cycle behind any conversion from tested cycles to years.

Explain what NIST SP 800-22, TestU01, and dieharder test and what they do not. A predictable sequence may pass statistical batteries. A task can consume probability resolution without consuming cryptographic unpredictability.

### Tool suite

`certify` wraps declared statistical suites and records their versions, parameters, sample requirements, and property scope. Sources include LFSRs, conventional pseudorandom generators, cryptographic generators, deterministic mathematical digit streams, and a calibrated simulated switching source.

`resolution-bench` runs fixed optimization instances under declared probability resolutions and random sources. It separates source identity from discretization.

### Experiments

Reproduce the resolution trend under fixed schedules and seeds, then estimate the saturation region with uncertainty. Demonstrate predictability through state recovery while keeping statistical-test results separate.

The absurd experiments certify digits of pi, specify a destructive flash-endurance protocol without running it automatically, and solve a small routing instance through human dice rolls.

## Essay 6: Replottable, Not Rerunnable

### Thesis

The release regenerates figures and enables partial verification, but does not regenerate the experimental or computational results from their originating process. Replottable traces, rerunnable experiments, and rebuildable comparisons are different capabilities.

### Argument to develop

Audit the released notebooks at the level of semantic labels. If a line labelled “Ground state” is computed as the minimum observed within a run, classify it as an empirical run statistic. Do not silently rehabilitate the label.

For the routing result, print the released tree and any shorter counterexample with coordinates, edges, decoded variables, every penalty term, objective, and total energy. The claim must remain conditional on the released instance, Hamiltonian, decoder, and validity conditions. Include independent certification and a record of unresolved ambiguities.

The essay should connect release practice to reproducibility terminology and compare releases without treating repository size as evidential quality. Any author correspondence is human-reviewed and recorded neutrally.

### Tool suite

`figure-audit` begins with explicit notebook adapters and a general inventory. It classifies plotted semantic annotations as certified, empirical run statistics, external references, constants, or unknown. Dynamic dependencies that cannot be resolved remain unknown.

`release-grade` evaluates separately whether a release supports replotting, verification, rerunning, and comparison reconstruction. Scores must cite the artifacts satisfying or failing each criterion.

### Experiments

Audit the spintronic and photonic releases. Certify tractable released instances with exact solvers. Extend the release audit to a declared corpus of papers.

The absurd experiments search public code for minimum-of-run values labelled as ground states and define a human-reviewed protocol for testing “available upon reasonable request.” Repository searches must use legitimate APIs, declared sampling rules, and manual validation to avoid inflated counts.

## Essay 7: The Easy Phase

### Thesis

Solver performance depends on the phase and degeneracy of the instance distribution. A problem family with a large ground-state fraction can make random guessing look competent, while unique-solution instances define a different problem class.

### Argument to develop

Count perfect partitions exactly where possible and state whether complementary partitions or globally inverted spin assignments are identified. Compare counts with asymptotic expectations and mark the released instances on a phase diagram using a declared definition of \(\kappa\).

Run random guessing, greedy methods, Karmarkar-Karp, complete search, simulated annealing, and the released simulator on the same instances. Comparisons across different instance ensembles must be identified as such.

Audit fitted time-to-solution curves for non-physical domains, including negative times and probabilities outside their range. A fit can describe observed data locally without defining a meaningful extrapolation everywhere.

### Tool suite

`phase-map` sweeps instance size and integer precision, counts perfect partitions with exact algorithms, and plots the phase structure with released instances marked.

`baseline-zoo` runs multiple solvers on identical serialized instances under declared budgets and stopping criteria.

`fit-domain` reports the mathematical and physical domain of a fitted model and identifies supplied data or extrapolations outside that domain.

### Experiments

Map solver performance across the phase diagram, generate genuinely rare or unique-solution instances with suitable integer ranges, and run the released simulator on both easy and hard ensembles. Trace important performance numbers across later papers and tables while preserving how their meanings change.

The absurd experiments treat a human with index cards as a room-temperature carbon-based machine, extrapolate a fitted curve into negative time, and write a clearly marked satirical abstract from the extrapolation.

## Cross-series experiments

### The Hall of Mirrors

Combine the audited comparison tables with the coin, Raspberry Pi, human, calculator, and dice-driven baselines. Render the same rows under several declared evaluative rules. The objective is to show sensitivity to rules, not to select the most embarrassing ordering.

### Abstracts reconstructed from evidence

Write an alternative abstract for each machine using only checked claims and generated values. Compare each sentence with the corresponding published abstract by evidential type, boundary, and omitted condition.

### Adversarial benchmark design

Given a machine's measured characteristics, construct an instance distribution expected to favor it and another expected to expose its weaknesses. Run the same baseline suite on both. Treat the result as benchmark sensitivity, not proof of bad intent.

### The preface as an executable claim

For each essay, vary one term in the series equation while holding the others fixed and report how the apparent capability changes. The preface should cite the resulting table.

## Suggested milestones

The first milestone establishes repository configuration, structured evidence records, deterministic merging, units, licensing, dependency locking, and continuous integration. The second implements Ising conventions, independent solvers, and ports the existing routing and partition checks. The third completes the consequential verification work for essays 6 and 7. The fourth builds capacity and table tools for essays 1 and 2. The fifth adds energy ledgers and routing-lineage tools. The sixth adds randomness and endurance tools. The final milestone completes cross-series experiments, the preface, citation verification, and a full evidential audit.

Milestones are ordered by dependency rather than by essay number. Page targets are planning guides, not invitations to pad an argument.

## Definition of done

The computational series is complete when a clean, documented clone can reproduce every computationally generated essay value, table, figure, certificate, and PDF within its declared environment; every external input is pinned and hashed; every mixed-boundary calculation is logged with a rationale; every uncertainty and unresolved dependency remains visible; and manual or physical findings are clearly separated from what the automated build actually performed.

