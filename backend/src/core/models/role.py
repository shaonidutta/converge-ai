"""
Role and Permission models for RBAC (Role-Based Access Control)
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.src.core.database.base import Base


def get_current_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class Role(Base):
    """
    Role model - Defines roles in the system (admin, ops_staff, manager, etc.)
    """
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, nullable=False, default=0, index=True)  # Hierarchy level
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False)
    
    # Relationships
    staff_members = relationship('Staff', back_populates='role')
    permission_associations = relationship('RolePermission', back_populates='role', cascade='all, delete-orphan')
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles', viewonly=True)
    
    def __repr__(self):
        return f"<Role(name='{self.name}', level={self.level})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'level': self.level,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Permission(Base):
    """
    Permission model - Defines granular permissions (bookings.view, users.edit, etc.)
    """
    __tablename__ = 'permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    module = Column(String(50), nullable=False, index=True)  # bookings, users, providers, etc.
    action = Column(String(50), nullable=False, index=True)  # create, read, update, delete, etc.
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    
    # Relationships
    role_associations = relationship('RolePermission', back_populates='permission', cascade='all, delete-orphan')
    roles = relationship('Role', secondary='role_permissions', back_populates='permissions', viewonly=True)
    
    def __repr__(self):
        return f"<Permission(name='{self.name}', module='{self.module}', action='{self.action}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'module': self.module,
            'action': self.action,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class RolePermission(Base):
    """
    Junction table for roles and permissions (many-to-many)
    """
    __tablename__ = 'role_permissions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey('permissions.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    
    # Relationships
    role = relationship('Role', back_populates='permission_associations')
    permission = relationship('Permission', back_populates='role_associations')
    
    # Indexes
    __table_args__ = (
        Index('idx_rp_role', 'role_id'),
        Index('idx_rp_permission', 'permission_id'),
        Index('unique_role_permission', 'role_id', 'permission_id', unique=True),
    )
    
    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'role_id': self.role_id,
            'permission_id': self.permission_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

