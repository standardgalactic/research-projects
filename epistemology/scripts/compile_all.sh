#!/usr/bin/env bash
# scripts/compile_all.sh
set -euo pipefail

ESSAYS_DIR="${1:-essays}"
OUT_DIR="${2:-out}"

shopt -s nullglob
mkdir -p "$OUT_DIR"

for tex in "$ESSAYS_DIR"/*.tex; do
  base="$(basename "$tex" .tex)"
  echo "==> Building $base"
  latexmk -interaction=nonstopmode -halt-on-error -pdf -outdir="$OUT_DIR" "$tex"
done

