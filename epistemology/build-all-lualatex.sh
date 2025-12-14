#!/usr/bin/env bash
set -u

PRE_RUNS=1
POST_RUNS=2

FAILED=()

run_lualatex () {
    lualatex \
        -interaction=nonstopmode \
        -halt-on-error \
        -output-directory="$1" \
        "$2" > /dev/null
}

find . -type f -name "*.tex" | while read -r texfile; do
    dir="$(dirname "$texfile")"
    base="$(basename "$texfile" .tex)"
    pdf="$dir/$base.pdf"
    aux="$dir/$base.aux"
    bcf="$dir/$base.bcf"

    echo "▶ Building: $texfile"

    if [[ -f "$pdf" ]]; then
        ts=$(date +"%Y%m%d-%H%M%S")
        mv "$pdf" "$dir/$base.backup-$ts.pdf"
    fi

    # Initial LaTeX
    ok=true
    for i in $(seq 1 $PRE_RUNS); do
        if ! run_lualatex "$dir" "$texfile"; then
            ok=false
            break
        fi
    done

    if [[ "$ok" = false ]]; then
        echo "  ✗ LaTeX failed (pre-bib)"
        FAILED+=("$texfile")
        continue
    fi

    # Bibliography
    if [[ -f "$bcf" ]]; then
        echo "  ↳ biber"
        (cd "$dir" && biber "$base" > /dev/null) || {
            echo "  ✗ biber failed"
            FAILED+=("$texfile")
            continue
        }
    elif [[ -f "$aux" ]] && grep -qi '\\bibdata' "$aux"; then
        echo "  ↳ bibtex"
        (cd "$dir" && bibtex "$base" > /dev/null) || {
            echo "  ✗ bibtex failed"
            FAILED+=("$texfile")
            continue
        }
    fi

    # Final LaTeX
    for i in $(seq 1 $POST_RUNS); do
        if ! run_lualatex "$dir" "$texfile"; then
            echo "  ✗ LaTeX failed (post-bib)"
            FAILED+=("$texfile")
            continue 2
        fi
    done

    echo "  ✓ Success"
done

echo
echo "======================"
echo " Build summary"
echo "======================"

if [[ ${#FAILED[@]} -eq 0 ]]; then
    echo "✓ All documents built successfully"
else
    echo "✗ Failed documents:"
    for f in "${FAILED[@]}"; do
        echo "  - $f"
    done
fi

