"""
Intent Classification Schemas

Pydantic models for intent classification request/response.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator
from src.nlp.intent.config import IntentType, EntityType


class IntentResult(BaseModel):
    """Single intent classification result"""

    intent: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    entities: Dict[str, str] = Field(default_factory=dict, description="Extracted entities")

    @field_validator('entities', mode='before')
    @classmethod
    def validate_entities(cls, v: Any) -> Dict[str, str]:
        """Ensure entities is always a dict, even if LLM returns empty string"""
        if v is None or v == '' or v == 'null':
            return {}
        if isinstance(v, dict):
            return v
        return {}
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent": "booking_management",
                "confidence": 0.95,
                "entities": {
                    "action": "book",
                    "service_type": "ac",
                    "date": "2025-10-10"
                }
            }
        }


class IntentClassificationResult(BaseModel):
    """
    Complete intent classification result with multiple intents.
    
    This is the structured output schema used by the LLM.
    """
    
    intents: List[IntentResult] = Field(
        ...,
        description="List of all detected intents with confidence scores",
        min_length=1
    )
    primary_intent: str = Field(..., description="Primary intent (highest confidence)")
    requires_clarification: bool = Field(
        default=False,
        description="Whether the query requires clarification"
    )
    clarification_reason: Optional[str] = Field(
        default=None,
        description="Reason why clarification is needed"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "intents": [
                    {
                        "intent": "booking_management",
                        "confidence": 0.9,
                        "entities": {"action": "book", "service_type": "ac"}
                    },
                    {
                        "intent": "pricing_inquiry",
                        "confidence": 0.85,
                        "entities": {"service_type": "ac"}
                    }
                ],
                "primary_intent": "booking_management",
                "requires_clarification": False,
                "clarification_reason": None
            }
        }


class IntentClassificationRequest(BaseModel):
    """Request for intent classification"""
    
    message: str = Field(..., min_length=1, max_length=5000, description="User message to classify")
    user_id: Optional[int] = Field(default=None, description="User ID for context")
    session_id: Optional[str] = Field(default=None, description="Session ID for context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to book AC service and know the price",
                "user_id": 123,
                "session_id": "session_abc123"
            }
        }


class IntentClassificationResponse(BaseModel):
    """Response from intent classification"""
    
    message: str = Field(..., description="Original user message")
    intents: List[IntentResult] = Field(..., description="Detected intents")
    primary_intent: str = Field(..., description="Primary intent")
    requires_clarification: bool = Field(..., description="Whether clarification is needed")
    clarification_reason: Optional[str] = Field(default=None, description="Reason for clarification")
    classification_method: str = Field(..., description="Method used (pattern_match, llm, fallback)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to book AC service and know the price",
                "intents": [
                    {
                        "intent": "booking_management",
                        "confidence": 0.9,
                        "entities": {"action": "book", "service_type": "ac"}
                    },
                    {
                        "intent": "pricing_inquiry",
                        "confidence": 0.85,
                        "entities": {"service_type": "ac"}
                    }
                ],
                "primary_intent": "booking_management",
                "requires_clarification": False,
                "clarification_reason": None,
                "classification_method": "llm",
                "processing_time_ms": 450
            }
        }


class EntityExtractionResult(BaseModel):
    """Result of entity extraction"""
    
    entities: Dict[str, str] = Field(default_factory=dict, description="Extracted entities")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entities": {
                    "service_type": "ac",
                    "action": "book",
                    "date": "2025-10-10",
                    "time": "14:00"
                }
            }
        }

