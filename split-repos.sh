#!/usr/bin/env bash
set -uo pipefail

OWNER="standardgalactic"

# Add/remove repositories here.
REPOS=(
    "admissibility-lab"
    "history"
    "textbook"
    "philosophy"
    "epistemology"
    "rhetoric"
    "compendium"
    "photonics"
    "rsvp-lab"
    "intelligence"
    "policy-selection"
    "interpretability"
)

# ------------------------------------------------------------
# Safety checks
# ------------------------------------------------------------

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "ERROR: Not inside a Git repository."
    exit 1
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
    echo "ERROR: GitHub CLI (gh) is not installed."
    exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
    echo "ERROR: GitHub CLI is not authenticated."
    exit 1
fi

echo
echo "Repository fission plan"
echo "======================="
echo

printf "%-32s %-10s %-10s\n" "FOLDER" "SIZE" "GITHUB"
printf "%-32s %-10s %-10s\n" "------" "----" "------"

problems=0

for name in "${REPOS[@]}"; do

    if [[ ! -d "$name" ]]; then
        printf "%-32s %-10s MISSING\n" "$name" "-"
        problems=1
        continue
    fi

    size="$(du -sh -- "$name" | cut -f1)"

    if gh repo view "$OWNER/$name" >/dev/null 2>&1; then
        status="EXISTS"
        problems=1
    else
        status="FREE"
    fi

    printf "%-32s %-10s %-10s\n" "$name" "$size" "$status"
done

echo

if (( problems )); then
    echo "ERROR: At least one requested migration is not safe."
    echo "Nothing has been created or pushed."
    exit 1
fi

echo "All requested repository names are free."
echo
read -r -p "Proceed with extraction and GitHub creation? [y/N] " answer

case "$answer" in
    y|Y|yes|YES)
        ;;
    *)
        echo "Cancelled."
        exit 0
        ;;
esac

echo

# ------------------------------------------------------------
# Migrate each subtree
# ------------------------------------------------------------

SUCCESS=()
FAILED=()

for name in "${REPOS[@]}"; do

    branch="extract/$name"
    remote="split-$name"

    echo
    echo "============================================================"
    echo "Migrating: $name"
    echo "============================================================"

    # Clean up temporary local refs from a previous interrupted run.
    git branch -D "$branch" >/dev/null 2>&1 || true
    git remote remove "$remote" >/dev/null 2>&1 || true

    echo "[1/5] Extracting history..."

    if ! git subtree split \
        --prefix="$name" \
        -b "$branch"
    then
        echo "FAILED: subtree extraction"
        FAILED+=("$name")
        continue
    fi

    echo "[2/5] Creating GitHub repository..."

    if ! gh repo create "$OWNER/$name" \
        --public
    then
        echo "FAILED: GitHub repository creation"
        FAILED+=("$name")
        git branch -D "$branch" >/dev/null 2>&1 || true
        continue
    fi

    echo "[3/5] Adding temporary remote..."

    git remote add \
        "$remote" \
        "git@github.com:$OWNER/$name.git"

    echo "[4/5] Pushing extracted history..."

    if ! git push \
        "$remote" \
        "$branch:main"
    then
        echo "FAILED: push"
        FAILED+=("$name")
        git remote remove "$remote" >/dev/null 2>&1 || true
        git branch -D "$branch" >/dev/null 2>&1 || true
        continue
    fi

    echo "[5/5] Verifying remote main branch..."

    if git ls-remote \
        --exit-code \
        "$remote" \
        refs/heads/main >/dev/null 2>&1
    then
        echo "VERIFIED: $OWNER/$name"
        SUCCESS+=("$name")
    else
        echo "FAILED: remote verification"
        FAILED+=("$name")
    fi

    # Remove temporary references.
    git remote remove "$remote" >/dev/null 2>&1 || true
    git branch -D "$branch" >/dev/null 2>&1 || true
done

# ------------------------------------------------------------
# Report
# ------------------------------------------------------------

echo
echo "============================================================"
echo "Migration report"
echo "============================================================"
echo

if ((${#SUCCESS[@]})); then
    echo "Successfully migrated and verified:"
    printf '  %s\n' "${SUCCESS[@]}"
fi

echo

if ((${#FAILED[@]})); then
    echo "FAILED or unverified:"
    printf '  %s\n' "${FAILED[@]}"
fi

echo
echo "IMPORTANT:"
echo "No source directories were removed from research-projects."
echo

if ((${#SUCCESS[@]})); then
    echo "After inspecting the new repositories, these verified"
    echo "directories are candidates for removal:"
    echo
    for name in "${SUCCESS[@]}"; do
        printf "git rm -r -- %q\n" "$name"
    done
fi
