#!/usr/bin/env bash
# launch_aiders_fixed.sh - More robust tmux management for multiple aider agents
set -euo pipefail

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

# --- Check Dependencies ---
for cmd in tmux jq "$AIDER_CMD"; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: '$cmd' command not found. Please install it first."
    exit 1
  fi
done

echo "--- Launching Aider Agents in Tmux Session: ${TMUX_SESSION_NAME} ---"
echo "Config File: ${CONFIG_JSON_PATH}"
echo "Using aider command: ${AIDER_CMD}"

# --- Clean any existing session ---
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
  echo "Warning: Session $TMUX_SESSION_NAME already exists. Killing existing session..."
  tmux kill-session -t "$TMUX_SESSION_NAME"
fi

# --- Get agents from config ---
num_agents=$(jq '.num_agents' "$CONFIG_JSON_PATH")
if [[ "$num_agents" -lt 1 ]]; then
    echo "Error: 'num_agents' is less than 1 in config file. Exiting."
    exit 1
fi

echo "Found $num_agents agent(s) in config file."

# --- Create session without attaching ---
tmux new-session -d -s "$TMUX_SESSION_NAME" -n "Initial" "echo 'Initializing session...'; sleep 5"
echo "Created new tmux session: $TMUX_SESSION_NAME"
sleep 2 # Give tmux time to fully create the session

# --- Process each agent ---
agent_index=0
jq -c '.agents[]' "$CONFIG_JSON_PATH" | while IFS= read -r agent_config; do
    # Extract agent info
    agent_id=$(echo "$agent_config" | jq -r '.agent_id')
    agent_desc=$(echo "$agent_config" | jq -r '.description')
    agent_prompt=$(echo "$agent_config" | jq -r '.prompt')
    files_context=$(echo "$agent_config" | jq -r '.files_context | join(" ")')
    
    window_name="Agent-${agent_id}"
    echo "Creating window for Agent ${agent_id}: ${agent_desc}"
    
    # Create a new window
    if [[ "$agent_index" -eq 0 ]]; then
        # Rename first window instead of creating a new one
        tmux rename-window -t "${TMUX_SESSION_NAME}:0" "$window_name"
    else
        # Create new windows for additional agents
        tmux new-window -t "$TMUX_SESSION_NAME" -n "$window_name"
    fi
    
    # Construct aider command
    aider_cmd="${AIDER_CMD} ${files_context} --message \"${agent_prompt}\""
    
    # Debug output
    echo "Window: $window_name, Command: $aider_cmd"
    
    # Send the command
    window_target="${TMUX_SESSION_NAME}:${agent_index}"
    echo "Sending command to window: $window_target"
    
    tmux send-keys -t "$window_target" "clear" C-m
    sleep 1
    tmux send-keys -t "$window_target" "$aider_cmd" C-m
    
    ((agent_index++))
    # Add some delay between creating windows
    sleep 2
done

# Select first window
tmux select-window -t "${TMUX_SESSION_NAME}:0"
sleep 1

echo "Setup complete. Attaching to tmux session: $TMUX_SESSION_NAME"
echo "Use 'Ctrl+b d' to detach from the session."
echo "Use 'Ctrl+b n' to switch to the next window, 'Ctrl+b p' for the previous window."

# Attach to the session
tmux attach-session -t "$TMUX_SESSION_NAME" 