"""
Dialog State Model

Stores conversation state for multi-turn dialog management.
Enables context tracking, slot-filling, and follow-up response handling.
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, JSON, 
    DateTime, ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
import enum

from src.core.database.base import Base, TimestampMixin


class DialogStateType(str, enum.Enum):
    """
    Conversation state types
    
    - IDLE: No active conversation flow
    - COLLECTING_INFO: Gathering required information from user
    - AWAITING_CONFIRMATION: Waiting for user to confirm an action
    - EXECUTING_ACTION: Processing the user's request
    - COMPLETED: Action completed, ready for new intent
    - ERROR: Error occurred, needs recovery
    """
    IDLE = "idle"
    COLLECTING_INFO = "collecting_info"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    EXECUTING_ACTION = "executing_action"
    COMPLETED = "completed"
    ERROR = "error"


class DialogState(Base, TimestampMixin):
    """
    Dialog State Model
    
    Tracks conversation state for context-aware multi-turn dialogs.
    
    Example state for booking flow:
    {
        "session_id": "session_abc123",
        "state": "collecting_info",
        "intent": "booking_management",
        "collected_entities": {
            "service_type": "ac",
            "action": "book",
            "city": "Mumbai"
        },
        "needed_entities": ["date", "time", "ac_type"],
        "pending_action": {
            "action": "create_booking",
            "params": {
                "service_id": 123,
                "user_id": 456
            }
        },
        "context": {
            "last_question": "What type of AC do you have?",
            "attempt_count": 1
        }
    }
    """
    __tablename__ = "dialog_states"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    user_id = Column(
        BigInteger, 
        ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    
    # Session Identifier (links to conversations)
    session_id = Column(
        String(100), 
        nullable=False, 
        unique=True,  # One active state per session
        index=True,
        comment="Unique session identifier from conversations"
    )
    
    # State Information
    state = Column(
        Enum(DialogStateType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DialogStateType.IDLE,
        index=True,
        comment="Current conversation state"
    )
    
    # Intent being processed
    intent = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Current intent being processed (e.g., booking_management)"
    )
    
    # Entities collected so far (JSON)
    collected_entities = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Entities extracted and validated so far"
    )
    
    # Entities still needed (JSON array)
    needed_entities = Column(
        JSON,
        nullable=False,
        default=list,
        comment="List of entity types still required"
    )
    
    # Pending action to execute (JSON)
    pending_action = Column(
        JSON,
        nullable=True,
        comment="Action waiting to be executed after confirmation or info collection"
    )
    
    # Additional context (JSON)
    context = Column(
        JSON,
        nullable=False,
        default=dict,
        comment="Additional context like last question asked, attempt count, etc."
    )
    
    # Expiration
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="State expires after this time (auto-cleanup)"
    )
    
    # Relationships
    user = relationship("User", back_populates="dialog_states")
    
    # Indexes
    __table_args__ = (
        Index('idx_dialog_state_session', 'session_id'),
        Index('idx_dialog_state_user', 'user_id'),
        Index('idx_dialog_state_expires', 'expires_at'),
        Index('idx_dialog_state_intent', 'intent'),
        Index('idx_dialog_state_state', 'state'),
    )
    
    def __repr__(self):
        return (
            f"<DialogState(id={self.id}, session={self.session_id}, "
            f"state={self.state.value}, intent={self.intent})>"
        )
    
    @classmethod
    def create_default_expiry(cls, hours: int = 24) -> datetime:
        """
        Create default expiration time
        
        Args:
            hours: Hours until expiration (default: 24)
            
        Returns:
            Datetime object for expiration
        """
        return datetime.now(timezone.utc) + timedelta(hours=hours)
    
    def is_expired(self) -> bool:
        """
        Check if dialog state has expired

        Returns:
            True if expired, False otherwise
        """
        # Make expires_at timezone-aware if it's naive
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at
    
    def is_active(self) -> bool:
        """
        Check if dialog state is active (not idle, not completed, not expired)
        
        Returns:
            True if active, False otherwise
        """
        return (
            self.state not in [DialogStateType.IDLE, DialogStateType.COMPLETED]
            and not self.is_expired()
        )
    
    def has_pending_action(self) -> bool:
        """
        Check if there's a pending action waiting to be executed
        
        Returns:
            True if pending action exists, False otherwise
        """
        return self.pending_action is not None and len(self.pending_action) > 0
    
    def needs_more_info(self) -> bool:
        """
        Check if more information is needed from user
        
        Returns:
            True if needed_entities is not empty, False otherwise
        """
        return (
            self.state == DialogStateType.COLLECTING_INFO
            and self.needed_entities is not None
            and len(self.needed_entities) > 0
        )
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for JSON serialization
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "state": self.state.value,
            "intent": self.intent,
            "collected_entities": self.collected_entities,
            "needed_entities": self.needed_entities,
            "pending_action": self.pending_action,
            "context": self.context,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

