# Contributing to the Spherepop / RSVP Tooling Suite

Thank you for your interest in contributing to the Spherepop / RSVP tooling ecosystem.

This project operates under strict epistemic and ethical constraints. Contributions are welcome only insofar as they preserve the project’s core commitment to **epistemic transparency, restraint, and non-deceptive design**.

This document specifies *non-negotiable requirements* for all contributions.

---

## 1. Project Scope and Intent

The Spherepop / RSVP tools are:

- Exploratory and educational
- Local and cooperative by design
- Explicitly non-diagnostic
- Explicitly non-authoritative
- Explicitly non-adversarial

They are **not** security tools, monitoring systems, penetration frameworks, or analytical instruments.

Any contribution that risks being interpreted as such will be rejected.

---

## 2. Mandatory Epistemic Disclosure

### 2.1 Runtime Disclosure

All user-facing tools **MUST**:

- Display an epistemic banner at startup **or**
- Include a persistent, visible disclaimer during execution

The disclosure must clearly state that:

- The tool performs no real analysis
- Output must not be interpreted as evidence
- Any perceived meaning is attributable to the observer

Failure to include runtime disclosure is grounds for immediate rejection.

### 2.2 Documentation Disclosure

All tools **MUST** include:

- A man page (`.1` or `.7`) with an **EPISTEMIC STATUS** section
- Clear **NON-GOALS** and **LIMITATIONS**

README-only disclosure is insufficient.

---

## 3. Mode Separation (`sp-mode`)

All tools that could plausibly be misinterpreted as doing analytical or evaluative work **MUST** participate in the `sp-mode` system.

### 3.1 Required Properties

- Modes must be **explicit** (`--mode satire`, `--mode instrument`)
- Modes must be **mutually exclusive**
- Default execution without an explicit mode is discouraged and may be disallowed

### 3.2 Prohibited Behavior

- Silent fallback between modes
- Mode inference
- Blended behavior that obscures epistemic intent

---

## 4. Linting and Build Gates

### 4.1 Epistemic Linting

All contributions **MUST** pass:

```sh
sp-lint-epistemic

