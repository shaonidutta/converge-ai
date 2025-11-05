"""
Operations Complaints API Routes
API endpoints for complaint management operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional, List

from src.core.database.connection import get_db
from src.core.security.dependencies import require_permissions
from src.core.models.staff import Staff
from src.services.ops_complaints_service import OpsComplaintsService
from src.schemas.ops_complaints import (
    ComplaintListRequest, ComplaintListResponse, ComplaintResponse,
    ComplaintUpdateRequest, ComplaintAssignRequest, ComplaintResolveRequest,
    ComplaintNoteRequest, ComplaintOperationResponse, ComplaintUpdateInfo
)

router = APIRouter(prefix="/complaints", tags=["Operations - Complaints"])


@router.get(
    "",
    response_model=ComplaintListResponse,
    status_code=status.HTTP_200_OK,
    summary="List complaints with filtering and pagination"
)
async def list_complaints(
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.view", "ops.priority_queue.view"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    
    # Filters
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status (open, in_progress, resolved, closed, escalated, all)"
    ),
    priority: Optional[str] = Query(
        None,
        description="Filter by priority (low, medium, high, critical, all)"
    ),
    complaint_type: Optional[str] = Query(
        None,
        description="Filter by complaint type"
    ),
    assigned_to: Optional[int] = Query(
        None,
        description="Filter by assigned staff ID"
    ),
    sla_risk: Optional[bool] = Query(
        None,
        description="Filter by SLA breach risk"
    ),
    date_from: Optional[str] = Query(
        None,
        description="Filter from date (ISO 8601 format)"
    ),
    date_to: Optional[str] = Query(
        None,
        description="Filter to date (ISO 8601 format)"
    ),
    
    # Pagination
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    
    # Sorting
    sort_by: str = Query(
        "created_at",
        description="Sort field (created_at, priority, status, response_due_at, resolution_due_at)"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order (asc, desc)"
    )
):
    """
    List complaints with comprehensive filtering and pagination
    
    **Permissions Required**: `complaints.view` OR `ops.priority_queue.view`
    
    **PII Access**:
    - Staff with `ops.full_access` or `ops.admin` permission see full user details
    - Other staff see redacted PII (masked email, phone, name)
    
    **Filters**:
    - `status`: Filter by complaint status
    - `priority`: Filter by complaint priority
    - `complaint_type`: Filter by complaint type
    - `assigned_to`: Filter by assigned staff ID
    - `sla_risk`: Filter by SLA breach risk (true/false)
    - `date_from/date_to`: Date range filter
    
    **Sorting**:
    - `sort_by`: Field to sort by (default: created_at)
    - `sort_order`: Sort direction (default: desc)
    
    **Pagination**:
    - `skip`: Number of items to skip (default: 0)
    - `limit`: Number of items to return (default: 20, max: 100)
    """
    try:
        # Build filters request
        from datetime import datetime
        
        filters = ComplaintListRequest(
            status=status_filter,
            priority=priority,
            complaint_type=complaint_type,
            assigned_to=assigned_to,
            sla_risk=sla_risk,
            date_from=datetime.fromisoformat(date_from.replace('Z', '+00:00')) if date_from else None,
            date_to=datetime.fromisoformat(date_to.replace('Z', '+00:00')) if date_to else None,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "list_complaints"
        }
        
        # TEMPORARY MOCK DATA FOR PHASE 3 TESTING
        mock_complaints = [
            {
                "id": 1,
                "complaint_type": "service_quality",
                "subject": "Poor service quality during AC repair",
                "description": "The technician arrived late and did not properly fix the AC unit. It's still not cooling properly.",
                "status": "open",
                "priority": "high",
                "user_info": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "mobile": "9876543210"
                },
                "booking_info": {
                    "id": 1,
                    "order_id": "ORD001",
                    "service_name": "AC Repair",
                    "scheduled_date": "2025-11-04T10:00:00Z",
                    "status": "confirmed"
                },
                "assigned_to_staff": None,
                "resolved_by_staff": None,
                "created_at": "2025-11-04T08:00:00Z",
                "updated_at": "2025-11-04T08:00:00Z",
                "assigned_at": None,
                "resolved_at": None,
                "response_due_at": "2025-11-04T12:00:00Z",
                "resolution_due_at": "2025-11-06T08:00:00Z",
                "sla_breach_risk": True,
                "resolution": None,
                "updates_count": 0
            },
            {
                "id": 2,
                "complaint_type": "billing",
                "subject": "Incorrect billing amount charged",
                "description": "I was charged ₹2500 for plumbing service but the quote was ₹1800. Please review the billing.",
                "status": "in_progress",
                "priority": "medium",
                "user_info": {
                    "id": 2,
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "mobile": "9876543211"
                },
                "booking_info": {
                    "id": 2,
                    "order_id": "ORD002",
                    "service_name": "Plumbing Service",
                    "scheduled_date": "2025-11-03T14:00:00Z",
                    "status": "completed"
                },
                "assigned_to_staff": {
                    "id": 1,
                    "employee_id": "EMP001",
                    "name": "Operations Admin",
                    "department": "Operations"
                },
                "resolved_by_staff": None,
                "created_at": "2025-11-03T16:00:00Z",
                "updated_at": "2025-11-04T09:00:00Z",
                "assigned_at": "2025-11-04T09:00:00Z",
                "resolved_at": None,
                "response_due_at": "2025-11-03T20:00:00Z",
                "resolution_due_at": "2025-11-05T16:00:00Z",
                "sla_breach_risk": False,
                "resolution": None,
                "updates_count": 2
            }
        ]

        return {
            "success": True,
            "complaints": mock_complaints,
            "total": len(mock_complaints),
            "skip": skip,
            "limit": limit,
            "has_more": False,
            "debug": "mock_data_v2"
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve complaints"
        )


@router.get(
    "/{complaint_id}",
    response_model=ComplaintResponse,
    status_code=status.HTTP_200_OK,
    summary="Get complaint details by ID"
)
async def get_complaint(
    complaint_id: int,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.view", "ops.priority_queue.view"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed complaint information by ID
    
    **Permissions Required**: `complaints.view` OR `ops.priority_queue.view`
    
    **Returns**: Full complaint details including user info, booking info, 
    assignment history, SLA status, and update count
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "get_complaint"
        }
        
        # TEMPORARY MOCK DATA FOR PHASE 3 TESTING
        if complaint_id == 1:
            mock_complaint = {
                "id": 1,
                "complaint_type": "service_quality",
                "subject": "Poor service quality during AC repair",
                "description": "The technician arrived late and did not properly fix the AC unit. It's still not cooling properly.",
                "status": "open",
                "priority": "high",
                "user_info": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "mobile": "9876543210"
                },
                "booking_info": {
                    "id": 1,
                    "order_id": "ORD001",
                    "service_name": "AC Repair",
                    "scheduled_date": "2025-11-04T10:00:00Z",
                    "status": "confirmed"
                },
                "assigned_to_staff": None,
                "resolved_by_staff": None,
                "created_at": "2025-11-04T08:00:00Z",
                "updated_at": "2025-11-04T08:00:00Z",
                "assigned_at": None,
                "resolved_at": None,
                "response_due_at": "2025-11-04T12:00:00Z",
                "resolution_due_at": "2025-11-06T08:00:00Z",
                "sla_breach_risk": True,
                "resolution": None,
                "updates_count": 0
            }
        elif complaint_id == 2:
            mock_complaint = {
                "id": 2,
                "complaint_type": "billing",
                "subject": "Incorrect billing amount charged",
                "description": "I was charged ₹2500 for plumbing service but the quote was ₹1800. Please review the billing.",
                "status": "in_progress",
                "priority": "medium",
                "user_info": {
                    "id": 2,
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "mobile": "9876543211"
                },
                "booking_info": {
                    "id": 2,
                    "order_id": "ORD002",
                    "service_name": "Plumbing Service",
                    "scheduled_date": "2025-11-03T14:00:00Z",
                    "status": "completed"
                },
                "assigned_to_staff": {
                    "id": 1,
                    "employee_id": "EMP001",
                    "name": "Operations Admin",
                    "department": "Operations"
                },
                "resolved_by_staff": None,
                "created_at": "2025-11-03T16:00:00Z",
                "updated_at": "2025-11-04T09:00:00Z",
                "assigned_at": "2025-11-04T09:00:00Z",
                "resolved_at": None,
                "response_due_at": "2025-11-03T20:00:00Z",
                "resolution_due_at": "2025-11-05T16:00:00Z",
                "sla_breach_risk": False,
                "resolution": None,
                "updates_count": 2
            }
        else:
            raise ValueError(f"Complaint {complaint_id} not found")

        return mock_complaint
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve complaint"
        )


@router.put(
    "/{complaint_id}",
    response_model=ComplaintOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update complaint fields"
)
async def update_complaint(
    complaint_id: int,
    update_data: ComplaintUpdateRequest,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.assign", "system.admin"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update complaint status, priority, or resolution
    
    **Permissions Required**: `complaints.assign` OR `ops.admin`
    
    **Updatable Fields**:
    - `status`: Change complaint status
    - `priority`: Change complaint priority
    - `resolution`: Add or update resolution text
    
    **Auto-behaviors**:
    - Setting status to 'resolved' or 'closed' automatically sets resolved_at timestamp
    - Resolver staff is automatically set to current staff
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "update_complaint"
        }
        
        # Call service
        service = OpsComplaintsService(db)
        result = await service.update_complaint(
            complaint_id=complaint_id,
            update_data=update_data,
            current_staff=current_staff,
            request_metadata=request_metadata
        )
        
        return ComplaintOperationResponse(
            success=True,
            message="Complaint updated successfully",
            complaint=result
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update complaint"
        )


@router.post(
    "/{complaint_id}/assign",
    response_model=ComplaintOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Assign complaint to staff member"
)
async def assign_complaint(
    complaint_id: int,
    assign_data: ComplaintAssignRequest,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.assign", "system.admin"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Assign complaint to a staff member

    **Permissions Required**: `complaints.assign` OR `ops.admin`

    **Auto-behaviors**:
    - Status automatically changes to 'in_progress' if currently 'open'
    - Assignment timestamp is set to current time
    - Optional assignment notes are added as internal update

    **Validation**:
    - Target staff member must exist and be active
    - Complaint must exist
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "assign_complaint"
        }

        # Call service
        service = OpsComplaintsService(db)
        result = await service.assign_complaint(
            complaint_id=complaint_id,
            assign_data=assign_data,
            current_staff=current_staff,
            request_metadata=request_metadata
        )

        return ComplaintOperationResponse(
            success=True,
            message="Complaint assigned successfully",
            complaint=result
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign complaint"
        )


@router.post(
    "/{complaint_id}/resolve",
    response_model=ComplaintOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Resolve complaint with resolution text"
)
async def resolve_complaint(
    complaint_id: int,
    resolve_data: ComplaintResolveRequest,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.resolve", "system.admin"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Resolve complaint with resolution description

    **Permissions Required**: `complaints.resolve` OR `ops.admin`

    **Auto-behaviors**:
    - Status is set to 'resolved' or 'closed' as specified
    - Resolved timestamp is set to current time
    - Resolver staff is set to current staff
    - Resolution note is added as customer-visible update

    **Validation**:
    - Resolution text must be at least 10 characters
    - Status must be either 'resolved' or 'closed'
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "resolve_complaint"
        }

        # Call service
        service = OpsComplaintsService(db)
        result = await service.resolve_complaint(
            complaint_id=complaint_id,
            resolve_data=resolve_data,
            current_staff=current_staff,
            request_metadata=request_metadata
        )

        return ComplaintOperationResponse(
            success=True,
            message="Complaint resolved successfully",
            complaint=result
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve complaint"
        )


@router.post(
    "/{complaint_id}/updates",
    response_model=ComplaintUpdateInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Add update/note to complaint"
)
async def add_complaint_update(
    complaint_id: int,
    note_data: ComplaintNoteRequest,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.view", "ops.priority_queue.view"))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Add update or note to complaint

    **Permissions Required**: `complaints.view` OR `ops.priority_queue.view`

    **Note Types**:
    - `is_internal=false`: Customer-visible updates (default)
    - `is_internal=true`: Internal staff notes only

    **Validation**:
    - Comment must be at least 5 characters
    - Complaint must exist
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "add_complaint_update"
        }

        # Call service
        service = OpsComplaintsService(db)
        result = await service.add_complaint_update(
            complaint_id=complaint_id,
            note_data=note_data,
            current_staff=current_staff,
            request_metadata=request_metadata
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add complaint update"
        )


@router.get(
    "/{complaint_id}/updates",
    response_model=List[ComplaintUpdateInfo],
    status_code=status.HTTP_200_OK,
    summary="Get complaint updates/notes"
)
async def get_complaint_updates(
    complaint_id: int,
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions("complaints.view", "ops.priority_queue.view"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_internal: bool = Query(
        True,
        description="Include internal notes (default: true)"
    )
):
    """
    Get all updates and notes for a complaint

    **Permissions Required**: `complaints.view` OR `ops.priority_queue.view`

    **Filtering**:
    - `include_internal=true`: Show all updates including internal notes
    - `include_internal=false`: Show only customer-visible updates

    **Ordering**: Updates are returned in reverse chronological order (newest first)
    """
    try:
        # Get request metadata for audit
        request_metadata = {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": "get_complaint_updates"
        }

        # TEMPORARY MOCK DATA FOR PHASE 3 TESTING
        if complaint_id == 2:
            mock_updates = [
                {
                    "id": 1,
                    "complaint_id": 2,
                    "staff_id": 1,
                    "staff_name": "Operations Admin",
                    "update_type": "internal_note",
                    "content": "Contacted customer to verify billing details. Customer confirmed the discrepancy.",
                    "is_internal": True,
                    "created_at": "2025-11-04T09:15:00Z"
                },
                {
                    "id": 2,
                    "complaint_id": 2,
                    "staff_id": 1,
                    "staff_name": "Operations Admin",
                    "update_type": "customer_update",
                    "content": "We are reviewing your billing concern and will provide a resolution within 24 hours.",
                    "is_internal": False,
                    "created_at": "2025-11-04T09:30:00Z"
                }
            ]
        else:
            mock_updates = []

        return mock_updates

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve complaint updates"
        )
