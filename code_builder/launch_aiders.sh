#!/usr/bin/env bash
set -euo pipefail # Exit on error, unset variable, or pipe failure

# --- Configuration & Arguments ---
CONFIG_JSON_PATH="${1:-}"
RUN_ID="${2:-}"
TMUX_SESSION_NAME="aider_run_${RUN_ID}"
# Use AIDER_CMD from environment or default to "aider"
AIDER_CMD="${AIDER_CMD:-aider}"

# --- Sanity Checks ---
if [[ -z "$CONFIG_JSON_PATH" || ! -f "$CONFIG_JSON_PATH" ]]; then
  echo "Error: Aider config JSON path is missing or file not found."
  echo "Usage: $0 <path/to/aider_config.json> <run_id>"
  exit 1
fi

if [[ -z "$RUN_ID" ]]; then
  echo "Error: Run ID is missing."
  echo "Usage: $0 <path/to/aider_config.json> <run_id>"
  exit 1
fi

# Check for required tools
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed. Please install tmux (e.g., 'brew install tmux' or 'sudo apt-get install tmux')."
    exit 1
fi
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install jq (e.g., 'brew install jq' or 'sudo apt-get install jq')."
    exit 1
fi

# Check if aider is available
if ! command -v "$AIDER_CMD" &> /dev/null; then
    echo "Warning: '$AIDER_CMD' command not found directly. Make sure aider-install ran correctly."
    echo "The AIDER_CMD variable is set to: $AIDER_CMD"
fi

# Check if we are inside the project root (optional but good practice)
if [ ! -f "./code_builder/config.yaml" ]; then
    echo "Warning: Script doesn't seem to be running from the project root."
    # cd to project root if possible, or exit depending on requirements
fi

echo "--- Launching Aider Agents in Tmux Session: ${TMUX_SESSION_NAME} ---"
echo "Config File: ${CONFIG_JSON_PATH}"
echo "Using aider command: ${AIDER_CMD}"

# --- Tmux Setup ---
# Kill existing session if it exists (optional, uncomment if desired)
# tmux kill-session -t "$TMUX_SESSION_NAME" 2>/dev/null || true

# Check if session exists, attach if so, otherwise create
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
  echo "Session $TMUX_SESSION_NAME already exists. Attaching..."
  tmux attach-session -t "$TMUX_SESSION_NAME"
  exit 0
fi

# --- Agent Launch ---
num_agents=$(jq '.num_agents' "$CONFIG_JSON_PATH")
echo "Number of agents to launch: $num_agents"

# Handle case of zero agents
if [[ "$num_agents" -lt 1 ]]; then
    echo "Error: 'num_agents' is less than 1 in config file. Exiting."
    exit 1
fi

# --- Create Windows and Send Commands ---
agent_index=0
first_window_created=false

jq -c '.agents[]' "$CONFIG_JSON_PATH" | while IFS= read -r agent_config; do
    agent_id=$(echo "$agent_config" | jq -r '.agent_id')
    agent_desc=$(echo "$agent_config" | jq -r '.description')
    agent_prompt=$(echo "$agent_config" | jq -r '.prompt')
    # Join files with spaces for the aider command line
    files_context=$(echo "$agent_config" | jq -r '.files_context | join(" ")')

    echo "Preparing Agent ${agent_id}: ${agent_desc}"

    # Construct the aider command
    # Ensure prompt quotes are handled if they exist within the JSON string
    aider_cmd="${AIDER_CMD} ${files_context} --message \"${agent_prompt}\""

    window_name="Agent-${agent_id}"
    target_window_index=$agent_index # Tmux window indices are 0-based

    if [[ "$first_window_created" == false ]]; then
        # Create the session with the first window (detached)
        echo "Creating session ${TMUX_SESSION_NAME} with first window ${window_name}"
        tmux new-session -d -s "$TMUX_SESSION_NAME" -n "$window_name"
        sleep 1.5 # Small delay after initial session creation
        first_window_created=true
        target_window_specifier="${TMUX_SESSION_NAME}:${target_window_index}"
    else
        # Create subsequent windows
        echo "Creating new window ${window_name} in session ${TMUX_SESSION_NAME}"
        # Create new window and get its index, though we can rely on agent_index here
        tmux new-window -t "${TMUX_SESSION_NAME}" -n "$window_name"
        sleep 1.5 # Small delay after creating window
        target_window_specifier="${TMUX_SESSION_NAME}:${target_window_index}"
    fi

    # Send the command to the target window
    echo "Sending command to ${target_window_specifier}"
    # Use C-m for Enter. Clear screen first for tidiness.
    tmux send-keys -t "$target_window_specifier" "clear" C-m
    sleep 0.2 # Tiny delay between commands
    # Send the aider command. Wrap in quotes just in case.
    tmux send-keys -t "$target_window_specifier" "${aider_cmd}" C-m

    ((agent_index++))
done

# --- Final Steps ---
# Select the first window (index 0) before attaching
sleep 1.5 # Wait a bit for commands to start
echo "Selecting first window..."
tmux select-window -t "${TMUX_SESSION_NAME}:0"

# Attach to the session
echo "Attaching to tmux session ${TMUX_SESSION_NAME}..."
echo "Use 'Ctrl+b d' to detach from the session."
echo "Use 'Ctrl+b n' to switch to the next window, 'Ctrl+b p' for the previous window."
tmux attach-session -t "$TMUX_SESSION_NAME" 