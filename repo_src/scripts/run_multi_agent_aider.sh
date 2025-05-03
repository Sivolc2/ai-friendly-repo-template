#!/usr/bin/env bash
# Script to run the multi-agent aider workflow in a virtual environment

set -e  # Exit on any error

# Ensure we're in the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create and activate virtual environment if it doesn't exist
VENV_DIR="./.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install/upgrade dependencies
echo "Installing required packages..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run the multi-agent aider workflow
echo "Starting multi-agent aider workflow..."
CONFIG_PATH="$SCRIPT_DIR/multi_agent_aider/config.yaml"
python -m multi_agent_aider.main_orchestrator --config "$CONFIG_PATH" "$@"

# Capture the run ID from the output for opening logs
RUN_ID=$(ls -t "$SCRIPT_DIR/state" | grep -m 1 "run_" | sed 's/run_\(.*\)\.json/\1/')

if [ -n "$RUN_ID" ]; then
    # Give some time for logs to be created
    sleep 2

    # Get the log directory for this run
    LOG_DIR="$SCRIPT_DIR/logs/run_$RUN_ID"
    
    # Check if logs exist
    if [ -d "$LOG_DIR" ]; then
        echo "Opening iTerm2 window to monitor agent logs..."
        
        # Create AppleScript to open a new iTerm window with tabs for each log file
        APPLESCRIPT=$(cat <<EOF
        tell application "iTerm"
            create window with default profile
            tell current window
                tell current session
                    write text "echo 'Monitoring logs for run $RUN_ID'; echo 'Press Ctrl+C to exit'"
                    write text "cd '$LOG_DIR'"
                    write text "ls -l"
EOF
        )
        
        # Add commands to tail each log file in its own tab
        for LOGFILE in "$LOG_DIR"/agent_*.log; do
            if [ -f "$LOGFILE" ]; then
                BASENAME=$(basename "$LOGFILE")
                APPLESCRIPT+=$(cat <<EOF
                    
                end tell
                create tab with default profile
                tell current session
                    write text "echo 'Monitoring $BASENAME'"
                    write text "cd '$LOG_DIR'"
                    write text "tail -f '$BASENAME'"
EOF
                )
            fi
        done
        
        # Close the AppleScript
        APPLESCRIPT+=$(cat <<EOF
                end tell
            end tell
        end tell
EOF
        )
        
        # Execute the AppleScript
        osascript -e "$APPLESCRIPT"
        
        echo "Log monitoring windows opened. Check the iTerm2 window."
    else
        echo "Log directory not found: $LOG_DIR"
    fi
else
    echo "Could not determine the latest run ID"
fi

# Deactivate virtual environment
deactivate 