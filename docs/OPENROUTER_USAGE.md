# OpenRouter Integration Guide

This template includes OpenRouter integration for LLM functionality, based on the implementation from the exocortex project.

## Setup

1. **Environment Variables**: The `.env` file in the project root already contains your OpenRouter API key:
   ```bash
   OPENROUTER_API_KEY=sk-or-v1-...
   OPENROUTER_MODEL_NAME=anthropic/claude-3.5-sonnet
   YOUR_SITE_URL=http://localhost:5173
   YOUR_APP_NAME=AI-Friendly Repo Template
   ```

2. **Install Dependencies**: The required `openai` package is already installed.

## Components

### 1. LLM Interface (`repo_src/backend/llm_chat/llm_interface.py`)

The core interface for interacting with OpenRouter:

```python
from repo_src.backend.llm_chat.llm_interface import ask_llm

# Basic usage
response = await ask_llm(
    prompt_text="Your prompt here",
    system_message="You are a helpful assistant.",
    model_override="anthropic/claude-3.5-sonnet",  # Optional
    max_tokens=2048,
    temperature=0.7
)
```

### 2. Chat Router (`repo_src/backend/routers/chat.py`)

FastAPI endpoints for chat functionality:

- **POST `/api/chat/`**: Send a chat request
  ```json
  {
    "prompt": "What is FastAPI?",
    "system_message": "You are a helpful assistant.",
    "model": "anthropic/claude-3.5-sonnet",
    "max_tokens": 2048,
    "temperature": 0.7
  }
  ```

- **GET `/api/chat/models`**: Get list of available models

### 3. Schemas (`repo_src/backend/data/schemas.py`)

Pydantic models for request/response:
- `ChatRequest`: Input schema for chat requests
- `ChatResponse`: Output schema with response and model used

## XML-like Prompting

As documented in the exocortex template, you can use XML-like tags for structured prompts:

```python
structured_prompt = """
<user_request>
Explain what FastAPI is in simple terms.
</user_request>

<supporting_context>
  <example>
    FastAPI is used by companies like Netflix and Uber.
  </example>
</supporting_context>

<instructions>
Keep your answer concise (2-3 sentences) and beginner-friendly.
</instructions>
"""

response = await ask_llm(
    prompt_text=structured_prompt,
    system_message="You are a helpful programming tutor."
)
```

## Testing

Run the test suite to verify the integration:

```bash
python repo_src/backend/tests/test_openrouter.py
```

Test results show successful integration with:
- ✅ Simple question-answer
- ✅ Creative tasks (haiku generation)
- ✅ Structured prompts with XML-like tags

## Usage Examples

### Example 1: Direct Function Call

```python
from repo_src.backend.llm_chat.llm_interface import ask_llm

async def generate_story(user_prompt: str):
    response = await ask_llm(
        prompt_text=f"<user_request>{user_prompt}</user_request>",
        system_message="You are a creative storyteller.",
        temperature=0.8
    )
    return response
```

### Example 2: API Endpoint (Already Implemented)

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about coding",
    "system_message": "You are a creative poetry assistant."
  }'
```

### Example 3: Custom Router

Create your own router using the LLM interface:

```python
from fastapi import APIRouter
from repo_src.backend.llm_chat.llm_interface import ask_llm

router = APIRouter(prefix="/api/custom")

@router.post("/analyze")
async def analyze_code(code: str):
    response = await ask_llm(
        prompt_text=f"<code>{code}</code><task>Analyze this code</task>",
        system_message="You are a code review expert."
    )
    return {"analysis": response}
```

## Available Models

Common models available through OpenRouter:
- `anthropic/claude-3.5-sonnet` - Most intelligent, best for complex tasks
- `anthropic/claude-3-haiku` - Fast and cost-effective
- `openai/gpt-4-turbo` - OpenAI's most capable model
- `openai/gpt-3.5-turbo` - Fast and cost-effective
- `meta-llama/llama-3.1-70b-instruct` - Open-source from Meta

Get the full list at: https://openrouter.ai/models

## References

- Original implementation: `../../interactives/exocortex`
- Template document: `../../interactives/exocortex/repo_src/backend/documents/Templates - Openrouter + xml Prompting.md`
- OpenRouter API docs: https://openrouter.ai/docs
