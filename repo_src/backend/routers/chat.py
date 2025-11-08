from fastapi import APIRouter, HTTPException, status
import os

from repo_src.backend.data.schemas import ChatRequest, ChatResponse
from repo_src.backend.llm_chat.llm_interface import ask_llm

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def handle_chat_request(request: ChatRequest):
    """
    Receives a user prompt and sends it to OpenRouter LLM.
    Returns the LLM's response.

    Args:
        request: ChatRequest containing the prompt and optional parameters

    Returns:
        ChatResponse with the LLM's response and model used
    """
    try:
        # Get the model to use (from request or default)
        model_used = request.model or os.getenv("OPENROUTER_MODEL_NAME", "anthropic/claude-3.5-sonnet")

        # Call the LLM
        response_text = await ask_llm(
            prompt_text=request.prompt,
            system_message=request.system_message,
            model_override=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        # Check if the response is an error message
        if response_text.startswith("Error:"):
            raise HTTPException(
                status_code=500,
                detail=response_text
            )

        return ChatResponse(
            response=response_text,
            model_used=model_used
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@router.get("/models")
async def get_available_models():
    """
    Returns a list of commonly used OpenRouter models.
    For a complete list, visit: https://openrouter.ai/models
    """
    return {
        "models": [
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "description": "Most intelligent model, best for complex tasks"
            },
            {
                "id": "anthropic/claude-3-haiku",
                "name": "Claude 3 Haiku",
                "description": "Fast and cost-effective for simpler tasks"
            },
            {
                "id": "openai/gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "OpenAI's most capable model"
            },
            {
                "id": "openai/gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and cost-effective OpenAI model"
            },
            {
                "id": "meta-llama/llama-3.1-70b-instruct",
                "name": "Llama 3.1 70B",
                "description": "Open-source model from Meta"
            }
        ]
    }
