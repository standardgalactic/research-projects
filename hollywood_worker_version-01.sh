#!/usr/bin/env bash

# --------------------------------------------------
# BLASTOIDS SYSTEM WORKER — SIMULATION MODE
# Harmless terminal activity generator
# --------------------------------------------------

clear

VERSION="1.0"
HOST=$(hostname)
START_TIME=$(date)

echo "Initializing Worker Node..."
sleep 1
echo "Host: $HOST"
echo "Start Time: $START_TIME"
echo "Version: $VERSION"
echo "-------------------------------------------"
sleep 1

random_delay() {
  sleep $(awk -v min=0.2 -v max=1.2 'BEGIN{srand(); print min+rand()*(max-min)}')
}

fake_progress() {
  for i in {1..20}; do
    printf "#"
    sleep 0.03
  done
  echo ""
}

check_filesystem() {
  echo "[*] Checking filesystem integrity..."
  random_delay
  pwd >/dev/null
  echo "[OK] Working directory verified."
}

scan_environment() {
  echo "[*] Scanning environment variables..."
  random_delay
  env | head -n 3 >/dev/null
  echo "[OK] Environment baseline stable."
}

network_check() {
  echo "[*] Performing network simulation check..."
  random_delay
  date >/dev/null
  echo "[OK] Network clock sync nominal."
}

cpu_probe() {
  echo "[*] Probing CPU thermal envelope..."
  random_delay
  uname -a >/dev/null
  echo "[OK] CPU metrics within tolerance."
}

vector_analysis() {
  echo "[*] Running vector field stabilization routine..."
  fake_progress
  echo "[OK] Field coherence nominal."
}

entropy_balance() {
  echo "[*] Calculating entropy gradients..."
  fake_progress
  echo "[OK] Entropy within operational band."
}

idle_spin() {
  echo "[*] Entering low-power monitoring state..."
  random_delay
}

while true; do

  check_filesystem
  random_delay

  scan_environment
  random_delay

  network_check
  random_delay

  cpu_probe
  random_delay

  vector_analysis
  random_delay

  entropy_balance
  random_delay

  idle_spin
  echo "-------------------------------------------"

done
