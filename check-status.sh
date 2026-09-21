#!/usr/bin/env bash

OWNER="standardgalactic"

printf "BYTES\tSIZE\tFILES\tSTATUS\tFOLDER\n"

for dir in */; do
    name="${dir%/}"
    bytes="$(du -sb -- "$dir" | cut -f1)"
    size="$(du -sh -- "$dir" | cut -f1)"
    files="$(find "$dir" -type f | wc -l)"

    if gh repo view "$OWNER/$name" >/dev/null 2>&1; then
        status="EXISTS"
    else
        status="FREE"
    fi

    printf "%s\t%s\t%s\t%s\t%s\n" \
        "$bytes" "$size" "$files" "$status" "$name"
done |
sort -nr |
cut -f2-
