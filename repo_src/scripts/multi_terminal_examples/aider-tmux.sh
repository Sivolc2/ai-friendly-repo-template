#!/bin/bash

# Aider Tmux Launcher
# This script creates tmux sessions with multiple Aider instances in different layouts

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it with 'brew install tmux'"
    exit 1
fi

# Function to display help
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Launch Aider instances in a tmux session with different layouts.

Options:
    -l, --layout LAYOUT    Specify layout: grid, horizontal, vertical (default: grid)
    -n, --number NUMBER    Number of panes to create (2-4, default: 4)
    -s, --session NAME     Tmux session name (default: aider_session)
    -c, --command CMD      Command to run in each pane (default: "aider --yes")
    -h, --help             Show this help message

Examples:
    $(basename "$0")                        # Launch 4 Aider instances in a grid layout
    $(basename "$0") -l horizontal -n 3     # Launch 3 Aider instances horizontally
    $(basename "$0") -l vertical -n 2       # Launch 2 Aider instances vertically
    $(basename "$0") -c "aider --model gpt-4-turbo"  # Use specific Aider command
EOF
}

# Default values
LAYOUT="grid"
NUMBER=4
SESSION="aider_session"
COMMAND="aider --yes"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--layout)
            LAYOUT="$2"
            shift 2
            ;;
        -n|--number)
            NUMBER="$2"
            shift 2
            ;;
        -s|--session)
            SESSION="$2"
            shift 2
            ;;
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate number of panes
if [[ $NUMBER -lt 2 || $NUMBER -gt 4 ]]; then
    echo "Error: Number of panes must be between 2 and 4"
    exit 1
fi

# Validate layout
if [[ "$LAYOUT" != "grid" && "$LAYOUT" != "horizontal" && "$LAYOUT" != "vertical" ]]; then
    echo "Error: Invalid layout. Choose from: grid, horizontal, vertical"
    exit 1
fi

# Check if aider is available
if ! command -v aider &> /dev/null; then
    echo "Warning: 'aider' command not found. Make sure it's installed or your virtual environment is activated."
    read -p "Continue anyway? (y/n): " confirm
    [[ $confirm != [yY] ]] && exit 1
fi

# Kill the session if it already exists
tmux kill-session -t "$SESSION" 2>/dev/null

# Create a new detached session
tmux new-session -d -s "$SESSION"

# Configure layout based on user choice
case $LAYOUT in
    grid)
        if [[ $NUMBER -ge 2 ]]; then
            # Split horizontally for first two panes
            tmux split-window -h -t "$SESSION"
        fi
        
        if [[ $NUMBER -ge 3 ]]; then
            # Split first pane vertically
            tmux select-pane -t "$SESSION:0.0"
            tmux split-window -v -t "$SESSION"
        fi
        
        if [[ $NUMBER -ge 4 ]]; then
            # Split second pane vertically
            tmux select-pane -t "$SESSION:0.1"
            tmux split-window -v -t "$SESSION"
        fi
        
        # Set tiled layout
        tmux select-layout -t "$SESSION" tiled
        ;;
        
    horizontal)
        # Create horizontal splits
        for ((i=1; i<NUMBER; i++)); do
            tmux split-window -h -t "$SESSION"
        done
        
        # Set even-horizontal layout
        tmux select-layout -t "$SESSION" even-horizontal
        ;;
        
    vertical)
        # Create vertical splits
        for ((i=1; i<NUMBER; i++)); do
            tmux split-window -v -t "$SESSION"
        done
        
        # Set even-vertical layout
        tmux select-layout -t "$SESSION" even-vertical
        ;;
esac

# Send the command to each pane
for ((i=0; i<NUMBER; i++)); do
    tmux send-keys -t "$SESSION:0.$i" "$COMMAND" C-m
done

# Enable mouse mode
tmux set -g mouse on

# Disable synchronize-panes by default
tmux set-window-option -t "$SESSION" synchronize-panes off

# Display helpful message
echo "Launching $NUMBER Aider instance(s) in $LAYOUT layout (tmux session: $SESSION)"
echo "Use 'Ctrl+a' as the tmux prefix key"
echo "Press 'Ctrl+a' then 'z' to zoom in/out of a pane"
echo "Press 'Ctrl+a' then ':' and type 'setw synchronize-panes on' to type in all panes at once"
echo "Press 'Ctrl+a' then 'd' to detach (session will keep running)"
echo "Run 'tmux attach-session -t $SESSION' to reconnect later"

# Attach to the tmux session
tmux attach-session -t "$SESSION" 