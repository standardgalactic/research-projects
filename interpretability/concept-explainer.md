# A Causal Guide to Understanding AI

## 1. Introduction: Why “Looking” Inside an AI Isn’t Enough

For years, efforts to understand how powerful AI models work were focused on visibility. Researchers developed techniques to visualize the intricate patterns of a neural network’s internal activations, much like creating a map of a complex city. These early methods, such as feature attribution, could show us which digital “neurons” light up when the AI performs a certain task, but they couldn’t definitively tell us why. They often conflated correlation with computation.

This is a critical distinction. Imagine a light on your car’s dashboard that turns on whenever the engine gets hot.

- **Correlation:** The light being on correlates with the engine being hot. They happen together. A purely observational approach might conclude that the light is an important part of the engine’s heating process.
- **Causation:** The engine getting hot causes a sensor to trigger the light. The light doesn’t cause the heat; it is a consequence of it. To understand the engine, you need to know what causes the heat (for example, a broken fan) and what the light is for (alerting the driver), which in turn causes the driver to pull over.

Early interpretability work often mistook correlation for computation. This document introduces a more powerful approach: the **causal paradigm** of mechanistic interpretability. This method shifts the goal from passively observing the model to actively experimenting on it.

## 2. The Causal Paradigm: From Observation to Intervention

In the causal paradigm, a system is mechanistically understood when we can identify its internal components whose **interventions** produce predictable changes consistent with an algorithmic description. This requires the ability to explain, predict, and control.

The core tool of this paradigm is the **intervention**. An intervention sets an internal variable in the model to a value it would not have taken on its own, deliberately breaking upstream dependencies.

| Approach | Observational Interpretability | Causal Interpretability |
|--------|------------------------------|------------------------|
| Core question | What internal patterns correlate with behavior? | What internal components are responsible for behavior? |
| Primary method | Visualization, attribution, activation inspection | Intervention, counterfactual testing, value substitution |
| Primary risk | Mistaking correlation for computation | Building brittle or incomplete abstractions |
| Goal | See what the internals look like | Explain, control, and reverse-engineer the algorithm |

## 3. Level 1: A Gentle Nudge with Activation Steering

Activation steering is one of the earliest intervention-based techniques. Researchers identify a **steering vector**—a direction in activation space—and add it during computation to bias outputs.

This demonstrates that internal representations are **causally efficacious**, but it does not reveal the algorithm itself.

Limitations include:

- Brittleness across contexts
- Incomplete explanations
- Weaker control than prompting or fine-tuning

## 4. Level 2: Tracing the Path with Causal Mediation

Causal mediation decomposes effects into pathways. A common method is **causal tracing**:

1. Corrupt the input
2. Observe degraded output
3. Restore specific internal components
4. Measure output recovery

Components whose restoration recovers performance are identified as **causal mediators**. This reveals structured pipelines rather than diffuse correlations.

## 5. Level 3: Uncovering the Algorithm with Causal Abstraction

Causal abstraction aims to verify that a network implements a specific algorithm.

The key criterion is **interventional equivalence**: interventions on the abstract algorithm must match interventions on the network.

This is tested using **interchange interventions**, where internal values are swapped across contexts. When behavior changes exactly as predicted, the abstraction is causally valid.

Validated abstractions are not metaphors; they are explanations.

## 6. Conclusion: The Science of Causal Reverse Engineering

Causal interpretability transforms AI understanding:

- Steering shows causal influence
- Mediation traces pathways
- Abstraction validates algorithms

By treating models as experimental systems, mechanistic interpretability becomes a science of **causal reverse engineering**, turning black boxes into mechanisms we can genuinely understand.