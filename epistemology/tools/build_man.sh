#!/usr/bin/env bash
set -euo pipefail
mkdir -p build/man
for f in man/*.1; do
	base="$(basename "$f")"
	groff -Tutf8 -man "$f" > "build/man/${base%.1}.txt"
done
echo "Man pages built to build/man/*.txt"

