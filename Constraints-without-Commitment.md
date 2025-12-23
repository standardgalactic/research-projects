# Constraints Without Commitment
## On the Limits of Algebraic Unification in Contemporary Deep Learning

## Overview

This paper examines the strengths and limits of Categorical Deep Learning (CDL) as a unifying mathematical framework for neural network architectures. While CDL succeeds in formalizing lawful computation and architectural invariants, it is argued to be structurally incapable of modeling commitment, accountability, or historically binding action.

The central claim is not that CDL is flawed, but that its abstraction necessarily erases the very features required to model agency.

---

## Main Argument

Categorical Deep Learning provides a powerful algebraic language for describing neural computation. It captures structure-preserving transformations, explains invariance and compositionality, and unifies diverse architectures under a single formalism.

However, CDL cannot represent commitment.

Specifically, it cannot model irreversible historical events, obligation, refusal, or ownership. CDL formalizes what computations are possible, but not what must or must not occur once an action has been taken. In philosophical terms, CDL is alethic rather than deontic.

---

## What CDL Does Well

The paper acknowledges CDL as a genuine theoretical success.

It unifies geometric, recurrent, and message-passing architectures, explains generalization and stability via parametric maps and functorial structure, accounts for weight tying and equivariance, and clarifies why certain architectures are data-efficient and robust.

CDL provides a clean and powerful theory of lawful computation.

---

## The Core Limitation

Despite these successes, CDL has a fundamental blind spot.

It models constraints but not commitment. It describes how systems compute, but not why they stop, refuse, or bind themselves. It cannot express irreversible acts or historical responsibility.

As a result, CDL cannot serve as a theory of agency or accountable behavior.

---

## Reversing the Direction of Derivation

Rather than extending CDL directly, the paper proposes a reversal of perspective.

First, begin with eventful implementations defined by histories of irreversible events.

Second, coarse-grain into a field-theoretic description (RSVP) consisting of scalar, vector, and entropy fields.

Third, recover existing theories as abstractions. Geometric Deep Learning retains symmetry while forgetting thermodynamic cost. Categorical Deep Learning retains algebraic lawfulness while forgetting event history.

In this view, CDL and GDL are quotients of a more primitive, event-aware theory.

---

## Formal Demonstrations

The paper provides concrete formal support for this claim.

It includes categorical constructions showing CDL and GDL as quotient categories of RSVP, minimal extensions such as event-recording morphisms and commitment-enriched categories, and a worked example using two-digit increment with carry.

This example demonstrates how event records break reparameterization symmetry, enable strong negation and refusal, and encode obligation that cannot be algebraically erased.

---

## Conclusion

The conclusion is deliberately narrow and precise.

CDL is complete for lawful computation but incomplete for modeling agency and history.

The missing elements—commitment, refusal, ownership—are not flaws in CDL but consequences of its abstraction. To model accountable systems, one must either retain event history or reintroduce commitment as a first-class primitive.

Algebra alone is insufficient.

---

## Implications

Purely algebraic theories of intelligence cannot explain historical binding. Agent-like AI requires event-aware or history-sensitive formalisms. CDL remains indispensable for architecture, but inadequate for agency.

---

## Keywords

Categorical Deep Learning, algebraic constraints, commitment, agency, event history, geometric deep learning, RSVP field theory, quotient categories, parametric maps.