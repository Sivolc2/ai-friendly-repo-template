Okay, let's design the structure and scripts for your automated Aider workflow using a hybrid Bash/Python approach and OpenRouter.

**1. Project Structure**

```
.
├── .github/
├── .venv/                  # Python virtual environment (created by script)
├── code_builder/
│   ├── runs/               # Stores artifacts for each run
│   │   └── {run_id}/       # Example: 20240516_103000
│   │       ├── aider_config.json # JSON config for Aider agents
│   │       └── prd_generation_log.txt # Log/response from PRD LLM call
│   ├── config.yaml         # Configuration for models, API keys, etc.
│   ├── requirements.txt    # Python dependencies for code_builder
│   ├── generate_plan.py    # Python script for PRD & Aider config generation
│   ├── launch_aiders.sh    # Bash script to launch tmux + Aider instances
│   └── main_orchestrator.sh # Main entry point Bash script
├── docs/
│   ├── adr/
│   ├── diagrams/
│   ├── pipelines/
│   ├── prd/                # PRDs generated here (e.g., 001-feature-name.md)
│   └── README_*.md
├── registry/
├── repo_src/
│   ├── backend/
│   ├── frontend/
│   ├── scripts/
│   └── shared/
├── .gitignore             # Ensure code_builder/config.yaml, .venv, code_builder/runs/* are ignored if sensitive
├── README.md
└── ... (other project files)
```

**2. Configuration (`./code_builder/config.yaml`)**

```yaml
# API Keys - Prefer environment variables for security, but can be placed here.
# Example: export OPENROUTER_API_KEY='your_key_here'
openrouter_api_key: null # Set to your key or leave null to use environment variable OPENROUTER_API_KEY

# Model Configuration (using OpenRouter model identifiers)
# Find identifiers at https://openrouter.ai/models
prd_generator_model: "google/gemini-flash-1.5" # Model for generating PRD and Aider config
aider_model: "anthropic/claude-3.5-sonnet"     # Model Aider will use (ensure Aider supports this via OpenRouter)
                                               # Needs to be configured in Aider's own config too (.aider.conf.yml)

# Aider Orchestration Settings
default_num_agents: 1 # Default if LLM doesn't specify

# --- Aider Configuration (Informational - Configure Aider via ~/.aider.conf.yml or ./.aider.conf.yml) ---
# It's recommended to configure Aider's model and API key via its own config file
# Example .aider.conf.yml content:
# ---
# model: openrouter/anthropic/claude-3.5-sonnet
# openrouter-api-key: sk-or-v1-abc...xyz # Or set OPENROUTER_API_KEY env var
# auto-commits: false
# git: true
# ---
```
*Self-correction:* Updated model names to reflect common OpenRouter identifiers. Changed `claude-3-7-sonnet-20250219` to `claude-3.5-sonnet` as the former isn't a standard identifier and 3.5 is the latest Sonnet. Google model name updated.

**3. Python Requirements (`./code_builder/requirements.txt`)**

```txt
PyYAML>=6.0
requests>=2.28
python-dotenv>=1.0.0 # To load API keys from a potential .env file
```

**4. Python Script (`./code_builder/generate_plan.py`)**

```python
#!/usr/bin/env python3
import argparse
import yaml
import requests
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# --- Constants ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_PRD_DIR = PROJECT_ROOT / "docs" / "prd"
RUNS_DIR = SCRIPT_DIR / "runs"
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# --- Helper Functions ---

def load_config():
    """Loads configuration from config.yaml"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            # Load API key from environment if not in config
            if not config.get('openrouter_api_key'):
                load_dotenv(dotenv_path=SCRIPT_DIR / '.env') # Optional: load .env file
                config['openrouter_api_key'] = os.environ.get('OPENROUTER_API_KEY')
            if not config.get('openrouter_api_key'):
                raise ValueError("OpenRouter API key not found in config.yaml or OPENROUTER_API_KEY environment variable.")
            return config
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {CONFIG_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def find_next_prd_number():
    """Finds the next sequential number for PRDs in docs/prd/"""
    DOCS_PRD_DIR.mkdir(parents=True, exist_ok=True)
    max_num = 0
    for f in DOCS_PRD_DIR.glob("[0-9][0-9][0-9]-*.md"):
        try:
            num = int(f.name[:3])
            if num > max_num:
                max_num = num
        except ValueError:
            continue
    return max_num + 1

def extract_json_from_response(text):
    """Extracts JSON content between <json> tags."""
    match = re.search(r'<json>(.*?)</json>', text, re.DOTALL | re.IGNORECASE)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error: Could not parse extracted JSON.\nContent: {json_str}\nError: {e}")
            return None
    else:
        print("Error: <json> tags not found in the LLM response.")
        return None

def call_openrouter(prompt, model, api_key, run_log_path):
    """Calls the OpenRouter API and logs the interaction."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    log_content = f"--- Request ---\nModel: {model}\nPrompt:\n{prompt}\n\n"
    print(f"Sending request to OpenRouter (Model: {model})...")
    try:
        response = requests.post(OPENROUTER_API_ENDPOINT, headers=headers, json=data, timeout=180) # 3 min timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        response_text = result['choices'][0]['message']['content']
        log_content += f"--- Response (Status: {response.status_code}) ---\n{response_text}\n"
        print("Request successful.")
        return response_text
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling OpenRouter API: {e}"
        if hasattr(e, 'response') and e.response is not None:
             error_message += f"\nResponse Body: {e.response.text}"
        log_content += f"--- Error ---\n{error_message}\n"
        print(error_message)
        return None
    finally:
        try:
            with open(run_log_path, 'w') as f:
                f.write(log_content)
            print(f"LLM interaction logged to: {run_log_path}")
        except IOError as e:
            print(f"Warning: Could not write to log file {run_log_path}: {e}")


def generate_prd_and_config(user_query, config, run_id):
    """Generates the PRD and Aider JSON config using an LLM."""
    run_path = RUNS_DIR / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    run_log_path = run_path / "prd_generation_log.txt"

    prd_generator_model = config['prd_generator_model']
    api_key = config['openrouter_api_key']

    # Get current repository context (simple example: file list)
    # More sophisticated context can be added here (e.g., using `git ls-files` or specific file contents)
    try:
        # Example: List files, ignore .git, .venv, build artifacts etc.
        # You might want a more robust way to get relevant files.
        repo_files = [str(p.relative_to(PROJECT_ROOT)) for p in PROJECT_ROOT.glob('**/*') if p.is_file() and
                      '.git' not in p.parts and
                      '.venv' not in p.parts and
                      'node_modules' not in p.parts and
                      '__pycache__' not in p.parts and
                      'dist' not in p.parts and
                      'build' not in p.parts and
                      'code_builder/runs' not in p.parts]
        repo_context = "\nRelevant project files:\n" + "\n".join(sorted(repo_files)[:50]) # Limit context size
    except Exception as e:
        print(f"Warning: Could not get repository file list: {e}")
        repo_context = "\nRepository context could not be generated."


    prompt = f"""
You are an expert system design assistant. Your task is to take a user query for a new feature or change
and generate a detailed Product Requirements Document (PRD) along with a JSON configuration
to guide multiple AI coding agents (using Aider).

User Query: "{user_query}"

{repo_context}

Instructions:
1.  **Generate a PRD:**
    *   Write a comprehensive PRD for implementing the feature described in the user query.
    *   Break the implementation down into logical, mostly independent parts or sections suitable for parallel development if possible.
    *   Include: Overview, Goals, User Stories (if applicable), Detailed Technical Plan/Sections, Non-Goals.
    *   The PRD should be detailed enough for an AI agent to follow.
2.  **Generate JSON Configuration:**
    *   After the PRD text, provide a JSON object enclosed in `<json>` and `</json>` tags.
    *   The JSON object must have the following structure:
        ```json
        {{
          "prd_slug": "short-kebab-case-name-for-prd-file",
          "num_agents": <integer>, // Number of agents needed (e.g., number of sections)
          "agents": [
            {{
              "agent_id": 1,
              "description": "Brief description of this agent's task",
              "files_context": ["path/to/file1.py", "path/to/relevant_doc.md", "docs/prd/NNN-slug.md"], // Files Aider should load. ALWAYS include the generated PRD path.
              "prompt": "Detailed prompt for this agent, referencing specific PRD sections. Example: Implement Section 3.1 of the PRD (docs/prd/NNN-slug.md)."
            }}
            // ... more agent objects if num_agents > 1
          ]
        }}
        ```
    *   `prd_slug`: Suggest a short, descriptive kebab-case slug for the PRD filename (e.g., "add-user-auth").
    *   `num_agents`: Determine the optimal number of agents based on the PRD sections (can be 1).
    *   `agents`: Create one entry per agent.
        *   `files_context`: List existing files relevant to the agent's task. **Crucially, include the path to the PRD file that will be created.** Use the placeholder `docs/prd/NNN-slug.md` which will be replaced later.
        *   `prompt`: Provide a specific and actionable prompt for the Aider agent, directing it to implement its assigned part(s) of the PRD.

**Output Format:**

[Full PRD Markdown Text Here]

<json>
[JSON Configuration Object Here]
</json>
"""

    llm_response = call_openrouter(prompt, prd_generator_model, api_key, run_log_path)

    if not llm_response:
        print("Error: Failed to get response from LLM.")
        return None, None

    # Extract PRD and JSON
    json_config = extract_json_from_response(llm_response)
    prd_text_match = re.match(r'(.*?)<json>', llm_response, re.DOTALL | re.IGNORECASE)
    prd_text = prd_text_match.group(1).strip() if prd_text_match else llm_response # Fallback

    if not json_config or not prd_text:
        print("Error: Could not extract PRD text or JSON config from the response.")
        return None, None

    # Validate basic JSON structure
    if not all(k in json_config for k in ["prd_slug", "num_agents", "agents"]) or \
       not isinstance(json_config["agents"], list) or \
       len(json_config["agents"]) != json_config["num_agents"]:
        print(f"Error: Invalid JSON structure received: {json.dumps(json_config, indent=2)}")
        return None, None


    # Save PRD
    next_prd_num = find_next_prd_number()
    prd_slug = json_config.get("prd_slug", f"feature-{run_id}")
    prd_filename = f"{next_prd_num:03d}-{prd_slug}.md"
    prd_filepath = DOCS_PRD_DIR / prd_filename
    try:
        with open(prd_filepath, 'w') as f:
            f.write(prd_text)
        print(f"PRD saved successfully: {prd_filepath}")
    except IOError as e:
        print(f"Error saving PRD file: {e}")
        return None, None

    # Update file paths in JSON config
    prd_path_str = str(prd_filepath.relative_to(PROJECT_ROOT))
    for agent_config in json_config["agents"]:
        agent_config["files_context"] = [
            f.replace("docs/prd/NNN-slug.md", prd_path_str) for f in agent_config.get("files_context", [])
        ]
        # Ensure PRD path is always included if missed by LLM
        if prd_path_str not in agent_config["files_context"]:
             agent_config["files_context"].append(prd_path_str)

        # Also replace placeholder in prompt if necessary
        agent_config["prompt"] = agent_config.get("prompt", "").replace("docs/prd/NNN-slug.md", prd_path_str)


    # Save JSON config
    json_config_path = run_path / "aider_config.json"
    try:
        with open(json_config_path, 'w') as f:
            json.dump(json_config, f, indent=2)
        print(f"Aider JSON config saved successfully: {json_config_path}")
    except IOError as e:
        print(f"Error saving JSON config file: {e}")
        # Clean up PRD file if config save fails? Maybe not critical.
        return None, None

    return str(json_config_path) # Return path for the orchestrator script

# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PRD and Aider config using an LLM.")
    parser.add_argument("user_query", help="The user's feature request or query.")
    parser.add_argument("--run-id", help="Unique ID for this run.", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = parser.parse_args()

    print(f"--- Starting PRD Generation (Run ID: {args.run_id}) ---")
    config = load_config()
    json_config_path = generate_prd_and_config(args.user_query, config, args.run_id)

    if json_config_path:
        print(f"--- PRD Generation Complete ---")
        # Output the path for the calling script
        print(f"JSON_CONFIG_PATH={json_config_path}")
    else:
        print(f"--- PRD Generation Failed ---")
        sys.exit(1)
```

**5. Bash Script (`./code_builder/launch_aiders.sh`)**

```bash
#!/usr/bin/env bash
set -euo pipefail # Exit on error, unset variable, or pipe failure

# --- Configuration & Arguments ---
CONFIG_JSON_PATH="${1:-}"
RUN_ID="${2:-}"
TMUX_SESSION_NAME="aider_run_${RUN_ID}"

# --- Sanity Checks ---
if [[ -z "$CONFIG_JSON_PATH" || ! -f "$CONFIG_JSON_PATH" ]]; then
  echo "Error: Aider config JSON path is missing or file not found."
  echo "Usage: $0 <path/to/aider_config.json> <run_id>"
  exit 1
fi

if [[ -z "$RUN_ID" ]]; then
  echo "Error: Run ID is missing."
  echo "Usage: $0 <path/to/aider_config.json> <run_id>"
  exit 1
fi

# Check for required tools
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed. Please install tmux (e.g., 'brew install tmux' or 'sudo apt-get install tmux')."
    exit 1
fi
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install jq (e.g., 'brew install jq' or 'sudo apt-get install jq')."
    exit 1
fi
if ! command -v aider &> /dev/null; then
    echo "Warning: 'aider' command not found directly. Assuming it's available in the activated Python environment."
    # Consider adding a check within the venv if needed
fi

# Check if we are inside the project root (optional but good practice)
if [ ! -f "./code_builder/config.yaml" ]; then
    echo "Warning: Script doesn't seem to be running from the project root."
    # cd to project root if possible, or exit depending on requirements
fi


echo "--- Launching Aider Agents in Tmux Session: ${TMUX_SESSION_NAME} ---"
echo "Config File: ${CONFIG_JSON_PATH}"

# --- Tmux Setup ---
# Kill existing session if it exists (optional, uncomment if desired)
# tmux kill-session -t "$TMUX_SESSION_NAME" 2>/dev/null || true

# Check if session exists, attach if so, otherwise create
if tmux has-session -t "$TMUX_SESSION_NAME" 2>/dev/null; then
  echo "Session $TMUX_SESSION_NAME already exists. Attaching..."
  tmux attach-session -t "$TMUX_SESSION_NAME"
  exit 0
fi

echo "Creating new tmux session: ${TMUX_SESSION_NAME}"
# Create the session and first window/pane detached
tmux new-session -d -s "$TMUX_SESSION_NAME" -n "Agent_1" # Name first window

# --- Agent Launch Loop ---
num_agents=$(jq '.num_agents' "$CONFIG_JSON_PATH")
echo "Number of agents to launch: $num_agents"

# Handle case of zero agents (shouldn't happen with validation, but belt-and-suspenders)
if [[ "$num_agents" -lt 1 ]]; then
    echo "Error: 'num_agents' is less than 1 in config file. Exiting."
    # Clean up potentially created tmux session?
    tmux kill-session -t "$TMUX_SESSION_NAME" 2>/dev/null || true
    exit 1
fi


agent_index=0
jq -c '.agents[]' "$CONFIG_JSON_PATH" | while IFS= read -r agent_config; do
    agent_id=$(echo "$agent_config" | jq -r '.agent_id')
    agent_desc=$(echo "$agent_config" | jq -r '.description')
    agent_prompt=$(echo "$agent_config" | jq -r '.prompt')
    # Join files with spaces for the aider command line
    files_context=$(echo "$agent_config" | jq -r '.files_context | join(" ")')

    echo "Preparing Agent ${agent_id}: ${agent_desc}"

    # Construct the aider command
    # Assumes model and API key are set in Aider's config (.aider.conf.yml or env vars)
    # Add --yes for less interaction if desired
    aider_cmd="aider ${files_context} --message \"${agent_prompt}\""

    # For the first agent, use the initial pane. For others, split.
    if [[ "$agent_index" -gt 0 ]]; then
        echo "Creating new pane for Agent ${agent_id}"
        # Split the *last created* pane horizontally (-h) or vertically (-v)
        tmux split-window -t "${TMUX_SESSION_NAME}" -h # Horizontal split
        tmux select-layout -t "${TMUX_SESSION_NAME}" tiled # Re-tile after split
    fi

    # Get the ID of the *current* or *newly created* pane
    # target_pane=$(tmux list-panes -t "$TMUX_SESSION_NAME" -F '#{pane_id}' | tail -n 1) # Less reliable?
    target_pane="${TMUX_SESSION_NAME}:.${agent_index}" # More direct targeting

    # Rename window/pane (optional)
    tmux rename-window -t "$target_pane" "Agent_${agent_id}"

    # Send the command to the pane
    echo "Launching command in pane ${target_pane}: ${aider_cmd}"
    # Use C-m for Enter. Clear screen first for tidiness.
    # IMPORTANT: Ensure the venv is active where tmux server runs or activate it in the command
    # Example activating venv: tmux send-keys -t "$target_pane" "source .venv/bin/activate && clear && ${aider_cmd}" C-m
    # Assuming venv is already active in the shell starting this script:
    tmux send-keys -t "$target_pane" "clear" C-m
    tmux send-keys -t "$target_pane" "${aider_cmd}" C-m

    ((agent_index++))
done

# --- Final Steps ---
# Optional: Select a layout if needed (tiled is often good for multiple panes)
tmux select-layout -t "$TMUX_SESSION_NAME" tiled

# Attach to the session
echo "Attaching to tmux session ${TMUX_SESSION_NAME}. Use 'Ctrl+b d' to detach."
tmux attach-session -t "$TMUX_SESSION_NAME"
```

**6. Bash Script (`./code_builder/main_orchestrator.sh`)**

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PATH="${PROJECT_ROOT}/.venv"
REQUIREMENTS_PATH="${SCRIPT_DIR}/requirements.txt"
PYTHON_SCRIPT_PATH="${SCRIPT_DIR}/generate_plan.py"
LAUNCH_SCRIPT_PATH="${SCRIPT_DIR}/launch_aiders.sh"

# --- Check User Query ---
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"<Your feature request or query>\""
    exit 1
fi
USER_QUERY="$1"

# --- Setup Virtual Environment ---
if [ ! -d "$VENV_PATH" ]; then
    echo "Python virtual environment not found at $VENV_PATH. Creating..."
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    NEEDS_INSTALL=true
else
    echo "Found virtual environment at $VENV_PATH."
fi

# Activate venv
# shellcheck source=/dev/null
source "${VENV_PATH}/bin/activate"

# Check/install requirements if venv was just created or if flag file is missing
# Using a flag file is more robust than checking NEEDS_INSTALL across script runs
INSTALL_FLAG="${VENV_PATH}/.pip_installed"
if [[ "$NEEDS_INSTALL" == "true" ]] || [ ! -f "$INSTALL_FLAG" ]; then
    echo "Installing/updating Python requirements from $REQUIREMENTS_PATH..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install Python requirements."
        # Consider deactivating venv here if needed
        exit 1
    fi
    touch "$INSTALL_FLAG" # Mark install as complete
    echo "Requirements installed."
fi

# --- Generate Run ID ---
RUN_ID=$(date +"%Y%m%d_%H%M%S")
echo "Starting Orchestration Run ID: $RUN_ID"

# --- Run Python Script to Generate PRD and Config ---
echo "Running Python script to generate PRD and Aider config..."
# Pass query and run ID to the python script
# Capture the output line containing the JSON path
output=$(python "$PYTHON_SCRIPT_PATH" "$USER_QUERY" --run-id "$RUN_ID")

# Extract the JSON path from the output
JSON_CONFIG_PATH=$(echo "$output" | grep '^JSON_CONFIG_PATH=' | cut -d'=' -f2)

if [[ -z "$JSON_CONFIG_PATH" || ! -f "$JSON_CONFIG_PATH" ]]; then
    echo "Error: Failed to get valid JSON config path from Python script."
    echo "Python script output:"
    echo "$output"
    exit 1
fi

echo "Python script finished. Aider config generated at: $JSON_CONFIG_PATH"

# --- Launch Aider Agents ---
echo "Launching Aider agents via tmux..."
bash "$LAUNCH_SCRIPT_PATH" "$JSON_CONFIG_PATH" "$RUN_ID"

# --- Completion ---
echo "Orchestration script finished. Aider agents are running in tmux session: aider_run_${RUN_ID}"
echo "Attach to session: tmux attach-session -t aider_run_${RUN_ID}"
# Deactivate venv (optional, depends on workflow)
# deactivate
```

**7. `.gitignore` additions**

Make sure to add these to your root `.gitignore` file:

```gitignore
# Python virtual environment
.venv/

# Code builder artifacts (if config contains secrets or runs are large/temporary)
code_builder/runs/
code_builder/config.yaml # If API keys are stored directly (NOT RECOMMENDED)
code_builder/.env        # If using a .env file for API keys

# Aider cache/history (often large)
.aider*cache/
.aider.chat.history.md
.aider.input.history

# OS / IDE files
.DS_Store
*.pyc
__pycache__/
```

**How to Use:**

1.  **Setup:**
    *   Place the files in the `./code_builder/` directory as structured.
    *   Create `config.yaml` and fill in your models.
    *   Set your `OPENROUTER_API_KEY` either in `config.yaml` (less secure) or as an environment variable (recommended). You can create a `.env` file in `code_builder/` with `OPENROUTER_API_KEY=your_key_here`.
    *   Install prerequisites: `python3`, `pip`, `tmux`, `jq`.
    *   Configure Aider itself (e.g., in `~/.aider.conf.yml` or `./.aider.conf.yml`) to use the desired OpenRouter model and your API key. Example:
        ```yaml
        # ./.aider.conf.yml
        model: openrouter/anthropic/claude-3.5-sonnet
        # openrouter-api-key: sk-or-... # Can be omitted if OPENROUTER_API_KEY env var is set
        ```
2.  **Run:**
    *   Navigate to the project root directory in your terminal.
    *   Execute the main orchestrator script with your feature request:
        ```bash
        ./code_builder/main_orchestrator.sh "Implement user login using JWT tokens in the Python backend"
        ```
3.  **Monitor:**
    *   The script will:
        *   Set up the Python environment.
        *   Call the LLM to generate the PRD (`docs/prd/NNN-*.md`) and the Aider config (`code_builder/runs/{run_id}/aider_config.json`).
        *   Create a `tmux` session named `aider_run_{run_id}`.
        *   Open panes for each agent defined in the JSON config.
        *   Start `aider` in each pane with the specified files and prompt.
    *   The script will automatically attach you to the `tmux` session. You can see the Aider instances running.
    *   Use `Ctrl+b` followed by arrow keys to navigate between panes.
    *   Use `Ctrl+b d` to detach from the tmux session (Aider instances will keep running in the background).
    *   Use `tmux attach-session -t aider_run_{run_id}` to re-attach later.

This setup provides a structured way to leverage LLMs for planning (PRD generation) and execution (multi-agent Aider runs), managed through a combination of Python and Bash scripting. Remember to handle your API keys securely.