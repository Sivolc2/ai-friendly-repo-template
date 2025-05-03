# Aider Orchestrator

This script automates the process of orchestrating multiple Aider agents to implement changes in your codebase. It handles PRD generation, parallelization, and log summarization.

## Prerequisites

- Python 3.8+
- Aider CLI tool installed (`pip install aider-chat`)
- Google API key for Gemini (for PRD generation)
- Access to OpenAI or Anthropic API keys for Aider agents

## Installation

Make sure you have the required Python packages:

```bash
pip install asyncio requests
```

## Configuration

You can configure the orchestrator by creating a `.env` file in the scripts directory. A template `.env.example` file is provided:

```bash
# Copy the example file to create your own configuration
cp .env.example .env
# Edit the file with your settings
nano .env
```

The configuration file supports:
- API keys for different providers (Google, OpenAI, Anthropic)
- Default model selections
- Aider-specific configurations

## Usage

```bash
python aider_orchestrator.py --change "Add user-password reset flow with email OTP" --max-agents 4
```

with Claude model:

```bash
python aider_orchestrator.py --change "Add user-password reset flow with email OTP" --claude
```

or with more configuration:

```bash
python aider_orchestrator.py \
  --change "Add user-password reset flow with email OTP" \
  --max-agents 4 \
  --model gpt-4o \
  --gemini-model gemini-1.5-pro \
  --files path/to/file1.py path/to/file2.py \
  --max-iterations 15
```

### Arguments

- `--change`: Description of the change to implement (required)
- `--max-agents`: Maximum number of agents to run in parallel (default: CPU count)
- `--files`: List of files to focus on (optional, if not specified all files are considered)
- `--model`: Model to use for Aider agents (default: from env or gpt-4o)
- `--claude`: Use Claude model (shorthand for `--model claude-3-opus-20240229`)
- `--gemini-model`: Model to use for PRD generation (default: from env or gemini-1.5-pro)
- `--api-key`: Google API key for Gemini (optional if GOOGLE_API_KEY environment variable is set)
- `--max-iterations`: Maximum number of iterations for each agent (default: from env or 10)

## Supported Models

### OpenAI Models
- `gpt-3.5-turbo`
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o` (default)

### Anthropic Models
- `claude-3.7-sonnet-latest` (default Claude model)
- `claude-3-sonnet-20240229`
- `claude-3-haiku-20240307`
- `claude-3-5-sonnet-20240620`

## Workflow

1. The script loads environment variables from `.env` if present
2. It generates a PRD using the gemini_prd_generator.py script
3. It determines the optimal number of Aider agents based on input parameters
4. If specific files are provided, it distributes them among the agents
5. It launches Aider agents in parallel to implement the changes
6. Each agent operates in non-interactive mode with the `--yes` flag
7. After completion, it parses and summarizes the logs

## Output Files

- **PRD**: Generated in `docs/prd/` directory with a timestamp in the filename
- **Agent Logs**: Individual agent logs stored in `.aider_logs/agent<N>_<timestamp>.jsonl`
- **Summary**: JSON summary of all agents in `.aider_logs/summary_<timestamp>.json`

## Example Change Specification

Here's a template for effective change requests:

```
Implement a user authentication system with the following features:
1. Email and password sign-up/login
2. Password reset via email OTP
3. Account lockout after 5 failed attempts
4. JWT token-based authentication
5. Basic role-based authorization (user/admin)
```

## Implementation Details

- Uses asyncio for concurrent execution of multiple Aider agents
- Automatically determines API provider based on model selection
- Loads environment variables from `.env` file if present
- Parses JSONL logs to count "assistant_response" events as iterations
- Considers an agent successful if it completes at least one iteration
- Organizes the workspace by moving PRDs to the docs/prd directory 