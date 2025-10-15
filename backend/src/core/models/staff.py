"""
Staff model for employees/staff members
Separate from users (customers) with proper RBAC
"""

from sqlalchemy import Column, BigInteger, Integer, String, Boolean, DateTime, Date, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.core.database.base import Base


def get_current_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class Staff(Base):
    """
    Staff model - Employees/Staff members (ops, admin, managers, etc.)
    Separate from users (customers)
    """
    __tablename__ = 'staff'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Employee Info
    employee_id = Column(String(50), unique=True, nullable=False, index=True)  # EMP001, EMP002, etc.
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    
    # Personal Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Employment Details
    department = Column(String(100), nullable=True)
    designation = Column(String(100), nullable=True)
    reporting_to = Column(BigInteger, ForeignKey('staff.id', ondelete='SET NULL'), nullable=True, index=True)
    date_of_joining = Column(Date, nullable=True)
    date_of_leaving = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False)
    
    # Relationships
    role = relationship('Role', back_populates='staff_members')
    
    # Self-referential relationship for reporting structure
    manager = relationship('Staff', remote_side=[id], backref='subordinates')
    
    # Sessions
    sessions = relationship('StaffSession', back_populates='staff', cascade='all, delete-orphan')
    
    # Activity logs
    activity_logs = relationship('StaffActivityLog', back_populates='staff', cascade='all, delete-orphan')
    
    # Relationships to other tables
    reviewed_priority_items = relationship('PriorityQueue', foreign_keys='PriorityQueue.reviewed_by_staff_id', back_populates='reviewed_by_staff')
    assigned_complaints = relationship('Complaint', foreign_keys='Complaint.assigned_to_staff_id', back_populates='assigned_to_staff')
    resolved_complaints = relationship('Complaint', foreign_keys='Complaint.resolved_by_staff_id', back_populates='resolved_by_staff')
    complaint_updates = relationship('ComplaintUpdate', back_populates='staff')

    # Audit logs
    audit_logs = relationship('OpsAuditLog', back_populates='staff', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Staff(employee_id='{self.employee_id}', name='{self.first_name} {self.last_name}')>"
    
    def to_dict(self, include_permissions=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'mobile': self.mobile,
            'department': self.department,
            'designation': self.designation,
            'reporting_to': self.reporting_to,
            'date_of_joining': self.date_of_joining.isoformat() if self.date_of_joining else None,
            'date_of_leaving': self.date_of_leaving.isoformat() if self.date_of_leaving else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'role': self.role.to_dict() if self.role else None
        }
        
        if include_permissions and self.role:
            data['permissions'] = [p.to_dict() for p in self.role.permissions]
        
        return data
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if staff has a specific permission"""
        if not self.role or not self.role.permissions:
            return False
        return any(p.name == permission_name for p in self.role.permissions)
    
    def has_any_permission(self, permission_names: list) -> bool:
        """Check if staff has any of the specified permissions"""
        if not self.role or not self.role.permissions:
            return False
        staff_permissions = {p.name for p in self.role.permissions}
        return bool(staff_permissions.intersection(set(permission_names)))
    
    def has_all_permissions(self, permission_names: list) -> bool:
        """Check if staff has all of the specified permissions"""
        if not self.role or not self.role.permissions:
            return False
        staff_permissions = {p.name for p in self.role.permissions}
        return set(permission_names).issubset(staff_permissions)


class StaffSession(Base):
    """
    Staff session model - Track staff login sessions
    """
    __tablename__ = 'staff_sessions'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    login_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    logout_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    staff = relationship('Staff', back_populates='sessions')
    
    def __repr__(self):
        return f"<StaffSession(staff_id={self.staff_id}, token='{self.session_token[:20]}...')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'session_token': self.session_token,
            'ip_address': self.ip_address,
            'login_at': self.login_at.isoformat() if self.login_at else None,
            'logout_at': self.logout_at.isoformat() if self.logout_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }


class StaffActivityLog(Base):
    """
    Staff activity log model - Audit trail for staff actions
    """
    __tablename__ = 'staff_activity_log'
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    module = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(BigInteger, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False, index=True)
    
    # Relationships
    staff = relationship('Staff', back_populates='activity_logs')
    
    # Indexes
    __table_args__ = (
        Index('idx_activity_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<StaffActivityLog(staff_id={self.staff_id}, action='{self.action}', module='{self.module}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'action': self.action,
            'module': self.module,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

