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
# Kill existing session if it exists
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
  echo "Session $TMUX_SESSION_NAME already exists. Killing old session..."
  tmux kill-session -t "$TMUX_SESSION_NAME"
  sleep 1
fi

echo "Creating new tmux session: ${TMUX_SESSION_NAME}"

# --- Agent Launch ---
num_agents=$(jq '.num_agents' "$CONFIG_JSON_PATH")
echo "Number of agents to launch: $num_agents"

# Handle case of zero agents
if [[ "$num_agents" -lt 1 ]]; then
    echo "Error: 'num_agents' is less than 1 in config file. Exiting."
    exit 1
fi

# Create a new session in detached mode
tmux new-session -d -s "$TMUX_SESSION_NAME" -n "Agents"
sleep 1  # Give tmux a moment to initialize

# Use a much simpler approach - running separate commands directly
agent_count=1
jq -c '.agents[]' "$CONFIG_JSON_PATH" | while IFS= read -r agent_config; do
    agent_id=$(echo "$agent_config" | jq -r '.agent_id')
    agent_desc=$(echo "$agent_config" | jq -r '.description')
    agent_prompt=$(echo "$agent_config" | jq -r '.prompt')
    # Join files with spaces for the aider command line
    files_context=$(echo "$agent_config" | jq -r '.files_context | join(" ")')

    echo "Preparing Agent ${agent_id}: ${agent_desc}"

    # Construct the aider command
    aider_cmd="${AIDER_CMD} ${files_context} --message \"${agent_prompt}\""

    # Create a new window for each agent
    if [[ "$agent_count" -eq 1 ]]; then
        # Rename the initial window
        tmux rename-window -t "${TMUX_SESSION_NAME}:0" "Agent-${agent_id}"
    else
        tmux new-window -t "${TMUX_SESSION_NAME}" -n "Agent-${agent_id}"
    fi
    
    # Send the command to the newly created window
    sleep 0.5
    tmux send-keys -t "${TMUX_SESSION_NAME}:$(($agent_count-1))" "clear" C-m
    sleep 0.5
    tmux send-keys -t "${TMUX_SESSION_NAME}:$(($agent_count-1))" "$aider_cmd" C-m
    
    ((agent_count++))
done

# Select the first window before attaching
sleep 1
tmux select-window -t "${TMUX_SESSION_NAME}:0"

# Attach to the session
echo "Attaching to tmux session ${TMUX_SESSION_NAME}..."
echo "Use 'Ctrl+b d' to detach from the session."
echo "Use 'Ctrl+b n' to switch to next window, 'Ctrl+b p' for previous window."
tmux attach-session -t "$TMUX_SESSION_NAME" 