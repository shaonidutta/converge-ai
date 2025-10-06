# Complaint and ComplaintUpdate models

from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, Index, Enum, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin
import enum


class ComplaintType(str, enum.Enum):
    """Complaint type enum"""
    SERVICE_QUALITY = "service_quality"
    PROVIDER_BEHAVIOR = "provider_behavior"
    BILLING = "billing"
    DELAY = "delay"
    CANCELLATION_ISSUE = "cancellation_issue"
    REFUND_ISSUE = "refund_issue"
    OTHER = "other"


class ComplaintPriority(str, enum.Enum):
    """Complaint priority enum"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplaintStatus(str, enum.Enum):
    """Complaint status enum"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ESCALATED = "escalated"


class Complaint(Base, TimestampMixin):
    """
    Complaint model - customer complaints with AI priority
    """
    __tablename__ = "complaints"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    booking_id = Column(BigInteger, ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    assigned_to = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)  # DEPRECATED - use assigned_to_staff_id
    resolved_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)  # DEPRECATED - use resolved_by_staff_id
    assigned_to_staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='SET NULL'), nullable=True)
    resolved_by_staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='SET NULL'), nullable=True)
    
    # Session
    session_id = Column(String(100), nullable=True)
    
    # Complaint Details
    complaint_type = Column(Enum(ComplaintType), nullable=False)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Priority & Status
    priority = Column(Enum(ComplaintPriority), default=ComplaintPriority.MEDIUM, nullable=False)
    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.OPEN, nullable=False)
    
    # Assignment
    assigned_at = Column(DateTime, nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # SLA Tracking
    response_due_at = Column(DateTime, nullable=True)
    resolution_due_at = Column(DateTime, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="complaints")
    user = relationship("User", foreign_keys=[user_id], back_populates="complaints")
    assignee = relationship("User", foreign_keys=[assigned_to])  # DEPRECATED
    resolver = relationship("User", foreign_keys=[resolved_by])  # DEPRECATED
    assigned_to_staff = relationship("Staff", foreign_keys=[assigned_to_staff_id], back_populates="assigned_complaints")
    resolved_by_staff = relationship("Staff", foreign_keys=[resolved_by_staff_id], back_populates="resolved_complaints")
    updates = relationship("ComplaintUpdate", back_populates="complaint", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_status', 'status'),
        Index('idx_priority', 'priority'),
        Index('idx_user', 'user_id'),
        Index('idx_booking', 'booking_id'),
        Index('idx_assigned', 'assigned_to', 'status'),
        Index('idx_created', 'created_at'),
        Index('idx_sla', 'response_due_at', 'resolution_due_at'),
    )
    
    def __repr__(self):
        return f"<Complaint(id={self.id}, type={self.complaint_type}, status={self.status}, priority={self.priority})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'complaint_type': self.complaint_type.value if self.complaint_type else None,
            'subject': self.subject,
            'description': self.description,
            'priority': self.priority.value if self.priority else None,
            'status': self.status.value if self.status else None,
            'assigned_to': self.assigned_to,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'resolution': self.resolution,
            'resolved_by': self.resolved_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'response_due_at': self.response_due_at.isoformat() if self.response_due_at else None,
            'resolution_due_at': self.resolution_due_at.isoformat() if self.resolution_due_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class ComplaintUpdate(Base, TimestampMixin):
    """
    ComplaintUpdate model - updates/comments on complaints
    """
    __tablename__ = "complaint_updates"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    complaint_id = Column(BigInteger, ForeignKey('complaints.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='CASCADE'), nullable=True)  # If update is from staff
    
    # Update Details
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False, nullable=False, comment='Internal notes not visible to customer')
    
    # Attachments (optional)
    attachments = Column(JSON, nullable=True, comment='Array of attachment URLs')
    
    # Relationships
    complaint = relationship("Complaint", back_populates="updates")
    user = relationship("User", back_populates="complaint_updates")
    staff = relationship("Staff", back_populates="complaint_updates")
    
    # Indexes
    __table_args__ = (
        Index('idx_complaint', 'complaint_id'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ComplaintUpdate(id={self.id}, complaint_id={self.complaint_id}, is_internal={self.is_internal})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'complaint_id': self.complaint_id,
            'user_id': self.user_id,
            'comment': self.comment,
            'is_internal': self.is_internal,
            'attachments': self.attachments,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

