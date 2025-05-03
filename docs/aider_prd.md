Okay, let's design and implement this multi-agent coding workflow.

This is a complex system involving multiple LLM calls, process management, and state tracking. We'll build it step-by-step.

**Core Concepts & Design**

1.  **Orchestrator:** A central Python script will manage the entire workflow.
2.  **Configuration:** A `config.yaml` file will store settings like available LLMs, API keys (ideally loaded from environment variables referenced in the config), default context files, etc.
3.  **PRD Generation:** A function/module will interact with a configured "PRD Generator" LLM (e.g., Gemini). It will take the user's proposed change and repo context (potentially using `git dump` or similar) and ask for a PRD that *includes* a structured breakdown for parallel `aider` agents.
4.  **Agent Execution (`tmux`):** A function/module will parse the PRD's agent breakdown, create a `tmux` session with the specified number of panes, and launch an `aider` instance in each pane with its assigned task (`--message`), target files, and any shared context files. Logs will be captured per agent.
5.  **Log Summarization:** A function/module will read the logs from each agent, send them to a configured "Summarizer" LLM, and present the summary, completion status, and grade.
6.  **State Management & Resumption:** We'll track the state (e.g., PRD generated, agents launched, tasks, log files, status) in a simple file (e.g., JSON). A separate script/function will allow listing runs, viewing logs, and potentially reopening `tmux` sessions or providing commands to resume manually.
7.  **`aider` Scripting:** We will rely heavily on `aider --message ... file1 file2 ... --yes > agent_log.txt 2>&1` for non-interactive execution.

**Project Structure**

```
multi-agent-aider/
├── config.yaml                 # Configuration file
├── main_orchestrator.py        # Main script to run the workflow
├── prd_generator.py            # Module for PRD generation
├── agent_runner.py             # Module for running aider agents via tmux
├── log_summarizer.py           # Module for summarizing agent logs
├── resume_manager.py           # Script/module for resuming/inspecting runs
├── utils.py                    # Utility functions (API calls, config loading)
├── state/                      # Directory to store run state files
│   └── run_YYYYMMDD_HHMMSS.json # Example state file
├── logs/                       # Directory to store logs from runs
│   └── run_YYYYMMDD_HHMMSS/    # Logs for a specific run
│       ├── agent_0.log
│       ├── agent_1.log
│       └── ...
├── scripts/                    # Helper scripts
│   └── run_tmux_agents.sh      # Bash script generated dynamically to launch tmux
├── .env                        # Store API keys (add to .gitignore)
└── requirements.txt            # Python dependencies
```

**1. Configuration (`config.yaml`)**

```yaml
# LLM Definitions
# Add configurations for each LLM you want to use.
# The 'api_key_env' specifies the environment variable holding the API key.
llms:
  gemini-1.5-pro:
    type: gemini
    model_name: models/gemini-1.5-pro-latest # Or specific versioned model
    api_key_env: GOOGLE_API_KEY
    # Add other specific Gemini params if needed (temperature, etc.)
  gpt-4o:
    type: openai
    model_name: gpt-4o
    api_key_env: OPENAI_API_KEY
    # Add other specific OpenAI params if needed
  claude-3.5-sonnet:
    type: anthropic
    model_name: claude-3-5-sonnet-20240620
    api_key_env: ANTHROPIC_API_KEY
    # Add other specific Anthropic params if needed

# Workflow Step LLM Configuration
# Assign a configured LLM to each step.
workflow_llms:
  prd_generator: gemini-1.5-pro
  # Aider agents themselves use the model configured within aider's own settings
  # (either via command line --model or aider's config)
  log_summarizer: claude-3.5-sonnet

# Default settings
defaults:
  aider_model: gpt-4o # Default model aider agents should use (can be overridden)
  tmux_session_prefix: aider_run_
  repo_path: . # Path to the git repository relative to where the script is run
  # List of files/patterns to always add as context to aider agents
  # Use aider's glob syntax if needed
  default_context_files:
    - README.md
    # - src/core_module/**.py

# --- Optional ---
# iTerm2 Integration (macOS only)
# If true, tries to use osascript for a potentially smoother tmux launch in iTerm
iterm2_integration: true
```

**2. Environment Variables (`.env`)**

```
# Create this file and add your API keys
# Add .env to your .gitignore file!
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**3. Utility Functions (`utils.py`)**

```python
import yaml
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import importlib.metadata
import logging

# Basic Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_path="config.yaml"):
    """Loads the YAML configuration file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Load API keys from environment variables specified in config
        for llm_key, llm_config in config.get('llms', {}).items():
            api_key_env = llm_config.get('api_key_env')
            if api_key_env:
                api_key = os.getenv(api_key_env)
                if not api_key:
                    logger.warning(f"Environment variable {api_key_env} for LLM '{llm_key}' not set.")
                config['llms'][llm_key]['api_key'] = api_key # Store the actual key
            else:
                 logger.warning(f"No 'api_key_env' specified for LLM '{llm_key}'.")

        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        raise

def get_llm_client(llm_name, config):
    """Initializes and returns an LLM client based on config."""
    llm_config = config.get('llms', {}).get(llm_name)
    if not llm_config:
        raise ValueError(f"LLM configuration for '{llm_name}' not found in config.")

    llm_type = llm_config.get('type')
    api_key = llm_config.get('api_key') # Key was loaded during config load

    if not api_key:
         raise ValueError(f"API key for LLM '{llm_name}' is missing. Check config and .env file.")

    logger.info(f"Initializing LLM client for: {llm_name} (type: {llm_type})")

    if llm_type == 'gemini':
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            # Ensure model name starts with 'models/' if it doesn't
            model_name = llm_config['model_name']
            if not model_name.startswith('models/'):
                model_name = f"models/{model_name}"
            model = genai.GenerativeModel(model_name)
            return model # Return the Gemini model object
        except ImportError:
            raise ImportError("google-generativeai package not installed. Run 'pip install google-generativeai'")
        except Exception as e:
            logger.error(f"Error initializing Gemini client for {llm_name}: {e}")
            raise

    elif llm_type == 'openai':
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            return client # Return the OpenAI client object
        except ImportError:
            raise ImportError("openai package not installed. Run 'pip install openai'")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client for {llm_name}: {e}")
            raise

    elif llm_type == 'anthropic':
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            return client # Return the Anthropic client object
        except ImportError:
            raise ImportError("anthropic package not installed. Run 'pip install anthropic'")
        except Exception as e:
            logger.error(f"Error initializing Anthropic client for {llm_name}: {e}")
            raise

    else:
        raise ValueError(f"Unsupported LLM type: {llm_type}")

def call_llm(client, llm_name, prompt, config):
    """Calls the appropriate LLM API based on the client type."""
    llm_config = config.get('llms', {}).get(llm_name)
    if not llm_config:
        raise ValueError(f"LLM configuration for '{llm_name}' not found.")

    llm_type = llm_config.get('type')
    model_name = llm_config.get('model_name')
    max_tokens = llm_config.get('max_output_tokens', 8192) # Default from example
    temperature = llm_config.get('temperature', 0.7)
    # Add other common parameters if needed (top_p, top_k)

    logger.info(f"Calling LLM: {llm_name} (Model: {model_name})")
    # logger.debug(f"Prompt: {prompt[:500]}...") # Log beginning of prompt

    try:
        if llm_type == 'gemini':
            # Assumes client is the Gemini model object
            response = client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig( # Use correct type
                    # candidate_count=1, # Default is 1
                    # stop_sequences=['...'],
                    max_output_tokens=max_tokens,
                    temperature=temperature,
                    # top_p=0.8,
                    # top_k=40
                )
            )
            # Handle potential safety blocks or empty responses
            if not response.candidates:
                 logger.warning("Gemini response has no candidates.")
                 # Check prompt feedback for block reason
                 if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                     logger.error(f"Gemini request blocked. Reason: {response.prompt_feedback.block_reason}")
                     if response.prompt_feedback.safety_ratings:
                        logger.error(f"Safety Ratings: {response.prompt_feedback.safety_ratings}")
                     raise RuntimeError(f"Gemini request blocked: {response.prompt_feedback.block_reason}")
                 return "Error: No content generated by Gemini (potentially blocked or empty)."

            # Check if the first candidate has content and parts
            candidate = response.candidates[0]
            if not hasattr(candidate, 'content') or not hasattr(candidate.content, 'parts') or not candidate.content.parts:
                logger.warning("Gemini candidate has no content parts.")
                # Log safety ratings if available
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    logger.error(f"Candidate Safety Ratings: {candidate.safety_ratings}")
                # Log finish reason if available
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    logger.error(f"Candidate Finish Reason: {candidate.finish_reason.name}")

                # If blocked due to safety, raise a specific error
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason.name == "SAFETY":
                     raise RuntimeError("Gemini generation stopped due to safety concerns.")

                return "Error: No text content generated by Gemini candidate."

            return candidate.content.parts[0].text

        elif llm_type == 'openai':
            # Assumes client is the OpenAI client object
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                # top_p=...
            )
            return response.choices[0].message.content

        elif llm_type == 'anthropic':
             # Assumes client is the Anthropic client object
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens, # Note: Anthropic uses max_tokens differently, more like a limit
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            # Handle different response structures if necessary
            if response.content and isinstance(response.content, list):
                 # Assuming the first block is the text response
                 text_blocks = [block.text for block in response.content if hasattr(block, 'text')]
                 return "\n".join(text_blocks) if text_blocks else "Error: No text content in Anthropic response"
            else:
                logger.warning("Unexpected Anthropic response format or empty content.")
                return "Error: Unexpected response format from Anthropic."

        else:
            raise ValueError(f"Unsupported LLM type for calling: {llm_type}")

    except Exception as e:
        logger.error(f"Error calling LLM {llm_name}: {e}")
        # Log more details for debugging specific API errors
        if hasattr(e, 'response'): logger.error(f"API Response: {e.response.text}")
        # Reraise the exception to be handled by the caller
        raise

def get_run_id():
    """Generates a unique timestamp-based run ID."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_state(run_id, state_data, state_dir="state"):
    """Saves the current run state to a JSON file."""
    state_path = Path(state_dir)
    state_path.mkdir(exist_ok=True)
    file_path = state_path / f"run_{run_id}.json"
    try:
        with open(file_path, 'w') as f:
            json.dump(state_data, f, indent=4)
        logger.info(f"Run state saved to {file_path}")
    except IOError as e:
        logger.error(f"Error saving state file {file_path}: {e}")

def load_state(run_id, state_dir="state"):
    """Loads a run state from a JSON file."""
    file_path = Path(state_dir) / f"run_{run_id}.json"
    if not file_path.exists():
        logger.warning(f"State file not found for run_id {run_id}: {file_path}")
        return None
    try:
        with open(file_path, 'r') as f:
            state_data = json.load(f)
        logger.info(f"Run state loaded from {file_path}")
        return state_data
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading state file {file_path}: {e}")
        return None

def run_command(command, cwd=None, capture_output=True, text=True, check=False, shell=False):
    """Runs a shell command."""
    logger.info(f"Running command: {' '.join(command) if isinstance(command, list) else command}")
    try:
        # Use shell=True carefully, ensure command components are trusted
        result = subprocess.run(command, cwd=cwd, capture_output=capture_output, text=text, check=check, shell=shell)
        if capture_output:
            logger.debug(f"Command stdout: {result.stdout[:500]}...")
            logger.debug(f"Command stderr: {result.stderr[:500]}...")
        return result
    except FileNotFoundError:
        logger.error(f"Error: Command not found: {command[0] if isinstance(command, list) else command.split()[0]}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {command}")
        logger.error(f"Stderr: {e.stderr}")
        if check: raise # Reraise if check=True
        return e # Return the error object otherwise
    except Exception as e:
        logger.error(f"An unexpected error occurred while running command: {command}. Error: {e}")
        raise

def check_aider_version():
    """Checks if aider is installed and returns its version."""
    try:
        version = importlib.metadata.version('aider-chat')
        logger.info(f"Found aider version: {version}")
        return version
    except importlib.metadata.PackageNotFoundError:
        logger.error("Error: 'aider-chat' package not found. Please install aider: pip install aider-chat")
        return None

```

**4. PRD Generator (`prd_generator.py`)**

```python
import os
import json
from pathlib import Path
from utils import logger, load_config, get_llm_client, call_llm, run_command

def get_repo_context(repo_path_str):
    """Gets repository context using 'git ls-files' and reading files (simplified)."""
    # A more robust version might use 'git log' summaries or a dedicated tool like 'git-dump' if installed/configured.
    # This version lists files and tries to read them, skipping large/binary files.
    repo_path = Path(repo_path_str)
    if not (repo_path / ".git").is_dir():
        logger.warning(f"'{repo_path_str}' does not appear to be a git repository root.")
        # Fallback or error? For now, let's try ls-files anyway.
        # return "Error: Not a git repository."

    logger.info(f"Gathering repository context from: {repo_path}")
    try:
        # Get list of tracked files
        result = run_command(["git", "ls-files"], cwd=repo_path_str, check=True)
        files = result.stdout.strip().split('\n')
        logger.info(f"Found {len(files)} files tracked by git.")

        context = f"Repository Structure (tracked files in {repo_path.name}):\n"
        MAX_FILE_SIZE = 100 * 1024 # 100 KB limit per file
        MAX_TOTAL_CONTEXT = 500 * 1024 # 500 KB total limit (adjust as needed)
        current_context_size = len(context)

        for file_path_rel in files:
            if current_context_size >= MAX_TOTAL_CONTEXT:
                logger.warning("Reached maximum total context size limit. Skipping remaining files.")
                context += "\n[Context Truncated: Max total size reached]"
                break

            file_path_abs = repo_path / file_path_rel
            try:
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
                             logger.warning("Reached maximum total context size limit while adding file name. Skipping remaining files.")
                             context += "\n[Context Truncated: Max total size reached]"
                             break # Stop adding files completely

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


def generate_prd_prompt(proposed_change, repo_context):
    """Constructs the prompt for the PRD generator LLM."""
    # This prompt needs to be carefully crafted and potentially tuned
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

def parse_prd_response(response_text):
    """Parses the LLM response to extract PRD text and the agent breakdown JSON."""
    prd_text = ""
    agent_breakdown_json = None

    try:
        # Find the start of the JSON block
        json_start_index = response_text.find('{')
        # Find the last closing brace (this is heuristic, might fail for nested JSON in text)
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
                         logger.error(f"Failed to parse JSON even from markdown block: {nested_json_err}")
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
            # Keep the prd_text as it might still be useful
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
        # Proceeding, but agent_runner will need to handle this (e.g., run as 1 agent)

    logger.info("PRD generation complete.")
    return prd_text, agent_breakdown, response_text # Return raw response too for saving

```

**5. Agent Runner (`agent_runner.py`)**

```python
import os
import subprocess
import time
import platform
from pathlib import Path
from utils import logger, run_command

def generate_tmux_script(session_name, agent_tasks, repo_path_abs, log_dir_abs, config):
    """Generates a bash script to set up tmux and run aider agents."""
    script_path = Path("scripts") / f"run_{session_name}.sh"
    script_path.parent.mkdir(exist_ok=True)

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


def run_agents_in_tmux(agent_breakdown, run_id, config):
    """Orchestrates running aider agents based on the breakdown using tmux."""
    if not agent_breakdown or not agent_breakdown.get('agents'):
        logger.warning("No valid agent breakdown provided. Cannot run agents.")
        # TODO: Maybe run as a single agent with the original proposed change? Needs design.
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
            # This might need adjustment based on your iTerm setup preferences
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
            logger.info(f"iTerm2 tab should have been created for session '{session_name}'. Attach manually if needed: tmux attach -t {session_name}")

        else:
            logger.info("Running tmux script directly.")
            # Run the script in the background; it will create the detached tmux session
            result = run_command(['bash', script_path], capture_output=True, text=True)
            if result.returncode != 0:
                 logger.error(f"Tmux script execution failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
                 return False, session_name # Return session name even if script failed internally
            logger.info(f"Tmux script executed. Session '{session_name}' should be running.")
            logger.info(f"You can attach using: tmux attach-session -t {session_name}")

        # Note: This doesn't wait for agents to finish. It just launches them.
        # Monitoring completion would require polling tmux panes or checking log files.
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

```

**6. Log Summarizer (`log_summarizer.py`)**

```python
import os
from pathlib import Path
from utils import logger, load_config, get_llm_client, call_llm

def generate_summary_prompt(agent_id, task_description, log_content):
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

def summarize_agent_log(agent_id, task_description, log_file_path, config):
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


def summarize_run(run_id, state_data, config):
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

```

**7. Main Orchestrator (`main_orchestrator.py`)**

```python
import argparse
import sys
from pathlib import Path

# Setup sys.path to find sibling modules - Adjust if structure differs
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from utils import logger, load_config, get_run_id, save_state, check_aider_version
from prd_generator import generate_prd
from agent_runner import run_agents_in_tmux
from log_summarizer import summarize_run

def main():
    # --- Essential Checks ---
    # Check if aider is installed
    if not check_aider_version():
        sys.exit(1) # Exit if aider is not found

    # Check for tmux
    try:
        import shutil
        if not shutil.which("tmux"):
            logger.error("Error: 'tmux' command not found. Please install tmux.")
            sys.exit(1)
        logger.info(f"Found tmux at: {shutil.which('tmux')}")
    except Exception as e:
        logger.warning(f"Could not reliably check for tmux: {e}. Assuming it exists.")


    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Orchestrate multi-agent aider workflow.")
    parser.add_argument("proposed_change", help="The natural language description of the proposed change.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file.")
    # Add option to override repo path?
    # parser.add_argument("--repo-path", help="Override repository path from config.")

    args = parser.parse_args()

    # --- Load Config ---
    try:
        config = load_config(args.config)
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
    save_state(run_id, current_state) # Initial save

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
        save_state(run_id, current_state)
        logger.info("PRD generated successfully.")
        print("\n--- PRD ---")
        print(prd_text if prd_text else "[No PRD text generated]")
        print("\n--- Agent Breakdown ---")
        import json
        print(json.dumps(agent_breakdown, indent=2) if agent_breakdown else "[No valid agent breakdown generated]")
        print("-" * 20)

        # Handle case where breakdown failed but PRD text exists
        if not agent_breakdown or not agent_breakdown.get("agents"):
             logger.warning("Agent breakdown generation failed or is empty. Cannot proceed with parallel agent execution.")
             logger.info("Workflow stopping after PRD generation.")
             # Optionally, could try running the original change with a single agent here
             sys.exit(0) # Exit gracefully

    except Exception as e:
        logger.error(f"Workflow failed during PRD generation: {e}")
        current_state["status"] = "failed_prd"
        save_state(run_id, current_state)
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
        save_state(run_id, current_state)
        if not success:
             sys.exit(1) # Exit if launch failed

    except Exception as e:
        logger.error(f"Workflow failed during agent execution: {e}")
        current_state["status"] = "failed_agent_launch"
        save_state(run_id, current_state)
        sys.exit(1)

    # --- Post-Execution Steps (Manual for now) ---
    logger.info("\n--- Workflow Paused ---")
    logger.info(f"Aider agents have been launched in tmux session: {session_name}")
    logger.info("Monitor the tmux session to see agent progress.")
    logger.info(f"Once agents appear complete (check logs in logs/run_{run_id}/), you can run:")
    logger.info(f"python log_summarizer.py {run_id} --config {args.config}")
    logger.info("Or use 'python resume_manager.py' for more options.")

    # --- Automatic Summarization (Optional - requires waiting/polling) ---
    # Implementing reliable waiting/polling is complex (check tmux panes, log file changes/keywords)
    # For this version, we rely on the user to run summarization separately.
    # logger.info("\n--- Step 3: Summarizing Logs (Run Separately) ---")
    # try:
    #     # Placeholder: In a real automated system, you'd wait here.
    #     input("Press Enter after agents have finished in tmux to summarize logs...")
    #     summaries = summarize_run(run_id, current_state, config)
    #     current_state["summaries"] = summaries
    #     current_state["status"] = "summarized"
    #     save_state(run_id, current_state)
    # except Exception as e:
    #     logger.error(f"Workflow failed during log summarization: {e}")
    #     current_state["status"] = "failed_summarization"
    #     save_state(run_id, current_state)
    #     sys.exit(1)

    logger.info(f"\nWorkflow orchestration initiated for Run ID: {run_id}")

if __name__ == "__main__":
    main()
```

**8. Resume Manager (`resume_manager.py`)**

```python
import argparse
import json
import sys
from pathlib import Path
import subprocess

# Setup sys.path to find sibling modules
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

from utils import logger, load_state, run_command, load_config # Assuming load_config is needed
from log_summarizer import summarize_run # To trigger summarization

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
                    "change": proposed_change[:60] + "...", # Truncate
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
            print(f"    Task: {task[:80]}...")
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
    parser_summarize.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file used for the run (needed for LLM settings).")
    parser_summarize.add_argument("--state-dir", default="state", help="Directory containing run state files.")
    # log_dir is inferred from run_id

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
                      from utils import save_state # Import here to avoid circular dependency if utils imports resume_manager
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
```

**9. Requirements (`requirements.txt`)**

```
PyYAML
requests # Only if using direct HTTP calls, google/openai/anthropic libs handle this
google-generativeai
openai
anthropic
# Add other dependencies if needed (e.g., for specific repo context tools)
```

**How to Use**

1.  **Setup:**
    *   Install Python 3.8+.
    *   Install `tmux`.
    *   Install `aider`: `pip install aider-chat`
    *   Install required Python packages: `pip install -r requirements.txt`
    *   Create `.env` file and add your API keys.
    *   Review and customize `config.yaml` (LLM models, repo path, context files). Ensure the LLM names match keys in the `llms` section.
    *   Make sure your project is a git repository.
2.  **Run Workflow:**
    ```bash
    # Navigate to the directory containing main_orchestrator.py
    python main_orchestrator.py "Implement a new feature to parse user CSV uploads and store results in the database"
    ```
    *   This will:
        *   Generate the PRD and agent breakdown using the configured PRD LLM.
        *   Print the PRD and breakdown.
        *   Generate a `tmux` script in `./scripts/`.
        *   Execute the script to launch `aider` agents in a new `tmux` session (potentially in a new iTerm tab/window if configured).
        *   Inform you of the `tmux` session name.
3.  **Monitor Agents:**
    *   Attach to the tmux session: `tmux attach-session -t <session_name>` (e.g., `tmux attach -t aider_run_20231027_123456`)
    *   Watch the agents work in their respective panes. Logs are also saved in `./logs/run_<run_id>/`.
4.  **Summarize (After Agents Finish):**
    *   Once the agents seem done (check logs/panes), run the summarizer:
        ```bash
        # Use the run_id printed by the orchestrator
        python resume_manager.py summarize <run_id> --config config.yaml
        ```
    *   This reads the logs, calls the summarizer LLM for each, prints the summaries, and updates the run's state file.
5.  **Inspect / Resume:**
    *   List runs: `python resume_manager.py list`
    *   View details: `python resume_manager.py details <run_id>`
    *   View a specific log: `python resume_manager.py log <run_id> <agent_id>`
    *   Get tmux attach command: `python resume_manager.py attach <run_id>`

**Considerations & Future Improvements**

*   **Robust State:** The current JSON state is simple. For complex resuming or retries, a more robust state machine or database might be needed.
*   **Error Handling:** More granular error handling (e.g., retrying LLM calls, specific `aider` error codes) can be added.
*   **Agent Completion Detection:** Automatically detecting when `aider` agents finish is non-trivial. It would involve monitoring `tmux` panes (checking for exit codes, specific output) or tailing log files for completion markers.
*   **Dependency Management:** The current PRD prompt asks the LLM to consider dependencies, but it might fail. If Agent 0 modifies a file Agent 1 depends on, the parallel execution might break. A more advanced system could introduce sequential steps or dependency graphs.
*   **Complex Tasks:** `aider --message` is for single tasks. Multi-step tasks for an agent would require a different approach (e.g., feeding subsequent messages based on log output, or using `aider`'s API if/when available and stable).
*   **Code Merging:** If agents *do* modify the same files (even if unintended), merge conflicts can occur. `aider`'s auto-commit helps isolate changes per agent run, but manual merging might be needed later.
*   **Repo Context:** The `git ls-files` + read approach is basic. Using `git dump`, `ctags`, or other code analysis tools could provide richer context to the PRD LLM.
*   **Interactive Resumption:** `resume_manager.py` could be enhanced to offer options like "Retry agent X" which would regenerate and run the specific `aider` command for that agent.
*   **Security:** Ensure API keys are handled securely (using `.env` and `.gitignore` is a good start). Be cautious running arbitrary commands generated by LLMs.

This implementation provides a solid foundation for the requested workflow, leveraging `aider`'s scripting capabilities and `tmux` for parallel execution and visibility. Remember to tailor the prompts and configuration to your specific needs and LLM choices.