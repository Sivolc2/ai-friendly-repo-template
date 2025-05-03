#!/bin/bash

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it with 'brew install tmux'"
    exit 1
fi

# Get the full path to aider
AIDER_PATH=$(which aider)
if [ -z "$AIDER_PATH" ]; then
    echo "aider is not installed or not in your PATH. Please install it or activate your virtual environment."
    exit 1
fi

# Define session name
SESSION="aider_grid"

# Current working directory
CURRENT_DIR=$(pwd)

# Kill the session if it already exists
tmux kill-session -t $SESSION 2>/dev/null

# Create a new detached session
tmux new-session -d -s $SESSION

# Set the prefix key to Ctrl+a
tmux set-option -g prefix C-a
tmux unbind-key C-b
tmux bind-key C-a send-prefix

# Pane 0: Top-left
tmux send-keys -t $SESSION "cd $CURRENT_DIR && $AIDER_PATH --yes" C-m
sleep 1

# Split vertically to create Pane 1: Top-right
tmux split-window -h -t $SESSION
tmux send-keys -t $SESSION:0.1 "cd $CURRENT_DIR && $AIDER_PATH --yes" C-m
sleep 1

# Split Pane 0 horizontally to create Pane 2: Bottom-left
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION
tmux send-keys -t $SESSION:0.2 "cd $CURRENT_DIR && $AIDER_PATH --yes" C-m
sleep 1

# Split Pane 1 horizontally to create Pane 3: Bottom-right
tmux select-pane -t $SESSION:0.1
tmux split-window -v -t $SESSION
tmux send-keys -t $SESSION:0.3 "cd $CURRENT_DIR && $AIDER_PATH --yes" C-m
sleep 1

# Arrange panes in a tiled layout
tmux select-layout -t $SESSION tiled

# Enable synchronize-panes to type in all panes at once (disabled by default)
tmux set-window-option -t $SESSION synchronize-panes off

# Display helpful message
echo "Launching Aider grid in tmux session '$SESSION'..."
echo "Use 'Ctrl+a' as the tmux prefix key"
echo "Press 'Ctrl+a' then 'z' to zoom in/out of a pane"
echo "Press 'Ctrl+a' then ':' and type 'setw synchronize-panes on' to type in all panes at once"

# Attach to the tmux session
tmux attach-session -t $SESSION 