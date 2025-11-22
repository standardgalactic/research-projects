#!/usr/bin/env bash
#
# Headless Blender batch runner
#
# Usage examples:
#   ./run_blender_batch.sh scripts/01_rsvp_scalar_field.py -- --steps 100
#   ./run_blender_batch.sh scripts/*.py -- --steps 50
#
# Everything after "--" is forwarded to the Python scripts.

set -e

BLENDER_BIN="${BLENDER_BIN:-blender}"
OUTBASE="blender_runs"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOGDIR="$OUTBASE/logs_$TIMESTAMP"

mkdir -p "$LOGDIR"

run_script() {
    local script="$1"; shift
    local args=("$@")

    local name
    name=$(basename "$script" .py)
    local outdir="$OUTBASE/${name}_${TIMESTAMP}"

    mkdir -p "$outdir"
    local logfile="$LOGDIR/${name}.log"

    echo "Running $script -> $outdir"
    "$BLENDER_BIN" --background \
        --python "$script" -- \
        --output "$outdir" \
        "${args[@]}" \
        > "$logfile" 2>&1

    echo "Finished $script (see $logfile)"
}

if [[ "$@" == *"--"* ]]; then
    SCRIPTS=("${@%%--*}")
    FORWARDING="${*@#*-- }"
    FORWARD_ARR=($FORWARDING)
else
    SCRIPTS=("$@")
    FORWARD_ARR=()
fi

if [[ ${#SCRIPTS[@]} -eq 0 ]]; then
    echo "Error: no Blender .py scripts provided."
    exit 1
fi

for script in "${SCRIPTS[@]}"; do
    run_script "$script" "${FORWARD_ARR[@]}"
done

echo "All Blender headless runs completed."
echo "Logs stored in: $LOGDIR"
