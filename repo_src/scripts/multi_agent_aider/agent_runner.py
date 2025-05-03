import os
import subprocess
import time
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from utils import logger, run_command, get_file_size_info

def generate_tmux_script(session_name: str, agent_tasks: List[Dict[str, Any]], 
                        repo_path_abs: str, log_dir_abs: str, config: Dict[str, Any]) -> Optional[str]:
    """Generates a bash script to set up tmux and run aider agents."""
    scripts_dir = Path("scripts")
    script_path = scripts_dir / f"run_{session_name}.sh"
    scripts_dir.mkdir(exist_ok=True)

    default_context_files = config['defaults'].get('default_context_files', [])
    aider_model = config['defaults'].get('aider_model', 'gpt-4o') # Get default aider model

    # Ensure paths are absolute and quoted for shell script
    repo_path_quoted = f'"{repo_path_abs}"'
    log_dir_quoted = f'"{log_dir_abs}"'

    script_content = f"""#!/usr/bin/env bash
# Auto-generated script to run {len(agent_tasks)} aider agents in tmux
set -euo pipefail

SESSION="{session_name}"
REPO_PATH={repo_path_quoted}
LOG_DIR={log_dir_quoted}
NUM_PANES={len(agent_tasks)}
AIDER_MODEL="{aider_model}" # Pass aider model from config

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
"""
    pane_index = 0
    for agent_task in agent_tasks:
        agent_id = agent_task['agent_id']
        task_desc = agent_task['task_description'].replace('"', '\\"') # Escape quotes for shell
        target_files = agent_task.get('target_files', [])

        # Combine target files and default context files
        all_files = target_files + default_context_files
        # Ensure uniqueness and quote properly for shell command
        file_args = " ".join(f'"{f}"' for f in sorted(list(set(all_files))))

        # Construct the aider command for this agent
        # Using --yes for non-interactive execution
        # Redirecting stdout and stderr to the agent-specific log file
        log_file = Path(log_dir_abs) / f"agent_{agent_id}.log"
        log_file_quoted = f'"{log_file}"'
        # Add --model flag to aider command
        aider_command = f'aider --yes --model "$AIDER_MODEL" --message "{task_desc}" {file_args} > {log_file_quoted} 2>&1'

        # Add command to script for the corresponding pane
        script_content += f"""
echo "Launching Agent {agent_id} in pane {pane_index}..."
tmux send-keys -t "$SESSION:{pane_index}" 'clear' C-m
# Add cd just in case, though pane should start there
tmux send-keys -t "$SESSION:{pane_index}" 'cd "$REPO_PATH"' C-m
tmux send-keys -t "$SESSION:{pane_index}" '{aider_command}' C-m
"""
        pane_index += 1

    # Add instructions to attach
    script_content += f"""
echo "All agents launched."
echo "Run 'tmux attach-session -t $SESSION' to view."
# Optional: Automatically attach if not run via specific automation
# tmux attach-session -t "$SESSION"
"""

    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755) # Make executable
        logger.info(f"Generated tmux script: {script_path}")
        return str(script_path)
    except IOError as e:
        logger.error(f"Error writing tmux script {script_path}: {e}")
        return None


def run_agents_in_tmux(agent_breakdown: Dict[str, Any], run_id: str, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Orchestrates running aider agents based on the breakdown using tmux."""
    if not agent_breakdown or not agent_breakdown.get('agents'):
        logger.warning("No valid agent breakdown provided. Cannot run agents.")
        return False, None # Indicate failure, no session name

    num_agents = len(agent_breakdown['agents'])
    logger.info(f"Preparing to run {num_agents} aider agents in parallel using tmux.")

    repo_path = Path(config['defaults']['repo_path']).resolve()
    log_dir = Path("logs") / f"run_{run_id}"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_dir_abs = log_dir.resolve()

    session_name = f"{config['defaults']['tmux_session_prefix']}{run_id}"

    # Generate the script
    script_path = generate_tmux_script(
        session_name,
        agent_breakdown['agents'],
        str(repo_path),
        str(log_dir_abs),
        config
    )

    if not script_path:
        return False, None # Script generation failed

    # Execute the script
    logger.info(f"Executing tmux script: {script_path}")
    use_iterm_integration = config.get('iterm2_integration', False) and platform.system() == "Darwin"

    try:
        if use_iterm_integration:
            logger.info("Using iTerm2 AppleScript integration for tmux.")
            # Command to tell iTerm to run the script in a new tab/window
            applescript_command = f"""
            tell application "iTerm2"
                tell current window
                    create tab with default profile
                    tell current session
                        write text "bash '{script_path}'"
                    end tell
                end tell
            end tell
            """
            run_command(['osascript', '-e', applescript_command], check=True)
            logger.info(f"iTerm2 tab should have been created for session '{session_name}'.")

        else:
            logger.info("Running tmux script directly.")
            # Run the script in the background
            result = run_command(['bash', script_path], capture_output=True, text=True)
            if result.returncode != 0:
                 logger.error(f"Tmux script execution failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
                 return False, session_name # Return session name even if script failed internally
            logger.info(f"Tmux script executed. Session '{session_name}' should be running.")
            logger.info(f"You can attach using: tmux attach-session -t {session_name}")

        return True, session_name # Indicate success, return session name
    except FileNotFoundError:
        logger.error("Error: 'osascript' (for iTerm) or 'bash' command not found.")
        return False, session_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing tmux script or iTerm command: {e}")
        return False, session_name
    except Exception as e:
         logger.error(f"An unexpected error occurred during agent execution: {e}")
         return False, session_name 