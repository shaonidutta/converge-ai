"""
User profile endpoints
User profile management, password change, account deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import logging

from src.core.database.connection import get_db
from src.core.repositories import UserRepository
from src.core.security import hash_password, verify_password
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.auth import (
    UserResponse,
    UserUpdateRequest,
    PasswordChangeRequest,
    MessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User Profile"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Get authenticated user's profile information"
)
async def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current user profile
    
    Requires authentication
    
    Returns user profile data
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        mobile=current_user.mobile,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email_verified=current_user.email_verified,
        mobile_verified=current_user.mobile_verified,
        wallet_balance=float(current_user.wallet_balance),
        referral_code=current_user.referral_code,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat()
    )


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update user profile",
    description="Update authenticated user's profile information"
)
async def update_user_profile(
    request: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update user profile
    
    Requires authentication
    
    - **first_name**: New first name (optional)
    - **last_name**: New last name (optional)
    - **email**: New email address (optional)
    
    Returns updated user profile
    """
    repo = UserRepository(db)
    
    # Check if email is being changed and if it's already taken
    if request.email and request.email != current_user.email:
        existing_user = await repo.get_user_by_email(request.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
    
    # Prepare update data
    update_data = {}
    if request.first_name is not None:
        update_data["first_name"] = request.first_name
    if request.last_name is not None:
        update_data["last_name"] = request.last_name
    if request.email is not None:
        update_data["email"] = request.email
        update_data["email_verified"] = False  # Reset verification if email changed
    
    # Update user
    try:
        updated_user = await repo.update_user(current_user.id, **update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User profile updated: id={current_user.id}")
        
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            mobile=updated_user.mobile,
            first_name=updated_user.first_name,
            last_name=updated_user.last_name,
            email_verified=updated_user.email_verified,
            mobile_verified=updated_user.mobile_verified,
            wallet_balance=float(updated_user.wallet_balance),
            referral_code=updated_user.referral_code,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed. Please try again."
        )


@router.patch(
    "/me/password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change authenticated user's password"
)
async def change_password(
    request: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change user password
    
    Requires authentication
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 chars, uppercase, lowercase, digit, special char)
    
    Returns success message
    """
    repo = UserRepository(db)
    
    # Verify current password
    if not current_user.password_hash or not verify_password(
        request.current_password, 
        current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    try:
        new_password_hash = hash_password(request.new_password)
        updated_user = await repo.update_user(
            current_user.id,
            password_hash=new_password_hash
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"Password changed for user: id={current_user.id}")
        
        return MessageResponse(message="Password changed successfully")
        
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete account",
    description="Delete authenticated user's account (soft delete)"
)
async def delete_account(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Delete user account (soft delete)
    
    Requires authentication
    
    Account will be deactivated but data retained for compliance
    
    Returns success message
    """
    repo = UserRepository(db)
    
    try:
        # Soft delete user
        success = await repo.delete_user(current_user.id, soft_delete=True)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        logger.info(f"User account deleted: id={current_user.id}")
        
        return MessageResponse(
            message="Account deleted successfully. Your data will be retained for compliance purposes."
        )
        
    except Exception as e:
        logger.error(f"Account deletion failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed. Please try again."
        )


# Export
__all__ = ["router"]

