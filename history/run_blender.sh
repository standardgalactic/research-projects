#!/bin/bash
set -e

SCENE=$1
OUTDIR=${2:-figures}

mkdir -p "$OUTDIR"

BLEND="$OUTDIR/$SCENE.blend"
PNG="$OUTDIR/$SCENE.png"

blender -b -P figure_factory.py -- \
  --scene "$SCENE" \
  --blend "$BLEND" \
  --png "$PNG"

echo "Generated:"
echo "$BLEND"
echo "$PNG"
