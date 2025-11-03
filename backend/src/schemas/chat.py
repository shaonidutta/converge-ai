"""
Chat Schemas
Request/Response models for chat API
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# REQUEST MODELS
class ChatMessageRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID to continue conversation. If None, creates new session")
    channel: Optional[str] = Field("web", description="Channel: web, mobile, whatsapp")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to book an AC service",
                "session_id": "session_abc123",
                "channel": "web"
            }
        }


class ChatHistoryRequest(BaseModel):
    """Request to get chat history"""
    session_id: str = Field(..., description="Session ID")
    limit: Optional[int] = Field(50, ge=1, le=200, description="Number of messages to retrieve")
    skip: Optional[int] = Field(0, ge=0, description="Number of messages to skip")


# RESPONSE MODELS
class MessageResponse(BaseModel):
    """Single message in conversation"""
    id: int
    role: str  # "user" or "assistant"
    message: str
    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "role": "user",
                "message": "I want to book an AC service",
                "intent": "book_service",
                "intent_confidence": 0.95,
                "created_at": "2025-10-08T10:30:00Z"
            }
        }


class ChatMessageResponse(BaseModel):
    """Response after sending a message"""
    session_id: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    response_time_ms: int
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata including grounding_score, confidence, agent_used, etc.")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "user_message": {
                    "id": 1,
                    "role": "user",
                    "message": "I want to book an AC service",
                    "intent": "book_service",
                    "intent_confidence": 0.95,
                    "created_at": "2025-10-08T10:30:00Z"
                },
                "assistant_message": {
                    "id": 2,
                    "role": "assistant",
                    "message": "I can help you book an AC service...",
                    "intent": None,
                    "intent_confidence": None,
                    "created_at": "2025-10-08T10:30:01Z"
                },
                "response_time_ms": 1200,
                "metadata": {
                    "intent": "book_service",
                    "intent_confidence": 0.95,
                    "agent_used": "booking",
                    "classification_method": "pattern",
                    "grounding_score": 0.85,
                    "confidence": "high"
                }
            }
        }


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    session_id: str
    messages: List[MessageResponse]
    total: int

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "messages": [
                    {
                        "id": 1,
                        "role": "user",
                        "message": "Hello",
                        "intent": "greeting",
                        "intent_confidence": 0.98,
                        "created_at": "2025-10-08T10:30:00Z"
                    },
                    {
                        "id": 2,
                        "role": "assistant",
                        "message": "Hello! How can I help you?",
                        "intent": None,
                        "intent_confidence": None,
                        "created_at": "2025-10-08T10:30:01Z"
                    }
                ],
                "total": 2
            }
        }


class SessionResponse(BaseModel):
    """User's chat session"""
    session_id: str
    message_count: int
    last_message_at: datetime
    first_message_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "message_count": 10,
                "last_message_at": "2025-10-08T10:35:00Z",
                "first_message_at": "2025-10-08T10:30:00Z"
            }
        }

