#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import json

# Add the current directory to the module path
script_dir = Path(__file__).resolve().parent
sys.path.append(str(script_dir))

from utils import (
    logger, load_config, get_run_id, save_state, check_aider_version, 
    get_file_size_info, confirm_action
)
from prd_generator import generate_prd
from agent_runner import run_agents_in_tmux
from log_summarizer import summarize_run

def validate_environment():
    """Check if all required components are available."""
    # Check if aider is installed
    if not check_aider_version():
        sys.exit(1)  # Exit if aider is not found

    # Check for tmux
    try:
        import shutil
        if not shutil.which("tmux"):
            logger.error("Error: 'tmux' command not found. Please install tmux.")
            sys.exit(1)
        logger.info(f"Found tmux at: {shutil.which('tmux')}")
    except Exception as e:
        logger.warning(f"Could not reliably check for tmux: {e}. Assuming it exists.")

def print_prd_overview(prd_text: str, agent_breakdown: Dict[str, Any]):
    """Print a concise overview of the PRD and agent breakdown."""
    print("\n" + "=" * 80)
    print("PRD OVERVIEW".center(80))
    print("=" * 80)
    
    # Print first few lines of PRD (headers and objectives)
    lines = prd_text.split('\n')
    intro_lines = [line for line in lines[:30] if line.strip()]  # Get first 30 non-empty lines
    print('\n'.join(intro_lines[:10]))  # Print first 10 of those
    if len(intro_lines) > 10:
        print("...\n")
    
    # Print agent breakdown statistics
    num_agents = agent_breakdown.get("suggested_num_agents", 0)
    agents = agent_breakdown.get("agents", [])
    
    print("-" * 80)
    print(f"AGENT BREAKDOWN".center(80))
    print("-" * 80)
    print(f"Suggested number of agents: {num_agents}")
    print(f"Actual number of agents defined: {len(agents)}")
    
    # Get total file size for each agent
    for i, agent in enumerate(agents):
        agent_id = agent.get("agent_id", i)
        target_files = agent.get("target_files", [])
        # Calculate size statistics for the files
        size_info = get_file_size_info(target_files)
        
        print(f"\nAgent {agent_id}:")
        print(f"  - Task: {agent['task_description'][:100]}..." if len(agent['task_description']) > 100 else f"  - Task: {agent['task_description']}")
        print(f"  - Target files: {len(target_files)} files, {size_info['total']['size_str']} total")
        
    print("=" * 80)

def main():
    # --- Environment Validation ---
    validate_environment()

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Orchestrate multi-agent aider workflow.")
    parser.add_argument("proposed_change", help="The natural language description of the proposed change.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file.")
    parser.add_argument("--auto-accept", action="store_true", help="Automatically accept the PRD without prompting.")
    # Add option to override repo path
    parser.add_argument("--repo-path", help="Override repository path from config.")

    args = parser.parse_args()

    # --- Load Config ---
    try:
        config = load_config(args.config)
        if args.repo_path:
            config['defaults']['repo_path'] = args.repo_path
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # --- Workflow ---
    run_id = get_run_id()
    logger.info(f"Starting Workflow Run ID: {run_id}")

    # Initialize state
    current_state = {
        "run_id": run_id,
        "proposed_change": args.proposed_change,
        "config_file": args.config,
        "status": "started",
        "prd_text": None,
        "agent_breakdown": None,
        "tmux_session": None,
        "agents": [], # Will be populated from agent_breakdown
        "summaries": None,
        "raw_prd_response": None,
    }
    save_state(run_id, current_state, "state") # Initial save

    # 1. Generate PRD and Agent Breakdown
    logger.info("--- Step 1: Generating PRD ---")
    try:
        prd_text, agent_breakdown, raw_prd_response = generate_prd(args.proposed_change, config)
        if prd_text is None and agent_breakdown is None:
             raise RuntimeError("PRD generation failed completely.")

        current_state["prd_text"] = prd_text
        current_state["agent_breakdown"] = agent_breakdown
        current_state["raw_prd_response"] = raw_prd_response
        current_state["status"] = "prd_generated"
        if agent_breakdown and agent_breakdown.get("agents"):
             current_state["agents"] = agent_breakdown["agents"] # Store agent info
        save_state(run_id, current_state, "state")
        logger.info("PRD generated successfully.")
        
        # Print PRD overview with statistics
        if prd_text and agent_breakdown:
            print_prd_overview(prd_text, agent_breakdown)
            
            # User approval of PRD
            if not args.auto_accept:
                num_agents = len(agent_breakdown.get("agents", []))
                # Get total file size information
                all_files = []
                for agent in agent_breakdown.get("agents", []):
                    all_files.extend(agent.get("target_files", []))
                size_info = get_file_size_info(all_files)
                
                approval_message = f"Proceed with this PRD using {num_agents} agents? (Total files: {len(all_files)}, Size: {size_info['total']['size_str']})"
                if not confirm_action(approval_message):
                    print("PRD rejected by user. Exiting.")
                    current_state["status"] = "prd_rejected"
                    save_state(run_id, current_state, "state")
                    sys.exit(0)
                print("PRD accepted. Proceeding with agent execution.")
            else:
                print("Auto-accepting PRD and proceeding with agent execution.")
        else:
            print("\n--- PRD ---")
            print(prd_text if prd_text else "[No PRD text generated]")
            print("\n--- Agent Breakdown ---")
            print(json.dumps(agent_breakdown, indent=2) if agent_breakdown else "[No valid agent breakdown generated]")

        # Handle case where breakdown failed but PRD text exists
        if not agent_breakdown or not agent_breakdown.get("agents"):
             logger.warning("Agent breakdown generation failed or is empty. Cannot proceed with parallel agent execution.")
             logger.info("Workflow stopping after PRD generation.")
             # Optionally, could try running the original change with a single agent here
             sys.exit(0) # Exit gracefully

    except Exception as e:
        logger.error(f"Workflow failed during PRD generation: {e}")
        current_state["status"] = "failed_prd"
        save_state(run_id, current_state, "state")
        sys.exit(1)

    # 2. Kickoff Aider Agents in Tmux
    logger.info("\n--- Step 2: Launching Aider Agents ---")
    try:
        success, session_name = run_agents_in_tmux(agent_breakdown, run_id, config)
        current_state["tmux_session"] = session_name
        if success:
            logger.info(f"Agents launched successfully in tmux session: {session_name}")
            current_state["status"] = "agents_running" # Note: They are launched, not necessarily finished
        else:
            logger.error("Failed to launch agents in tmux.")
            current_state["status"] = "failed_agent_launch"
        save_state(run_id, current_state, "state")
        if not success:
             sys.exit(1) # Exit if launch failed

    except Exception as e:
        logger.error(f"Workflow failed during agent execution: {e}")
        current_state["status"] = "failed_agent_launch"
        save_state(run_id, current_state, "state")
        sys.exit(1)

    # --- Post-Execution Steps (Manual for now) ---
    logger.info("\n--- Workflow Paused ---")
    logger.info(f"Aider agents have been launched in tmux session: {session_name}")
    logger.info("Monitor the tmux session to see agent progress.")
    logger.info(f"Once agents appear complete (check logs in logs/run_{run_id}/), you can run:")
    logger.info(f"python resume_manager.py summarize {run_id} --config {args.config}")
    logger.info("Or use 'python resume_manager.py list' for more options.")

    logger.info(f"\nWorkflow orchestration initiated for Run ID: {run_id}")

if __name__ == "__main__":
    main() 