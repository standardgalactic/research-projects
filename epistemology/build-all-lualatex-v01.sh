#!/usr/bin/env bash
set -euo pipefail

# Number of lualatex runs *before* bibliography
PRE_RUNS=1

# Number of lualatex runs *after* bibliography
POST_RUNS=2

find . -type f -name "*.tex" | while read -r texfile; do
    dir="$(dirname "$texfile")"
    base="$(basename "$texfile" .tex)"
    pdf="$dir/$base.pdf"
    aux="$dir/$base.aux"
    bcf="$dir/$base.bcf"
    bbl="$dir/$base.bbl"

    echo "▶ Building: $texfile"

    # Backup existing PDF
    if [[ -f "$pdf" ]]; then
        timestamp=$(date +"%Y%m%d-%H%M%S")
        backup="$dir/$base.backup-$timestamp.pdf"
        echo "  ↳ Backing up existing PDF → $backup"
        mv "$pdf" "$backup"
    fi

    # Initial lualatex pass(es)
    for i in $(seq 1 $PRE_RUNS); do
        echo "  ↳ lualatex (pre-bib) pass $i"
        lualatex \
            -interaction=nonstopmode \
            -halt-on-error \
            -output-directory="$dir" \
            "$texfile"
    done

    # Decide bibliography engine
    if [[ -f "$bcf" ]]; then
        echo "  ↳ Detected biber (.bcf)"
        (cd "$dir" && biber "$base")
    elif [[ -f "$aux" ]] && grep -qi '\\bibdata' "$aux"; then
        echo "  ↳ Detected bibtex (\\bibdata in .aux)"
        (cd "$dir" && bibtex "$base")
    else
        echo "  ↳ No bibliography detected"
    fi

    # Final lualatex pass(es)
    for i in $(seq 1 $POST_RUNS); do
        echo "  ↳ lualatex (post-bib) pass $i"
        lualatex \
            -interaction=nonstopmode \
            -halt-on-error \
            -output-directory="$dir" \
            "$texfile"
    done
done

echo "✓ All documents built."

