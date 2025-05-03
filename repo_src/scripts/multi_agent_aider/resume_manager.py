import argparse
import json
import sys
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Any

# Import locally
from utils import logger, load_state, run_command, load_config
from log_summarizer import summarize_run

def list_runs(state_dir="state"):
    """Lists available runs by finding state files."""
    state_path = Path(state_dir)
    if not state_path.exists():
        print("No state directory found.")
        return []

    runs = []
    for state_file in state_path.glob("run_*.json"):
        run_id = state_file.stem.replace("run_", "")
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
                proposed_change = data.get('proposed_change', 'N/A')
                status = data.get('status', 'Unknown')
                timestamp_str = run_id.replace("_", " ") # Basic timestamp from ID
                runs.append({
                    "id": run_id,
                    "change": proposed_change[:60] + "..." if len(proposed_change) > 60 else proposed_change,
                    "status": status,
                    "timestamp": timestamp_str
                })
        except (IOError, json.JSONDecodeError) as e:
            print(f"Warning: Could not read or parse state file {state_file}: {e}")

    # Sort by timestamp descending (latest first)
    runs.sort(key=lambda x: x['timestamp'], reverse=True)
    return runs

def display_run_details(run_id, state_data, log_dir="logs"):
    """Displays details about a specific run."""
    if not state_data:
        print(f"No state data found for run {run_id}")
        return

    print(f"\n--- Details for Run: {run_id} ---")
    print(f"Status: {state_data.get('status', 'Unknown')}")
    print(f"Proposed Change: {state_data.get('proposed_change', 'N/A')}")
    print(f"Config File: {state_data.get('config_file', 'N/A')}")
    print(f"Tmux Session: {state_data.get('tmux_session', 'N/A')}")

    agents = state_data.get('agents', [])
    print(f"\nAgents ({len(agents)}):")
    if not agents:
        print("  No agent breakdown available.")
    else:
        for agent in agents:
            agent_id = agent.get('agent_id', 'N/A')
            task = agent.get('task_description', 'N/A')
            files = agent.get('target_files', [])
            log_file = Path(log_dir) / f"run_{run_id}" / f"agent_{agent_id}.log"
            log_exists = log_file.exists()
            print(f"  - Agent ID: {agent_id}")
            print(f"    Task: {task[:80]}..." if len(task) > 80 else f"    Task: {task}")
            print(f"    Files: {files}")
            print(f"    Log File: {log_file} (Exists: {log_exists})")

    summaries = state_data.get('summaries')
    if summaries:
        print("\nSummaries:")
        for agent_id, summary in summaries.items():
            print(f"  --- Agent {agent_id} ---")
            print(summary)
            print("-" * 20)

def view_log(run_id, agent_id, log_dir="logs", pager="less"):
    """Views a specific agent's log file using a pager."""
    log_file = Path(log_dir) / f"run_{run_id}" / f"agent_{agent_id}.log"
    if not log_file.exists():
        print(f"Error: Log file not found: {log_file}")
        return

    try:
        print(f"Opening log {log_file} with {pager}...")
        subprocess.run([pager, str(log_file)])
    except FileNotFoundError:
        print(f"Error: Pager command '{pager}' not found. Trying 'cat'.")
        try:
             subprocess.run(['cat', str(log_file)])
        except FileNotFoundError:
             print("Error: 'cat' command not found. Cannot display log.")
        except Exception as e:
             print(f"Error displaying log with cat: {e}")
    except Exception as e:
        print(f"Error opening log with {pager}: {e}")


def attach_tmux(session_name):
    """Attaches to the specified tmux session."""
    if not session_name:
        print("Error: No tmux session name provided in state.")
        return

    print(f"Attempting to attach to tmux session: {session_name}")
    print(f"Run command: tmux attach-session -t {session_name}")
    try:
        # We can't directly attach from the script easily, just show the command.
        # For a more integrated feel, one could try running tmux attach in the current terminal
        # using os.system or subprocess.run without capturing, but it messes with script flow.
        pass # Just print the command
    except Exception as e:
        print(f"Error generating attach command: {e}")

# --- Main Resume Manager Logic ---
def resume_main():
    parser = argparse.ArgumentParser(description="Manage and resume multi-agent aider runs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List command
    parser_list = subparsers.add_parser("list", help="List recent runs.")
    parser_list.add_argument("--state-dir", default="state", help="Directory containing run state files.")

    # Details command
    parser_details = subparsers.add_parser("details", help="Show details for a specific run.")
    parser_details.add_argument("run_id", help="The ID of the run (e.g., 20231027_103000).")
    parser_details.add_argument("--state-dir", default="state", help="Directory containing run state files.")
    parser_details.add_argument("--log-dir", default="logs", help="Directory containing run logs.")

    # Log command
    parser_log = subparsers.add_parser("log", help="View the log for a specific agent in a run.")
    parser_log.add_argument("run_id", help="The ID of the run.")
    parser_log.add_argument("agent_id", type=int, help="The ID of the agent.")
    parser_log.add_argument("--log-dir", default="logs", help="Directory containing run logs.")
    parser_log.add_argument("--pager", default="less", help="Pager command to use (e.g., less, more, cat).")

    # Attach command
    parser_attach = subparsers.add_parser("attach", help="Show command to attach to the tmux session for a run.")
    parser_attach.add_argument("run_id", help="The ID of the run.")
    parser_attach.add_argument("--state-dir", default="state", help="Directory containing run state files.")

    # Summarize command
    parser_summarize = subparsers.add_parser("summarize", help="Generate summaries for agent logs of a completed run.")
    parser_summarize.add_argument("run_id", help="The ID of the run.")
    parser_summarize.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file.")
    parser_summarize.add_argument("--state-dir", default="state", help="Directory containing run state files.")

    args = parser.parse_args()

    if args.command == "list":
        runs = list_runs(args.state_dir)
        if not runs:
            print("No runs found.")
        else:
            print("Recent Runs:")
            # Simple table format
            print(f"{'ID':<20} {'Status':<20} {'Change Snippet':<65}")
            print("-" * 105)
            for run in runs:
                print(f"{run['id']:<20} {run['status']:<20} {run['change']:<65}")

    elif args.command == "details":
        state_data = load_state(args.run_id, args.state_dir)
        display_run_details(args.run_id, state_data, args.log_dir)

    elif args.command == "log":
        view_log(args.run_id, args.agent_id, args.log_dir, args.pager)

    elif args.command == "attach":
        state_data = load_state(args.run_id, args.state_dir)
        if state_data:
            attach_tmux(state_data.get('tmux_session'))
        else:
             print(f"Could not load state for run {args.run_id} to find tmux session.")

    elif args.command == "summarize":
        try:
            config = load_config(args.config)
            state_data = load_state(args.run_id, args.state_dir)
            if not state_data:
                print(f"Error: Cannot load state for run {args.run_id}")
                sys.exit(1)

            if state_data.get("status") == "summarized":
                print(f"Run {args.run_id} has already been summarized. Displaying stored summaries:")
                display_run_details(args.run_id, state_data) # Display details including summaries
            else:
                 print(f"Generating summaries for run {args.run_id}...")
                 summaries = summarize_run(args.run_id, state_data, config)
                 if summaries:
                      # Update state file with summaries
                      state_data["summaries"] = summaries
                      state_data["status"] = "summarized"
                      from utils import save_state # Import here if needed
                      save_state(args.run_id, state_data, args.state_dir)
                      print(f"Summaries generated and saved to state file for run {args.run_id}.")
                 else:
                      print("Log summarization failed or produced no results.")

        except FileNotFoundError:
             print(f"Error: Configuration file '{args.config}' not found.")
             sys.exit(1)
        except Exception as e:
             print(f"An error occurred during summarization: {e}")
             sys.exit(1)

if __name__ == "__main__":
    resume_main() 