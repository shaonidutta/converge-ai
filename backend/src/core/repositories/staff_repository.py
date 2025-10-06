"""
Staff Repository
Database operations for Staff model (employees)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_, func
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
import logging

from backend.src.core.models import Staff, Role
from backend.src.core.security import hash_password

logger = logging.getLogger(__name__)


class StaffRepository:
    """Repository for Staff (employee) database operations"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create_staff(
        self,
        employee_id: str,
        role_id: int,
        email: str,
        mobile: str,
        password: str,
        first_name: str,
        last_name: Optional[str] = None,
        **kwargs
    ) -> Staff:
        """
        Create a new staff member
        
        Args:
            employee_id: Employee ID (e.g., EMP001)
            role_id: Role ID
            email: Staff email
            mobile: Staff mobile number
            password: Plain text password (will be hashed)
            first_name: Staff first name
            last_name: Staff last name
            **kwargs: Additional staff fields
            
        Returns:
            Staff: Created staff object
        """
        try:
            # Hash password
            password_hash = hash_password(password)
            
            # Create staff
            staff = Staff(
                employee_id=employee_id,
                role_id=role_id,
                email=email,
                mobile=mobile,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                **kwargs
            )
            
            self.db.add(staff)
            await self.db.commit()
            await self.db.refresh(staff)
            
            logger.info(f"Staff created: id={staff.id}, employee_id={employee_id}")
            return staff
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create staff: {e}")
            raise
    
    async def get_staff_by_id(self, staff_id: int, load_role: bool = True) -> Optional[Staff]:
        """
        Get staff by ID
        
        Args:
            staff_id: Staff ID
            load_role: Whether to load role and permissions
            
        Returns:
            Optional[Staff]: Staff object or None
        """
        try:
            stmt = select(Staff).where(Staff.id == staff_id)
            
            if load_role:
                stmt = stmt.options(
                    selectinload(Staff.role).selectinload(Role.permissions)
                )
            
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get staff by id: {e}")
            return None
    
    async def get_staff_by_email(self, email: str, load_role: bool = True) -> Optional[Staff]:
        """
        Get staff by email
        
        Args:
            email: Staff email
            load_role: Whether to load role and permissions
            
        Returns:
            Optional[Staff]: Staff object or None
        """
        try:
            stmt = select(Staff).where(Staff.email == email)
            
            if load_role:
                stmt = stmt.options(
                    selectinload(Staff.role).selectinload(Role.permissions)
                )
            
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get staff by email: {e}")
            return None
    
    async def get_staff_by_mobile(self, mobile: str, load_role: bool = True) -> Optional[Staff]:
        """
        Get staff by mobile number
        
        Args:
            mobile: Staff mobile number
            load_role: Whether to load role and permissions
            
        Returns:
            Optional[Staff]: Staff object or None
        """
        try:
            stmt = select(Staff).where(Staff.mobile == mobile)
            
            if load_role:
                stmt = stmt.options(
                    selectinload(Staff.role).selectinload(Role.permissions)
                )
            
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get staff by mobile: {e}")
            return None
    
    async def get_staff_by_employee_id(
        self,
        employee_id: str,
        load_role: bool = True
    ) -> Optional[Staff]:
        """
        Get staff by employee ID
        
        Args:
            employee_id: Employee ID (e.g., EMP001)
            load_role: Whether to load role and permissions
            
        Returns:
            Optional[Staff]: Staff object or None
        """
        try:
            stmt = select(Staff).where(Staff.employee_id == employee_id)
            
            if load_role:
                stmt = stmt.options(
                    selectinload(Staff.role).selectinload(Role.permissions)
                )
            
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get staff by employee_id: {e}")
            return None
    
    async def update_staff(
        self,
        staff_id: int,
        **kwargs
    ) -> Optional[Staff]:
        """
        Update staff fields
        
        Args:
            staff_id: Staff ID
            **kwargs: Fields to update
            
        Returns:
            Optional[Staff]: Updated staff object or None
        """
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return await self.get_staff_by_id(staff_id)
            
            # Update staff
            await self.db.execute(
                update(Staff)
                .where(Staff.id == staff_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            # Get updated staff
            staff = await self.get_staff_by_id(staff_id)
            logger.info(f"Staff updated: id={staff_id}, fields={list(update_data.keys())}")
            return staff
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update staff: {e}")
            raise
    
    async def delete_staff(self, staff_id: int, soft_delete: bool = True) -> bool:
        """
        Delete staff (soft or hard delete)
        
        Args:
            staff_id: Staff ID
            soft_delete: If True, mark as inactive; if False, delete from DB
            
        Returns:
            bool: True if successful
        """
        try:
            if soft_delete:
                # Soft delete - mark as inactive
                await self.db.execute(
                    update(Staff)
                    .where(Staff.id == staff_id)
                    .values(is_active=False)
                )
            else:
                # Hard delete - remove from database
                await self.db.execute(
                    delete(Staff).where(Staff.id == staff_id)
                )
            
            await self.db.commit()
            logger.info(f"Staff deleted: id={staff_id}, soft={soft_delete}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete staff: {e}")
            return False
    
    async def update_last_login(self, staff_id: int) -> bool:
        """
        Update staff's last login timestamp
        
        Args:
            staff_id: Staff ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(Staff)
                .where(Staff.id == staff_id)
                .values(last_login=datetime.now(timezone.utc))
            )
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False
    
    async def search_staff(
        self,
        query: Optional[str] = None,
        role_id: Optional[int] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Staff]:
        """
        Search staff with filters
        
        Args:
            query: Search query (name, email, mobile, employee_id)
            role_id: Filter by role
            department: Filter by department
            is_active: Filter by active status
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List[Staff]: List of matching staff
        """
        try:
            # Build query
            stmt = select(Staff).options(
                selectinload(Staff.role).selectinload(Role.permissions)
            )
            
            # Apply filters
            conditions = []
            
            if query:
                search_pattern = f"%{query}%"
                conditions.append(
                    or_(
                        Staff.first_name.ilike(search_pattern),
                        Staff.last_name.ilike(search_pattern),
                        Staff.email.ilike(search_pattern),
                        Staff.mobile.ilike(search_pattern),
                        Staff.employee_id.ilike(search_pattern)
                    )
                )
            
            if role_id is not None:
                conditions.append(Staff.role_id == role_id)
            
            if department:
                conditions.append(Staff.department == department)
            
            if is_active is not None:
                conditions.append(Staff.is_active == is_active)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Apply pagination
            stmt = stmt.limit(limit).offset(offset)
            
            # Execute query
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Failed to search staff: {e}")
            return []


# Export
__all__ = ["StaffRepository"]

