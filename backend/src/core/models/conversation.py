# Conversation model

from sqlalchemy import Column, BigInteger, String, Text, Numeric, Integer, Boolean, ForeignKey, Index, Enum, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin
import enum


class MessageRole(str, enum.Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"


class Channel(str, enum.Enum):
    """Communication channel enum"""
    WEB = "web"
    MOBILE = "mobile"
    WHATSAPP = "whatsapp"


class Conversation(Base, TimestampMixin):
    """
    Conversation model - chat history with provenance & quality metrics
    """
    __tablename__ = "conversations"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Session
    session_id = Column(String(100), nullable=False, index=True)
    
    # Message
    role = Column(Enum(MessageRole), nullable=False)
    message = Column(Text, nullable=False)
    
    # NLP
    intent = Column(String(50), nullable=True)
    intent_confidence = Column(Numeric(4, 3), nullable=True)
    
    # Agent Execution (JSON for flexibility)
    agent_calls = Column(JSON, nullable=True, comment='Array of agent execution details')
    
    # Provenance (JSON for source tracking)
    provenance = Column(JSON, nullable=True, comment='Sources used: SQL tables, vector docs, etc')
    
    # Quality Metrics
    grounding_score = Column(Numeric(4, 3), nullable=True)
    faithfulness_score = Column(Numeric(4, 3), nullable=True)
    relevancy_score = Column(Numeric(4, 3), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Review Flag
    flagged_for_review = Column(Boolean, default=False, nullable=False)
    review_reason = Column(String(255), nullable=True)
    
    # Metadata
    channel = Column(Enum(Channel), default=Channel.WEB, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    
    # Indexes
    __table_args__ = (
        Index('idx_session', 'session_id'),
        Index('idx_user', 'user_id'),
        Index('idx_intent', 'intent'),
        Index('idx_flagged', 'flagged_for_review'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id={self.session_id}, role={self.role}, intent={self.intent})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'role': self.role.value if self.role else None,
            'message': self.message,
            'intent': self.intent,
            'intent_confidence': float(self.intent_confidence) if self.intent_confidence else None,
            'agent_calls': self.agent_calls,
            'provenance': self.provenance,
            'grounding_score': float(self.grounding_score) if self.grounding_score else None,
            'faithfulness_score': float(self.faithfulness_score) if self.faithfulness_score else None,
            'relevancy_score': float(self.relevancy_score) if self.relevancy_score else None,
            'response_time_ms': self.response_time_ms,
            'flagged_for_review': self.flagged_for_review,
            'review_reason': self.review_reason,
            'channel': self.channel.value if self.channel else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

