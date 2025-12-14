# tools/sp_common.sh
#!/usr/bin/env bash
set -euo pipefail

log()  { printf "[sp] %s\n" "$*"; }
warn() { printf "[sp][warn] %s\n" "$*" >&2; }
die()  { printf "[sp][error] %s\n" "$*" >&2; exit 1; }

require() {
  command -v "$1" >/dev/null || die "missing dependency: $1"
}

