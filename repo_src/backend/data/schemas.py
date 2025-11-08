from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    """Schema for creating a new item"""
    pass

class ItemUpdate(BaseModel):
    """Schema for updating an existing item"""
    name: Optional[str] = None
    description: Optional[str] = None

class ItemResponse(ItemBase):
    """Schema for returning item data in responses"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Updated from orm_mode for Pydantic V2 compatibility

# Chat-related schemas for OpenRouter integration
class ChatRequest(BaseModel):
    """Schema for chat requests to the LLM"""
    prompt: str
    system_message: Optional[str] = "You are a helpful assistant."
    model: Optional[str] = None
    max_tokens: Optional[int] = 2048
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    """Schema for chat responses from the LLM"""
    response: str
    model_used: str 