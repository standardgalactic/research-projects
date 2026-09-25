---
applyTo: "experiments/**"
---

# Experiment instructions

- Classify each experiment as `computational`, `long_computational`, `manual`, `physical`, `destructive`, or `human_operated`.
- Computational experiments declare environment, dependencies, seeds, instance set, budget, stopping criteria, outputs, and expected runtime.
- Long experiments must support checkpointing and must not run in ordinary CI.
- Manual and physical experiments are protocols until reviewed data are supplied. Copilot may scaffold acquisition and analysis code but may not claim execution.
- Destructive experiments are never automated. Put a conspicuous warning before procedures involving storage wear, electrical stress, irreversible writes, abrasion, or equipment damage.
- Human-operated demonstrations require voluntary participation, minimal collection, anonymization, and an explicit statement that the result is not a population study.
- Include relevant safety precautions for glass, abrasive dust, electricity, lasers, magnetic devices, radiation sources, and mechanical equipment.
- Preserve raw observations and calibration records. Analysis outputs cite their raw-data hashes and protocol version.
- Absurd experiments follow the same evidence rules as serious experiments. State the hidden assumption or category error they isolate.
- Humor may affect names and captions, never specifications, measurements, uncertainty, or source descriptions.
- Do not contact authors, open external issues, or submit requests. External correspondence requires human review and action.

