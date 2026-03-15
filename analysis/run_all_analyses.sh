#!/usr/bin/env bash
set -euo pipefail

INPUT="following-activity.csv"
OUTDIR="analysis-results"

mkdir -p "$OUTDIR"

echo "Starting analysis run"
date

echo
echo "Running analyse_activity.py"
python3 analyse_activity.py < "$INPUT" \
    | tee "$OUTDIR/activity_analysis.txt"

echo
echo "Running analyse_languages.py"
python3 analyse_languages.py < "$INPUT" \
    | tee "$OUTDIR/language_counts.txt"

echo
echo "Running language_survival.py"
python3 language_survival.py < "$INPUT" \
    | tee "$OUTDIR/language_survival.txt"

echo
echo "Analysis complete"
date

echo
echo "Output files written to:"
echo "  $OUTDIR/activity_analysis.txt"
echo "  $OUTDIR/language_counts.txt"
echo "  $OUTDIR/language_survival.txt"
