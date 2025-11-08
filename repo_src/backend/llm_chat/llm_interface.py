import os
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME", "anthropic/claude-3.5-sonnet")

# These are optional but recommended for OpenRouter tracking
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "http://localhost:5173")
YOUR_APP_NAME = os.getenv("YOUR_APP_NAME", "AI-Friendly Repo Template")

def _get_current_datetime() -> str:
    """Get the current date and time formatted for system prompts"""
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY not found in .env file. LLM calls will fail.")

client = None
if OPENROUTER_API_KEY:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

async def ask_llm(
    prompt_text: str,
    system_message: str = "You are a helpful assistant.",
    model_override: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.7
) -> str:
    """
    Sends a prompt to the configured LLM via OpenRouter and returns the response.

    Args:
        prompt_text: The user prompt to send to the LLM
        system_message: The system message to set context for the LLM
        model_override: Optional model to use instead of the default
        max_tokens: Maximum tokens in the response (default: 2048)
        temperature: Sampling temperature 0-1 (default: 0.7)

    Returns:
        The LLM's response text, or an error message if the call fails
    """
    if not client:
        return "Error: OpenRouter client not initialized. Is OPENROUTER_API_KEY set in .env?"

    model_to_use = model_override or DEFAULT_MODEL_NAME

    # Add current date/time to system message if not already present
    if "Current date and time:" not in system_message:
        current_datetime = _get_current_datetime()
        system_message = f"Current date and time: {current_datetime}\n\n{system_message}"

    try:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt_text}
        ]

        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_APP_NAME
            }
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenRouter API with model {model_to_use}: {e}")
        return f"Error: Failed to get response from LLM. Details: {str(e)}"
