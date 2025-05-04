# Code Builder - Aider Multi-Agent Workflow

This directory contains tools to help you use AI agents for code generation and implementation. The setup uses a hybrid approach with Python and Bash scripts to leverage OpenRouter for accessing LLM models, and Aider for code generation.

## Setup

1. **Prerequisites**:
   - Python 3.8-3.13 (any recent Python version works with aider-install)
   - `tmux` (Terminal multiplexer)
   - `jq` (JSON processor)
   - OpenRouter API Key (https://openrouter.ai/keys)

2. **Configuration**:
   - Copy the env.template file to create your .env file:
     ```bash
     cp code_builder/env.template code_builder/.env
     ```
   - Edit the .env file to add your OpenRouter API key
   - Optionally, copy `.aider.conf.yml.example` to `.aider.conf.yml` in the project root to configure Aider
   
   All API keys are stored in the .env file, not in config.yaml.

3. **Python Environment**:
   The scripts automatically set up a Python virtual environment at `.venv/` in the project root and use aider-install to install aider in its own separate environment.

## Usage

1. **Run the main script**:
   ```bash
   ./code_builder/main_orchestrator.sh "Implement a feature to do X"
   ```

2. **What happens**:
   - The script creates a Python virtual environment (if needed)
   - Calls an LLM to generate a PRD and configuration for Aider agents
   - Saves the PRD in `docs/prd/`
   - Starts Aider agents in tmux panes, each tasked with implementing a part of the PRD

3. **Interacting with Agents**:
   - Use `Ctrl+b` then arrow keys to navigate between tmux panes
   - Use `Ctrl+b d` to detach from the tmux session (agents keep running)
   - Use `tmux attach-session -t aider_run_YYYYMMDD_HHMMSS` to re-attach to a session

## Components

- `main_orchestrator.sh`: Main entry point script
- `generate_plan.py`: Python script to generate PRD and Aider configuration
- `launch_aiders.sh`: Script to launch Aider instances in tmux
- `config.yaml`: Configuration for models and API keys

## Design Differences

The implementation follows the original design with a few adjustments:

- Added an example Aider config file for easier setup
- Added improved error handling for API calls
- Ensured the scripts work with venv activation/deactivation logic
- Made path handling more robust across different operating systems

## Troubleshooting

- **Aider Command Not Found**: If aider isn't found in your PATH after installation, try running `python -m aider-install` manually. This should add aider to your PATH.
- **API Key Issues**: Make sure your OpenRouter API key is set correctly and has sufficient credits
- **Tmux Errors**: Ensure tmux is installed (`brew install tmux` on macOS, `apt install tmux` on Ubuntu)
- **Permission Denied**: Make scripts executable (`chmod +x code_builder/*.sh code_builder/*.py`)

## Notes

- The PRD generation model and Aider model can be configured in `code_builder/config.yaml`
- Each run creates a directory in `code_builder/runs/` with logs and configurations 