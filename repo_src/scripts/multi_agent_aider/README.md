# Multi-Agent Aider Workflow

This system orchestrates multiple parallel aider agents to work on different parts of a coding task. It uses a Product Requirements Document (PRD) generator to analyze the task, break it down into smaller pieces, and coordinate aider agents to work on those pieces in parallel.

## Features

- Generates a PRD based on a natural language description of a change
- Breaks down the work into tasks for multiple aider agents 
- Launches agents in parallel using tmux
- Provides user approval of PRD with stats on agent count and file sizes
- Summarizes agent work using LLMs
- State management to track runs and progress
- Resume management for ongoing runs

## Requirements

- Python 3.8+
- tmux
- aider-chat (installed via pip)
- API keys for your LLMs (OpenAI, Anthropic, Gemini, etc.)

## Installation

1. Ensure you have Python 3.8+ installed
2. Install tmux if not already installed
   - macOS: `brew install tmux`
   - Ubuntu/Debian: `apt install tmux`
3. Set up the virtual environment and install dependencies:
   ```
   python -m venv ../.venv
   source ../.venv/bin/activate
   pip install -r ../requirements.txt
   ```
4. Create a `.env` file in the `scripts` directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   ```

## Configuration

The `config.yaml` file contains:
- LLM definitions (models, API keys, parameters)
- Workflow step configurations 
- Default settings
- iTerm2 integration for macOS

Adjust these settings according to your preferences and available models.

## Usage

Run the workflow with:

```
./run_multi_agent_aider.sh "Implement a feature to parse user CSV uploads and store results in the database"
```

Or directly:

```
source ../.venv/bin/activate
python -m multi_agent_aider.main_orchestrator "Your change description here"
```

### Options

- `-c, --config`: Path to the configuration file (default: config.yaml)
- `--repo-path`: Override repository path from config
- `--auto-accept`: Automatically accept the PRD without prompting

### Workflow

1. PRD Generation: The system analyzes your repository and generates a PRD with agent breakdown
2. User Approval: You'll be shown stats about the PRD and can approve/reject it
3. Agent Execution: Multiple aider agents are launched in tmux
4. Monitoring: Watch the agents work in their tmux panes
5. Summarization: After completion, summarize the work using the resume manager

### Management Commands

The resume manager provides commands for managing runs:

```
python -m multi_agent_aider.resume_manager list  # List all runs
python -m multi_agent_aider.resume_manager details <run_id>  # Show details for a run
python -m multi_agent_aider.resume_manager log <run_id> <agent_id>  # View agent log
python -m multi_agent_aider.resume_manager attach <run_id>  # Show tmux attach command
python -m multi_agent_aider.resume_manager summarize <run_id>  # Summarize agent logs
```

## Output Directory Structure

- `state/`: Run state files (JSON)
- `logs/run_<run_id>/`: Log files for each agent
- `scripts/`: Generated tmux scripts

## Limitations

- Dependency management is basic - agents may conflict if they modify the same files
- Automatic completion detection is not implemented - you need to manually monitor agent progress
- Error handling is basic and may require manual intervention for certain failures

## Contributing

Feel free to open issues or submit pull requests for improvements to the multi-agent workflow. 