"""
Ops Routes (Thin Controllers)
Ops user management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

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
from src.services import OpsService

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

