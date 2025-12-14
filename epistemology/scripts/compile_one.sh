#!/usr/bin/env bash
# scripts/compile_one.sh
set -euo pipefail

TEX_FILE="${1:?need path to .tex}"
OUT_DIR="${2:-out}"

mkdir -p "$OUT_DIR"
latexmk -interaction=nonstopmode -halt-on-error -pdf -outdir="$OUT_DIR" "$TEX_FILE"

