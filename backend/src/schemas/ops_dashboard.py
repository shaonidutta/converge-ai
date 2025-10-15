"""
Pydantic schemas for Ops Dashboard APIs
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class RelatedEntitySummary(BaseModel):
    """
    Summary information for related entity (default response)
    
    Lightweight response with essential info only.
    Used when expand=false (default).
    """
    type: str = Field(..., description="Entity type: complaint, booking, refund, etc.")
    id: int = Field(..., description="Entity ID")
    status: str = Field(..., description="Entity status")
    priority: Optional[str] = Field(None, description="Priority level (if applicable)")
    sla_breach_risk: bool = Field(False, description="SLA breach risk flag")
    response_due_at: Optional[datetime] = Field(None, description="Response due time (if applicable)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "complaint",
                "id": 456,
                "status": "open",
                "priority": "high",
                "sla_breach_risk": True,
                "response_due_at": "2025-10-15T14:30:00Z"
            }
        }


class RelatedEntityFull(BaseModel):
    """
    Full details for related entity (expand=true)
    
    Comprehensive response with all available details.
    Used when expand=true.
    """
    type: str = Field(..., description="Entity type: complaint, booking, refund, etc.")
    id: int = Field(..., description="Entity ID")
    status: str = Field(..., description="Entity status")
    priority: Optional[str] = Field(None, description="Priority level (if applicable)")
    sla_breach_risk: bool = Field(False, description="SLA breach risk flag")
    response_due_at: Optional[datetime] = Field(None, description="Response due time (if applicable)")
    resolution_due_at: Optional[datetime] = Field(None, description="Resolution due time (if applicable)")
    
    # Additional details (varies by entity type)
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional entity-specific details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "complaint",
                "id": 456,
                "status": "open",
                "priority": "high",
                "sla_breach_risk": True,
                "response_due_at": "2025-10-15T14:30:00Z",
                "resolution_due_at": "2025-10-16T10:30:00Z",
                "details": {
                    "subject": "Poor service quality",
                    "complaint_type": "service_quality",
                    "assigned_to_staff_id": 10,
                    "assigned_to_staff_name": "Jane Smith",
                    "booking_id": 789
                }
            }
        }


class PriorityQueueItem(BaseModel):
    """
    Priority queue item response
    
    Represents a single item in the ops priority queue.
    PII fields (user_name, user_mobile, user_email) are conditionally
    included based on staff permissions (ops.full_access).
    """
    id: int = Field(..., description="Priority queue item ID")
    user_id: int = Field(..., description="Customer user ID")
    
    # PII fields - conditionally included based on permissions
    user_name: Optional[str] = Field(None, description="Customer name (redacted without ops.full_access)")
    user_mobile: Optional[str] = Field(None, description="Customer mobile (redacted without ops.full_access)")
    user_email: Optional[str] = Field(None, description="Customer email (redacted without ops.full_access)")
    
    session_id: str = Field(..., description="Conversation session ID")
    intent_type: str = Field(..., description="Intent type: complaint, refund, cancellation, booking")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Intent classification confidence (0-1)")
    priority_score: int = Field(..., ge=0, le=100, description="Priority score (0-100, higher = more urgent)")
    sentiment_score: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")
    message_snippet: Optional[str] = Field(None, description="Message snippet (truncated without ops.full_access)")
    
    # Review status
    is_reviewed: bool = Field(..., description="Whether item has been reviewed")
    reviewed_by_staff_id: Optional[int] = Field(None, description="Staff ID who reviewed")
    reviewed_by_staff_name: Optional[str] = Field(None, description="Staff name who reviewed")
    reviewed_at: Optional[datetime] = Field(None, description="Review timestamp")
    action_taken: Optional[str] = Field(None, description="Action taken during review")
    
    # Timestamps
    created_at: datetime = Field(..., description="Item creation timestamp")
    updated_at: datetime = Field(..., description="Item last update timestamp")
    
    # Related entity (summary or full based on expand parameter)
    related_entity: Optional[Union[RelatedEntitySummary, RelatedEntityFull]] = Field(
        None, 
        description="Related entity info (complaint, booking, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "user_name": "John Doe",
                "user_mobile": "9876543210",
                "user_email": "john@example.com",
                "session_id": "sess_abc123",
                "intent_type": "complaint",
                "confidence_score": 0.95,
                "priority_score": 85,
                "sentiment_score": -0.75,
                "message_snippet": "Very disappointed with the service quality...",
                "is_reviewed": False,
                "reviewed_by_staff_id": None,
                "reviewed_by_staff_name": None,
                "reviewed_at": None,
                "action_taken": None,
                "created_at": "2025-10-15T10:30:00Z",
                "updated_at": "2025-10-15T10:30:00Z",
                "related_entity": {
                    "type": "complaint",
                    "id": 456,
                    "status": "open",
                    "priority": "high",
                    "sla_breach_risk": True,
                    "response_due_at": "2025-10-15T14:30:00Z"
                }
            }
        }


class PriorityQueueResponse(BaseModel):
    """
    Priority queue list response with pagination
    
    Returns a paginated list of priority queue items with metadata.
    """
    items: List[PriorityQueueItem] = Field(..., description="List of priority queue items")
    total: int = Field(..., ge=0, description="Total number of items matching filters")
    skip: int = Field(..., ge=0, description="Number of items skipped (pagination offset)")
    limit: int = Field(..., ge=1, le=100, description="Number of items per page")
    has_more: bool = Field(..., description="Whether more items are available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "user_name": "John Doe",
                        "user_mobile": "9876543210",
                        "user_email": "john@example.com",
                        "session_id": "sess_abc123",
                        "intent_type": "complaint",
                        "confidence_score": 0.95,
                        "priority_score": 85,
                        "sentiment_score": -0.75,
                        "message_snippet": "Very disappointed with the service quality...",
                        "is_reviewed": False,
                        "reviewed_by_staff_id": None,
                        "reviewed_by_staff_name": None,
                        "reviewed_at": None,
                        "action_taken": None,
                        "created_at": "2025-10-15T10:30:00Z",
                        "updated_at": "2025-10-15T10:30:00Z",
                        "related_entity": {
                            "type": "complaint",
                            "id": 456,
                            "status": "open",
                            "priority": "high",
                            "sla_breach_risk": True,
                            "response_due_at": "2025-10-15T14:30:00Z"
                        }
                    }
                ],
                "total": 45,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }


class PriorityQueueFilters(BaseModel):
    """
    Filters for priority queue queries
    
    Used internally for building database queries.
    """
    status: Optional[str] = None  # 'pending', 'reviewed', 'all'
    intent_type: Optional[str] = None
    priority_min: Optional[int] = None
    priority_max: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

