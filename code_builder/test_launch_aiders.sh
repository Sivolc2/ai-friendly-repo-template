#!/usr/bin/env bash
# test_launch_aiders.sh - Debug script for tmux session creation
# Run with: bash code_builder/test_launch_aiders.sh

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_JSON_PATH="${SCRIPT_DIR}/sample_aider_config.json"
RUN_ID="test_$(date +%s)"
TMUX_SESSION_NAME="aider_test_${RUN_ID}"
AIDER_CMD="aider" # replace with actual path if needed

echo "=== TMUX DEBUGGING TEST ==="
echo "Script directory: ${SCRIPT_DIR}"
echo "Config file: ${CONFIG_JSON_PATH}"
echo "Session name: ${TMUX_SESSION_NAME}"
echo "Aider command: ${AIDER_CMD}"

# --- Check for dependencies ---
echo -n "Checking for tmux... "
if ! command -v tmux &> /dev/null; then
    echo "NOT FOUND - Please install tmux first."
    exit 1
else
    echo "FOUND ($(tmux -V))"
fi

echo -n "Checking for jq... "
if ! command -v jq &> /dev/null; then
    echo "NOT FOUND - Please install jq first."
    exit 1
else
    echo "FOUND ($(jq --version))"
fi

echo -n "Checking for aider... "
if ! command -v $AIDER_CMD &> /dev/null; then
    echo "NOT FOUND - Path to aider might be incorrect."
    exit 1
else
    echo "FOUND ($AIDER_CMD)"
fi

# --- Check config file ---
echo -n "Checking config file... "
if [ ! -f "$CONFIG_JSON_PATH" ]; then
    echo "NOT FOUND - The sample config file is missing."
    exit 1
else
    echo "FOUND"
    echo "Config contents:"
    cat "$CONFIG_JSON_PATH"
fi

# --- List existing tmux sessions ---
echo -n "Existing tmux sessions: "
if tmux list-sessions 2>/dev/null; then
    echo "Found existing sessions (above)."
else
    echo "No existing sessions."
fi

# --- Clean up any existing test session ---
echo -n "Cleaning up any existing test session... "
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
    tmux kill-session -t "$TMUX_SESSION_NAME"
    echo "Killed existing session."
else
    echo "No existing session to clean up."
fi

# --- Create TMux Session - STEP BY STEP ---
echo "=== STEP-BY-STEP TMUX SESSION CREATION ==="

# --- Step 1: Create new session detached with a window ---
echo "Step 1: Creating new detached session..."
NEW_WINDOW_NAME="Agent-1"
echo "Command: tmux new-session -d -s \"$TMUX_SESSION_NAME\" -n \"$NEW_WINDOW_NAME\""
if tmux new-session -d -s "$TMUX_SESSION_NAME" -n "$NEW_WINDOW_NAME"; then
    echo "  SUCCESS: New session created."
else
    echo "  FAILED: Could not create new session."
    exit 1
fi

# --- Step 2: Check if session exists ---
echo "Step 2: Checking if session was created..."
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
    echo "  SUCCESS: Session exists."
else
    echo "  FAILED: Session does not exist after creation."
    exit 1
fi

# --- Step 3: List windows in the session ---
echo "Step 3: Listing windows in the session..."
echo "Command: tmux list-windows -t \"$TMUX_SESSION_NAME\""
if ! tmux list-windows -t "$TMUX_SESSION_NAME"; then
    echo "  FAILED: Could not list windows."
    exit 1
fi

# --- Step 4: Try to target the window ---
echo "Step 4: Testing window targeting..."
for target_format in \
    "$TMUX_SESSION_NAME:0" \
    "$TMUX_SESSION_NAME:0.0" \
    "$TMUX_SESSION_NAME:$NEW_WINDOW_NAME" \
    "$TMUX_SESSION_NAME"
do
    echo "  Testing target: $target_format"
    if tmux select-window -t "$target_format" 2>/dev/null; then
        echo "    SUCCESS: Can target '$target_format'"
    else
        echo "    FAILED: Cannot target '$target_format'"
    fi
done

# --- Step 5: Try sending keys ---
echo "Step 5: Testing send-keys..."
for target_format in \
    "$TMUX_SESSION_NAME:0" \
    "$TMUX_SESSION_NAME:0.0" \
    "$TMUX_SESSION_NAME:$NEW_WINDOW_NAME" \
    "$TMUX_SESSION_NAME"
do
    echo "  Testing send-keys to: $target_format"
    if tmux send-keys -t "$target_format" "echo 'Hello from TMUX'" C-m 2>/dev/null; then
        echo "    SUCCESS: Sent keys to '$target_format'"
    else
        echo "    FAILED: Cannot send keys to '$target_format'"
    fi
done

# --- Step 6: Try actual aider commands ---
echo "Step 6: Testing actual aider command..."
TARGET_WINDOW="$TMUX_SESSION_NAME:0"
AIDER_TEST_CMD="$AIDER_CMD README.md --message \"This is a test\""

echo "  Command to send: $AIDER_TEST_CMD"
echo "  Target window: $TARGET_WINDOW"

echo "  Sleeping for 2 seconds before sending command..."
sleep 2

if tmux send-keys -t "$TARGET_WINDOW" "clear" C-m; then
    echo "    SUCCESS: Sent 'clear' command"
else
    echo "    FAILED: Could not send 'clear' command"
fi

sleep 1
echo "  Sending aider command..."
if tmux send-keys -t "$TARGET_WINDOW" "$AIDER_TEST_CMD" C-m; then
    echo "    SUCCESS: Sent aider command"
else
    echo "    FAILED: Could not send aider command"
fi

# --- Step 7: Attach to the session ---
echo ""
echo "=== TEST COMPLETED ==="
echo "Attaching to test session. Use Ctrl+b d to detach."
echo "You should see the aider command running."
echo ""
sleep 2
tmux attach-session -t "$TMUX_SESSION_NAME" 