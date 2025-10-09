"""
Dialog State Schemas

Pydantic models for dialog state management request/response.
"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime

from src.core.models.dialog_state import DialogStateType


class DialogStateBase(BaseModel):
    """Base schema for dialog state"""
    
    session_id: str = Field(..., description="Session identifier")
    state: DialogStateType = Field(..., description="Current conversation state")
    intent: Optional[str] = Field(None, description="Current intent being processed")
    collected_entities: Dict[str, Any] = Field(
        default_factory=dict,
        description="Entities collected so far"
    )
    needed_entities: List[str] = Field(
        default_factory=list,
        description="Entities still needed"
    )
    pending_action: Optional[Dict[str, Any]] = Field(
        None,
        description="Action waiting to be executed"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context information"
    )


class DialogStateCreate(DialogStateBase):
    """Schema for creating a new dialog state"""
    
    user_id: int = Field(..., description="User ID", gt=0)
    expires_in_hours: int = Field(
        default=24,
        description="Hours until state expires",
        ge=1,
        le=168  # Max 1 week
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "session_id": "session_abc123",
                "state": "collecting_info",
                "intent": "booking_management",
                "collected_entities": {
                    "service_type": "ac",
                    "action": "book",
                    "city": "Mumbai"
                },
                "needed_entities": ["date", "time", "ac_type"],
                "pending_action": None,
                "context": {
                    "last_question": "What type of AC do you have?",
                    "attempt_count": 1
                },
                "expires_in_hours": 24
            }
        }


class DialogStateUpdate(BaseModel):
    """Schema for updating an existing dialog state"""
    
    state: Optional[DialogStateType] = Field(None, description="New state")
    intent: Optional[str] = Field(None, description="New intent")
    collected_entities: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated collected entities (merges with existing)"
    )
    needed_entities: Optional[List[str]] = Field(
        None,
        description="Updated needed entities (replaces existing)"
    )
    pending_action: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated pending action"
    )
    context: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated context (merges with existing)"
    )
    expires_in_hours: Optional[int] = Field(
        None,
        description="New expiration time in hours",
        ge=1,
        le=168
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "state": "awaiting_confirmation",
                "collected_entities": {
                    "date": "2025-10-10",
                    "time": "14:00"
                },
                "needed_entities": [],
                "pending_action": {
                    "action": "create_booking",
                    "params": {
                        "service_id": 123,
                        "user_id": 456,
                        "date": "2025-10-10",
                        "time": "14:00"
                    }
                },
                "context": {
                    "last_question": "Shall I book AC servicing for Oct 10 at 2 PM?",
                    "attempt_count": 2
                }
            }
        }


class DialogStateResponse(DialogStateBase):
    """Schema for dialog state response"""
    
    id: int = Field(..., description="Dialog state ID")
    user_id: int = Field(..., description="User ID")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "session_id": "session_abc123",
                "state": "collecting_info",
                "intent": "booking_management",
                "collected_entities": {
                    "service_type": "ac",
                    "action": "book",
                    "city": "Mumbai"
                },
                "needed_entities": ["date", "time", "ac_type"],
                "pending_action": None,
                "context": {
                    "last_question": "What type of AC do you have?",
                    "attempt_count": 1
                },
                "expires_at": "2025-10-10T14:00:00Z",
                "created_at": "2025-10-09T14:00:00Z",
                "updated_at": "2025-10-09T14:00:00Z"
            }
        }


class DialogStateStatus(BaseModel):
    """Schema for dialog state status check"""
    
    has_active_state: bool = Field(..., description="Whether an active state exists")
    state: Optional[DialogStateResponse] = Field(None, description="Active state if exists")
    is_follow_up_likely: bool = Field(
        ...,
        description="Whether next message is likely a follow-up"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "has_active_state": True,
                "state": {
                    "id": 1,
                    "user_id": 123,
                    "session_id": "session_abc123",
                    "state": "collecting_info",
                    "intent": "booking_management",
                    "collected_entities": {"city": "Mumbai"},
                    "needed_entities": ["date", "time"],
                    "pending_action": None,
                    "context": {"last_question": "What date works for you?"},
                    "expires_at": "2025-10-10T14:00:00Z",
                    "created_at": "2025-10-09T14:00:00Z",
                    "updated_at": "2025-10-09T14:00:00Z"
                },
                "is_follow_up_likely": True
            }
        }


class EntityUpdate(BaseModel):
    """Schema for updating a single entity"""
    
    entity_name: str = Field(..., description="Name of the entity")
    entity_value: Any = Field(..., description="Value of the entity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity_name": "date",
                "entity_value": "2025-10-10"
            }
        }


class FollowUpDetectionResult(BaseModel):
    """Schema for follow-up detection result"""
    
    is_follow_up: bool = Field(..., description="Whether message is a follow-up")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    reason: str = Field(..., description="Reason for the decision")
    expected_entity: Optional[str] = Field(
        None,
        description="Entity type expected in follow-up"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_follow_up": True,
                "confidence": 0.95,
                "reason": "Active dialog state exists, message is short (1 word), matches expected entity type (date)",
                "expected_entity": "date"
            }
        }

