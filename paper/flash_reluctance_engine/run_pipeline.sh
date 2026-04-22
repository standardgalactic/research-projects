#!/usr/bin/env bash

set -euo pipefail

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "=== Flash-Reluctance Pipeline Test ==="

run_blender() {
local script="$1"
local log="$LOG_DIR/$(basename "$script").log"

echo ""
echo "Running $script ..."
if blender --background --python "$script" >"$log" 2>&1; then
    echo "SUCCESS: $script"
else
    echo "FAILURE: $script"
    echo "--- Last 20 lines ---"
    tail -n 20 "$log"
    exit 1
fi

}

run_python() {
local script="$1"
local log="$LOG_DIR/$(basename "$script").log"

echo ""
echo "Running $script ..."
if python "$script" >"$log" 2>&1; then
    echo "SUCCESS: $script"
else
    echo "FAILURE: $script"
    echo "--- Last 20 lines ---"
    tail -n 20 "$log"
    exit 1
fi

}

# Check Blender exists

if ! command -v blender >/dev/null 2>&1; then
echo "Blender not found in PATH"
exit 1
fi

run_blender fr_01_rotor_geometry.py
run_blender fr_02_thermal_system.py
run_blender fr_03_animation_v3.py

run_python fr_04_analysis_v3.py

echo ""
echo "=== Pipeline completed successfully ==="

