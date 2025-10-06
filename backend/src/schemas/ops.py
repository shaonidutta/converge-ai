"""
Ops user schemas
Pydantic models for ops user management
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import re


class OpsRegisterRequest(BaseModel):
    """Ops user registration request schema"""
    email: EmailStr = Field(..., description="Ops user email address")
    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name")
    employee_id: str = Field(..., min_length=3, max_length=20, description="Employee ID")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    role_id: int = Field(..., description="Role ID to assign")
    
    @field_validator('mobile')
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        """Validate mobile number format"""
        mobile = re.sub(r'[^\d+]', '', v)
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
                "email": "ops@convergeai.com",
                "mobile": "+919876543210",
                "password": "OpsPass123!",
                "first_name": "Operations",
                "last_name": "User",
                "employee_id": "OPS001",
                "department": "Operations",
                "role_id": 2
            }
        }


class OpsLoginRequest(BaseModel):
    """Ops user login request schema"""
    identifier: str = Field(..., description="Email, mobile, or employee ID")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "ops@convergeai.com",
                "password": "OpsPass123!"
            }
        }


class RoleResponse(BaseModel):
    """Role response schema"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    level: int
    is_active: bool
    
    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    """Permission response schema"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    resource: str
    action: str
    
    class Config:
        from_attributes = True


class OpsUserResponse(BaseModel):
    """Ops user response schema"""
    id: int
    email: str
    mobile: str
    first_name: Optional[str]
    last_name: Optional[str]
    employee_id: str
    department: Optional[str]
    is_active: bool
    role: Optional[RoleResponse]
    created_at: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "ops@convergeai.com",
                "mobile": "+919876543210",
                "first_name": "Operations",
                "last_name": "User",
                "employee_id": "OPS001",
                "department": "Operations",
                "is_active": True,
                "role": {
                    "id": 2,
                    "name": "ops_manager",
                    "display_name": "Operations Manager",
                    "description": "Manages operations",
                    "level": 5,
                    "is_active": True
                },
                "created_at": "2025-10-07T12:00:00Z"
            }
        }


class OpsAuthResponse(BaseModel):
    """Ops authentication response with user and tokens"""
    user: OpsUserResponse
    tokens: dict
    permissions: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "ops@convergeai.com",
                    "mobile": "+919876543210",
                    "first_name": "Operations",
                    "last_name": "User",
                    "employee_id": "OPS001",
                    "department": "Operations",
                    "is_active": True,
                    "role": {
                        "id": 2,
                        "name": "ops_manager",
                        "display_name": "Operations Manager",
                        "description": "Manages operations",
                        "level": 5,
                        "is_active": True
                    },
                    "created_at": "2025-10-07T12:00:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                },
                "permissions": [
                    "bookings.view",
                    "bookings.edit",
                    "users.view"
                ]
            }
        }


class OpsUpdateRequest(BaseModel):
    """Ops user update request schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    role_id: Optional[int] = None
    is_active: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Updated",
                "last_name": "Name",
                "department": "Customer Support",
                "role_id": 3,
                "is_active": True
            }
        }


# Export
__all__ = [
    "OpsRegisterRequest",
    "OpsLoginRequest",
    "RoleResponse",
    "PermissionResponse",
    "OpsUserResponse",
    "OpsAuthResponse",
    "OpsUpdateRequest",
]

