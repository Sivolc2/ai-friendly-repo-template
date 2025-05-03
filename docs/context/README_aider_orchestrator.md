# Aider Orchestrator

The Aider Orchestrator is a Python script that automates the process of orchestrating multiple Aider agents to implement changes in your codebase. It handles PRD generation, parallelization, and log summarization to help you manage complex coding tasks.

## Features

- **PRD Generation**: Automatically generates a PRD using Gemini AI based on your change description
- **Parallel Execution**: Runs multiple Aider agents in parallel to implement changes faster
- **Task Distribution**: Can divide files among agents for efficient workload distribution
- **Log Analysis**: Collects and summarizes logs from all agents for easy review
- **Configurable**: Adjust the number of agents, model selections, and other parameters

## Usage

```bash
python repo_src/scripts/aider_orchestrator.py \
    --change "Add user-password reset flow with email OTP" \
    --max-agents 4 \
    --model gpt-4o \
    --gemini-model gemini-1.5-pro
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--change` | Description of the change to implement (required) | - |
| `--max-agents` | Maximum number of agents to run in parallel | CPU count |
| `--files` | List of specific files to focus on | All files |
| `--model` | Model to use for Aider agents | gpt-4o |
| `--gemini-model` | Model to use for PRD generation | gemini-1.5-pro |
| `--api-key` | Google API key for Gemini (if not set in env) | From environment |
| `--max-iterations` | Maximum iterations per agent | 10 |

## Output Files

- **PRDs**: Stored in `docs/prd/` directory
- **Logs**: Individual agent logs stored in `.aider_logs/agent*_*.jsonl`
- **Summary**: JSON summary of all agents in `.aider_logs/summary_*.json`

## Design Differences

This implementation differs from traditional Aider usage in several key ways:

1. **Non-interactive Operation**: Agents run in non-interactive mode using the `--yes` flag
2. **Parallel Execution**: Multiple agents work simultaneously rather than sequentially
3. **Task Distribution**: Ability to distribute work among agents based on file groups
4. **PRD Integration**: Automatically generates and references a PRD for more guided implementation
5. **Summary Analytics**: Consolidates logs from all agents into a single summary report

## Requirements

- Python 3.8+
- Aider CLI tool
- Access to Gemini API
- Git repository

## Future Enhancements

Potential improvements include:

- Branch isolation for conflict-free merges
- Smarter task splitting based on PRD parsing
- Fail-fast health checks with automatic rollback
- Supervisor/reviewer agent to critique the work of implementation agents
- Dashboard integration for monitoring progress

## Implementation Notes

- The script uses Python's asyncio for concurrency to maximize throughput
- PRDs are generated with gemini_prd_generator.py and then moved to the docs/prd directory
- Log parsing counts "assistant_response" events as iterations to measure progress
- Agents are considered successful if they complete at least one iteration 