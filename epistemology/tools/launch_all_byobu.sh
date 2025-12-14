#!/usr/bin/env bash
set -euo pipefail

SESSION="spherepop-redteam"

byobu new-session -d -s "$SESSION" -n alpine
byobu send-keys -t "$SESSION:0" "docker run -it spherepop:alpine" C-m

byobu new-window -t "$SESSION" -n arch
byobu send-keys -t "$SESSION:1" "docker run -it spherepop:arch" C-m

byobu new-window -t "$SESSION" -n fedora
byobu send-keys -t "$SESSION:2" "docker run -it spherepop:fedora" C-m

byobu new-window -t "$SESSION" -n nixos
byobu send-keys -t "$SESSION:3" "docker run -it spherepop:nixos" C-m

byobu attach -t "$SESSION"

