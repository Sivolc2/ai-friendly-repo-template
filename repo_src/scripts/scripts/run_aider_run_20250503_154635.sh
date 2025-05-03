#!/usr/bin/env bash
# Auto-generated script to run 1 aider agents in tmux
set -euo pipefail

SESSION="aider_run_20250503_154635"
REPO_PATH="/Users/clovisvinant/Central/Projects/templates/ai-friendly-repo-template/repo_src/scripts"
LOG_DIR="/Users/clovisvinant/Central/Projects/templates/ai-friendly-repo-template/repo_src/scripts/logs/run_20250503_154635"
NUM_PANES=1
AIDER_MODEL="gpt-4o" # Pass aider model from config

# Check if session exists
if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session $SESSION already exists. Attaching..."
  tmux attach-session -t "$SESSION"
  exit 0
fi

echo "Creating tmux session: $SESSION with $NUM_PANES panes..."
tmux new-session -d -s "$SESSION" -c "$REPO_PATH" # Start in repo path

# Create remaining panes if needed
for (( i=1; i<NUM_PANES; i++ )); do
  tmux split-window -t "$SESSION:" -c "$REPO_PATH" -d # Split current, stay focused, set dir
done

# Arrange panes
tmux select-layout -t "$SESSION:" tiled

# Delay slightly to ensure panes are ready
sleep 1

# Launch aider in each pane

echo "Launching Agent 0 in pane 0..."
tmux send-keys -t "$SESSION:0" 'clear' C-m
# Add cd just in case, though pane should start there
tmux send-keys -t "$SESSION:0" 'cd "$REPO_PATH"' C-m
tmux send-keys -t "$SESSION:0" 'aider --yes --model "$AIDER_MODEL" --message "Create a file named 'hello.txt' in the root directory of the repository and add the text 'Hello, World!' to it.  Commit the change with the message 'feat: Add hello.txt'." "./hello.txt" "README.md" > "/Users/clovisvinant/Central/Projects/templates/ai-friendly-repo-template/repo_src/scripts/logs/run_20250503_154635/agent_0.log" 2>&1' C-m

echo "All agents launched."
echo "Run 'tmux attach-session -t $SESSION' to view."
# Optional: Automatically attach if not run via specific automation
# tmux attach-session -t "$SESSION"
