"""
Authentication schemas
Pydantic models for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserRegisterRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr = Field(..., description="User email address")
    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    referral_code: Optional[str] = Field(None, max_length=20, description="Referral code")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        """Validate mobile number format"""
        # Remove spaces and special characters
        mobile = re.sub(r'[^\d+]', '', v)
        
        # Check if it's a valid format
        if not re.match(r'^\+?\d{10,15}$', mobile):
            raise ValueError('Invalid mobile number format')
        
        return mobile
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "mobile": "+919876543210",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "referral_code": "REF123"
            }
        }


class UserLoginRequest(BaseModel):
    """User login request schema"""
    identifier: str = Field(..., description="Email or mobile number")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiry in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    email: Optional[str]
    mobile: str
    first_name: Optional[str]
    last_name: Optional[str]
    email_verified: bool
    mobile_verified: bool
    wallet_balance: float
    referral_code: Optional[str]
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "email": "user@example.com",
                "mobile": "+919876543210",
                "first_name": "John",
                "last_name": "Doe",
                "email_verified": True,
                "mobile_verified": True,
                "wallet_balance": 100.00,
                "referral_code": "JOHN123",
                "is_active": True,
                "created_at": "2025-10-06T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """Authentication response with user and tokens"""
    user: UserResponse
    tokens: TokenResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 123,
                    "email": "user@example.com",
                    "mobile": "+919876543210",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email_verified": True,
                    "mobile_verified": True,
                    "wallet_balance": 100.00,
                    "referral_code": "JOHN123",
                    "is_active": True,
                    "created_at": "2025-10-06T12:00:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass123!"
            }
        }


class UserUpdateRequest(BaseModel):
    """User profile update request schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com"
            }
        }


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully"
            }
        }


# Export
__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    "UserUpdateRequest",
    "MessageResponse",
]

