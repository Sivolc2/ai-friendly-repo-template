#!/usr/bin/env bash
#
# tmux_aider_grid.sh
# Launch N parallel Aider instances in a single tmux window
# Usage: ./tmux_aider_grid.sh [N]         (defaults to 4)

set -euo pipefail

NUM_PANES="${1:-4}"        # default to 4 if no arg supplied
SESSION="aider_grid"

# Re‑use the session if it already exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session $SESSION already running – attaching..."
  tmux attach-session -t "$SESSION"
  exit 0
fi

# Create the tmux session & first pane (without starting aider yet)
tmux new-session -d -s "$SESSION"

# Create the remaining panes
for (( i=1; i<NUM_PANES; i++ )); do
  # Split the *current* pane; -d keeps focus in original pane so the loop is simple
  tmux split-window -t "$SESSION" -d
done

# Fire up Aider in every pane
tmux list-panes -t "$SESSION" -F '#{pane_id}' | while read -r pane; do
  tmux send-keys -t "$pane" "clear; aider --yes" C-m
done

# Make it look nice
tmux select-layout -t "$SESSION" tiled

# Attach
tmux attach-session -t "$SESSION"
