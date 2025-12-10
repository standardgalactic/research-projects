#!/bin/bash
set -euo pipefail

###############################################
# Dynamic Multi-Axis Drift Summarizer Experiment
###############################################

MODEL="${MODEL:-granite3.2:8b}"
CHUNK_LINES=256
SESSION="AXIS_SUMMARY"

SUMMARY_FILE="axis_summary.txt"
AXIS_LOG="axis_drift.csv"

mkdir -p tmp
> "$SUMMARY_FILE"
> "$AXIS_LOG"

echo "iteration,axis_clarity,axis_novelty,axis_depth" >> "$AXIS_LOG"

# initial axis weights (start uniform)
w_clarity=1.0
w_novelty=1.0
w_depth=1.0


###############################################
# Input → plain text
###############################################

INPUT="${1:-sample.txt}"
if [[ ! -f "$INPUT" ]]; then
  echo "Missing input"
  exit 1
fi

ext="${INPUT##*.}"
WORK="$INPUT"

if [[ "$ext" == "md" ]]; then
  WORK="${INPUT%.md}.txt"
  pandoc "$INPUT" -t plain -o "$WORK"
fi


###############################################
# Split into chunks
###############################################

rm -rf tmp/ch
mkdir -p tmp/ch
split -l "$CHUNK_LINES" "$WORK" tmp/ch/part_


iter=0

###############################################
# Main chunk loop
###############################################

for part in tmp/ch/part_*; do
  iter=$((iter+1))

  rm -f tmp/cand*.txt tmp/cand*.live

  byobu kill-session -t "$SESSION" >/dev/null 2>&1 || true


  #############################################
  # Create 3 candidate summaries
  #############################################

  byobu new-session -d -s "$SESSION" \
"(cat \"$part\" | ollama run $MODEL 'Summarize clearly'; echo DONE) \
 | tee tmp/cand1.txt; while :; do sleep 3600; done"

  byobu split-window -h -t "$SESSION" \
"(cat \"$part\" | ollama run $MODEL 'Summarize creatively'; echo DONE) \
 | tee tmp/cand2.txt; while :; do sleep 3600; done"

  byobu split-window -v -t "$SESSION" \
"(cat \"$part\" | ollama run $MODEL 'Summarize in depth'; echo DONE) \
 | tee tmp/cand3.txt; while :; do sleep 3600; done"

  byobu select-layout -t "$SESSION" tiled >/dev/null 2>&1 || true


  echo
  echo "### Observe summaries; detach to proceed ###"
  byobu attach-session -t "$SESSION"


  #############################################
  # Wait for DONE on all 3
  #############################################

  while true; do
    ok1=0; ok2=0; ok3=0
    [[ -f tmp/cand1.txt && "$(tail -n1 tmp/cand1.txt)" == "DONE" ]] && ok1=1
    [[ -f tmp/cand2.txt && "$(tail -n1 tmp/cand2.txt)" == "DONE" ]] && ok2=1
    [[ -f tmp/cand3.txt && "$(tail -n1 tmp/cand3.txt)" == "DONE" ]] && ok3=1
    (( ok1 && ok2 && ok3 )) && break
    sleep 2
  done

  sed -i '$ d' tmp/cand1.txt
  sed -i '$ d' tmp/cand2.txt
  sed -i '$ d' tmp/cand3.txt

  byobu kill-session -t "$SESSION" >/dev/null 2>&1 || true


  #############################################
  # Evaluate each candidate on 3 axes
  #############################################

  echo
  echo "Scoring axis values…"

  cat > tmp/axis_prompt.txt <<EOF
Rate each candidate 0–5 on three axes:
clarity, novelty, depth.
Return JSON ONLY:

{
 "cand1": {"clarity":0,"novelty":0,"depth":0},
 "cand2": {"clarity":0,"novelty":0,"depth":0},
 "cand3": {"clarity":0,"novelty":0,"depth":0}
}

CANDIDATE 1:
$(cat tmp/cand1.txt)

CANDIDATE 2:
$(cat tmp/cand2.txt)

CANDIDATE 3:
$(cat tmp/cand3.txt)
EOF

  ollama run "$MODEL" < tmp/axis_prompt.txt > tmp/axis_raw.json
  sed -n '/{/,/}/p' tmp/axis_raw.json > tmp/axis.json || true


  #############################################
  # Extract axis averages & dynamic weighting
  #############################################

  get() {
    jq -r ".$1" tmp/axis.json 2>/dev/null || echo "0"
  }

  c1c=$(get cand1.clarity)
  c1n=$(get cand1.novelty)
  c1d=$(get cand1.depth)

  c2c=$(get cand2.clarity)
  c2n=$(get cand2.novelty)
  c2d=$(get cand2.depth)

  c3c=$(get cand3.clarity)
  c3n=$(get cand3.novelty)
  c3d=$(get cand3.depth)


  #############################################
  # Weighted selection (teleology hidden)
  #############################################

  score1=$(echo "$w_clarity*$c1c + $w_novelty*$c1n + $w_depth*$c1d" | bc -l)
  score2=$(echo "$w_clarity*$c2c + $w_novelty*$c2n + $w_depth*$c2d" | bc -l)
  score3=$(echo "$w_clarity*$c3c + $w_novelty*$c3n + $w_depth*$c3d" | bc -l)

  best="tmp/cand1.txt"
  (( $(echo "$score2 > $score1" | bc -l) )) && best="tmp/cand2.txt"
  (( $(echo "$score3 > $score1" | bc -l) )) && best="tmp/cand3.txt"


  #############################################
  # Append best
  #############################################

  echo "### Iteration $iter: selected $(basename "$best")"
  echo >> "$SUMMARY_FILE"
  echo "### Iteration $iter ###" >> "$SUMMARY_FILE"
  cat "$best" >> "$SUMMARY_FILE"


  #############################################
  # Update axis weights (drift-reversal)
  #############################################

  # get current axis means
  mean_c=$(echo "($c1c+$c2c+$c3c)/3" | bc -l)
  mean_n=$(echo "($c1n+$c2n+$c3n)/3" | bc -l)
  mean_d=$(echo "($c1d+$c2d+$c3d)/3" | bc -l)

  # simple negative-slope reinforcement toward weak axes
  w_clarity=$(echo "$w_clarity * (1 + (1 - mean_c)/10)" | bc -l)
  w_novelty=$(echo "$w_novelty * (1 + (1 - mean_n)/10)" | bc -l)
  w_depth=$(echo "$w_depth * (1 + (1 - mean_d)/10)" | bc -l)

  echo "$iter,$w_clarity,$w_novelty,$w_depth" >> "$AXIS_LOG"

done

echo "Done."
