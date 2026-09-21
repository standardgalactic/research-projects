#!/usr/bin/env bash

OWNER="standardgalactic"

printf "%-45s %s\n" "FOLDER" "GITHUB REPO"
printf "%-45s %s\n" "------" "-----------"

for dir in */; do
    name="${dir%/}"

    # Skip hidden/special directories if any appear.
    [[ "$name" == ".git" ]] && continue

    if gh repo view "$OWNER/$name" >/dev/null 2>&1; then
        printf "%-45s EXISTS\n" "$name"
    else
        printf "%-45s FREE\n" "$name"
    fi
done

