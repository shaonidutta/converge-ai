"""
Ops Service
Business logic for ops user management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timezone
from typing import List, Optional
import logging

from src.core.models import Staff, Role, Permission
from src.core.security.password import hash_password, verify_password
from src.core.security.jwt import create_access_token, create_refresh_token
from src.schemas.ops import (
    OpsRegisterRequest,
    OpsLoginRequest,
    OpsAuthResponse,
    OpsUserResponse,
    OpsUpdateRequest,
)
from src.core.repositories.staff_repository import StaffRepository

logger = logging.getLogger(__name__)


class OpsService:
    """Service class for ops user management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.staff_repo = StaffRepository(db)
    
    async def register_ops_user(
        self, 
        request: OpsRegisterRequest,
        current_staff: Staff
    ) -> OpsAuthResponse:
        """
        Register a new ops user
        
        Args:
            request: Registration request
            current_staff: Staff creating the new user
            
        Returns:
            OpsAuthResponse with user data and tokens
            
        Raises:
            ValueError: If validation fails
        """
        # Check for duplicates
        existing_email = await self.staff_repo.get_staff_by_email(request.email)
        if existing_email:
            raise ValueError("Email already registered")

        existing_mobile = await self.staff_repo.get_staff_by_mobile(request.mobile)
        if existing_mobile:
            raise ValueError("Mobile number already registered")

        existing_employee = await self.staff_repo.get_staff_by_employee_id(
            request.employee_id
        )
        if existing_employee:
            raise ValueError("Employee ID already registered")
        
        # Verify role exists
        role_result = await self.db.execute(
            select(Role).where(Role.id == request.role_id, Role.is_active == True)
        )
        role = role_result.scalar_one_or_none()
        
        if not role:
            raise ValueError("Invalid role")
        
        # Create staff
        staff = await self.staff_repo.create_staff(
            employee_id=request.employee_id,
            role_id=request.role_id,
            email=request.email,
            mobile=request.mobile,
            password=request.password,
            first_name=request.first_name,
            last_name=request.last_name,
            department=request.department
        )
        
        # Get permissions
        permissions_result = await self.db.execute(
            select(Permission.code)
            .join(Role.permissions)
            .where(Role.id == staff.role_id)
        )
        permissions = [p[0] for p in permissions_result.all()]
        
        # Generate tokens
        access_token = create_access_token(
            subject=staff.email,
            user_id=staff.id,
            user_type="staff",
            additional_claims={"role": role.name}
        )
        refresh_token = create_refresh_token(
            subject=staff.email,
            user_id=staff.id,
            user_type="staff"
        )
        
        logger.info(
            f"Ops user registered: id={staff.id}, employee_id={staff.employee_id}"
        )

        from src.core.config import settings

        return OpsAuthResponse(
            user=OpsUserResponse(
                id=staff.id,
                employee_id=staff.employee_id,
                email=staff.email,
                mobile=staff.mobile,
                first_name=staff.first_name,
                last_name=staff.last_name,
                department=staff.department,
                is_active=staff.is_active,
                role={
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "level": role.level,
                    "is_active": role.is_active
                },
                created_at=staff.created_at.isoformat() if staff.created_at else None
            ),
            tokens={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            },
            permissions=permissions
        )
    
    async def login_ops_user(self, request: OpsLoginRequest) -> OpsAuthResponse:
        """
        Login ops user
        
        Args:
            request: Login request
            
        Returns:
            OpsAuthResponse with user data and tokens
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find staff by email, mobile, or employee_id
        staff = None
        if "@" in request.identifier:
            staff = await self.staff_repo.get_staff_by_email(request.identifier)
        elif request.identifier.isdigit():
            staff = await self.staff_repo.get_staff_by_mobile(request.identifier)
        else:
            staff = await self.staff_repo.get_staff_by_employee_id(request.identifier)
        
        if not staff:
            raise ValueError("Invalid credentials")
        
        # Verify password
        if not verify_password(request.password, staff.password_hash):
            raise ValueError("Invalid credentials")
        
        # Check if staff is active
        if not staff.is_active:
            raise ValueError("Account is inactive")
        
        # Get role
        role_result = await self.db.execute(
            select(Role).where(Role.id == staff.role_id)
        )
        role = role_result.scalar_one()
        
        # Get permissions
        permissions_result = await self.db.execute(
            select(Permission.name)
            .join(Role.permissions)
            .where(Role.id == staff.role_id)
        )
        permissions = [p[0] for p in permissions_result.all()]
        
        # Update last login
        staff.last_login = datetime.now(timezone.utc)
        await self.db.commit()
        
        # Generate tokens
        access_token = create_access_token(
            subject=staff.email,
            user_id=staff.id,
            user_type="staff",
            additional_claims={"role": role.name}
        )
        refresh_token = create_refresh_token(
            subject=staff.email,
            user_id=staff.id,
            user_type="staff"
        )
        
        logger.info(f"Ops user logged in: id={staff.id}, employee_id={staff.employee_id}")

        from src.core.config import settings

        return OpsAuthResponse(
            user=OpsUserResponse(
                id=staff.id,
                employee_id=staff.employee_id,
                email=staff.email,
                mobile=staff.mobile,
                first_name=staff.first_name,
                last_name=staff.last_name,
                department=staff.department,
                is_active=staff.is_active,
                role={
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "level": role.level,
                    "is_active": role.is_active
                },
                created_at=staff.created_at.isoformat() if staff.created_at else None
            ),
            tokens={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            },
            permissions=permissions
        )
    
    async def list_ops_users(
        self,
        role_id: Optional[int] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[OpsUserResponse]:
        """
        List ops users with filters
        
        Args:
            role_id: Filter by role
            department: Filter by department
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of OpsUserResponse
        """
        query = select(Staff, Role).join(Role, Staff.role_id == Role.id)
        
        if role_id:
            query = query.where(Staff.role_id == role_id)
        
        if department:
            query = query.where(Staff.department == department)
        
        if is_active is not None:
            query = query.where(Staff.is_active == is_active)
        
        query = query.order_by(Staff.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        staff_list = result.all()
        
        return [
            OpsUserResponse(
                id=staff.id,
                employee_id=staff.employee_id,
                email=staff.email,
                mobile=staff.mobile,
                first_name=staff.first_name,
                last_name=staff.last_name,
                department=staff.department,
                is_active=staff.is_active,
                role={
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "description": role.description,
                    "level": role.level,
                    "is_active": role.is_active
                },
                created_at=staff.created_at.isoformat() if staff.created_at else ""
            )
            for staff, role in staff_list
        ]
    
    async def get_ops_user(self, staff_id: int) -> OpsUserResponse:
        """
        Get ops user by ID
        
        Args:
            staff_id: Staff ID
            
        Returns:
            OpsUserResponse
            
        Raises:
            ValueError: If staff not found
        """
        result = await self.db.execute(
            select(Staff, Role)
            .join(Role, Staff.role_id == Role.id)
            .where(Staff.id == staff_id)
        )
        staff_data = result.one_or_none()
        
        if not staff_data:
            raise ValueError("Staff not found")
        
        staff, role = staff_data
        
        return OpsUserResponse(
            id=staff.id,
            employee_id=staff.employee_id,
            email=staff.email,
            mobile=staff.mobile,
            first_name=staff.first_name,
            last_name=staff.last_name,
            department=staff.department,
            is_active=staff.is_active,
            role={
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "level": role.level,
                "is_active": role.is_active
            },
            created_at=staff.created_at.isoformat() if staff.created_at else ""
        )


    async def update_ops_user(
        self,
        staff_id: int,
        request: OpsUpdateRequest
    ) -> OpsUserResponse:
        """
        Update ops user

        Args:
            staff_id: Staff ID
            request: Update request

        Returns:
            OpsUserResponse with updated data

        Raises:
            ValueError: If staff not found or validation fails
        """
        # Get staff
        staff = await self.staff_repo.get_staff_by_id(staff_id)
        if not staff:
            raise ValueError("Staff not found")

        # Check email uniqueness if being changed
        if request.email and request.email != staff.email:
            existing = await self.staff_repo.get_staff_by_email(request.email)
            if existing:
                raise ValueError("Email already in use")
            staff.email = request.email

        # Check mobile uniqueness if being changed
        if request.mobile and request.mobile != staff.mobile:
            existing = await self.staff_repo.get_staff_by_mobile(request.mobile)
            if existing:
                raise ValueError("Mobile number already in use")
            staff.mobile = request.mobile

        # Update other fields
        if request.first_name is not None:
            staff.first_name = request.first_name

        if request.last_name is not None:
            staff.last_name = request.last_name

        if request.department is not None:
            staff.department = request.department

        if request.role_id is not None:
            # Verify role exists
            role_result = await self.db.execute(
                select(Role).where(
                    Role.id == request.role_id,
                    Role.is_active == True
                )
            )
            role = role_result.scalar_one_or_none()
            if not role:
                raise ValueError("Invalid role")
            staff.role_id = request.role_id

        if request.is_active is not None:
            staff.is_active = request.is_active

        await self.db.commit()
        await self.db.refresh(staff)

        # Get role name
        role_result = await self.db.execute(
            select(Role).where(Role.id == staff.role_id)
        )
        role = role_result.scalar_one()

        logger.info(f"Ops user updated: id={staff.id}")

        return OpsUserResponse(
            id=staff.id,
            employee_id=staff.employee_id,
            email=staff.email,
            mobile=staff.mobile,
            first_name=staff.first_name,
            last_name=staff.last_name,
            department=staff.department,
            is_active=staff.is_active,
            role={
                "id": role.id,
                "name": role.name,
                "display_name": role.display_name,
                "description": role.description,
                "level": role.level,
                "is_active": role.is_active
            },
            created_at=staff.created_at.isoformat() if staff.created_at else ""
        )


# Export
__all__ = ["OpsService"]

