"""
OpsAuditLog model - Audit trail for ops operations
"""

from sqlalchemy import Column, BigInteger, String, Text, Boolean, ForeignKey, Index, JSON, DateTime
from sqlalchemy.orm import relationship
from src.core.database.base import Base
from datetime import datetime, timezone


class OpsAuditLog(Base):
    """
    OpsAuditLog model - Audit trail for operational access and actions
    
    Tracks:
    - Who accessed what data
    - When PII was accessed
    - What actions were performed
    - Request metadata (IP, user agent)
    
    Critical for compliance and security monitoring.
    """
    __tablename__ = "ops_audit_log"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=False)
    
    # Action Details
    action = Column(String(100), nullable=False)  # 'view_priority_queue', 'expand_details', 'review_item'
    resource_type = Column(String(50), nullable=True)  # 'priority_queue', 'complaint', 'booking'
    resource_id = Column(BigInteger, nullable=True)
    
    # PII Access Tracking
    pii_accessed = Column(Boolean, default=False, nullable=False)

    # Request Metadata
    request_metadata = Column(JSON, nullable=True)  # Store request params, filters used
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    staff = relationship("Staff", back_populates="audit_logs")
    
    # Indexes
    __table_args__ = (
        Index('idx_staff_action', 'staff_id', 'action', 'created_at'),
        Index('idx_pii_access', 'pii_accessed', 'created_at'),
        Index('idx_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<OpsAuditLog(id={self.id}, staff_id={self.staff_id}, action={self.action}, pii={self.pii_accessed})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'pii_accessed': self.pii_accessed,
            'request_metadata': self.request_metadata,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

