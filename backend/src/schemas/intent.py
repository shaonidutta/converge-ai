"""
Intent Classification Schemas

Pydantic models for intent classification request/response.
"""

import json
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator, model_validator
from src.nlp.intent.config import IntentType, EntityType


class IntentResult(BaseModel):
    """Single intent classification result"""

    model_config = {
        "extra": "ignore",  # Ignore extra fields to allow LLM flexibility
        "json_schema_extra": {
            "example": {
                "intent": "booking_management",
                "confidence": 0.95,
                "entities_json": "{\"action\": \"book\", \"service_type\": \"ac\", \"date\": \"2025-10-10\"}"
            }
        }
    }

    @model_validator(mode='before')
    @classmethod
    def handle_entities_field(cls, data: Any) -> Any:
        """Convert LLM's 'entities' field to 'entities_json' if needed"""
        if isinstance(data, dict) and 'entities' in data and 'entities_json' not in data:
            entities_value = data.pop('entities')  # Remove entities field
            if entities_value is not None:
                if isinstance(entities_value, dict):
                    data['entities_json'] = json.dumps(entities_value) if entities_value else None
                elif isinstance(entities_value, list):
                    # Handle list format like ['plumbing']
                    if entities_value and len(entities_value) == 1 and isinstance(entities_value[0], str):
                        data['entities_json'] = json.dumps({"service_type": entities_value[0]})
                    elif entities_value:
                        data['entities_json'] = json.dumps({"values": entities_value})
                    else:
                        data['entities_json'] = None
                elif isinstance(entities_value, str):
                    data['entities_json'] = entities_value if entities_value else None
                else:
                    data['entities_json'] = None
            else:
                data['entities_json'] = None
        return data

    intent: str = Field(..., description="Detected intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)")
    entities_json: Optional[str] = Field(default=None, description="Extracted entities as JSON string (optional)")

    @field_validator('entities_json', mode='before')
    @classmethod
    def validate_entities_json(cls, v: Any) -> Optional[str]:
        """Convert entities dict to JSON string"""
        if v is None or v == '' or v == 'null':
            return None
        if isinstance(v, dict):
            if not v:  # Empty dict
                return None
            return json.dumps(v)
        if isinstance(v, str):
            return v if v else None
        return None

    @property
    def entities(self) -> Dict[str, Any]:
        """Get entities as dict"""
        if self.entities_json:
            try:
                return json.loads(self.entities_json)
            except:
                return {}
        return {}


class IntentClassificationResult(BaseModel):
    """
    Complete intent classification result with multiple intents.

    This is the structured output schema used by the LLM.
    """

    model_config = {
        "extra": "ignore",  # Ignore extra fields to allow LLM flexibility
        "json_schema_extra": {
            "example": {
                "intents": [
                    {
                        "intent": "booking_management",
                        "confidence": 0.9,
                        "entities_json": "{\"action\": \"book\", \"service_type\": \"ac\"}"
                    },
                    {
                        "intent": "pricing_inquiry",
                        "confidence": 0.85,
                        "entities_json": "{\"service_type\": \"ac\"}"
                    }
                ],
                "primary_intent": "booking_management",
                "requires_clarification": False,
                "clarification_reason": None
            }
        }
    }

    @model_validator(mode='before')
    @classmethod
    def handle_intents_entities(cls, data: Any) -> Any:
        """Convert LLM's 'entities' fields in intents array to 'entities_json'"""
        if isinstance(data, dict) and 'intents' in data:
            intents = data['intents']
            if isinstance(intents, list):
                for intent_item in intents:
                    if isinstance(intent_item, dict) and 'entities' in intent_item and 'entities_json' not in intent_item:
                        entities_value = intent_item.pop('entities')
                        if entities_value is not None:
                            if isinstance(entities_value, dict):
                                intent_item['entities_json'] = json.dumps(entities_value) if entities_value else None
                            elif isinstance(entities_value, list):
                                if entities_value and len(entities_value) == 1 and isinstance(entities_value[0], str):
                                    intent_item['entities_json'] = json.dumps({"service_type": entities_value[0]})
                                elif entities_value:
                                    intent_item['entities_json'] = json.dumps({"values": entities_value})
                                else:
                                    intent_item['entities_json'] = None
                            elif isinstance(entities_value, str):
                                intent_item['entities_json'] = entities_value if entities_value else None
                            else:
                                intent_item['entities_json'] = None
                        else:
                            intent_item['entities_json'] = None
        return data

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
    context_used: bool = Field(
        default=False,
        description="Whether conversation context was used for classification"
    )
    context_summary: Optional[str] = Field(
        default=None,
        description="Summary of context used (e.g., '3 previous messages, active dialog state')"
    )


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
    classification_method: str = Field(..., description="Method used (pattern_match, llm, context_aware_llm, fallback)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    context_used: bool = Field(default=False, description="Whether conversation context was used")
    context_summary: Optional[str] = Field(default=None, description="Summary of context used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to book AC service and know the price",
                "intents": [
                    {
                        "intent": "booking_management",
                        "confidence": 0.9,
                        "entities_json": "{\"action\": \"book\", \"service_type\": \"ac\"}"
                    },
                    {
                        "intent": "pricing_inquiry",
                        "confidence": 0.85,
                        "entities_json": "{\"service_type\": \"ac\"}"
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

