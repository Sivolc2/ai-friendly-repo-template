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
    """Loads configuration from config.yaml and environment variables"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            
            # Load API key from environment, with priority to .env file
            load_dotenv(dotenv_path=SCRIPT_DIR / '.env') # Load .env file if it exists
            
            # Get API key from environment variable
            config['openrouter_api_key'] = os.environ.get('OPENROUTER_API_KEY')
            
            if not config.get('openrouter_api_key'):
                raise ValueError("OpenRouter API key not found in environment. Please set OPENROUTER_API_KEY in your environment or in code_builder/.env file.")
            
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