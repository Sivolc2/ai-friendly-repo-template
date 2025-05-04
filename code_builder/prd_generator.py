#!/usr/bin/env python3
"""
Standalone PRD Generator

Usage:
  python standalone_prd.py "Your feature request"

This script assumes your environment is already set up with the required packages 
and the OpenRouter API key is available in the environment.
"""

import argparse
import yaml
import requests
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# --- Constants ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DOCS_PRD_DIR = PROJECT_ROOT / "docs" / "prd"
CONFIG_PATH = SCRIPT_DIR / "config.yaml"
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# --- Setup ---
print("Starting standalone PRD generator...")
DOCS_PRD_DIR.mkdir(parents=True, exist_ok=True)

# --- Helper Functions ---

def load_config():
    """Load configuration from config.yaml and environment variables"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
            print(f"Loaded configuration from {CONFIG_PATH}")
            return config
    except FileNotFoundError:
        print(f"Warning: Configuration file not found at {CONFIG_PATH}, using defaults")
        return {
            'prd_generator_model': 'anthropic/claude-3-opus-20240229'  # Default to a reliable model
        }
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return {
            'prd_generator_model': 'anthropic/claude-3-opus-20240229'  # Default to a reliable model
        }

def load_api_key():
    """Load API key from environment or .env file"""
    # Try loading from .env file first
    load_dotenv(dotenv_path=SCRIPT_DIR / '.env')
    
    # Get from environment
    api_key = os.environ.get('OPENROUTER_API_KEY')
    
    if not api_key:
        print("ERROR: No OpenRouter API key found!")
        print("Please set OPENROUTER_API_KEY in your environment or in code_builder/.env file")
        sys.exit(1)
    
    print("API key loaded successfully")
    return api_key

def find_next_prd_number():
    """Find the next sequential PRD number"""
    max_num = 0
    for f in DOCS_PRD_DIR.glob("[0-9][0-9][0-9]-*.md"):
        try:
            num = int(f.name[:3])
            if num > max_num:
                max_num = num
        except ValueError:
            continue
    return max_num + 1

def call_api(prompt, model, api_key):
    """Call the OpenRouter API without retries"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://example.com"  # Add a referer to reduce potential 403 errors
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    print(f"Calling OpenRouter API with model: {model}")
    print(f"Request prompt length: {len(prompt)} characters")
    
    # Save the request for debugging
    debug_file = DOCS_PRD_DIR / "last_request.json"
    try:
        with open(debug_file, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass  # Ignore errors writing debug file
    
    try:
        # Show a simple progress indicator
        print("Making API request...")
        sys.stdout.flush()
        
        # Use a longer timeout for slower models
        response = requests.post(
            OPENROUTER_API_ENDPOINT,
            headers=headers,
            json=data,
            timeout=600  # 10 minute timeout
        )
        
        # Print status code immediately
        print(f" Response status: {response.status_code}")
        
        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse the JSON response
        result = response.json()
        
        # Save the response for debugging
        debug_resp_file = DOCS_PRD_DIR / "last_response.json"
        try:
            with open(debug_resp_file, 'w') as f:
                json.dump(result, f, indent=2)
        except:
            pass  # Ignore errors writing debug file
        
        # Extract and return the text
        response_text = result['choices'][0]['message']['content']
        print(f"Received response ({len(response_text)} characters)")
        return response_text
        
    except requests.exceptions.Timeout:
        print(f"\nTimeout error. The request took too long to complete.")
        
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text[:500]}...")  # First 500 chars
            
    except Exception as e:
        print(f"\nError: {e}")
        traceback.print_exc()
    
    print("Failed to get a response from the API.")
    return None

def execute_git_dump():
    """Execute the git dump command to export repo contents to repo_contents.txt"""
    try:
        repo_contents_path = PROJECT_ROOT / 'repo_contents.txt'
        # Run the git dump command and save the output to repo_contents.txt
        os.system(f"git dump")
        print(f"Repository contents dumped to {repo_contents_path}")
    except Exception as e:
        print(f"Error executing git dump: {e}")

def get_repo_context():
    """Get repository context from repo_contents.txt"""
    try:
        # Ensure the repo_contents.txt is up-to-date
        execute_git_dump()
        repo_contents_path = PROJECT_ROOT / 'repo_contents.txt'
        with open(repo_contents_path, 'r') as f:
            repo_files = f.read()
        return "\nRelevant project files:\n" + repo_files
    except Exception as e:
        print(f"Warning: Could not get repository file list: {e}")
        return "\nRepository context could not be generated."

def generate_prd(user_query):
    """Generate a PRD from the user query"""
    # Load configuration and API key
    config = load_config()
    api_key = load_api_key()
    
    # Get the model to use
    model = config.get('prd_generator_model', 'anthropic/claude-3-opus-20240229')
    
    # Get repository context
    repo_context = get_repo_context()
    print(f"Generated repository context with {len(repo_context.splitlines())} lines")
    
    # Get the prompt template
    prd_prompt = config.get('prd_prompt', """
Please think through this request then implement the following feature:

User Query: "{user_query}"

{repo_context}
""")
    
    # Format the prompt
    prompt = prd_prompt.format(user_query=user_query, repo_context=repo_context)
    
    # Call the API
    response = call_api(prompt, model, api_key)
    
    if not response:
        print("Failed to generate PRD. API call unsuccessful.")
        return None
    
    # Generate a filename
    next_num = find_next_prd_number()
    prd_slug = "-".join(user_query.lower().split()[:5]).replace("/", "-")
    prd_slug = re.sub(r'[^a-z0-9-]', '', prd_slug)
    prd_filename = f"{next_num:03d}-{prd_slug}.md"
    prd_filepath = DOCS_PRD_DIR / prd_filename
    
    # Save the PRD
    try:
        with open(prd_filepath, 'w') as f:
            f.write(response)
        print(f"PRD saved to: {prd_filepath}")
        return prd_filepath
    except Exception as e:
        print(f"Error saving PRD: {e}")
        traceback.print_exc()
        return None

# --- Main Function ---

def main():
    parser = argparse.ArgumentParser(description='Generate a PRD from a feature request')
    parser.add_argument('query', help='The feature request or query')
    args = parser.parse_args()
    
    print(f"Generating PRD for query: {args.query}")
    
    # Generate the PRD
    prd_path = generate_prd(args.query)
    
    if prd_path:
        print("\nPRD generation successful!")
        print(f"PRD saved at: {prd_path}")
        
        # Try to open the file
        if sys.platform == 'darwin':  # macOS
            os.system(f"open '{prd_path}'")
        elif sys.platform.startswith('linux'):  # Linux
            os.system(f"xdg-open '{prd_path}'")
        else:
            print(f"You can view the PRD at: {prd_path}")
    else:
        print("\nPRD generation failed.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1) 