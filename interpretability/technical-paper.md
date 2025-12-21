# A Unified Event-Historical Framework for Causal Mechanistic Interpretability

## Abstract

Recent advances in mechanistic interpretability have grounded explanations of neural networks in causal reasoning, progressing from descriptive inspection to interventions, counterfactuals, and causal abstractions. However, existing state-centric approaches overlook irreversibility, history sensitivity, and regime shifts that are critical to understanding complex learned systems. This paper introduces a unified paradigm that resolves these limitations by distinguishing between value-carrying texture-nodes and regime-selecting event-nodes. This typed framework enables a formalization of two-channel mediation and graph rewrite semantics, providing a principled explanation for empirical puzzles such as substitution failure and algorithmic mixture. By reinterpreting training dynamics as a process of kernel formation, the framework also clarifies phenomena like grokking and sudden circuit emergence. This event-historical perspective extends beyond neural networks to large-scale knowledge systems, reconceiving mechanistic understanding as event-historical causal reverse engineering that preserves empirical rigor while incorporating time, constraint, and irreversibility as first-class explanatory elements.

---

## 1. Introduction

The remarkable capabilities of large neural networks have spurred a concerted effort to move beyond treating them as black boxes and toward understanding their internal operations. Initial interpretability work focused on correlational methods like visualization and feature attribution, but these approaches struggled to distinguish functional mechanisms from epiphenomenal patterns. In response, the field has matured toward mechanistic interpretability, which seeks to reverse-engineer the algorithms within these networks by identifying the causal processes that generate their behavior.

A coherent causal paradigm has emerged, defining genuine understanding as the ability to intervene on internal variables, evaluate counterfactuals, and validate algorithmic abstractions. However, this paradigm implicitly relies on a state-based ontology, where the causal influence of a system’s history is assumed to be fully captured by its present state. This overlooks the critical role of irreversible commitments and discrete regime changes.

This paper’s central thesis is that these limitations can be resolved by adopting a unified, event-historical framework grounded in a typed distinction between texture-nodes and event-nodes. This extension preserves the rigor of existing causal methods while providing a more complete vocabulary for describing substitution failure, algorithmic mixture, and circuit formation during training.

---

## 2. The Causal Paradigm and Its State-Centric Limits

Mechanistic interpretability, in its strict sense, requires identifying internal components whose interventions produce predictable changes consistent with an algorithmic description. Causality distinguishes true mechanisms from correlations by enabling explanation, control, and counterfactual reasoning.

### Intervention

An intervention sets an internal variable to a value it would not naturally take, severing upstream dependencies. By evaluating downstream effects, researchers can test necessity and sufficiency claims.

### Progression of Methods

- **Activation steering** establishes causal efficacy of representations but lacks algorithmic specificity.
- **Causal mediation and tracing** reveal structured information pathways but assume a fixed computational regime.
- **Causal abstraction** tests interventional equivalence between networks and algorithms but often presumes regime stability.

### Limits of State-Based Functionalism

State-based functionalism collapses history into instantaneous configuration. Two numerically identical states reached through different irreversible histories may diverge in future behavior. Interventions admissible under one history may be incoherent under another. Mechanistic understanding must therefore reconstruct history, not merely inspect state.

---

## 3. The Event-Historical Framework

To address these limits, we introduce a minimal typed extension to causal graphs.

### Texture-Nodes

Texture-nodes are causal variables whose influence is exhausted by the instantaneous value they carry. Interventions substitute one value for another within a fixed regime.

### Event-Nodes

Event-nodes are causal variables whose role is to select a regime, constraining admissible future states. Their effect is structural, not reducible to a numerical value.

### Kernel Histories

Structural irreversibility arises when an event-node firing permanently restricts future possibilities. The ordered sequence of such events constitutes a **kernel history**, which determines admissible computational trajectories.

Event-nodes may induce graph rewrite semantics, replacing subgraphs and enabling discrete regime shifts to be modeled explicitly.

---

## 4. Formal Implications and Unification

### Two-Channel Mediation Theorem

The total causal effect of an input decomposes into:
- a texture-mediated channel (value propagation), and
- an event-mediated channel (regime selection).

Value-based mediation is sufficient if and only if the event state remains invariant under intervention.

### Reinterpreting Empirical Phenomena

- **Causal tracing** becomes event-history archaeology, probing necessary kernel commitments.
- **Substitution failure** arises from kernel incompatibility, not semantic error.
- **Algorithmic mixture** reflects kernel switching via early event-node selection.

---

## 5. Spherepop Calculus Grounding

Spherepop calculus provides an axiomatic language for event-level commitment:

- **Pop**: irreversible exclusion of pathways.
- **Bind**: formation of dependency constraints.
- **Refuse**: principled non-activation.
- **Collapse**: irreversible quotienting of distinctions.

Kernel histories correspond to Spherepop programs acting on option-space. Mechanistic interpretability itself becomes a Spherepop process, where experiments irreversibly eliminate hypotheses.

---

## 6. Applications

### Transformer Circuits

In Indirect Object Identification, partial restoration failures are explained by kernel mismatch. Event-aware restoration aligns kernel histories and enables successful texture recovery.

### Training Dynamics

- **Texture learning** adjusts parameters within regimes.
- **Kernel formation** stabilizes new regimes.

Grokking and sudden circuit emergence correspond to delayed kernel commitments.

### Knowledge Networks

In systems like wikis:
- textures are content and links,
- events are governance and policy decisions.

Resilience depends more on event-level structure than content redundancy.

---

## 7. Conclusion

Mechanistic understanding requires reconstructing the irreversible commitments shaping a system’s behavior. By distinguishing texture-nodes from event-nodes and grounding this distinction in causal theory and Spherepop calculus, this framework unifies disparate empirical phenomena and extends beyond neural networks.

Mechanistic interpretability becomes an event-historical science: reverse engineering constraint, not merely computation. Understanding lies not only in what is present, but in what has been irrevocably ruled out.