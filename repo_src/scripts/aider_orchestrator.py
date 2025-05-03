#!/usr/bin/env python3
"""
Aider Orchestrator

This script:
1. Generates a PRD for a given change using gemini_prd_generator.py
2. Determines the optimal number of Aider agents to run in parallel
3. Launches Aider agents in parallel to implement the change
4. Parses and summarizes logs to verify success and failure

Usage:
    python aider_orchestrator.py --change "Add user-password reset flow with email OTP" --max-agents 4
"""

import os
import sys
import json
import time
import asyncio
import argparse
import datetime
import subprocess
from pathlib import Path
import shutil
import multiprocessing
from typing import List, Dict, Any, Optional, Tuple

# Determine project root directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Directory to store Aider logs
LOGS_DIR = PROJECT_ROOT / ".aider_logs"

# Default models
DEFAULT_MODELS = {
    "openai": os.environ.get("DEFAULT_AIDER_MODEL", "gpt-4o"),
    "anthropic": os.environ.get("DEFAULT_CLAUDE_MODEL", "claude-3-opus-20240229"),
    "gemini": os.environ.get("DEFAULT_GEMINI_MODEL", "gemini-1.5-pro")
}

# Model provider mapping
MODEL_PROVIDERS = {
    # OpenAI models
    "gpt-3.5-turbo": "openai",
    "gpt-4": "openai",
    "gpt-4-turbo": "openai",
    "gpt-4o": "openai",
    # Anthropic models
    "claude-3-opus-20240229": "anthropic",
    "claude-3-sonnet-20240229": "anthropic",
    "claude-3-haiku-20240307": "anthropic",
    "claude-3-5-sonnet-20240620": "anthropic",
    # Add more models as needed
}

async def run_command(cmd: List[str], env: Optional[Dict[str, str]] = None) -> Tuple[int, str, str]:
    """Run a command asynchronously and return exit code, stdout, and stderr"""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )
    stdout, stderr = await process.communicate()
    return process.returncode, stdout.decode(), stderr.decode()

def _split_seq(seq, num_chunks):
    """Split a sequence into approximately equal chunks"""
    avg = len(seq) / num_chunks
    result = []
    last = 0.0

    while last < len(seq):
        result.append(seq[int(last):int(last + avg)])
        last += avg

    return result

def _get_provider_from_model(model: str) -> str:
    """Determine the provider based on the model name"""
    return MODEL_PROVIDERS.get(model, "openai")  # Default to OpenAI if unknown

def _load_env_file():
    """Load environment variables from .env file in the scripts directory"""
    env_path = SCRIPT_DIR / ".env"
    
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
        with open(env_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    if key not in os.environ:  # Don't override existing env vars
                        os.environ[key] = value
        return True
    else:
        print(f"No .env file found at {env_path}")
        return False

async def _generate_prd(change: str, output_filename: str, gemini_model: str, api_key: Optional[str] = None) -> str:
    """Generate a PRD using the gemini_prd_generator.py script"""
    print(f"Generating PRD for change: {change}")
    
    # Build the command to run the gemini_prd_generator script
    cmd = [
        sys.executable,
        str(SCRIPT_DIR / "gemini_prd_generator.py"),
        "--prompt", change,
        "--filename", output_filename,
        "--model", gemini_model
    ]
    
    # Add API key if provided
    if api_key:
        cmd.extend(["--api-key", api_key])
    
    # Run the command
    returncode, stdout, stderr = await run_command(cmd)
    
    if returncode != 0:
        print(f"Error generating PRD: {stderr}")
        sys.exit(1)
    
    # Parse the output to get the path to the generated PRD
    prd_path = None
    for line in stdout.splitlines():
        if "Output file:" in line:
            prd_path = line.split("Output file:")[1].strip()
            break
    
    if not prd_path:
        print("Could not determine PRD output path from generator output.")
        sys.exit(1)
    
    # Ensure path is absolute
    if not os.path.isabs(prd_path):
        prd_path = os.path.abspath(os.path.join(os.getcwd(), prd_path))
    
    # Move the PRD to the docs/prd directory for better organization
    prd_dir = PROJECT_ROOT / "docs" / "prd"
    prd_dir.mkdir(parents=True, exist_ok=True)
    
    new_prd_path = prd_dir / Path(prd_path).name
    shutil.copy(prd_path, new_prd_path)
    
    print(f"PRD generated and copied to: {new_prd_path}")
    return str(new_prd_path)

async def _run_aider_agent(
    agent_id: int, 
    change: str, 
    prd_path: str, 
    files: List[str] = None,
    model: str = None, 
    max_iterations: int = 10
) -> str:
    """Run an Aider agent with the given parameters"""
    # Use default model if none specified
    if model is None:
        model = DEFAULT_MODELS["openai"]
    
    # Create a unique log file path for this agent
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / f"agent{agent_id}_{timestamp}.jsonl"
    
    # Build command to run Aider
    cmd = ["aider", "--yes"]  # Non-interactive mode
    
    # Add model selection
    cmd.extend(["--model", model])
    
    # Determine provider for API key selection in environment
    provider = _get_provider_from_model(model)
    
    # Add analytics logging
    cmd.extend(["--analytics-log", str(log_file)])
    
    # Add files if specified
    if files:
        cmd.extend(files)
    
    # Build the message that includes the change and reference to the PRD
    message = f"Implement the following change: {change}\n\nRefer to the PRD at {prd_path} for details."
    cmd.extend(["--message", message])
    
    # Set up environment variables
    env = os.environ.copy()
    env["AIDER_MAX_ITERATIONS"] = str(max_iterations)
    
    # Set provider-specific API key if needed
    if provider == "anthropic" and "ANTHROPIC_API_KEY" in env:
        env["AIDER_ANTHROPIC_API_KEY"] = env["ANTHROPIC_API_KEY"]
    elif provider == "openai" and "OPENAI_API_KEY" in env:
        env["AIDER_OPENAI_API_KEY"] = env["OPENAI_API_KEY"]
    
    print(f"Starting Aider agent {agent_id} with model {model} (provider: {provider}) and log file: {log_file}")
    
    # Run Aider
    returncode, stdout, stderr = await run_command(cmd, env)
    
    if returncode != 0:
        print(f"Agent {agent_id} failed with error: {stderr}")
    else:
        print(f"Agent {agent_id} completed successfully")
    
    return str(log_file)

def _summarize_logs(log_files: List[str]) -> Dict[str, Any]:
    """Parse and summarize the logs from multiple Aider agents"""
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agents": {},
        "total_iterations": 0,
        "successful_agents": 0,
        "failed_agents": 0
    }
    
    for i, log_file in enumerate(log_files):
        agent_id = f"agent{i}"
        agent_summary = {
            "log_file": log_file,
            "iterations": 0,
            "success": False
        }
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        if event.get("event") == "assistant_response":
                            agent_summary["iterations"] += 1
                    except json.JSONDecodeError:
                        continue
            
            # Consider an agent successful if it completed at least one iteration
            agent_summary["success"] = agent_summary["iterations"] > 0
            
            if agent_summary["success"]:
                summary["successful_agents"] += 1
            else:
                summary["failed_agents"] += 1
                
            summary["total_iterations"] += agent_summary["iterations"]
            summary["agents"][agent_id] = agent_summary
            
        except Exception as e:
            print(f"Error parsing log file {log_file}: {e}")
            summary["agents"][agent_id] = {
                "log_file": log_file,
                "error": str(e),
                "success": False
            }
            summary["failed_agents"] += 1
    
    return summary

async def orchestrate_agents(
    change: str, 
    max_agents: int,
    files: List[str] = None,
    model: str = None,
    gemini_model: str = None,
    api_key: Optional[str] = None,
    max_iterations: int = 10
) -> Dict[str, Any]:
    """
    Orchestrate multiple Aider agents to implement a change
    
    Args:
        change: Description of the change to implement
        max_agents: Maximum number of agents to run in parallel
        files: List of files to focus on (if None, all files are considered)
        model: Model to use for Aider agents
        gemini_model: Model to use for PRD generation
        api_key: Google API key for Gemini (if not set in environment)
        max_iterations: Maximum number of iterations for each agent
        
    Returns:
        Summary of the orchestration process
    """
    # Load environment variables from .env file
    _load_env_file()
    
    # Use default models if not specified
    if model is None:
        model = DEFAULT_MODELS["openai"]
    
    if gemini_model is None:
        gemini_model = DEFAULT_MODELS["gemini"]
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prd_filename = f"prd_{timestamp}.md"
    
    # Generate PRD
    prd_path = await _generate_prd(change, prd_filename, gemini_model, api_key)
    
    # Determine number of agents and file distribution
    num_agents = max_agents
    file_groups = []
    
    if files:
        # Split files among agents
        if len(files) < num_agents:
            num_agents = len(files)
        
        file_groups = _split_seq(files, num_agents)
    else:
        # If no files specified, all agents work on the entire repo
        file_groups = [None] * num_agents
    
    print(f"Launching {num_agents} Aider agents in parallel using model: {model}")
    
    # Launch agents in parallel
    tasks = []
    for i in range(num_agents):
        agent_files = file_groups[i] if file_groups else None
        task = _run_aider_agent(i, change, prd_path, agent_files, model, max_iterations)
        tasks.append(task)
    
    # Wait for all agents to complete
    log_files = await asyncio.gather(*tasks)
    
    # Summarize logs
    summary = _summarize_logs(log_files)
    summary["prd_path"] = prd_path
    summary["change"] = change
    summary["model_used"] = model
    summary["provider"] = _get_provider_from_model(model)
    
    # Save summary to a file
    summary_path = LOGS_DIR / f"summary_{timestamp}.json"
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Orchestration complete. Summary saved to: {summary_path}")
    return summary

async def main():
    parser = argparse.ArgumentParser(description="Orchestrate multiple Aider agents to implement a change")
    parser.add_argument("--change", required=True, help="Description of the change to implement")
    parser.add_argument("--max-agents", type=int, default=multiprocessing.cpu_count(), 
                      help=f"Maximum number of agents to run in parallel (default: {multiprocessing.cpu_count()})")
    parser.add_argument("--files", nargs="*", help="List of files to focus on (if not specified, all files are considered)")
    
    # Model group for mutually exclusive model selection
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument("--model", default=None, 
                           help="Model to use for Aider agents (default: from env or gpt-4o)")
    model_group.add_argument("--claude", action="store_const", const="claude-3-opus-20240229", dest="model",
                           help="Use Claude model (shorthand for --model claude-3-opus-20240229)")
    
    parser.add_argument("--gemini-model", default=None, 
                      help="Model to use for PRD generation (default: from env or gemini-1.5-pro)")
    parser.add_argument("--api-key", help="Google API key for Gemini (if not set in environment)")
    parser.add_argument("--max-iterations", type=int, default=None, 
                      help="Maximum number of iterations for each agent (default: from env or 10)")
    
    args = parser.parse_args()
    
    # Use env var for max iterations if not specified
    max_iterations = args.max_iterations
    if max_iterations is None:
        max_iterations = int(os.environ.get("AIDER_MAX_ITERATIONS", 10))
    
    await orchestrate_agents(
        change=args.change,
        max_agents=args.max_agents,
        files=args.files,
        model=args.model,
        gemini_model=args.gemini_model,
        api_key=args.api_key,
        max_iterations=max_iterations
    )

if __name__ == "__main__":
    asyncio.run(main()) 