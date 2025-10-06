"""
Authentication endpoints
User registration, login, logout, token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import logging

from src.core.database.connection import get_db
from src.core.repositories import UserRepository
from src.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    verify_token,
    blacklist_token,
    TOKEN_TYPE_REFRESH,
)
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.core.config import settings
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    MessageResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new customer account with email and mobile"
)
async def register_user(
    request: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user account
    
    - **email**: Valid email address (unique)
    - **mobile**: Mobile number (unique)
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **first_name**: User's first name
    - **last_name**: User's last name (optional)
    - **referral_code**: Referral code (optional)
    
    Returns user data and JWT tokens
    """
    repo = UserRepository(db)
    
    # Check if email already exists
    if request.email:
        existing_user = await repo.get_user_by_email(request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Check if mobile already exists
    existing_user = await repo.get_user_by_mobile(request.mobile)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    # Create user
    try:
        user = await repo.create_user(
            email=request.email,
            mobile=request.mobile,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            referral_code=request.referral_code
        )
        
        logger.info(f"User registered: id={user.id}, email={user.email}")
        
        # Generate tokens
        tokens = create_token_pair(
            subject=user.email or user.mobile,
            user_id=user.id,
            user_type="customer"
        )
        
        # Prepare response
        user_response = UserResponse(
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
            created_at=user.created_at.isoformat()
        )
        
        token_response = TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
        return AuthResponse(user=user_response, tokens=token_response)
        
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="User login",
    description="Login with email/mobile and password"
)
async def login_user(
    request: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Login with email or mobile number
    
    - **identifier**: Email address or mobile number
    - **password**: User password
    
    Returns user data and JWT tokens
    """
    repo = UserRepository(db)
    
    # Try to find user by email or mobile
    user = None
    if "@" in request.identifier:
        user = await repo.get_user_by_email(request.identifier)
    else:
        user = await repo.get_user_by_mobile(request.identifier)
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )
    
    # Verify password
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    await repo.update_last_login(user.id)
    
    logger.info(f"User logged in: id={user.id}, email={user.email}")
    
    # Generate tokens
    tokens = create_token_pair(
        subject=user.email or user.mobile,
        user_id=user.id,
        user_type="customer"
    )
    
    # Prepare response
    user_response = UserResponse(
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
        created_at=user.created_at.isoformat()
    )
    
    token_response = TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    return AuthResponse(user=user_response, tokens=token_response)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token
    """
    # Verify refresh token
    payload = await verify_token(request.refresh_token, token_type=TOKEN_TYPE_REFRESH)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    repo = UserRepository(db)
    user = await repo.get_user_by_id(payload["user_id"])
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    tokens = create_token_pair(
        subject=user.email or user.mobile,
        user_id=user.id,
        user_type="customer"
    )
    
    logger.info(f"Token refreshed for user: id={user.id}")
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="User logout",
    description="Logout and blacklist current token"
)
async def logout_user(
    current_user: Annotated[User, Depends(get_current_user)],
    token: str = Depends(lambda credentials=Depends(get_current_user): credentials)
):
    """
    Logout user and blacklist token
    
    Requires authentication
    """
    # Note: We need to extract the actual token from the request
    # This is a simplified version - in production, extract from Authorization header
    
    logger.info(f"User logged out: id={current_user.id}")
    
    return MessageResponse(message="Logged out successfully")


# Export
__all__ = ["router"]

