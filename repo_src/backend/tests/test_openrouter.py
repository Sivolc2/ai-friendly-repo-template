"""
Test script for OpenRouter integration.

This test verifies that the OpenRouter LLM interface is working correctly
by sending a simple test prompt and checking the response.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from the project root .env file
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from repo_src.backend.llm_chat.llm_interface import ask_llm

async def test_basic_chat():
    """Test basic chat functionality with OpenRouter"""
    print("Testing OpenRouter integration...")
    print("-" * 50)

    # Test 1: Simple question
    print("\nTest 1: Simple question")
    response = await ask_llm(
        prompt_text="What is 2+2? Answer in one sentence.",
        system_message="You are a helpful math assistant.",
    )
    print(f"Response: {response}")

    # Test 2: Creative task
    print("\nTest 2: Creative task")
    response = await ask_llm(
        prompt_text="Write a haiku about coding.",
        system_message="You are a creative poetry assistant.",
    )
    print(f"Response: {response}")

    # Test 3: With XML-like tags (as mentioned in the template docs)
    print("\nTest 3: Structured prompt with XML-like tags")
    structured_prompt = """
<user_request>
Explain what FastAPI is in simple terms.
</user_request>

<instructions>
Keep your answer concise (2-3 sentences) and beginner-friendly.
</instructions>
"""
    response = await ask_llm(
        prompt_text=structured_prompt,
        system_message="You are a helpful programming tutor.",
    )
    print(f"Response: {response}")

    print("\n" + "-" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_basic_chat())
