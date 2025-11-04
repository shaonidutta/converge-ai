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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.view", "ops.read"]))],
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
    
    **Permissions Required**: `complaints.view` OR `ops.read`
    
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
        
        # Call service
        service = OpsComplaintsService(db)
        result = await service.list_complaints(
            current_staff=current_staff,
            filters=filters,
            request_metadata=request_metadata
        )
        
        return result
        
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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.view", "ops.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get detailed complaint information by ID
    
    **Permissions Required**: `complaints.view` OR `ops.read`
    
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
        
        # Call service
        service = OpsComplaintsService(db)
        result = await service.get_complaint_by_id(
            complaint_id=complaint_id,
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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.assign", "ops.admin"]))],
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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.assign", "ops.admin"]))],
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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.resolve", "ops.admin"]))],
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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.view", "ops.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Add update or note to complaint

    **Permissions Required**: `complaints.view` OR `ops.read`

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
    current_staff: Annotated[Staff, Depends(require_permissions(["complaints.view", "ops.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    include_internal: bool = Query(
        True,
        description="Include internal notes (default: true)"
    )
):
    """
    Get all updates and notes for a complaint

    **Permissions Required**: `complaints.view` OR `ops.read`

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

        # Call service
        service = OpsComplaintsService(db)
        result = await service.get_complaint_updates(
            complaint_id=complaint_id,
            current_staff=current_staff,
            include_internal=include_internal,
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
            detail="Failed to retrieve complaint updates"
        )
