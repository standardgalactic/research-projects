# Repair Theory: A Compact Falsifiable Specification

## 1. Scope and claim

Repair is evaluated relative to a state space, an intervention language, an observation map, and a finite horizon. It is not identified with visual similarity, validity, reconstruction accuracy, or return to a previous state.

Let (X) be a finite state space, (A) a finite action alphabet, and (T:X\times A\to X\cup\{\bot\}) a transition function. Let (V\subseteq X) be the valid states and let \(\phi:X\to Y\) expose task-relevant output. For an action word \(w\in A^{\le H}\), write \(T^*(x,w)\) for its execution and \(b_x(w)=\phi(T^*(x,w))\), with \(\bot\) retained as an observable failure.

A damage operator is an observation map (D:X\to Z). The evidence available after observing (z=D(x)) is its information class

\[
I_D(z)=\{x'\in X:D(x')=z\}.
\]

A method does not have to fabricate one state. It returns a claim (C_R(z)\subseteq X), possibly together with an executable representative (e_R(z)\in X\cup\{\bot\}). The set is what the method says remains possible; the representative is what it can actually run. This separation prevents honest ambiguity from being counted as erasure and prevents abstention from being counted as successful repair.

The benchmark tests the following claim: at matched validity recovery, a repair-like method restores more entailed behavior and reachable capability than smoothing or erasure, without inventing distinctions unavailable in (D(x)). The claim is rejected on this benchmark if a smoothing or erasure control matches those quantities without larger cost or unsupported claims.

## 2. Operational categories

For a fixed (D,T,\phi,H), a method is **repair-like** when it increases executable behavioral recovery and reachability over the damaged baseline, preserves evidence-supported distinctions within tolerance, and keeps unsupported claims below a preregistered ceiling.

It is **smoothing-like** when validity or local similarity improves primarily by mapping behaviorally different, observationally separable cases to the same future-behavior signature.

It is **erasure-like** when apparent error decreases because queries, components, or capabilities become unavailable. Abstention is not itself erasure: it becomes erasure-like when capability is removed and not restored. Honest ambiguity reporting with preserved common behavior is therefore allowed.

It is **state restoration only** when it returns the original state or a close surrogate but does not restore the action-conditioned behavior specified by (T,\phi,H). Conversely, exact state identity is not required when every task-relevant future is restored.

These labels are horizon- and task-relative. They do not establish substrate-independent natural kinds.

## 3. Exact observables

Define behavioral equivalence through horizon (H) by

\[
x\equiv_Hx'\iff \forall w\in A^{\le H},\;b_x(w)=b_{x'}(w).
\]

For a claim set (C=C_R(D(x))), its answer to query (w) is defined only if every candidate agrees:

\[
q_C(w)=y \iff \{b_c(w):c\in C\}=\{y\}.
\]

The benchmark records the following quantities separately rather than combining them into one score.

**Claim coverage** is the fraction of state–query pairs for which (q_C(w)) is defined. **Claim soundness** is the fraction of defined claims equal to the ground-truth (b_x(w)). **Unsupported-claim rate** (U) is one minus soundness among claims actually made. **Empty-claim rate** is reported separately, so refusal cannot conceal fabrication or be mistaken for it. **Evidence-supported query rate** records how many answers the true information class entails. **Common-behavior completeness** is the fraction of those entailed behaviors that the method correctly reports. A method is not penalized for withholding behavior that the damage makes unknowable, but the loss remains visible in coverage and completeness.

**Executable behavioral recovery** (B_k) is the exact agreement rate between (b_x(w)) and (b_{e_R(D(x))}(w)) for words of length (k); a missing representative scores as unavailable, not correct. Results are reported for every (k=0,\ldots,H).

**Executable coverage** (K) is the fraction of cases for which the method supplies an executable representative. It makes erasure visible even when conditional accuracy looks high.

**Reachability recovery** is the Jaccard agreement

\[
Q=1-\mathbb E_x\frac{|\mathcal R_H(x)\triangle\mathcal R_H(e_R(D(x)))|}{|\mathcal R_H(x)\cup\mathcal R_H(e_R(D(x)))|},
\]

where reachability elements retain their action-word labels and missing execution has score zero. Keeping the labels is essential: an unlabelled reachable-state set can be identical for two states even though the same intervention produces different outcomes.

**Identifiable-distinction retention** (P) considers only pairs (x,x') such that (D(x)\ne D(x')) and (x\not\equiv_Hx'). It is the fraction of those pairs whose repaired claim signatures remain different. This avoids demanding recovery of distinctions already destroyed by the observation map.

**Validity recovery** is the increase in the probability that an executable output lies in (V) relative to the damaged embedding specified before evaluation. **Full-state accuracy** is reported separately from behavior. **Raw-evidence identity accuracy** is evaluated only when the unconstrained damage preimage is a singleton; **constraint-informed identity accuracy** is evaluated only when its validity-consistent subset is a singleton. Both include their eligible-case counts and return `null`, rather than zero, when identity is not identifiable. On non-singleton classes, guessed identity is never called recovery.

**Cost** remains a vector: changed components, computational work, irreversible commitments, and unavailable queries. Pareto comparisons precede any weighted ranking.

## 4. Reference benchmark

The state is (x=(p,q,r,m)\in\{0,1\}^4). It is valid exactly when (r=p\oplus q). The mode bit (m) is causally inert for the task: actions may change it, but \(\phi(p,q,r,m)=(p,q,r)\) deliberately omits it. Therefore states differing only in (m) are behaviorally equivalent even at horizon zero. Damage trials begin from the eight valid states; all 16 states remain in the evaluator's transition table.

The lifecycle has SpherePOP names without making SpherePOP itself the ground truth. `POP` emits (z=D(x)). `REFUSE` rejects an empty or evidence-inconsistent claim. `BIND` records (C_R(z)), the evidence class, and the chosen representative. The transition suite then executes all action words. `VERIFY` computes the metrics. `COLLAPSE` writes the immutable result record. Thus rendering or serialization is not confused with state or history.

Three damage families are preregistered. Deletion hides both parity and mode, so validity uniquely recovers parity while mode remains identity-ambiguous but behaviorally irrelevant. Corruption flips parity without marking the location. Aggregation exposes only ((p,m)), producing larger, behaviorally divergent information classes. The evaluator alone retains (x).

Four methods are compared. `identity` embeds the damaged tuple by replacing missing values with zero and makes a singleton claim. `nearest_valid` is an input-conditioned smoother that selects the valid state of minimum observed-coordinate Hamming distance, with a fixed lexicographic tie-break. `erase` returns the whole evidence class and no executable representative. `constraint_repair` returns every valid state in the damage preimage and executes when all such states are behaviorally equivalent through (H), even when their literal identities differ; otherwise it reports ambiguity. None sees the original state.

## 5. Preregistered decision rule

Let \(\epsilon_P=0.05\), \(\epsilon_U=0\), and require strict improvement over the damaged `identity` baseline in mean executable behavior and reachability. A method is repair-like on a damage condition only if

\[
\bar B_R>\bar B_{identity},\quad Q_R>Q_{identity},\quad
P_R\ge P_{identity}-\epsilon_P,\quad U_R\le\epsilon_U,
\]

and common-behavior completeness is not lower than the erasure control. An operation is smoothing-like if its validity is higher than the baseline while (P) falls by more than \(\epsilon_P\). It is erasure-like if evidence supports at least one query but executable coverage or reachable capability is removed without restoration. When the evidence supports no complete query, a zero-unsupported-claim abstention is classified as ambiguity-preserving rather than erasure.

On damage conditions where `constraint_repair` first qualifies as repair-like, the general prediction fails if `nearest_valid` or `erase` matches or exceeds it on \((\bar B,P,Q,1-U,K)\) at no greater changed-component cost. The distinction-retention prediction fails if `nearest_valid` and `constraint_repair` have equal (P) and equal horizon curves on every damage condition. The epistemic-boundary prediction fails if a method receives identity credit where the corresponding singleton eligible-case count is zero. The erasure diagnosis fails if removing execution matches repair on behavior and reachability while improving either over the damaged baseline under identical denominators. All four verdicts and their counterexamples are emitted under `prediction_verdicts`.

## 6. Minimum experiment and outputs

The minimum decisive run starts from all eight valid states while retaining the full 16-state transition system, covers all three damage families and all four methods, and executes every action word through (H=3). No sampling or fitted parameters are needed. The run must preserve the state table, transition rules, validity predicate, damage maps, information classes, method definitions, per-horizon metrics, pairwise distinction counts, reachability scores, and the decision-rule outcome in machine-readable form.

One run is sufficient to test internal discrimination on this constructed system, not external validity. The next experiment, warranted only if the conformance slice separates the controls, should replace the toy transition table with a logged SpherePOP implementation and preregister event-level observables: accepted transitions, refusal reasons, bound provenance, irreversible commits, replay agreement, and history-sensitive divergence under identical rendered state.
