#!/bin/bash

# ML Workspace Launcher
# This script creates a tmux session with a layout optimized for machine learning workflows

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it with 'brew install tmux'"
    exit 1
fi

# Default session name
SESSION="ml_workspace"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--session)
            SESSION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $(basename "$0") [-s|--session SESSION_NAME]"
            echo "Creates a tmux session with a layout optimized for machine learning workflows"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $(basename "$0") [-s|--session SESSION_NAME]"
            exit 1
            ;;
    esac
done

# Kill the session if it already exists
tmux kill-session -t "$SESSION" 2>/dev/null

# Create a new detached session
tmux new-session -d -s "$SESSION"

# Set up the layout:
# - Left pane (40%): for code editing
# - Top right (30%): for running experiments
# - Bottom right (30%): for monitoring (htop, nvidia-smi, etc.)

# First, split the screen vertically (left 40%, right 60%)
tmux split-window -h -p 60 -t "$SESSION"

# Then split the right pane horizontally (top and bottom)
tmux split-window -v -p 50 -t "$SESSION:0.1"

# Name the windows for clarity
tmux rename-window -t "$SESSION:0" "ML Workspace"

# Set up each pane with initial commands
# Pane 0: Code editor (left)
tmux send-keys -t "$SESSION:0.0" "echo 'Code Editor Pane'; cd $(pwd)" C-m
tmux send-keys -t "$SESSION:0.0" "# Use your preferred editor here, e.g.:" C-m
tmux send-keys -t "$SESSION:0.0" "# vim" C-m

# Pane 1: Experiment runner (top right)
tmux send-keys -t "$SESSION:0.1" "echo 'Experiment Runner Pane'; cd $(pwd)" C-m
tmux send-keys -t "$SESSION:0.1" "# Start your training here, e.g.:" C-m
tmux send-keys -t "$SESSION:0.1" "# python train.py" C-m

# Pane 2: Monitoring (bottom right)
tmux send-keys -t "$SESSION:0.2" "echo 'Monitoring Pane'" C-m

# Check if we're running on a system with NVIDIA GPUs
if command -v nvidia-smi &> /dev/null; then
    # System has NVIDIA GPUs, set up a monitoring loop
    tmux send-keys -t "$SESSION:0.2" "while true; do clear; date; echo ''; nvidia-smi; sleep 2; done" C-m
else
    # No NVIDIA GPUs, use htop if available
    if command -v htop &> /dev/null; then
        tmux send-keys -t "$SESSION:0.2" "htop" C-m
    else
        tmux send-keys -t "$SESSION:0.2" "top" C-m
    fi
fi

# Set tiled layout
tmux select-layout -t "$SESSION" main-vertical

# Enable mouse mode
tmux set -g mouse on

# Select the code editor pane
tmux select-pane -t "$SESSION:0.0"

# Display helpful message
echo "Launching ML Workspace (tmux session: $SESSION)"
echo "The layout has three panes:"
echo "  - Left: Code editor"
echo "  - Top right: Experiment runner"
echo "  - Bottom right: System monitoring"
echo ""
echo "Use 'Ctrl+a' as the tmux prefix key"
echo "Press 'Ctrl+a' then 'z' to zoom in/out of a pane"
echo "Press 'Ctrl+a' then 'd' to detach (session will keep running)"
echo "Run 'tmux attach-session -t $SESSION' to reconnect later"

# Attach to the tmux session
tmux attach-session -t "$SESSION" 