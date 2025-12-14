#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[install_utils] installing bash utilities..."
install -m 0755 "$ROOT/bash/rsvp-workspace" /usr/bin/rsvp-workspace
install -m 0755 "$ROOT/bash/rsvp-latex" /usr/bin/rsvp-latex
install -m 0755 "$ROOT/bash/spherepop-newpaper" /usr/bin/spherepop-newpaper

echo "[install_utils] building C utilities..."
cc -O2 "$ROOT/c/rsvp_pde_skeleton.c" -o /usr/bin/rsvp-pde-skeleton
cc -O2 "$ROOT/c/semantic_impedance.c" -o /usr/bin/semantic-impedance

echo "[install_utils] building Go utilities..."
go build -o /usr/bin/rsvp-validate "$ROOT/go/rsvp_validate.go"

echo "[install_utils] done."

