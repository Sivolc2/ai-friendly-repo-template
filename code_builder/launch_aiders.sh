#!/usr/bin/env bash
# launch_aiders.sh - Robust tmux management for multiple aider agents
set -euo pipefail # Exit on error, unset variable, or pipe failure

# --- Configuration & Arguments ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_JSON_PATH="${1:-}"
RUN_ID="${2:-}"
# Use a fixed session name rather than a dynamic one
TMUX_SESSION_NAME="aider_session"
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

# Check if we are inside the project root (optional but good practice)
if [ ! -f "./code_builder/config.yaml" ]; then
    echo "Warning: Script doesn't seem to be running from the project root."
    # cd to project root if possible, or exit depending on requirements
fi

echo "--- Launching Aider Agents in Tmux Session: ${TMUX_SESSION_NAME} ---"
echo "Config File: ${CONFIG_JSON_PATH}"
echo "Using aider command: ${AIDER_CMD}"

# --- Clean any existing session ---
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
  echo "Warning: Session $TMUX_SESSION_NAME already exists. Killing existing session..."
  tmux kill-session -t "$TMUX_SESSION_NAME"
  sleep 2 # Give tmux time to fully kill the session
fi

# --- Get agents from config ---
num_agents=$(jq '.num_agents' "$CONFIG_JSON_PATH")
if [[ "$num_agents" -lt 1 ]]; then
    echo "Error: 'num_agents' is less than 1 in config file. Exiting."
    exit 1
fi

echo "Found $num_agents agent(s) in config file."

# --- Create session without attaching ---
echo "Creating new tmux session: $TMUX_SESSION_NAME"
if ! tmux new-session -d -s "$TMUX_SESSION_NAME"; then
    echo "Error: Failed to create tmux session."
    exit 1
fi

# Verify session exists
if ! tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
    echo "Error: Session doesn't exist after creation."
    exit 1
fi

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
    
    # Create a window for this agent
    if [[ "$agent_index" -eq 0 ]]; then
        # First window already exists, just rename it
        tmux rename-window -t "$TMUX_SESSION_NAME" "$window_name"
    else
        # Create new window
        tmux new-window -t "$TMUX_SESSION_NAME" -n "$window_name"
    fi
    
    # Verify window exists
    if ! tmux list-windows -t "$TMUX_SESSION_NAME" | grep -q "$window_name"; then
        echo "Warning: Window $window_name wasn't created properly."
    fi
    
    # Construct aider command
    env_file="code_builder/.env"
    if [[ -f "$env_file" ]]; then
        # Wrap the entire command in single quotes to prevent shell interpretation issues
        aider_cmd='export $(grep -v "^#" "'"${env_file}"'" | xargs) && '"${AIDER_CMD}"' '"${files_context}"' --message "'"${agent_prompt}"'"'
    else
        # Wrap the command in single quotes to preserve the message with spaces
        aider_cmd=''"${AIDER_CMD}"' '"${files_context}"' --message "'"${agent_prompt}"'"'
    fi
    
    # Send command to window
    echo "Sending command to window $window_name"
    
    # Debug: show exact command (one line)
    echo "Command: ${aider_cmd}"
    
    # Send the clear command first
    tmux send-keys -t "${TMUX_SESSION_NAME}:${window_name}" "clear" C-m
    sleep 1
    
    # Send the aider command - using printf to handle multi-line issues better
    if [[ "$aider_cmd" == *$'\n'* ]]; then
        echo "Warning: Command contains newlines; using printf to properly escape them"
        # Replace newlines with spaces in the command
        aider_cmd_sanitized=$(echo "$aider_cmd" | tr '\n' ' ')
        tmux send-keys -t "${TMUX_SESSION_NAME}:${window_name}" "$aider_cmd_sanitized" C-m
    else
    # Send the aider command
    tmux send-keys -t "${TMUX_SESSION_NAME}:${window_name}" "$aider_cmd" C-m
    
    ((agent_index++))
    sleep 2
done

# Select first window
first_window=$(tmux list-windows -t "$TMUX_SESSION_NAME" | head -n 1 | cut -d: -f1)
tmux select-window -t "${TMUX_SESSION_NAME}:${first_window}"

echo "Setup complete. Attaching to tmux session: $TMUX_SESSION_NAME"
echo "Use 'Ctrl+b d' to detach from the session."
echo "Use 'Ctrl+b n' to switch to the next window, 'Ctrl+b p' for the previous window."

# Attach to session
tmux attach-session -t "$TMUX_SESSION_NAME" 