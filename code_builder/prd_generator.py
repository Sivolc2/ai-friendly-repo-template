#!/usr/bin/env python3
"""
Standalone PRD Generator

Usage:
  python standalone_prd.py "Your feature request"
  python standalone_prd.py "Your feature request" --context context_file1.md context_file2.md

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
DOCS_CONTEXT_DIR = PROJECT_ROOT / "docs" / "context"
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

def list_context_files():
    """List all available context files in the docs/context directory"""
    context_files = list(DOCS_CONTEXT_DIR.glob("*.md"))
    return context_files

def load_context_files(context_filenames):
    """Load the content from specified context files"""
    context_content = []
    missing_files = []
    
    for filename in context_filenames:
        # Check if it's a relative path or just a filename
        if '/' in filename:
            context_file = PROJECT_ROOT / filename
        else:
            context_file = DOCS_CONTEXT_DIR / filename
            
        if not context_file.exists():
            missing_files.append(str(context_file))
            continue
            
        try:
            with open(context_file, 'r') as f:
                content = f.read()
                context_content.append(f"--- Context from {context_file.name} ---\n{content}\n")
                print(f"Loaded context file: {context_file.name}")
        except Exception as e:
            print(f"Error loading context file {context_file.name}: {e}")
    
    # Exit with error if any specified context files were missing
    if missing_files:
        print(f"ERROR: The following context files were not found:")
        for missing in missing_files:
            print(f"  - {missing}")
        print("Please check the file paths and try again.")
        sys.exit(1)
        
    return "\n".join(context_content)

def get_repo_context():
    """Get a list of files in the repository for context"""
    try:
        repo_files = [str(p.relative_to(PROJECT_ROOT)) for p in PROJECT_ROOT.glob('**/*') if p.is_file() and
                      '.git' not in p.parts and
                      '.venv' not in p.parts and
                      'node_modules' not in p.parts and
                      '__pycache__' not in p.parts and
                      'dist' not in p.parts and
                      'build' not in p.parts]
        
        return "\nRelevant project files:\n" + "\n".join(sorted(repo_files)[:50])  # Limit to 50 files
    except Exception as e:
        print(f"Warning: Could not get repository file list: {e}")
        return "\nRepository context could not be generated."

def generate_prd(user_query, context_files=None):
    """Generate a PRD from the user query"""
    # Load configuration and API key
    config = load_config()
    api_key = load_api_key()
    
    # Get the model to use
    model = config.get('prd_generator_model', 'anthropic/claude-3-opus-20240229')
    
    # Get repository context
    repo_context = get_repo_context()
    print(f"Generated repository context with {len(repo_context.splitlines())} lines")
    
    # Get default context files from config
    default_context_files = config.get('default_context_files', [])
    if default_context_files is None:
        default_context_files = []
    
    # Combine user-specified and default context files, removing duplicates
    if context_files is None:
        context_files = []
    
    # Remove any duplicates while preserving order
    all_context_files = []
    seen = set()
    for file in context_files + default_context_files:
        if file not in seen:
            all_context_files.append(file)
            seen.add(file)
    
    # Load context files if specified
    additional_context = ""
    if all_context_files:
        additional_context = load_context_files(all_context_files)
        print(f"Loaded {len(all_context_files)} context files with total {len(additional_context)} characters")
    
    # Get the prompt template
    prd_prompt = config.get('prd_prompt', """
Please think through this request then implement the following feature:

User Query: "{user_query}"

{repo_context}
""")
    
    # Add context files to the template if not already handled in the config
    if additional_context and "{additional_context}" not in prd_prompt:
        prd_prompt += "\n\n--- Additional Context ---\n{additional_context}"
    
    # Format the prompt
    prompt = prd_prompt.format(
        user_query=user_query, 
        repo_context=repo_context,
        additional_context=additional_context
    )
    
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
    parser.add_argument('query', help='The feature request or query', nargs='?')
    parser.add_argument('--context', nargs='+', help='Additional context files to include (from docs/context/ or full path)')
    parser.add_argument('--list-context', action='store_true', help='List available context files and exit')
    
    args = parser.parse_args()
    
    # List context files and exit if requested
    if args.list_context:
        print("\nAvailable context files:")
        context_files = list_context_files()
        if context_files:
            for cf in context_files:
                print(f"  - {cf.name}")
        else:
            print("  No context files found in docs/context/")
        print("\nUsage example: python prd_generator.py \"Your feature request\" --context README_prd_maker.md")
        return
    
    # Ensure query is provided if not just listing context files
    if not args.query:
        parser.error("the following arguments are required: query")
    
    print(f"Generating PRD for query: {args.query}")
    
    if args.context:
        print(f"Using context files: {', '.join(args.context)}")
    
    # Generate the PRD
    prd_path = generate_prd(args.query, args.context)
    
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