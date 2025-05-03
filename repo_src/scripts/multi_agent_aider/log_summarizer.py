import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from utils import logger, load_config, get_llm_client, call_llm

def generate_summary_prompt(agent_id: int, task_description: str, log_content: str) -> str:
    """Creates the prompt for the log summarizer LLM."""
    return f"""
You are an AI assistant reviewing the work of another AI coding agent (`aider`).
Analyze the following log file for Agent {agent_id}, who was tasked with:

**Task Description:**
{task_description}

**Agent {agent_id} Log:**
```log
{log_content[:30000]}
```
(Log may be truncated)

**Instructions:**

1.  **Summarize:** Briefly describe what the agent attempted to do and what the outcome was according to the log.
2.  **Completion Status:** Did the agent successfully complete the assigned task based *only* on the information in this log? (e.g., Does it show successful application of changes? Does it end without errors related to the core task?) State clearly: "Completed", "Partially Completed", "Failed", or "Unclear".
3.  **Key Events/Changes:** Highlight significant actions, errors encountered, files created/modified, or decisions made by the agent. Mention any specific problems or reasons for failure if applicable.
4.  **Assign Grade:** Give a letter grade (A, B, C, D, F) reflecting how well the agent appeared to perform its specific task according to this log.
    *   A: Task seemingly completed successfully with no major issues noted.
    *   B: Task mostly completed, minor issues or workarounds noted.
    *   C: Task partially completed, significant issues or errors occurred.
    *   D: Agent attempted task but failed due to errors or inability to apply changes.
    *   F: Agent did not make progress, got stuck in loops, or produced unusable results based on the log.

**Output Format:**

Provide the summary in a clear, structured format. Example:

**Agent {agent_id} Summary:**
**Task:** [Brief restatement of task]
**Status:** [Completed/Partially Completed/Failed/Unclear]
**Grade:** [A/B/C/D/F]
**Details:**
[Bulleted list or paragraph summarizing key events, changes, errors, and outcome based on the log.]
"""

def summarize_agent_log(agent_id: int, task_description: str, log_file_path: str, config: Dict[str, Any]) -> str:
    """Reads a log file and calls the LLM to summarize it."""
    logger.info(f"Summarizing log for Agent {agent_id} from: {log_file_path}")
    try:
        with open(log_file_path, 'r') as f:
            log_content = f.read()
    except FileNotFoundError:
        logger.error(f"Log file not found: {log_file_path}")
        return f"**Agent {agent_id} Summary:**\n**Status:** Error\n**Grade:** F\n**Details:** Log file not found at {log_file_path}."
    except IOError as e:
        logger.error(f"Error reading log file {log_file_path}: {e}")
        return f"**Agent {agent_id} Summary:**\n**Status:** Error\n**Grade:** F\n**Details:** Failed to read log file: {e}"

    if not log_content.strip():
         logger.warning(f"Log file is empty: {log_file_path}")
         return f"**Agent {agent_id} Summary:**\n**Task:** {task_description}\n**Status:** Unclear\n**Grade:** F\n**Details:** Log file is empty. Agent likely did not run or produced no output."

    summarizer_llm_name = config['workflow_llms']['log_summarizer']
    prompt = generate_summary_prompt(agent_id, task_description, log_content)

    try:
        llm_client = get_llm_client(summarizer_llm_name, config)
        summary = call_llm(llm_client, summarizer_llm_name, prompt, config)
        return summary
    except Exception as e:
        logger.error(f"Failed to get summary for Agent {agent_id}: {e}")
        return f"**Agent {agent_id} Summary:**\n**Status:** Error\n**Grade:** F\n**Details:** Failed to generate summary due to LLM call error: {e}"


def summarize_run(run_id: str, state_data: Dict[str, Any], config: Dict[str, Any]) -> Optional[Dict[int, str]]:
    """Summarizes logs for all agents in a given run."""
    summaries = {}
    agents_data = state_data.get('agents', [])
    log_dir = Path("logs") / f"run_{run_id}"

    if not agents_data:
        logger.warning(f"No agent data found in state for run {run_id}. Cannot summarize.")
        return None

    logger.info(f"Starting log summarization for run {run_id}...")
    for agent_info in agents_data:
        agent_id = agent_info['agent_id']
        task_desc = agent_info['task_description']
        log_file = log_dir / f"agent_{agent_id}.log"
        summary = summarize_agent_log(agent_id, task_desc, log_file, config)
        summaries[agent_id] = summary
        print("-" * 30 + f"\nAgent {agent_id} Summary:\n" + "-" * 30 + f"\n{summary}\n")

    logger.info(f"Log summarization complete for run {run_id}.")
    return summaries 