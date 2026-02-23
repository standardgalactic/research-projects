#!/usr/bin/env bash

# ======================================================
# PERFUNCTORY WORKER NODE — MULTI-MODE TERMINAL SIMULATOR
# Safe, Harmless, Lightweight
# ======================================================

VERSION="2.0"
HOST=$(hostname)
START_TIME=$(date)

clear

# ---- Colors ----
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

random_delay() {
  sleep $(awk -v min=0.2 -v max=1.0 'BEGIN{srand(); print min+rand()*(max-min)}')
}

spinner() {
  local s='-\|/'
  local i=0
  while [ $i -lt 15 ]; do
    printf "\r${CYAN}[%c] Processing...${RESET}" "${s:i++%${#s}:1}"
    sleep 0.05
  done
  printf "\r"
}

fake_progress() {
  for i in {1..30}; do
    printf "#"
    sleep 0.02
  done
  echo ""
}

banner() {
  echo -e "${GREEN}---------------------------------------------${RESET}"
  echo -e "${GREEN}$1${RESET}"
  echo -e "${GREEN}---------------------------------------------${RESET}"
}

# ======================================================
# MODE 1 — Hacker Movie Flash
# ======================================================
mode_hacker() {
  banner "MODE: HACKER INTERFACE"
  echo -e "${CYAN}Initializing secure shell matrix...${RESET}"
  spinner
  echo -e "${YELLOW}Decrypting node clusters...${RESET}"
  fake_progress
  echo -e "${GREEN}Access Layer Stabilized.${RESET}"
}

# ======================================================
# MODE 2 — Corporate Server Rack
# ======================================================
mode_corporate() {
  banner "MODE: ENTERPRISE NODE MONITOR"
  echo "[*] Checking service daemons..."
  random_delay
  echo "[OK] API Gateway: ACTIVE"
  echo "[OK] Load Balancer: STABLE"
  echo "[OK] Redundancy Channel: SYNCED"
  echo "[INFO] Uptime: $(date)"
}

# ======================================================
# MODE 3 — Cold War Defense System
# ======================================================
mode_coldwar() {
  banner "MODE: VECTOR DEFENSE GRID"
  echo -e "${YELLOW}Radar Sweep Initiated...${RESET}"
  spinner
  echo -e "${GREEN}Trajectory Bands Within Tolerance.${RESET}"
  echo -e "${CYAN}Missile Readiness: STANDBY${RESET}"
  echo -e "${GREEN}Launch Silos: SECURE${RESET}"
}

# ======================================================
# MODE 4 — AI Research Lab
# ======================================================
mode_ai() {
  banner "MODE: AI MODEL TRAINING"
  echo "[*] Gradient Descent Iteration..."
  fake_progress
  echo "[INFO] Loss: 0.$((RANDOM % 900 + 100))"
  echo "[INFO] Accuracy: $((RANDOM % 20 + 80)).$((RANDOM % 100))%"
  echo "[OK] Model Convergence Stable."
}

# ======================================================
# MODE 5 — RSVP Field Simulation
# ======================================================
mode_rsvp() {
  banner "MODE: RSVP FIELD ANALYSIS"
  echo "[*] Calculating scalar field coherence..."
  spinner
  echo "[OK] Φ Stability Index: 0.$((RANDOM % 900 + 100))"
  echo "[*] Vector Alignment Check..."
  spinner
  echo "[OK] ∇Φ - ∇S alignment nominal."
  echo "[INFO] Entropy Gradient Within Spinodal Band."
}

# ======================================================
# Startup Header
# ======================================================
echo -e "${GREEN}CINEMATIC WORKER NODE v${VERSION}${RESET}"
echo "Host: $HOST"
echo "Started: $START_TIME"
echo ""

# ======================================================
# Main Loop
# ======================================================

while true; do

  case $((RANDOM % 5)) in
    0) mode_hacker ;;
    1) mode_corporate ;;
    2) mode_coldwar ;;
    3) mode_ai ;;
    4) mode_rsvp ;;
  esac

  echo ""
  random_delay

done
