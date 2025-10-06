"""
JWT token management
Secure token generation, verification, and blacklisting
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import logging

from src.core.config import settings
from src.core.cache import redis_client

logger = logging.getLogger(__name__)


# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_access_token(
    subject: str,
    user_id: int,
    user_type: str = "customer",
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create JWT access token (short-lived)
    
    Args:
        subject: Token subject (usually user email or phone)
        user_id: User ID
        user_type: Type of user (customer, staff)
        additional_claims: Additional claims to include in token
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_access_token(
        ...     subject="user@example.com",
        ...     user_id=123,
        ...     user_type="customer"
        ... )
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    to_encode = {
        "sub": subject,
        "user_id": user_id,
        "user_type": user_type,
        "type": TOKEN_TYPE_ACCESS,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    user_id: int,
    user_type: str = "customer"
) -> str:
    """
    Create JWT refresh token (long-lived)
    
    Args:
        subject: Token subject (usually user email or phone)
        user_id: User ID
        user_type: Type of user (customer, staff)
        
    Returns:
        str: Encoded JWT token
        
    Example:
        >>> token = create_refresh_token(
        ...     subject="user@example.com",
        ...     user_id=123
        ... )
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    to_encode = {
        "sub": subject,
        "user_id": user_id,
        "user_type": user_type,
        "type": TOKEN_TYPE_REFRESH,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


async def verify_token(token: str, token_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token to verify
        token_type: Expected token type (access or refresh)

    Returns:
        Optional[Dict]: Decoded token payload or None if invalid

    Example:
        >>> payload = await verify_token(token, token_type="access")
        >>> if payload:
        ...     print(payload["user_id"])
    """
    try:
        # Decode token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check if token is blacklisted
        if await is_token_blacklisted(token):
            logger.warning(f"Attempted to use blacklisted token")
            return None

        # Verify token type if specified
        if token_type and payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None

        return payload

    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode token without verification (for debugging/logging only)

    Args:
        token: JWT token to decode

    Returns:
        Optional[Dict]: Decoded token payload or None

    Warning:
        DO NOT use this for authentication! Only for debugging.
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False, "verify_exp": False}
        )
    except Exception as e:
        logger.error(f"Token decode error: {e}")
        return None


async def blacklist_token(token: str, reason: str = "logout") -> bool:
    """
    Add token to blacklist (Redis)
    
    Args:
        token: JWT token to blacklist
        reason: Reason for blacklisting
        
    Returns:
        bool: True if successful
        
    Example:
        >>> await blacklist_token(token, reason="logout")
    """
    try:
        # Decode token to get expiry
        payload = decode_token_without_verification(token)
        if not payload:
            return False
        
        # Calculate TTL (time until token expires)
        exp = payload.get("exp")
        if not exp:
            return False
        
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        ttl = int((exp_datetime - now).total_seconds())
        
        if ttl <= 0:
            # Token already expired
            return True
        
        # Store in Redis with TTL
        key = f"blacklist:token:{token}"
        await redis_client.set(key, reason, ttl=ttl)
        
        logger.info(f"Token blacklisted: reason={reason}, ttl={ttl}s")
        return True
        
    except Exception as e:
        logger.error(f"Failed to blacklist token: {e}")
        return False


async def is_token_blacklisted(token: str) -> bool:
    """
    Check if token is blacklisted
    
    Args:
        token: JWT token to check
        
    Returns:
        bool: True if blacklisted
        
    Example:
        >>> if await is_token_blacklisted(token):
        ...     print("Token is blacklisted")
    """
    try:
        key = f"blacklist:token:{token}"
        result = await redis_client.exists(key)
        return result > 0
    except Exception as e:
        logger.error(f"Failed to check token blacklist: {e}")
        # Fail secure: if Redis is down, don't allow token
        return True


def create_token_pair(
    subject: str,
    user_id: int,
    user_type: str = "customer",
    additional_claims: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Create both access and refresh tokens
    
    Args:
        subject: Token subject
        user_id: User ID
        user_type: Type of user
        additional_claims: Additional claims for access token
        
    Returns:
        Dict: {
            "access_token": str,
            "refresh_token": str,
            "token_type": "bearer"
        }
        
    Example:
        >>> tokens = create_token_pair(
        ...     subject="user@example.com",
        ...     user_id=123
        ... )
        >>> print(tokens["access_token"])
    """
    access_token = create_access_token(
        subject=subject,
        user_id=user_id,
        user_type=user_type,
        additional_claims=additional_claims
    )
    
    refresh_token = create_refresh_token(
        subject=subject,
        user_id=user_id,
        user_type=user_type
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# Export
__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "blacklist_token",
    "is_token_blacklisted",
    "create_token_pair",
    "TOKEN_TYPE_ACCESS",
    "TOKEN_TYPE_REFRESH",
]

