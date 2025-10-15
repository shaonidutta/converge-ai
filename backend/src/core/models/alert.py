"""
Alert models for notification system
Supports in-app notifications, email, SMS, etc.
"""

from sqlalchemy import Column, BigInteger, String, Boolean, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.core.database.base import Base


def get_current_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class Alert(Base):
    """
    Alert model - System notifications for staff members
    Supports various alert types and severities
    """
    __tablename__ = 'alerts'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Alert Info
    alert_type = Column(String(50), nullable=False, index=True)  # 'sla_breach', 'critical_complaint', etc.
    severity = Column(String(20), nullable=False, index=True)  # 'info', 'warning', 'critical'
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related Resource
    resource_type = Column(String(50), nullable=True)  # 'complaint', 'booking', etc.
    resource_id = Column(BigInteger, nullable=True)
    
    # Assignment
    assigned_to_staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=True, index=True)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    is_dismissed = Column(Boolean, default=False, nullable=False)

    # Additional Data
    alert_metadata = Column(JSON, nullable=True)  # Additional alert data (renamed from 'metadata')
    
    # Timestamps
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Relationships
    assigned_to_staff = relationship('Staff', back_populates='alerts')
    
    # Indexes
    __table_args__ = (
        Index('idx_staff_unread', 'assigned_to_staff_id', 'is_read', 'created_at'),
        Index('idx_type_severity', 'alert_type', 'severity', 'created_at'),
        Index('idx_resource', 'resource_type', 'resource_id'),
    )
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity}, staff_id={self.assigned_to_staff_id})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'assigned_to_staff_id': self.assigned_to_staff_id,
            'is_read': self.is_read,
            'is_dismissed': self.is_dismissed,
            'metadata': self.alert_metadata,  # Expose as 'metadata' in API
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'dismissed_at': self.dismissed_at.isoformat() if self.dismissed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }


class AlertRule(Base):
    """
    AlertRule model - Configurable rules for automatic alert generation
    Supports SLA, threshold, and event-based rules
    """
    __tablename__ = 'alert_rules'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Rule Info
    rule_name = Column(String(100), unique=True, nullable=False)
    rule_type = Column(String(50), nullable=False, index=True)  # 'sla', 'threshold', 'event'
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    
    # Configuration
    conditions = Column(JSON, nullable=False)  # Rule conditions
    alert_config = Column(JSON, nullable=False)  # Alert configuration
    
    # Audit
    created_by_staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='SET NULL'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False)
    
    # Relationships
    created_by_staff = relationship('Staff', foreign_keys=[created_by_staff_id])
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name={self.rule_name}, type={self.rule_type}, enabled={self.is_enabled})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'rule_name': self.rule_name,
            'rule_type': self.rule_type,
            'is_enabled': self.is_enabled,
            'conditions': self.conditions,
            'alert_config': self.alert_config,
            'created_by_staff_id': self.created_by_staff_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class AlertSubscription(Base):
    """
    AlertSubscription model - Staff alert preferences
    Controls which alerts staff members receive and through which channels
    """
    __tablename__ = 'alert_subscriptions'
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Subscription Info
    staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False, index=True)
    
    # Delivery Channels
    delivery_channels = Column(JSON, nullable=True)  # ['in_app', 'email', 'sms']
    
    # Timestamps
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False)
    
    # Relationships
    staff = relationship('Staff', back_populates='alert_subscriptions')
    
    # Constraints
    __table_args__ = (
        Index('unique_subscription', 'staff_id', 'alert_type', unique=True),
        Index('idx_staff_enabled', 'staff_id', 'is_enabled'),
    )
    
    def __repr__(self):
        return f"<AlertSubscription(id={self.id}, staff_id={self.staff_id}, type={self.alert_type}, enabled={self.is_enabled})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'staff_id': self.staff_id,
            'alert_type': self.alert_type,
            'is_enabled': self.is_enabled,
            'delivery_channels': self.delivery_channels,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

