#!/usr/bin/env bash

# icepick.sh
# Compact repository snapshot for LLM analysis

set -euo pipefail

OUTPUT="${1:-icepick_snapshot.txt}"
ROOT="${2:-.}"

MAX_LINES=300
MAX_SIZE_KB=128

echo "Creating snapshot of: $ROOT"
echo "Output file: $OUTPUT"

should_include_full() {
    case "$1" in
        */README*|README*|*/LICENSE|LICENSE|*/Makefile|Makefile|*/Dockerfile|Dockerfile)
            return 0
            ;;
        *.md|*.toml|*.yaml|*.yml|*.json)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

{
    echo "===== ICEPICK SNAPSHOT ====="
    echo "Generated: $(date)"
    echo "Root: $(cd "$ROOT" && pwd)"
    echo

    echo "===== DIRECTORY TREE ====="

    tree -a \
        -I '.git|node_modules|target|dist|build|coverage|.next|.venv|venv|__pycache__|*.egg-info' \
        "$ROOT"

    echo
    echo "===== FILE CONTENTS ====="

    find "$ROOT" -type f \
        ! -path "*/.git/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/target/*" \
        ! -path "*/dist/*" \
        ! -path "*/build/*" \
        ! -path "*/coverage/*" \
        ! -path "*/.venv/*" \
        ! -path "*/venv/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.next/*" \
        ! -name "*.pdf" \
        ! -name "*.mp3" \
        ! -name "*.wav" \
        ! -name "*.ogg" \
        ! -name "*.flac" \
        ! -name "*.mp4" \
        ! -name "*.webm" \
        ! -name "*.mov" \
        ! -name "*.png" \
        ! -name "*.jpg" \
        ! -name "*.jpeg" \
        ! -name "*.gif" \
        ! -name "*.svg" \
        ! -name "*.ico" \
        ! -name "*.zip" \
        ! -name "*.tar" \
        ! -name "*.gz" \
        ! -name "*.7z" \
        ! -name "*.rar" \
        ! -name "*.aux" \
        ! -name "*.log" \
        ! -name "*.out" \
        ! -name "*.toc" \
        ! -name "*.synctex.gz" \
        ! -name "*.fdb_latexmk" \
        ! -name "*.fls" \
        ! -name "*.bbl" \
        ! -name "*.bcf" \
        ! -name "*.blg" \
        ! -name "*.srt" \
        ! -name "*.vtt" \
        ! -name "*.tsv" \
        ! -name "*.pyc" \
        | sort |
    while read -r file; do

        if ! file "$file" | grep -qi "text"; then
            continue
        fi

        echo
        echo "----- FILE: $file -----"

        size_kb=$(du -k "$file" | cut -f1)

        if should_include_full "$file"; then
            cat "$file"

        elif [ "$size_kb" -gt "$MAX_SIZE_KB" ]; then
            echo "[[ LARGE FILE: ${size_kb}KB ]]"
            echo "[[ SHOWING FIRST ${MAX_LINES} LINES ]]"
            head -n "$MAX_LINES" "$file"

        else
            lines=$(wc -l < "$file")

            if [ "$lines" -gt "$MAX_LINES" ]; then
                echo "[[ TRUNCATED: ${lines} lines ]]"
                head -n "$MAX_LINES" "$file"
            else
                cat "$file"
            fi
        fi

        echo
        echo "----- END FILE: $file -----"
        echo

    done

    echo "===== END SNAPSHOT ====="

} > "$OUTPUT"

echo "Snapshot complete."
echo "Size: $(du -h "$OUTPUT" | cut -f1)"