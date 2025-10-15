"""
User Routes (Thin Controllers)
User profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.auth import (
    UserResponse,
    UserUpdateRequest,
    MessageResponse,
)
from src.services import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile"
)
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get current user profile"""
    try:
        user_service = UserService(db)
        return await user_service.get_user_profile(current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update user profile"
)
async def update_profile(
    request: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update user profile"""
    try:
        user_service = UserService(db)
        return await user_service.update_user_profile(current_user, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete user account"
)
async def delete_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Delete user account (soft delete)"""
    try:
        user_service = UserService(db)
        await user_service.delete_user_account(current_user)
        return MessageResponse(message="Account deleted successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )

