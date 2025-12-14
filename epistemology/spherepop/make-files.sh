#!/usr/bin/env bash
set -euo pipefail

PROJECT="spherepop_manuscripts"

echo "Creating Spherepop multi-journal LaTeX workspace..."

# Root
mkdir -p "$PROJECT"
cd "$PROJECT"

# Shared infrastructure
mkdir -p shared/{preamble,macros,sections,appendices,bib}

# Shared preamble and macros
touch shared/preamble/preamble.tex
touch shared/macros/macros.tex

# Shared core sections (reused across all papers)
mkdir -p shared/sections/core
touch shared/sections/core/{
introduction.tex,
motivation.tex,
event_ontology.tex,
deterministic_replay.tex,
semantic_equivalence.tex,
abstraction_vs_compression.tex,
stability_and_perturbation.tex,
speculation_and_counterfactuals.tex,
comparison_to_ai.tex,
discussion.tex,
conclusion.tex
}

# Shared appendices (selectively included)
mkdir -p shared/appendices
touch shared/appendices/{
formal_semantics.tex,
operational_semantics.tex,
complexity_analysis.tex,
stability_proofs.tex,
philosophical_notes.tex
}

# Bibliography
touch shared/bib/references.bib

# -------- Core Versions --------

# 1. Philosophy / Foundations
mkdir -p philosophy/{sections,appendices}
touch philosophy/main.tex
touch philosophy/sections/{metaphysics.tex,epistemology.tex,reduction.tex}
touch philosophy/appendices/{formal_notes.tex}

# 2. AI Theory
mkdir -p ai_theory/{sections,appendices}
touch ai_theory/main.tex
touch ai_theory/sections/{formal_model.tex,limitations_of_llms.tex,implications_for_architecture.tex}
touch ai_theory/appendices/{proofs.tex}

# 3. Cognitive / Interdisciplinary
mkdir -p cognitive_science/{sections,appendices}
touch cognitive_science/main.tex
touch cognitive_science/sections/{memory_and_learning.tex,animal_cognition.tex,development.tex}
touch cognitive_science/appendices/{empirical_notes.tex}

# -------- Orthogonal Versions --------

# 4. Information / Entropy / Complexity
mkdir -p entropy/{sections,appendices}
touch entropy/main.tex
touch entropy/sections/{entropy_and_structure.tex,phase_transitions.tex}
touch entropy/appendices/{thermodynamics.tex}

# 5. Systems / OS / PL Theory
mkdir -p systems/{sections,appendices}
touch systems/main.tex
touch systems/sections/{kernel_model.tex,event_sourcing.tex,consistency.tex}
touch systems/appendices/{implementation_notes.tex}

# 6. Physics / Structural Mathematics
mkdir -p structural_math/{sections,appendices}
touch structural_math/main.tex
touch structural_math/sections/{invariance.tex,geometry_of_semantics.tex}
touch structural_math/appendices/{formal_correspondence.tex}

# Utilities
mkdir -p tools
touch tools/build_all.sh
touch tools/clean.sh

echo "Directory structure created successfully."

