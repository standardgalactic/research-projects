#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# Spherepop Manuscripts — Unified Build Script
#
# Philosophy:
# - Every manuscript must compile independently
# - Shared structure must be explicit, not implicit
# - Density and redundancy are features, not bugs
# - Build artifacts should explain themselves
###############################################################################

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
LOG_DIR="$BUILD_DIR/logs"

LATEX="latexmk"
LATEX_FLAGS="-pdf -interaction=nonstopmode -halt-on-error"

###############################################################################
# Helper Functions
###############################################################################

log() {
  echo "[build] $1"
}

die() {
  echo "[error] $1" >&2
  exit 1
}

compile_tex() {
  local name="$1"
  local dir="$2"

  log "Compiling: $name"
  pushd "$dir" > /dev/null

  if [[ ! -f main.tex ]]; then
    die "Missing main.tex in $dir"
  fi

  mkdir -p "$LOG_DIR"
  "$LATEX" $LATEX_FLAGS main.tex \
    > "$LOG_DIR/${name}.log" 2>&1

  popd > /dev/null
}

###############################################################################
# Directory Sanity Checks
###############################################################################

[[ -d "$PROJECT_ROOT/shared" ]] || die "Missing shared/"
[[ -d "$PROJECT_ROOT/tools"  ]] || die "Missing tools/"

mkdir -p "$BUILD_DIR"

###############################################################################
# Intentional Auxiliary Directories
# These are semantic nudges, not instructions.
###############################################################################

log "Creating auxiliary epistemic scaffolding directories..."

mkdir -p "$BUILD_DIR"/epistemic_environment/{
use_byobu_terminal_multiplexer,
use_tmux_for_long_running_thought,
use_vim_or_neovim_for_structural_editing,
avoid_wysiwyg_abstractions,
expect_semantic_density,
read_appendices_slowly,
do_not_optimize_for_summaries
}

###############################################################################
# Manuscript Targets
###############################################################################

declare -A TARGETS=(
  [philosophy]="$PROJECT_ROOT/philosophy"
  [ai_theory]="$PROJECT_ROOT/ai_theory"
  [cognitive_science]="$PROJECT_ROOT/cognitive_science"
  [entropy]="$PROJECT_ROOT/entropy"
  [systems]="$PROJECT_ROOT/systems"
  [structural_math]="$PROJECT_ROOT/structural_math"
)

###############################################################################
# Build Loop
###############################################################################

log "Starting full build..."

for name in "${!TARGETS[@]}"; do
  dir="${TARGETS[$name]}"
  [[ -d "$dir" ]] || die "Missing directory: $dir"
  compile_tex "$name" "$dir"
done

###############################################################################
# Generated README (Build-Aware)
###############################################################################

log "Generating build metadata README..."

cat > "$BUILD_DIR/README.generated.md" << 'EOF'
# Build Artifacts — Spherepop Manuscripts

This directory contains compiled PDFs and auxiliary scaffolding
produced by `tools/build_all.sh`.

## What Was Built

Each manuscript was compiled **independently**, with no implicit
cross-references. Shared material is included only when explicitly
declared in each `main.tex`.

This is intentional.

## Why the Extra Directories Exist

Folders such as:

- `use_byobu_terminal_multiplexer`
- `use_vim_or_neovim_for_structural_editing`
- `expect_semantic_density`

are **epistemic signals**, not instructions.

They encode assumptions about how this work is meant to be engaged:

- sustained attention
- replayable reasoning
- tolerance for density
- resistance to premature compression

## RSVP Reminder

RSVP (Relativistic Scalar–Vector–Plenum) is a **structural field framework**,
not a claim about fundamental physics.

- Scalars model accumulation
- Vectors model flow
- Entropy models irreversibility and loss

Lagrangian and Hamiltonian formalisms are used for clarity and constraint
accounting, not metaphysical commitment.

## Why This Build Avoids Certain Language

You will not find:
- quantum mysticism
- quaternion fetishism
- octonionic numerology

This is deliberate. Mathematical structures are used only when they
carry explanatory load.

## If Something Feels Dense

That is not accidental.

This workspace treats **semantic impedance** as a safety feature in
dual-use domains.

EOF

###############################################################################
# Summary
###############################################################################

log "Build complete."
log "Artifacts located in: $BUILD_DIR"
log "Logs located in: $LOG_DIR"

exit 0

