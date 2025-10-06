# User model

from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """
    User model - stores all user accounts (customers, providers, ops staff)
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Basic Info
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Wallet
    wallet_balance = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Referral
    referral_code = Column(String(20), unique=True, nullable=True, index=True)
    referred_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    referrer = relationship("User", remote_side=[id], backref="referrals")
    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user")
    booking_items = relationship("BookingItem", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    priority_queue_items = relationship("PriorityQueue", foreign_keys="[PriorityQueue.user_id]", back_populates="user")
    complaints = relationship("Complaint", foreign_keys="[Complaint.user_id]", back_populates="user")
    complaint_updates = relationship("ComplaintUpdate", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_mobile', 'mobile'),
        Index('idx_referral', 'referral_code'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, mobile={self.mobile}, name={self.first_name} {self.last_name})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'mobile': self.mobile,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'wallet_balance': float(self.wallet_balance) if self.wallet_balance else 0.00,
            'referral_code': self.referral_code,
            'referred_by': self.referred_by,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

