"""
User model for customers
Includes authentication fields
"""

from sqlalchemy import Column, BigInteger, String, Numeric, Boolean, ForeignKey, Index, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.src.core.database.base import Base, TimestampMixin


def get_current_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class User(Base, TimestampMixin):
    """
    User model - stores all user accounts (customers, providers, ops staff)
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Basic Info
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Authentication
    password_hash = Column(String(255), nullable=True)  # Nullable for social login users
    email_verified = Column(Boolean, default=False, nullable=False)
    mobile_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime, nullable=True)

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
    
    def to_dict(self, include_sensitive: bool = False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'mobile': self.mobile,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email_verified': self.email_verified,
            'mobile_verified': self.mobile_verified,
            'wallet_balance': float(self.wallet_balance) if self.wallet_balance else 0.00,
            'referral_code': self.referral_code,
            'referred_by': self.referred_by,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_sensitive:
            data['password_hash'] = self.password_hash

        return data

