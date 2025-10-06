"""
User Repository
Database operations for User model (customers)
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, or_, and_, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from backend.src.core.models import User, Address
from backend.src.core.security import hash_password

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for User (customer) database operations"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize repository
        
        Args:
            db: Async database session
        """
        self.db = db
    
    async def create_user(
        self,
        email: str,
        mobile: str,
        password: str,
        first_name: str,
        last_name: Optional[str] = None,
        **kwargs
    ) -> User:
        """
        Create a new user
        
        Args:
            email: User email
            mobile: User mobile number
            password: Plain text password (will be hashed)
            first_name: User first name
            last_name: User last name
            **kwargs: Additional user fields
            
        Returns:
            User: Created user object
            
        Example:
            >>> user = await repo.create_user(
            ...     email="user@example.com",
            ...     mobile="9876543210",
            ...     password="SecurePass123!",
            ...     first_name="John",
            ...     last_name="Doe"
            ... )
        """
        try:
            # Hash password
            password_hash = hash_password(password)
            
            # Create user
            user = User(
                email=email,
                mobile=mobile,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name,
                **kwargs
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"User created: id={user.id}, email={email}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by id: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            Optional[User]: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            return None
    
    async def get_user_by_mobile(self, mobile: str) -> Optional[User]:
        """
        Get user by mobile number
        
        Args:
            mobile: User mobile number
            
        Returns:
            Optional[User]: User object or None
        """
        try:
            result = await self.db.execute(
                select(User).where(User.mobile == mobile)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by mobile: {e}")
            return None
    
    async def get_user_by_email_or_mobile(
        self,
        email: Optional[str] = None,
        mobile: Optional[str] = None
    ) -> Optional[User]:
        """
        Get user by email or mobile
        
        Args:
            email: User email
            mobile: User mobile number
            
        Returns:
            Optional[User]: User object or None
        """
        try:
            conditions = []
            if email:
                conditions.append(User.email == email)
            if mobile:
                conditions.append(User.mobile == mobile)
            
            if not conditions:
                return None
            
            result = await self.db.execute(
                select(User).where(or_(*conditions))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Failed to get user by email or mobile: {e}")
            return None
    
    async def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Optional[User]:
        """
        Update user fields
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Optional[User]: Updated user object or None
            
        Example:
            >>> user = await repo.update_user(
            ...     user_id=123,
            ...     first_name="Jane",
            ...     email_verified=True
            ... )
        """
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                return await self.get_user_by_id(user_id)
            
            # Update user
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(**update_data)
            )
            await self.db.commit()
            
            # Get updated user
            user = await self.get_user_by_id(user_id)
            logger.info(f"User updated: id={user_id}, fields={list(update_data.keys())}")
            return user
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to update user: {e}")
            raise
    
    async def delete_user(self, user_id: int, soft_delete: bool = True) -> bool:
        """
        Delete user (soft or hard delete)
        
        Args:
            user_id: User ID
            soft_delete: If True, mark as inactive; if False, delete from DB
            
        Returns:
            bool: True if successful
        """
        try:
            if soft_delete:
                # Soft delete - mark as inactive
                await self.db.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(is_active=False)
                )
            else:
                # Hard delete - remove from database
                await self.db.execute(
                    delete(User).where(User.id == user_id)
                )
            
            await self.db.commit()
            logger.info(f"User deleted: id={user_id}, soft={soft_delete}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to delete user: {e}")
            return False
    
    async def search_users(
        self,
        query: Optional[str] = None,
        is_active: Optional[bool] = None,
        email_verified: Optional[bool] = None,
        mobile_verified: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """
        Search users with filters
        
        Args:
            query: Search query (name, email, mobile)
            is_active: Filter by active status
            email_verified: Filter by email verification
            mobile_verified: Filter by mobile verification
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            List[User]: List of matching users
        """
        try:
            # Build query
            stmt = select(User)
            
            # Apply filters
            conditions = []
            
            if query:
                search_pattern = f"%{query}%"
                conditions.append(
                    or_(
                        User.first_name.ilike(search_pattern),
                        User.last_name.ilike(search_pattern),
                        User.email.ilike(search_pattern),
                        User.mobile.ilike(search_pattern)
                    )
                )
            
            if is_active is not None:
                conditions.append(User.is_active == is_active)
            
            if email_verified is not None:
                conditions.append(User.email_verified == email_verified)
            
            if mobile_verified is not None:
                conditions.append(User.mobile_verified == mobile_verified)
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Apply pagination
            stmt = stmt.limit(limit).offset(offset)
            
            # Execute query
            result = await self.db.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Failed to search users: {e}")
            return []
    
    async def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful
        """
        try:
            await self.db.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_login=datetime.now(timezone.utc))
            )
            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
            return False


# Export
__all__ = ["UserRepository"]

