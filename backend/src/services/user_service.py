"""
User Service
Business logic for user profile management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.core.models import User
from src.schemas.auth import UserResponse, UserUpdateRequest
from src.core.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Service class for user management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_user_profile(self, user: User) -> UserResponse:
        """
        Get user profile

        Args:
            user: Current user

        Returns:
            UserResponse with user data
        """
        return UserResponse(
            id=user.id,
            email=user.email,
            mobile=user.mobile,
            first_name=user.first_name,
            last_name=user.last_name,
            email_verified=user.email_verified,
            mobile_verified=user.mobile_verified,
            wallet_balance=float(user.wallet_balance),
            referral_code=user.referral_code,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
    
    async def update_user_profile(
        self,
        user: User,
        request: UserUpdateRequest
    ) -> UserResponse:
        """
        Update user profile

        Args:
            user: Current user
            request: Update profile request

        Returns:
            UserResponse with updated user data

        Raises:
            ValueError: If email or mobile already exists
        """
        # Check if email is being changed and already exists
        if request.email and request.email != user.email:
            existing_user = await self.user_repo.get_user_by_email(request.email)
            if existing_user:
                raise ValueError("Email already in use")
            user.email = request.email

        # Check if mobile is being changed and already exists
        if request.mobile and request.mobile != user.mobile:
            existing_mobile = await self.user_repo.get_user_by_mobile(request.mobile)
            if existing_mobile:
                raise ValueError("Mobile number already in use")
            user.mobile = request.mobile
        
        # Update other fields
        if request.first_name is not None:
            user.first_name = request.first_name
        
        if request.last_name is not None:
            user.last_name = request.last_name
        
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"User profile updated: user_id={user.id}")

        return UserResponse(
            id=user.id,
            email=user.email,
            mobile=user.mobile,
            first_name=user.first_name,
            last_name=user.last_name,
            email_verified=user.email_verified,
            mobile_verified=user.mobile_verified,
            wallet_balance=float(user.wallet_balance),
            referral_code=user.referral_code,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None
        )
    
    async def delete_user_account(self, user: User) -> None:
        """
        Delete user account (soft delete)
        
        Args:
            user: Current user
        """
        user.is_active = False
        await self.db.commit()
        
        logger.info(f"User account deleted: user_id={user.id}")


# Export
__all__ = ["UserService"]

