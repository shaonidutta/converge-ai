"""
Authentication Routes (Thin Controllers)
User registration, login, logout, token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.security import blacklist_token
from src.core.models import User
from src.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    RefreshTokenRequest,
    MessageResponse,
)
from src.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
async def register_user(
    request: UserRegisterRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user account"""
    try:
        auth_service = AuthService(db)
        return await auth_service.register_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user"
)
async def login_user(
    request: UserLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login with email/mobile and password"""
    try:
        auth_service = AuthService(db)
        return await auth_service.login_user(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token using refresh token"""
    try:
        auth_service = AuthService(db)
        return await auth_service.refresh_access_token(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user"
)
async def logout_user(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Logout user and blacklist token"""
    try:
        # Token is blacklisted in the dependency
        return MessageResponse(message="Logged out successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )




