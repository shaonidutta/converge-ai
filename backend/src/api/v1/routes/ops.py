"""
Ops Routes (Thin Controllers)
Ops user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional
from datetime import datetime

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_staff, require_permissions
from src.core.models import Staff
from src.schemas.ops import (
    OpsRegisterRequest,
    OpsLoginRequest,
    OpsAuthResponse,
    OpsUserResponse,
    OpsUpdateRequest,
)
from src.schemas.ops_dashboard import PriorityQueueResponse
from src.services import OpsService, OpsDashboardService

router = APIRouter(prefix="/ops", tags=["Ops Management"])


@router.post(
    "/auth/register",
    response_model=OpsAuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register ops user"
)
async def register_ops_user(
    request: OpsRegisterRequest,
    current_staff: Annotated[Staff, Depends(require_permissions(["staff.create"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new ops user (requires staff.create permission)"""
    try:
        ops_service = OpsService(db)
        return await ops_service.register_ops_user(request, current_staff)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register ops user"
        )


@router.post(
    "/auth/login",
    response_model=OpsAuthResponse,
    summary="Login ops user"
)
async def login_ops_user(
    request: OpsLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login ops user with email/mobile/employee_id and password"""
    try:
        ops_service = OpsService(db)
        return await ops_service.login_ops_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.get(
    "/users",
    response_model=List[OpsUserResponse],
    summary="List ops users"
)
async def list_ops_users(
    current_staff: Annotated[Staff, Depends(require_permissions(["staff.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    role_id: Optional[int] = Query(None, description="Filter by role"),
    department: Optional[str] = Query(None, description="Filter by department"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """List ops users with filters (requires staff.read permission)"""
    try:
        ops_service = OpsService(db)
        return await ops_service.list_ops_users(
            role_id,
            department,
            is_active,
            skip,
            limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ops users"
        )


@router.get(
    "/users/{staff_id}",
    response_model=OpsUserResponse,
    summary="Get ops user"
)
async def get_ops_user(
    staff_id: int,
    current_staff: Annotated[Staff, Depends(require_permissions(["staff.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get ops user by ID (requires staff.read permission)"""
    try:
        ops_service = OpsService(db)
        return await ops_service.get_ops_user(staff_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch ops user"
        )


@router.put(
    "/users/{staff_id}",
    response_model=OpsUserResponse,
    summary="Update ops user"
)
async def update_ops_user(
    staff_id: int,
    request: OpsUpdateRequest,
    current_staff: Annotated[Staff, Depends(require_permissions(["staff.update"]))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update ops user (requires staff.update permission)"""
    try:
        ops_service = OpsService(db)
        return await ops_service.update_ops_user(staff_id, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update ops user"
        )

# ============================================================================
# OPS DASHBOARD ENDPOINTS
# ============================================================================

@router.get(
    "/dashboard/priority-queue",
    response_model=PriorityQueueResponse,
    status_code=status.HTTP_200_OK,
    summary="Get priority queue items"
)
async def get_priority_queue(
    request: Request,
    current_staff: Annotated[Staff, Depends(require_permissions(["ops.read"]))],
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by review status: pending, reviewed, all"
    ),
    intent_type: Optional[str] = Query(
        None,
        description="Filter by intent type: complaint, booking, refund, cancellation"
    ),
    priority_min: Optional[int] = Query(
        None,
        ge=0,
        le=100,
        description="Minimum priority score (0-100)"
    ),
    priority_max: Optional[int] = Query(
        None,
        ge=0,
        le=100,
        description="Maximum priority score (0-100)"
    ),
    date_from: Optional[datetime] = Query(
        None,
        description="Filter from date (ISO 8601 format)"
    ),
    date_to: Optional[datetime] = Query(
        None,
        description="Filter to date (ISO 8601 format)"
    ),
    sort_by: str = Query(
        "priority_score",
        description="Sort by field: priority_score, created_at, confidence_score"
    ),
    sort_order: str = Query(
        "desc",
        description="Sort order: asc, desc"
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Pagination offset"
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Pagination limit (max 100)"
    ),
    expand: bool = Query(
        False,
        description="Fetch full related entity details (expensive)"
    ),
    fields: Optional[str] = Query(
        None,
        description="Specific fields to include in expansion (comma-separated)"
    )
):
    """
    Get priority queue items with filtering and pagination

    **Permissions Required**: `ops.read`

    **PII Access**:
    - Users with `ops.full_access` permission see full PII (mobile, email, name)
    - Users without full access see redacted PII

    **Performance**:
    - Default: Returns summary info (fast)
    - With `expand=true`: Returns full details (slower, rate limited)

    **Filters**:
    - `status`: pending (default for ops), reviewed, all
    - `intent_type`: complaint, booking, refund, cancellation
    - `priority_min/max`: Priority score range (0-100)
    - `date_from/to`: Date range filter

    **Sorting**:
    - `sort_by`: priority_score (default), created_at, confidence_score
    - `sort_order`: desc (default), asc

    **Pagination**:
    - `skip`: Offset (default 0)
    - `limit`: Items per page (default 20, max 100)

    **Expansion**:
    - `expand=false` (default): Summary info only
    - `expand=true`: Full related entity details
    - `fields`: Specific fields to include (e.g., "subject,description")
    """
    try:
        # Extract request metadata for audit logging
        request_metadata = {
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }

        # Call service
        ops_dashboard_service = OpsDashboardService(db)
        result = await ops_dashboard_service.get_priority_queue(
            current_staff=current_staff,
            status=status_filter,
            intent_type=intent_type,
            priority_min=priority_min,
            priority_max=priority_max,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
            skip=skip,
            limit=limit,
            expand=expand,
            fields=fields,
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
            detail="Failed to retrieve priority queue"
        )


