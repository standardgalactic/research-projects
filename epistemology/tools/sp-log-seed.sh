#!/usr/bin/env bash
set -euo pipefail
LOGFILE="${1:-/tmp/spherepop.log}"
mkdir -p "$(dirname "$LOGFILE")" 2>/dev/null || true
touch "$LOGFILE"
printf "%s spherepop[%d]: seed: log initialized\n" "$(date '+%b %d %H:%M:%S')" "$$" >>"$LOGFILE"
echo "Seeded $LOGFILE"

