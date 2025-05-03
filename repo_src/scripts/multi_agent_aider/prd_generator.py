import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any

from utils import logger, load_config, get_llm_client, call_llm, run_command, get_file_size_info

def get_repo_context(repo_path_str: str) -> str:
    """Gets repository context using 'git ls-files' and reading files."""
    repo_path = Path(repo_path_str)
    if not (repo_path / ".git").is_dir():
        logger.warning(f"'{repo_path_str}' does not appear to be a git repository root.")

    logger.info(f"Gathering repository context from: {repo_path}")
    try:
        # Get list of tracked files
        result = run_command(["git", "ls-files"], cwd=repo_path_str, check=True)
        files = result.stdout.strip().split('\n')
        logger.info(f"Found {len(files)} files tracked by git.")

        context = f"Repository Structure (tracked files in {repo_path.name}):\n"
        MAX_FILE_SIZE = 100 * 1024 # 100 KB limit per file
        MAX_TOTAL_CONTEXT = 500 * 1024 # 500 KB total limit
        current_context_size = len(context)

        for file_path_rel in files:
            if current_context_size >= MAX_TOTAL_CONTEXT:
                logger.warning("Reached maximum total context size limit. Skipping remaining files.")
                context += "\n[Context Truncated: Max total size reached]"
                break

            file_path_abs = repo_path / file_path_rel
            try:
                if not file_path_abs.exists():
                    continue
                    
                file_size = file_path_abs.stat().st_size
                if file_size > MAX_FILE_SIZE:
                    context += f"- {file_path_rel} (Skipped: Too large > {MAX_FILE_SIZE // 1024}KB)\n"
                    current_context_size += len(f"- {file_path_rel} (Skipped...)\n")
                    continue
                if file_size == 0:
                    context += f"- {file_path_rel} (Empty file)\n"
                    current_context_size += len(f"- {file_path_rel} (Empty file)\n")
                    continue

                # Attempt to read as text, skipping binary files
                with open(file_path_abs, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(MAX_FILE_SIZE) # Read up to max size
                    file_header = f"\n--- File: {file_path_rel} ---\n"
                    file_content_str = file_header + content + "\n--- End File ---\n"

                    if current_context_size + len(file_content_str) <= MAX_TOTAL_CONTEXT:
                        context += file_content_str
                        current_context_size += len(file_content_str)
                    else:
                        # Try adding just the file name if content exceeds limit
                        file_name_entry = f"- {file_path_rel} (Content skipped: Exceeds total size limit)\n"
                        if current_context_size + len(file_name_entry) <= MAX_TOTAL_CONTEXT:
                            context += file_name_entry
                            current_context_size += len(file_name_entry)
                        else:
                             logger.warning("Reached maximum total context size limit while adding file name.")
                             context += "\n[Context Truncated: Max total size reached]"
                             break

            except FileNotFoundError:
                logger.warning(f"File listed by git not found: {file_path_abs}")
                context += f"- {file_path_rel} (Skipped: Not found)\n"
                current_context_size += len(f"- {file_path_rel} (Skipped...)\n")
            except OSError as e:
                logger.warning(f"Could not read file {file_path_abs}: {e}")
                context += f"- {file_path_rel} (Skipped: Read error)\n"
                current_context_size += len(f"- {file_path_rel} (Skipped...)\n")
            except Exception as e:
                 logger.warning(f"Unexpected error processing file {file_path_abs}: {e}")
                 context += f"- {file_path_rel} (Skipped: Unexpected error)\n"
                 current_context_size += len(f"- {file_path_rel} (Skipped...)\n")

        logger.info(f"Generated repository context (Size: {current_context_size / 1024:.2f} KB)")
        return context

    except subprocess.CalledProcessError as e:
        logger.error(f"Error running 'git ls-files' in {repo_path_str}: {e}")
        logger.error(f"Stderr: {e.stderr}")
        return f"Error: Could not list files in git repository at {repo_path_str}."
    except Exception as e:
        logger.error(f"Unexpected error getting repo context: {e}")
        return "Error: Unexpected error generating repository context."


def generate_prd_prompt(proposed_change: str, repo_context: str) -> str:
    """Constructs the prompt for the PRD generator LLM."""
    prompt = f"""
You are an expert software architect and project manager. Your task is to generate a Product Requirements Document (PRD) and an implementation plan based on a proposed change and the current repository context.

**Proposed Change:**
{proposed_change}

**Current Repository Context:**
```
{repo_context[:40000]}
```
(Context may be truncated for brevity)

**Instructions:**

1.  **Analyze:** Understand the proposed change in the context of the existing repository structure and files.
2.  **Generate PRD:** Create a concise PRD including:
    *   **Goal:** What is the objective of this change?
    *   **Scope:** What is included and excluded?
    *   **High-Level Requirements:** Key functionalities or changes needed.
3.  **Implementation Plan:** Outline the steps to implement the change.
4.  **Agent Breakdown for Parallel Execution:**
    *   Analyze the implementation plan and identify tasks suitable for parallel execution by independent `aider` agents. Consider file dependencies – agents should ideally work on separate, non-conflicting sets of files or tasks.
    *   **Suggest an optimal number of parallel agents (N).** Base this on the natural divisions in the work.
    *   Provide a breakdown in the following JSON format directly within this response. Ensure the JSON is valid. Do not include the JSON block inside a markdown code block.

```json
{{
  "suggested_num_agents": N,
  "agents": [
    {{
      "agent_id": 0,
      "task_description": "Detailed description of the task for agent 0. Be specific about what functions/classes/files to create or modify.",
      "target_files": ["path/to/file1.py", "path/to/relevant/dir/"] // List files or directories aider should focus on
    }},
    {{
      "agent_id": 1,
      "task_description": "Detailed description of the task for agent 1.",
      "target_files": ["path/to/another/file.js", "path/to/config.json"]
    }}
    // Add more agent objects as needed up to N-1
  ]
}}
```

**Output Format:**

Provide the PRD and Implementation Plan first as clear markdown text. Then, provide the Agent Breakdown strictly in the JSON format specified above, ensuring it is valid JSON.
"""
    return prompt

def parse_prd_response(response_text: str) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Parses the LLM response to extract PRD text and the agent breakdown JSON."""
    prd_text = ""
    agent_breakdown_json = None

    try:
        # Find the start of the JSON block
        json_start_index = response_text.find('{')
        # Find the last closing brace
        json_end_index = response_text.rfind('}')

        if json_start_index != -1 and json_end_index != -1 and json_start_index < json_end_index:
            # Extract potential JSON string
            potential_json_str = response_text[json_start_index : json_end_index + 1]

            # Try parsing the extracted string
            try:
                agent_breakdown_json = json.loads(potential_json_str)
                # If successful, assume the text before it is the PRD
                prd_text = response_text[:json_start_index].strip()
                logger.info("Successfully parsed agent breakdown JSON from LLM response.")
            except json.JSONDecodeError as json_err:
                logger.warning(f"Could not parse JSON block directly: {json_err}")
                # Fallback: Look for JSON within markdown code blocks if direct parsing fails
                import re
                match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
                if match:
                    potential_json_str = match.group(1)
                    try:
                        agent_breakdown_json = json.loads(potential_json_str)
                        # Assume text before the block is PRD
                        prd_text = response_text[:match.start()].strip()
                        logger.info("Successfully parsed agent breakdown JSON from markdown code block.")
                    except json.JSONDecodeError as nested_json_err:
                         logger.error(f"Failed to parse JSON from markdown block: {nested_json_err}")
                         prd_text = response_text # Assign all text as PRD if JSON fails
                         agent_breakdown_json = None
                else:
                    logger.error("Agent breakdown JSON block not found or invalid in the response.")
                    prd_text = response_text # Assign all text as PRD if JSON fails
                    agent_breakdown_json = None
        else:
            logger.error("Could not find valid start/end braces for the agent breakdown JSON block.")
            prd_text = response_text # Assign all text as PRD if JSON fails
            agent_breakdown_json = None

    except Exception as e:
        logger.error(f"Error parsing PRD response: {e}")
        prd_text = response_text # Fallback
        agent_breakdown_json = None

    # Basic validation of the parsed structure
    if agent_breakdown_json:
        if not isinstance(agent_breakdown_json, dict) or \
           "suggested_num_agents" not in agent_breakdown_json or \
           "agents" not in agent_breakdown_json or \
           not isinstance(agent_breakdown_json["agents"], list):
            logger.error("Parsed JSON does not match the expected agent breakdown structure.")
            # Invalidate the JSON if structure is wrong
            agent_breakdown_json = None
            prd_text = response_text
        else:
            # Validate agent structure
            for i, agent in enumerate(agent_breakdown_json["agents"]):
                 if not isinstance(agent, dict) or \
                    "agent_id" not in agent or \
                    "task_description" not in agent or \
                    "target_files" not in agent or \
                    not isinstance(agent["target_files"], list):
                    logger.error(f"Invalid structure for agent at index {i} in parsed JSON.")
                    agent_breakdown_json = None # Invalidate the whole structure
                    prd_text = response_text
                    break # Stop checking other agents

    if not agent_breakdown_json:
         logger.warning("Could not extract a valid agent breakdown. Proceeding without parallel agents might be necessary.")

    return prd_text.strip(), agent_breakdown_json


def generate_prd(proposed_change, config):
    """Generates the PRD and agent breakdown."""
    logger.info("Starting PRD generation process...")
    prd_llm_name = config['workflow_llms']['prd_generator']
    repo_path = config['defaults']['repo_path']

    # 1. Get Repo Context
    repo_context = get_repo_context(repo_path)
    if repo_context.startswith("Error:"):
        logger.error(f"Failed to get repository context: {repo_context}")
        return None, None, None # Indicate failure

    # 2. Prepare Prompt
    prompt = generate_prd_prompt(proposed_change, repo_context)

    # 3. Call LLM
    try:
        llm_client = get_llm_client(prd_llm_name, config)
        response_text = call_llm(llm_client, prd_llm_name, prompt, config)
    except Exception as e:
        logger.error(f"Failed to call PRD generator LLM: {e}")
        return None, None, None # Indicate failure

    # 4. Parse Response
    prd_text, agent_breakdown = parse_prd_response(response_text)

    if not prd_text and not agent_breakdown:
         logger.error("LLM response was empty or completely failed parsing.")
         return None, None, None

    if not agent_breakdown:
        logger.warning("PRD generated, but failed to get a valid agent breakdown structure from the LLM.")

    logger.info("PRD generation complete.")
    return prd_text, agent_breakdown, response_text # Return raw response too for saving 
