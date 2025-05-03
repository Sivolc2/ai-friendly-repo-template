import yaml
import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
import importlib.metadata
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()

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
    temperature = llm_config.get('temperature', 0.7)
    # Add other common parameters if needed (top_p, top_k)

    logger.info(f"Calling LLM: {llm_name} (Model: {model_name})")
    # logger.debug(f"Prompt: {prompt[:500]}...") # Log beginning of prompt

    try:
        if llm_type == 'gemini':
            # For Gemini
            import google.generativeai as genai
            max_tokens = llm_config.get('max_output_tokens', 8192)
            
            # Assumes client is the Gemini model object
            response = client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=temperature,
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
            # For OpenAI
            max_tokens = llm_config.get('max_tokens', 4096)
            
            # Assumes client is the OpenAI client object
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content

        elif llm_type == 'anthropic':
            # For Anthropic
            max_tokens = llm_config.get('max_tokens', 4096)
            
            # Assumes client is the Anthropic client object
            response = client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
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
        if hasattr(e, 'response'): 
            logger.error(f"API Response: {e.response}")
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
            if result.stdout and len(result.stdout) > 0:
                logger.debug(f"Command stdout: {result.stdout[:500]}...")
            if result.stderr and len(result.stderr) > 0:
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

def get_file_size_info(file_paths: List[str]) -> Dict[str, Dict[str, Union[int, str]]]:
    """Calculate size information for a list of files.
    
    Args:
        file_paths: List of file paths to calculate size for
        
    Returns:
        Dictionary with file paths as keys and size info dictionaries as values
    """
    file_info = {}
    total_size = 0
    
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists() or not path.is_file():
            continue
            
        size_bytes = path.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        else:
            size_str = f"{size_kb:.2f} KB"
            
        file_info[file_path] = {
            "size_bytes": size_bytes,
            "size_str": size_str
        }
        total_size += size_bytes
        
    # Add total size info
    total_kb = total_size / 1024
    total_mb = total_kb / 1024
    total_size_str = f"{total_mb:.2f} MB" if total_mb >= 1 else f"{total_kb:.2f} KB"
    
    return {
        "files": file_info,
        "total": {
            "size_bytes": total_size,
            "size_str": total_size_str
        }
    }

def confirm_action(prompt_text: str, default: bool = True) -> bool:
    """Asks the user to confirm an action with a yes/no prompt.
    
    Args:
        prompt_text: The text to display when asking for confirmation
        default: The default answer if the user just presses Enter
        
    Returns:
        True if the user confirmed, False otherwise
    """
    valid_responses = {
        'y': True, 'yes': True, 'ye': True,
        'n': False, 'no': False
    }
    
    default_str = "Y/n" if default else "y/N"
    prompt = f"{prompt_text} [{default_str}]: "
    
    while True:
        response = input(prompt).lower()
        
        if response == '':
            return default
            
        if response in valid_responses:
            return valid_responses[response]
            
        print("Please respond with 'yes' or 'no' (or 'y' or 'n').") 