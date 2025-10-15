"""
Authentication dependencies for FastAPI
Dependency injection for authentication and authorization
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.core.database.connection import get_db
from src.core.security.jwt import verify_token, TOKEN_TYPE_ACCESS
from src.core.models import User, Staff

logger = logging.getLogger(__name__)


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user (customer)
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        User: Authenticated user object
        
    Raises:
        HTTPException: 401 if authentication fails
        
    Usage:
        @app.get("/profile")
        async def get_profile(current_user: User = Depends(get_current_user)):
            return {"user": current_user}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token
        token = credentials.credentials

        # Verify token
        payload = await verify_token(token, token_type=TOKEN_TYPE_ACCESS)
        if payload is None:
            raise credentials_exception
        
        # Extract user info
        user_id: int = payload.get("user_id")
        user_type: str = payload.get("user_type")
        
        if user_id is None or user_type != "customer":
            raise credentials_exception
        
        # Get user from database
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise credentials_exception


async def get_current_staff(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Staff:
    """
    Get current authenticated staff member
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
        
    Returns:
        Staff: Authenticated staff object
        
    Raises:
        HTTPException: 401 if authentication fails
        
    Usage:
        @app.get("/admin/dashboard")
        async def admin_dashboard(staff: Staff = Depends(get_current_staff)):
            return {"staff": staff}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token
        token = credentials.credentials

        # Verify token
        payload = await verify_token(token, token_type=TOKEN_TYPE_ACCESS)
        if payload is None:
            raise credentials_exception
        
        # Extract staff info
        user_id: int = payload.get("user_id")
        user_type: str = payload.get("user_type")
        
        if user_id is None or user_type != "staff":
            raise credentials_exception
        
        # Get staff from database
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(Staff)
            .options(selectinload(Staff.role).selectinload(Staff.role.property.mapper.class_.permissions))
            .where(Staff.id == user_id)
        )
        staff = result.scalar_one_or_none()
        
        if staff is None:
            raise credentials_exception
        
        # Check if staff is active
        if not staff.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Staff account is inactive"
            )
        
        return staff
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Staff authentication error: {e}")
        raise credentials_exception


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise
    Useful for endpoints that work with or without authentication
    
    Args:
        credentials: HTTP Bearer token (optional)
        db: Database session
        
    Returns:
        Optional[User]: User object or None
        
    Usage:
        @app.get("/products")
        async def get_products(user: Optional[User] = Depends(get_optional_current_user)):
            # Show personalized products if user is logged in
            if user:
                return get_personalized_products(user)
            return get_default_products()
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_permissions(*required_permissions: str):
    """
    Dependency factory to check staff permissions
    
    Args:
        *required_permissions: Permission names required
        
    Returns:
        Dependency function
        
    Usage:
        @app.post("/bookings")
        async def create_booking(
            staff: Staff = Depends(require_permissions("bookings.create"))
        ):
            return {"message": "Booking created"}
    """
    async def permission_checker(
        staff: Staff = Depends(get_current_staff)
    ) -> Staff:
        """Check if staff has required permissions"""
        # Check if staff has any of the required permissions
        if not staff.has_any_permission(list(required_permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {', '.join(required_permissions)}"
            )
        return staff
    
    return permission_checker


def require_role(*required_roles: str):
    """
    Dependency factory to check staff role
    
    Args:
        *required_roles: Role names required
        
    Returns:
        Dependency function
        
    Usage:
        @app.get("/admin/users")
        async def list_users(
            staff: Staff = Depends(require_role("admin", "super_admin"))
        ):
            return {"users": [...]}
    """
    async def role_checker(
        staff: Staff = Depends(get_current_staff)
    ) -> Staff:
        """Check if staff has required role"""
        if staff.role.name not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient role. Required: {', '.join(required_roles)}"
            )
        return staff
    
    return role_checker


# Export
__all__ = [
    "get_current_user",
    "get_current_staff",
    "get_optional_current_user",
    "require_permissions",
    "require_role",
]

