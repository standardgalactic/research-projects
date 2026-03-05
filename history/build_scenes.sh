#!/usr/bin/env bash

set -e

BLENDER=${BLENDER:-blender}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/run_scene.py"

SCENES=(
    ising_descent
    history_lattice
    history_dag
    crdt_convergence
    entropy_collapse
)

if [ $# -eq 0 ]; then
    echo "No scene specified — rendering all scenes."
    for s in "${SCENES[@]}"; do
        echo "Rendering $s"
        $BLENDER -b -P "$SCRIPT" -- "$s"
    done
    exit 0
fi

SCENE="$1"

echo "Rendering $SCENE"
$BLENDER -b -P "$SCRIPT" -- "$SCENE"