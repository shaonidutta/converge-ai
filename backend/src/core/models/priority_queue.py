# PriorityQueue model

from sqlalchemy import Column, BigInteger, String, Text, Numeric, Integer, Boolean, ForeignKey, Index, Enum, DateTime
from sqlalchemy.orm import relationship
from src.core.database.base import Base, TimestampMixin
import enum


class IntentType(str, enum.Enum):
    """Intent type enum"""
    COMPLAINT = "complaint"
    REFUND = "refund"
    CANCELLATION = "cancellation"
    BOOKING = "booking"


class PriorityQueue(Base, TimestampMixin):
    """
    PriorityQueue model - operations priority system
    """
    __tablename__ = "priority_queue"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reviewed_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)  # DEPRECATED - use reviewed_by_staff_id
    reviewed_by_staff_id = Column(BigInteger, ForeignKey('staff.id', ondelete='SET NULL'), nullable=True)
    
    # Session
    session_id = Column(String(100), nullable=False)
    
    # Intent & Scoring
    intent_type = Column(Enum(IntentType), nullable=False)
    confidence_score = Column(Numeric(4, 3), nullable=False)
    priority_score = Column(Integer, nullable=False)
    sentiment_score = Column(Numeric(4, 3), nullable=True)
    
    # Context
    message_snippet = Column(Text, nullable=True)
    
    # Review Status
    is_reviewed = Column(Boolean, default=False, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    action_taken = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="priority_queue_items")
    reviewer = relationship("User", foreign_keys=[reviewed_by])  # DEPRECATED
    reviewed_by_staff = relationship("Staff", foreign_keys=[reviewed_by_staff_id], back_populates="reviewed_priority_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_priority', 'is_reviewed', 'priority_score', 'created_at'),
        Index('idx_reviewed_by', 'reviewed_by'),
    )
    
    def __repr__(self):
        return f"<PriorityQueue(id={self.id}, intent={self.intent_type}, priority={self.priority_score}, reviewed={self.is_reviewed})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'intent_type': self.intent_type.value if self.intent_type else None,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'priority_score': self.priority_score,
            'sentiment_score': float(self.sentiment_score) if self.sentiment_score else None,
            'message_snippet': self.message_snippet,
            'is_reviewed': self.is_reviewed,
            'reviewed_by': self.reviewed_by,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

