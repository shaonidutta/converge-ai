"""
Operations Complaints API Schemas
Pydantic models for complaint management operations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from src.core.models.complaint import ComplaintType, ComplaintPriority, ComplaintStatus


class ComplaintSortBy(str, Enum):
    """Sort options for complaint listing"""
    CREATED_AT = "created_at"
    PRIORITY = "priority"
    STATUS = "status"
    RESPONSE_DUE_AT = "response_due_at"
    RESOLUTION_DUE_AT = "resolution_due_at"


class SortOrder(str, Enum):
    """Sort order options"""
    ASC = "asc"
    DESC = "desc"


class ComplaintListRequest(BaseModel):
    """Request model for listing complaints with filters"""
    
    # Filters
    status: Optional[str] = Field(None, description="Filter by status (open, in_progress, resolved, closed, escalated, all)")
    priority: Optional[str] = Field(None, description="Filter by priority (low, medium, high, critical, all)")
    complaint_type: Optional[str] = Field(None, description="Filter by complaint type")
    assigned_to: Optional[int] = Field(None, description="Filter by assigned staff ID")
    sla_risk: Optional[bool] = Field(None, description="Filter by SLA breach risk")
    
    # Date range
    date_from: Optional[datetime] = Field(None, description="Filter from date (ISO 8601)")
    date_to: Optional[datetime] = Field(None, description="Filter to date (ISO 8601)")
    
    # Pagination
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")
    
    # Sorting
    sort_by: ComplaintSortBy = Field(ComplaintSortBy.CREATED_AT, description="Sort field")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['open', 'in_progress', 'resolved', 'closed', 'escalated', 'all']:
            raise ValueError('Invalid status filter')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ['low', 'medium', 'high', 'critical', 'all']:
            raise ValueError('Invalid priority filter')
        return v


class UserInfo(BaseModel):
    """User information for complaint response"""
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "name": "John Doe",
                "email": "john@example.com",
                "mobile": "9876543210"
            }
        }


class BookingInfo(BaseModel):
    """Booking information for complaint response"""
    id: int
    order_id: str
    status: str
    total_amount: Optional[float] = None
    scheduled_date: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 456,
                "order_id": "ORDA5D9F532",
                "status": "completed",
                "total_amount": 1500.0,
                "scheduled_date": "2025-01-15T10:00:00Z"
            }
        }


class StaffInfo(BaseModel):
    """Staff information for complaint response"""
    id: int
    employee_id: str
    name: str
    department: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 789,
                "employee_id": "EMP001",
                "name": "Jane Smith",
                "department": "Operations"
            }
        }


class ComplaintUpdateInfo(BaseModel):
    """Complaint update information"""
    id: int
    comment: str
    is_internal: bool
    staff_info: Optional[StaffInfo] = None
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 101,
                "comment": "Following up with customer regarding resolution",
                "is_internal": True,
                "staff_info": {
                    "id": 789,
                    "employee_id": "EMP001",
                    "name": "Jane Smith",
                    "department": "Operations"
                },
                "created_at": "2025-01-15T14:30:00Z"
            }
        }


class ComplaintResponse(BaseModel):
    """Full complaint details response"""
    
    # Basic info
    id: int
    complaint_type: str
    subject: str
    description: str
    
    # Status and priority
    status: str
    priority: str
    
    # Relationships
    user_info: UserInfo
    booking_info: Optional[BookingInfo] = None
    assigned_to_staff: Optional[StaffInfo] = None
    resolved_by_staff: Optional[StaffInfo] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # SLA tracking
    response_due_at: Optional[datetime] = None
    resolution_due_at: Optional[datetime] = None
    sla_breach_risk: bool = False
    
    # Resolution
    resolution: Optional[str] = None
    
    # Updates count
    updates_count: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "complaint_type": "service_quality",
                "subject": "Poor service quality",
                "description": "The technician was unprofessional and did not complete the work properly",
                "status": "in_progress",
                "priority": "high",
                "user_info": {
                    "id": 123,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "mobile": "9876543210"
                },
                "booking_info": {
                    "id": 456,
                    "order_id": "ORDA5D9F532",
                    "status": "completed",
                    "total_amount": 1500.0,
                    "scheduled_date": "2025-01-15T10:00:00Z"
                },
                "assigned_to_staff": {
                    "id": 789,
                    "employee_id": "EMP001",
                    "name": "Jane Smith",
                    "department": "Operations"
                },
                "created_at": "2025-01-15T12:00:00Z",
                "updated_at": "2025-01-15T14:00:00Z",
                "assigned_at": "2025-01-15T13:00:00Z",
                "response_due_at": "2025-01-16T12:00:00Z",
                "resolution_due_at": "2025-01-17T12:00:00Z",
                "sla_breach_risk": False,
                "updates_count": 3
            }
        }


class ComplaintListResponse(BaseModel):
    """Paginated list of complaints response"""
    
    complaints: List[ComplaintResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "complaints": [
                    {
                        "id": 1,
                        "complaint_type": "service_quality",
                        "subject": "Poor service quality",
                        "status": "in_progress",
                        "priority": "high",
                        "sla_breach_risk": False,
                        "created_at": "2025-01-15T12:00:00Z"
                    }
                ],
                "total": 25,
                "skip": 0,
                "limit": 20,
                "has_more": True
            }
        }


class ComplaintUpdateRequest(BaseModel):
    """Request to update complaint fields"""
    
    status: Optional[str] = Field(None, description="New status")
    priority: Optional[str] = Field(None, description="New priority")
    resolution: Optional[str] = Field(None, description="Resolution text")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in [s.value for s in ComplaintStatus]:
            raise ValueError(f'Invalid status. Must be one of: {[s.value for s in ComplaintStatus]}')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in [p.value for p in ComplaintPriority]:
            raise ValueError(f'Invalid priority. Must be one of: {[p.value for p in ComplaintPriority]}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "in_progress",
                "priority": "high",
                "resolution": "Issue has been identified and is being resolved"
            }
        }


class ComplaintAssignRequest(BaseModel):
    """Request to assign complaint to staff"""
    
    assigned_to_staff_id: int = Field(..., description="Staff ID to assign complaint to")
    notes: Optional[str] = Field(None, description="Assignment notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "assigned_to_staff_id": 789,
                "notes": "Assigning to senior operations agent for immediate attention"
            }
        }


class ComplaintResolveRequest(BaseModel):
    """Request to resolve complaint"""
    
    resolution: str = Field(..., min_length=10, description="Resolution description")
    status: Optional[str] = Field("resolved", description="Final status (resolved or closed)")
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['resolved', 'closed']:
            raise ValueError('Status must be either "resolved" or "closed"')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "resolution": "Issue has been fully resolved. Customer was contacted and confirmed satisfaction with the solution provided.",
                "status": "resolved"
            }
        }


class ComplaintNoteRequest(BaseModel):
    """Request to add update/note to complaint"""
    
    comment: str = Field(..., min_length=5, description="Update comment")
    is_internal: bool = Field(False, description="Whether this is an internal note")
    
    class Config:
        json_schema_extra = {
            "example": {
                "comment": "Customer called to follow up. Explained current status and next steps.",
                "is_internal": False
            }
        }


class ComplaintOperationResponse(BaseModel):
    """Response for complaint operations (assign, resolve, etc.)"""
    
    success: bool
    message: str
    complaint: ComplaintResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Complaint assigned successfully",
                "complaint": {
                    "id": 1,
                    "status": "in_progress",
                    "assigned_to_staff": {
                        "id": 789,
                        "employee_id": "EMP001",
                        "name": "Jane Smith"
                    }
                }
            }
        }
