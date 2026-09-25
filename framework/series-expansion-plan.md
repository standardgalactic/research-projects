# Expansion Plan: The Hardware-Claim Series

Seven essays, each currently 6 to 8 pages. The goal for each is roughly 12 to 16 pages: longer, more rigorous, and better cited. Every expansion follows the same pattern. Formalize the central claim, add a check that could have failed, widen the comparison beyond the spintronic paper, and anchor it in the relevant literature.

Citations marked **(verify)** are ones I'm confident exist but whose volume, page, or year should be checked before they go into a bibliography.

---

## Series-level work

These tasks cut across all seven essays and are best done first.

**A unifying thesis.** The series argues that a published capability is a function of more than the device:

> hardware claim = device + instance + boundary + metric + baseline + released evidence

Each essay isolates one term. Stating this once, in a short preface or a shared introduction section, lets each essay cite it rather than re-argue it. The order already escalates. Essays 1 to 3 reconstruct the claim from capacity, comparison, and boundary. Essays 4 and 5 examine lineage and certification. Essay 6 tests what the release lets a reader establish. Essay 7 shows the method transfers to a second paper.

**Shared notation.** Fix one symbol set across all essays: N spins, J couplings, h fields, t_iter iteration time, P power, f cost fraction outside a named boundary, TTS time-to-solution. The Shape of Search already uses y_t = M(K^t(x_0)); decide whether the series adopts it.

**A reproducibility bundle.** Collect `verify_vsim_release.py`, `verify_cmim_partitioning.py`, and the arithmetic for essays 1, 3, and 5 into one public-domain repository with a README. Each essay then cites a specific script and commit. This makes the series an instance of the counterpractice essay 6 proposes.

**A shared bibliography.** Merge the seven `thebibliography` blocks into one BibTeX file with consistent title casing. The same papers (Li et al. 2026, the arXiv preprint, Mohseni 2022, Hamerly 2019) appear in several essays.

**Author correspondence.** Before publishing essays 6 and 7, email the corresponding authors (Weisheng Zhao; Bhavin Shastri) with the specific findings and the scripts. Record replies in a log. Either a reply or a documented non-reply strengthens both essays, and a reply may resolve the instance-mismatch question outright.

**Figures.** Each essay currently has at most one table. Add one or two austere TikZ figures per essay, in the style used for The Shape of Search. Suggestions are listed per essay below.

---

## 1. The Spin Count

**Current core.** Component, system, and demonstrated compositional capacity. A storage bound (the one-bit coupling matrix at 96,000 spins exceeds the board's 512 MB) and a time bound (the paper's own flip-rate definition fixes an iteration as a sweep, so a 45 ns iteration at full size implies an almost frozen system).

**Rigor.**
- Present the two bounds as what they are: one representational, one temporal-dynamical. Make each a numbered proposition with its assumptions listed explicitly.
- Add a sensitivity table for the storage bound: 1-bit, 4-bit, and 8-bit couplings; symmetric and full storage; with and without an operating-system reservation.
- Recompute the time bound under a roofline model (bytes moved per flip against peak bandwidth), so the argument uses standard vocabulary rather than an ad hoc estimate.
- Check the Zynq-7020 block RAM figure against AMD's data sheet rather than vendor listings.
- Treat the sparse case formally. Give the entropy bound for density p and show where, as p rises, the storage bound starts to bind again.
- Add the arXiv table's spin "Number" row (96k beside 1,143, 80, 8, 1) as direct evidence that component counts were used as a comparison dimension.

**New sections.**
- *Capacity claims elsewhere in the Ising literature.* The 1.3-Mbit multi-chip annealer, multi-chip simulated bifurcation machines, and sparse p-bit machines each state their capacity differently. Compare how each separates spin count from connectivity.
- *What a composed-capacity claim would require.* A short positive section: the minimum evidence (an instance at scale N, with the coupling store and iteration time reported together).

**Figure.** Log-log plot of spin store (linear) against coupling store (quadratic) as N grows, with the board's DDR3 and block RAM marked as horizontal lines.

**Citations to add.**
- Williams, Waterman & Patterson, "Roofline: An Insightful Visual Performance Model," *Communications of the ACM* 52(4), 2009.
- AMD/Xilinx, *Zynq-7000 SoC Data Sheet: Overview* (DS190).
- TUL, *PYNQ-Z2 Reference Manual*.
- Tatsumura, Yamasaki & Goto, "Scaling out Ising machines using a multi-chip architecture for simulated bifurcation," *Nature Electronics* 4, 2021.
- Yamamoto et al., "A 1.3-Mbit annealing system composed of fully-synchronized 9-board × 9-chip × 16-kbit annealing processor chips," A-SSCC 2021.
- Aadit et al., "Massively parallel probabilistic computing with sparse Ising machines," *Nature Electronics* 5, 2022.
- Lucas, "Ising formulations of many NP problems," *Frontiers in Physics* 2, 2014.
- Mohseni, McMahon & Byrnes, "Ising machines as hardware solvers of combinatorial optimization problems," *Nature Reviews Physics* 4, 2022.

---

## 2. The Comparison Table

**Current core.** In the arXiv version, every efficiency entry equals 1/(t_spin × 10⁶ × P), so the column contains no solution quality. The published version switches to time-to-solution, and the machine's lead shrinks by up to three orders of magnitude.

**Rigor.**
- Sharpen the framing: comparative superiority is partly a property of the evaluative rule. The machine didn't get slower; the table got less permissive. Keep the published version authoritative for the final claim and the preprint as evidence of how the comparison was first assembled.
- Record which arXiv version was used (v1, v2, …) and check for intermediate versions with further changes.
- Obtain the published Table 1 itself (library access) and reconstruct every row that can be reconstructed, the way Table 3 does for the preprint.
- Formalize the platform-independence assumption: state exactly what equality of transition kernels would require, and which rows meet that condition on resolution grounds.
- Add a boundary audit table: for each row, record which boundary its time figure is drawn at and which boundary its power figure is drawn at.

**New sections.**
- *The quantum-speedup benchmarking debates as precedent.* The 2013 to 2015 exchanges over D-Wave benchmarking produced most of the methodology this essay asks for: defining speedup relative to the best classical baseline, time-to-target metrics, and instance-class sensitivity.
- *Benchmarking as a discipline.* Standard guidance from experimental algorithmics and high-performance computing on what a fair comparison must report.

**Figure.** A dot plot of each platform's advantage ratio in the preprint and in the published version, connected by lines, so the contraction is visible at a glance.

**Citations to add.**
- Rønnow et al., "Defining and detecting quantum speedup," *Science* 345, 2014.
- McGeoch & Wang, "Experimental evaluation of an adiabatic quantum system for combinatorial optimization," Computing Frontiers 2013.
- King et al., "Benchmarking a quantum annealing processor with the time-to-target metric," arXiv:1508.05087, 2015 **(verify)**.
- Johnson, "A theoretician's guide to the experimental analysis of algorithms," in *Data Structures, Near Neighbor Searches, and Methodology* (DIMACS), 2002.
- Hoefler & Belli, "Scientific benchmarking of parallel computing systems," SC15, 2015.
- Hamerly et al., "Experimental investigation of performance differences between coherent Ising machines and a quantum annealer," *Science Advances* 5, 2019.
- Aramon et al., "Physics-inspired optimization for quadratic unconstrained problems using a digital annealer," *Frontiers in Physics* 7, 2019.

---

## 3. The Location of Chance

**Current core.** A Glauber update splits into valuation and sampling. Sampling is on the chip; valuation, coupling, and scheduling are on the FPGA. The junctions carry about 0.1% of iteration energy, so an Amdahl bound caps what improving them can achieve.

**Rigor.**
- State the energy result explicitly: eliminating the junctions' cost entirely improves total energy efficiency by at most about 1/(1 − 0.001) ≈ 1.001, a tenth of a percent. This turns a verbal point about boundaries into an architectural result.
- Replace the "if updated in parallel" hedge on the time share with a bound that holds under both parallel and sequential update schedules.
- Apply the Amdahl bound to the photonic machine from essay 7 as well. Its loop closes through a PC, so the same calculation should be possible from its released code.
- Tighten the naming criterion into a definition with a threshold, and apply it to three or four named machines from the literature.

**New sections.**
- *The energy of data movement.* The standard observation that moving data costs far more than computing on it explains why valuation dominates.
- *A catalog of naming.* A short survey table: machine, name, where valuation happens, where sampling happens, and where coupling is stored. Coherent Ising machines, memristor Hopfield networks, p-bit computers, the two machines from this series, and a quantum annealer.

**Figure.** A stacked bar of one iteration's energy and time, partitioned by component, with the named component highlighted.

**Citations to add.**
- Horowitz, "Computing's energy problem (and what we can do about it)," ISSCC 2014.
- Hill & Marty, "Amdahl's law in the multicore era," *Computer* 41(7), 2008.
- Camsari, Faria, Sutton & Datta, "Stochastic p-bits for invertible logic," *Physical Review X* 7, 2017.
- Borders et al., "Integer factorization using stochastic magnetic tunnel junctions," *Nature* 573, 2019.
- Böhm, Verschaffelt & Van der Sande, "A poor man's coherent Ising machine based on opto-electronic feedback systems," *Nature Communications* 10, 2019.

---

## 4. Chips That Route Chips

**Current core.** Three kinds of self-reference: processing one's own description (reflexive computation), solving a problem of one's own kind (type-level recurrence), and helping produce a successor (genealogical recursion). The chip shows only the second. Lineages improve or drift depending on whether they contain a check that self-agreement can't pass.

**Rigor.**
- Add the verified instance details: 7 terminals, 8 candidate Steiner points, 450 spins, solved exactly by enumeration in about a hundredth of a second.
- Make the proposition about non-degenerate lineage more precise. Define the check V as a predicate over generations and separate "detects inherited error" from "corrects it."
- Distinguish the three lineage outcomes (convergence, invisible persistence, erosion) by what the reference criterion is, not just by example.

**New sections.**
- *Machine learning in chip design.* The reinforcement-learning floorplanning paper and the independent assessment that followed are the most direct present-day case of tools shaping their successors in chip design, including a public dispute over evaluation. It fits the essay's argument closely.
- *Global routing as practiced.* A short section on what industrial global routing actually involves (millions of nets, congestion, the ISPD benchmark suites), to make the scale gap concrete.
- *Philosophy of technical lineage.* A brief engagement with Simondon on the genesis of technical objects, if the essay is to reach beyond engineering.

**Figure.** A three-column diagram of the three lineages (plates, compilers, models), each showing the generation-to-generation arrow and where the external check enters.

**Citations to add.**
- Kahng, Lienig, Markov & Hu, *VLSI Physical Design: From Graph Partitioning to Timing Closure*, Springer, 2011.
- Mirhoseini et al., "A graph placement methodology for fast chip design," *Nature* 594, 2021.
- Cheng, Kahng et al., "Assessment of reinforcement learning for macro placement," ISPD 2023 **(verify authorship and venue details)**.
- Nam, Sze & Yildiz, "The ISPD global routing benchmark suite," ISPD 2008 **(verify)**.
- Simondon, *On the Mode of Existence of Technical Objects* (1958; English translation 2017).
- Shumailov et al., "AI models collapse when trained on recursively generated data," *Nature* 631, 2024 (already cited; keep).

---

## 5. Certified Chance

**Current core.** "Random" names seven properties, each certified to a different audience. A deterministic 16-bit shift register matches the junctions, so the task doesn't need unpredictability, and the physical source earns its place through cost. The switching curve is a windowed fit, and the 13-year lifetime is a usage assumption.

**Rigor.**
- Treat the 45% versus 55% midpoint as version drift requiring explanation, not a contradiction. The fit, the sample, or the operating condition may have changed between versions. Say so explicitly and propose what would resolve it.
- Formalize the endurance point: lifetime = endurance ÷ duty cycle. Tabulate lifetime at 0.3 ns, 1 ns, 45 ns, and the implied 41 µs interval.
- Distinguish censored from failure data properly. 10¹³ is a tested-to figure, so it's a lower bound, and the essay should say what distribution assumptions a lifetime projection from censored data needs.
- Run the shift-register comparison in simulation using the released routing instance: vary register width and measure success, to confirm the resolution effect independently.
- Clarify which NIST battery was likely used once Supplementary Note 2 is available.

**New sections.**
- *Magnetic entropy sources in the literature.* Superparamagnetic junction random number generators and "spin dice" devices, and how their certification practices compare.
- *Test batteries beyond NIST.* TestU01 and Diehard as the standard for statistical testing of generators, and why passing them still says nothing about unpredictability.

**Figure.** A matrix with the seven properties as rows and the certifying tests as columns, marked where each test speaks.

**Citations to add.**
- L'Ecuyer & Simard, "TestU01: A C library for empirical testing of random number generators," *ACM Transactions on Mathematical Software* 33(4), 2007.
- Knuth, *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 3rd ed., 1997.
- Vodenicarevic et al., "Low-energy truly random number generation with superparamagnetic tunnel junctions for unconventional computing," *Physical Review Applied* 8, 2017.
- Fukushima et al., "Spin dice: a scalable truly random number generator based on spintronics," *Applied Physics Express* 7, 2014.
- Motwani & Raghavan, *Randomized Algorithms*, Cambridge University Press, 1995.
- Nelson, *Accelerated Testing: Statistical Models, Test Plans, and Data Analyses*, Wiley, 1990.

---

## 6. Replottable, Not Rerunnable

**Current core.** The release was meant only for figures, but its notebooks define instances and energy functions. The "Ground state" lines are run minima. A valid routing tree of length 32 beats the one shown as optimal (36). The gap figure measures dispersion.

**Rigor.** This is the essay where precision matters most, since it makes a factual claim about a published figure.
- Print both edge sets in full: the released final tree (length 36) and the exhaustive minimum (length 32), with coordinates.
- Print every penalty term's value for both configurations, and both energies under the notebook's own Hamiltonian and weights.
- State the decisive claim conditionally and exactly: *under the released notebook's own instance, objective, and validity conditions, the configuration labelled optimal has length 36, while a valid configuration of length 32 exists.*
- Make the semantic-type point explicit. A run minimum is an empirical quantity, not a certified ground-state energy. Normalizing a gap against it measures dispersion relative to the best sample, which is a different type of quantity from distance to an established optimum.
- For Fig. 5, report the best known state as "best known under 2,000 annealing restarts," and add an exact solver check (a MILP or branch-and-bound on 40 variables is tractable) to certify it.
- Cite the specific commit hash of the repository used.

**New sections.**
- *The reproducibility literature.* Empirical studies of code and data availability in computational research, and the difference between repeatability, reproducibility, and replicability in ACM's and the National Academies' vocabularies.
- *A second release for comparison.* Contrast with the photonic paper's fuller release (code, data, simulator), which enabled the deeper checks in essay 7. This makes the counterpractice concrete rather than hypothetical.
- *Author response.* Whatever reply the correspondence yields.

**Figure.** The routing instance drawn twice, side by side: the length-36 tree and the length-32 tree, with module outlines.

**Citations to add.**
- Stodden, Seiler & Ma, "An empirical analysis of journal policy effectiveness for computational reproducibility," *PNAS* 115(11), 2018.
- Collberg & Proebsting, "Repeatability in computer systems research," *Communications of the ACM* 59(3), 2016.
- Wilkinson et al., "The FAIR Guiding Principles for scientific data management and stewardship," *Scientific Data* 3, 2016.
- Donoho, "An invitation to reproducible computational research," *Biostatistics* 11(3), 2010.
- ACM, *Artifact Review and Badging*, version 1.1, 2020.

---

## 7. The Easy Phase

**Current core.** About 1% of spin assignments are ground states in the released instances, so random guessing succeeds about once in a hundred tries. The D-Wave comparison used unique-solution instances, a class absent at those sizes under the stated range. The TTS fit goes negative below 24 integers. Lidar and Biham serve as a candid precedent.

**Rigor.**
- Add the success-probability arithmetic: with ground-state fraction near 10⁻², success after 100 independent samples is 1 − 0.99¹⁰⁰ ≈ 0.634, and after 300 it is about 0.951. A strong success curve can arise without a strong search process.
- Compare the exact counts with Mertens's asymptotic formula for the number of perfect partitions in the easy phase, as an independent check.
- Add classical baselines beyond random guessing: the Karmarkar–Karp differencing heuristic and a complete anytime algorithm. Both solve these instances instantly and anchor what the benchmark can distinguish.
- Resolve the 1–8 versus 0–16 range question against the Supplementary Information.
- Run the photonic machine's released simulator on unique-solution instances, if feasible, to see how it performs on the harder class the annealer faced.
- Present the negative-time extrapolation as a fitted curve used outside its admissible domain, and state that domain.

**New sections.**
- *Phase transitions in computational hardness.* The broader literature on where hard instances lie, of which number partitioning is the cleanest example.
- *Planted-solution benchmarks.* How the quantum-annealing community built instance classes with known, controllable hardness, as the positive model for what a benchmark should report.
- *A short methods note on counting.* The subset-sum recurrence, its cost, and why it's exact.

**Figure.** Ground-state fraction against N for the released instances, with the random-guess success curve 1 − (1 − p)ᵏ drawn beside it.

**Citations to add.**
- Cheeseman, Kanefsky & Taylor, "Where the really hard problems are," IJCAI 1991.
- Hayes, "The easiest hard problem," *American Scientist* 90(2), 2002.
- Gent & Walsh, "Phase transitions and annealed theories: number partitioning as a case study," ECAI 1996 **(verify)**.
- Karmarkar & Karp, "The differencing method of set partitioning," Technical Report UCB/CSD 82/113, UC Berkeley, 1982.
- Korf, "A complete anytime algorithm for number partitioning," *Artificial Intelligence* 106(2), 1998.
- Hen et al., "Probing for quantum speedup in spin-glass problems with planted solutions," *Physical Review A* 92, 2015.
- Rønnow et al. 2014 (shared with essay 2).

---

## Suggested order of work

1. Series-level: reproducibility bundle, shared bibliography, and author emails (the replies take time, so send these first).
2. Essay 6, since it carries the most consequential factual claim and benefits most from explicit edge sets and an exact solver check.
3. Essay 7, for the same reason, plus the classical baselines.
4. Essays 1 to 3, which mostly need formalization and literature.
5. Essays 4 and 5, which need the widest new reading.
6. A preface stating the unifying thesis, written last, once the expanded essays show what the series actually established.
