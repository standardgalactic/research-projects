#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[install_spherepop_utils] installing bash utilities..."
install -m 0755 "$ROOT/bash/sp-init"      /usr/bin/sp-init
install -m 0755 "$ROOT/bash/sp-tree"      /usr/bin/sp-tree
install -m 0755 "$ROOT/bash/sp-lean"      /usr/bin/sp-lean
install -m 0755 "$ROOT/bash/sp-notebooks" /usr/bin/sp-notebooks
install -m 0755 "$ROOT/bash/sp-proto"     /usr/bin/sp-proto
install -m 0755 "$ROOT/bash/sp-manifest"  /usr/bin/sp-manifest

echo "[install_spherepop_utils] building C utilities..."
cc -O2 "$ROOT/c/sp_logfmt.c"   -o /usr/bin/sp-logfmt
cc -O2 "$ROOT/c/sp_eventlint.c" -o /usr/bin/sp-eventlint

echo "[install_spherepop_utils] building Go utilities..."
go build -o /usr/bin/sp-index "$ROOT/go/sp_index.go"
go build -o /usr/bin/sp-watch "$ROOT/go/sp_watch.go"

echo "[install_spherepop_utils] done."

