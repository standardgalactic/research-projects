# Event-Nodes & Texture-Nodes: A Simple Guide

## Introduction: Why Values Aren't the Whole Story

To understand how a complex system works—whether it's an AI model or a biological process—we often start by looking at its internal *values* or *states* at a single moment in time. We might inspect a neuron's activation or check the value of a variable. This is a useful snapshot, but it has a critical limitation.

This guide solves a puzzle that these state-based views can't: **How can two identical situations lead to different futures?** The puzzle arises because a system's history isn't just a backstory; it's baked into its present reality. Two systems can look identical right now, but if they arrived there differently, they may react in completely different ways.

To solve this, we introduce two concepts: **Event-Nodes** and **Texture-Nodes**. Using a simple analogy, we show how a system's history acts as a set of constraints that actively shape what futures are possible.

---

## 1. The Core Analogy: Designing a Video Game World

Imagine a procedural world generator for a video game. It lets you make two fundamentally different kinds of choices.

First, you make a **structural choice** about the kind of world you want:

- Lava World  
- Forest World  
- Underwater World  

Second, after choosing the world type, you make **fine-grained adjustments** to customize it:

- Lava brightness  
- Tree density  
- Fish color  

These two kinds of choices correspond directly to **Event-Nodes** (structural commitments) and **Texture-Nodes** (fine-tuning parameters).

---

## 2. Texture-Nodes: The Dials and Sliders

A **Texture-Node** is like a dial or slider. It adjusts how a system behaves *within* an already-chosen regime.

Key properties:

- **They carry values**  
  A Texture-Node is a causal variable whose influence is determined entirely by its current value.

- **They modulate within regimes**  
  A slider for tree density only makes sense once you're in a Forest World.

- **They are usually reversible**  
  You can move the slider back. Restoring the value restores the prior behavior.

Texture-Nodes change *how* something happens, not *what kind of thing* is happening.

---

## 3. Event-Nodes: The Big, Irreversible Choices

An **Event-Node** is the generator choice itself: Lava, Forest, or Underwater.

Key properties:

- **They select regimes**  
  An Event-Node chooses the rule-set that governs all future possibilities.

- **They impose constraints**  
  Choosing Lava World doesn't just add lava—it removes trees, oceans, and mountains as possibilities.

- **They are structurally irreversible**  
  No amount of slider adjustment can turn a Lava World into a Forest World.

Event-Nodes change *what is possible at all*.

---

## 4. Side-by-Side Comparison

| Dimension | Texture-Nodes | Event-Nodes |
|--------|--------------|-------------|
| Analogy | Dials and sliders | Generator choice |
| Role | Carries a value | Selects a regime |
| Type of change | Modulation | Structural constraint |
| Effect | Substitutes values | Eliminates futures |
| Reversibility | Usually reversible | Structurally irreversible |

---

## 5. Why This Matters: History and Failure

History matters because **past events constrain present meaning**.

### Substitution Failure Example

- You choose *Underwater World* (an Event).
- You adjust *Coral Reef Density* (a Texture).
- You then try to insert a value meant for *Mountain Height*.

The system fails—not due to a bad number, but because the *mountain regime no longer exists*. The failure reflects a **mismatch of histories**, not a simple error.

This explains why systems can fail even when values look correct: the *event-level commitments* are incompatible.

---

## 6. Key Takeaway

In any complex system:

- **Texture-Nodes** adjust behavior *within* a world.
- **Event-Nodes** define *which world exists at all*.

One changes the picture.  
The other changes the frame.
