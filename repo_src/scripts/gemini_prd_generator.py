#!/usr/bin/env python3
"""
Gemini PRD Generator

This script:
1. Runs git dump to capture repository context
2. Sends the context to Google Gemini API with a prompt to create a PRD
3. Saves the response in the docs/guides directory
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
import requests
import time

# Determine project root directory
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Available Gemini models with their API versions
GEMINI_MODELS = {
    "gemini-1.5-pro": {
        "description": "Gemini 1.5 Pro - Balanced performance model",
        "api_version": "v1"
    },
    "gemini-2.5-pro-preview-03-25": {
        "description": "Gemini 2.5 Pro Preview - Advanced reasoning and coding capabilities",
        "api_version": "v1"
    },
    "gemini-2.5-flash-preview-04-17": {
        "description": "Gemini 2.5 Flash Preview - Optimized for adaptive thinking and cost efficiency",
        "api_version": "v1"
    }
}

def load_env_file():
    """Load environment variables from .env file in the scripts directory"""
    env_path = SCRIPT_DIR / ".env"
    
    if env_path.exists():
        print(f"Loading environment variables from {env_path}")
        with open(env_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        return True
    else:
        print(f"Warning: No .env file found at {env_path}")
        return False

def run_git_dump():
    """Run git dump script and verify the output file exists"""
    repo_context_path = PROJECT_ROOT / "repo_context.txt"
    
    print(f"Running git dump script...")
    try:
        subprocess.run(["git", "dump"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running git dump: {e}")
        sys.exit(1)
    
    if not repo_context_path.exists():
        print(f"Error: Expected repo_context.txt not found at {repo_context_path}")
        sys.exit(1)
    
    print(f"Git dump successful, context saved to {repo_context_path}")
    return repo_context_path

def send_to_gemini(repo_context_path, prompt, api_key, model_name="gemini-1.5-pro"):
    """Send repository context and prompt to Gemini API"""
    
    # Read the repository context
    with open(repo_context_path, 'r') as file:
        repo_context = file.read()
    
    # Construct the full prompt
    full_prompt = f"{prompt}\n\nRepository Context:\n{repo_context}"
    
    # Get the appropriate API version for the selected model
    api_version = GEMINI_MODELS[model_name]["api_version"]
    
    # Set up the API request
    url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": 8192
        }
    }
    
    # Add API key as query parameter
    params = {
        "key": api_key
    }
    
    print(f"Sending request to Gemini API using model: {model_name} (API version: {api_version})...")
    response = requests.post(url, headers=headers, json=data, params=params)
    
    if response.status_code != 200:
        print(f"Error from Gemini API: {response.status_code}")
        print(response.text)
        sys.exit(1)
    
    response_data = response.json()
    
    # Extract the generated text from the response
    try:
        generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        return generated_text
    except (KeyError, IndexError) as e:
        print(f"Error parsing Gemini API response: {e}")
        print(f"Response: {response_data}")
        sys.exit(1)

def save_to_guides(content, filename):
    """Save the generated PRD to the docs/guides directory"""
    guides_dir = PROJECT_ROOT / "docs" / "guides"
    
    # Create the guides directory if it doesn't exist
    guides_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure the filename has the .md extension
    if not filename.endswith(".md"):
        filename = f"{filename}.md"
    
    output_path = guides_dir / filename
    
    with open(output_path, 'w') as file:
        file.write(content)
    
    print(f"PRD saved to {output_path}")
    return output_path

def main():
    # Load environment variables from .env file
    load_env_file()
    
    parser = argparse.ArgumentParser(description="Generate PRD using Gemini API based on git repository context")
    parser.add_argument("--prompt", required=True, help="The prompt to send to Gemini API")
    parser.add_argument("--filename", required=True, help="Name of the output file (will be saved in docs/guides)")
    parser.add_argument("--api-key", help="Google API key for Gemini (if not provided, will use GOOGLE_API_KEY env var)")
    
    # Add model selection argument
    model_choices = list(GEMINI_MODELS.keys())
    default_model = "gemini-1.5-pro"
    
    # Create model help text from the dictionary
    model_help = f"Gemini model to use (default: {default_model}). Available models:\n"
    for model, info in GEMINI_MODELS.items():
        model_help += f"  - {model}: {info['description']} (API version: {info['api_version']})\n"
    
    parser.add_argument("--model", choices=model_choices, default=default_model, help=model_help)
    
    args = parser.parse_args()
    
    # Get API key from args or environment variable
    api_key = args.api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Google API key is required. Provide it with --api-key or set GOOGLE_API_KEY environment variable.")
        sys.exit(1)
    
    # Display selected model
    print(f"Using model: {args.model} - {GEMINI_MODELS[args.model]['description']}")
    
    # Run the workflow
    repo_context_path = run_git_dump()
    generated_content = send_to_gemini(repo_context_path, args.prompt, api_key, args.model)
    output_path = save_to_guides(generated_content, args.filename)
    
    print(f"✅ PRD generation complete!")
    print(f"Output file: {output_path}")

if __name__ == "__main__":
    main() 