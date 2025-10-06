"""
Authentication Service
Business logic for user authentication operations
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import Optional
import logging

from src.core.models import User
from src.core.security.password import hash_password, verify_password
from src.core.security.jwt import create_access_token, create_refresh_token, verify_token
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
)
from src.core.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register_user(self, request: UserRegisterRequest) -> AuthResponse:
        """
        Register a new user
        
        Args:
            request: Registration request data
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            ValueError: If email or mobile already exists
        """
        # Check if email already exists
        existing_user = await self.user_repo.get_user_by_email(request.email)
        if existing_user:
            raise ValueError("Email already registered")

        # Check if mobile already exists
        existing_mobile = await self.user_repo.get_user_by_mobile(request.mobile)
        if existing_mobile:
            raise ValueError("Mobile number already registered")

        # Create user
        user = await self.user_repo.create_user(
            email=request.email,
            mobile=request.mobile,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name
        )
        
        # Generate tokens
        access_token = create_access_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )
        refresh_token = create_refresh_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )

        logger.info(f"User registered successfully: id={user.id}, email={user.email}")

        from src.schemas.auth import UserResponse, TokenResponse
        from src.core.config import settings

        return AuthResponse(
            user=UserResponse(
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
            ),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    
    async def login_user(self, request: UserLoginRequest) -> AuthResponse:
        """
        Login user with email/mobile and password
        
        Args:
            request: Login request data
            
        Returns:
            AuthResponse with user data and tokens
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by email or mobile
        user = None
        if "@" in request.identifier:
            user = await self.user_repo.get_user_by_email(request.identifier)
        else:
            user = await self.user_repo.get_user_by_mobile(request.identifier)
        
        if not user:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise ValueError("Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()
        
        # Generate tokens
        access_token = create_access_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )
        refresh_token = create_refresh_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )
        
        logger.info(f"User logged in: id={user.id}, email={user.email}")

        from src.schemas.auth import UserResponse, TokenResponse
        from src.core.config import settings

        return AuthResponse(
            user=UserResponse(
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
            ),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    
    async def refresh_access_token(self, request: RefreshTokenRequest) -> AuthResponse:
        """
        Refresh access token using refresh token
        
        Args:
            request: Refresh token request
            
        Returns:
            AuthResponse with new tokens
            
        Raises:
            ValueError: If refresh token is invalid
        """
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        if not payload:
            raise ValueError("Invalid refresh token")
        
        user_id = int(payload.get("sub"))

        # Get user
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.is_active:
            raise ValueError("Account is inactive")
        
        # Generate new tokens
        access_token = create_access_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )
        refresh_token = create_refresh_token(
            subject=user.email,
            user_id=user.id,
            user_type="customer"
        )
        
        logger.info(f"Token refreshed: user_id={user.id}")

        from src.schemas.auth import UserResponse, TokenResponse
        from src.core.config import settings

        return AuthResponse(
            user=UserResponse(
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
            ),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
    
    async def change_password(self, user: User, request: PasswordChangeRequest) -> None:
        """
        Change user password
        
        Args:
            user: Current user
            request: Change password request
            
        Raises:
            ValueError: If current password is incorrect
        """
        # Verify current password
        if not verify_password(request.current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = hash_password(request.new_password)
        
        # Update password
        user.password_hash = new_password_hash
        await self.db.commit()
        
        logger.info(f"Password changed: user_id={user.id}")


# Export
__all__ = ["AuthService"]

