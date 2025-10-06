# BookingItem model

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, Text, ForeignKey, Index, Enum, Date, Time, DateTime
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin
import enum


class ItemPaymentStatus(str, enum.Enum):
    """Item payment status enum"""
    UNPAID = "unpaid"
    PAID = "paid"
    REFUND = "refund"
    FAILED = "failed"


class ItemStatus(str, enum.Enum):
    """Item status enum"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CancelBy(str, enum.Enum):
    """Cancel by enum"""
    EMPTY = ""
    PROVIDER = "provider"
    CUSTOMER = "customer"


class BookingItem(Base, TimestampMixin):
    """
    BookingItem model - order line items with scheduling
    """
    __tablename__ = "booking_items"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    booking_id = Column(BigInteger, ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    rate_card_id = Column(Integer, ForeignKey('rate_cards.id', ondelete='RESTRICT'), nullable=False)
    provider_id = Column(BigInteger, ForeignKey('providers.id', ondelete='SET NULL'), nullable=True)
    address_id = Column(BigInteger, ForeignKey('addresses.id', ondelete='RESTRICT'), nullable=False)
    
    # Service Details
    service_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    # Amounts
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    final_amount = Column(Numeric(10, 2), nullable=False)
    
    # Scheduling
    scheduled_date = Column(Date, nullable=False)
    scheduled_time_from = Column(Time, nullable=False)
    scheduled_time_to = Column(Time, nullable=False)
    
    # Execution
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    # Cancellation
    cancel_by = Column(Enum(CancelBy), default=CancelBy.EMPTY, nullable=False)
    cancel_reason = Column(Text, nullable=True)
    
    # Payment
    payment_status = Column(Enum(ItemPaymentStatus), default=ItemPaymentStatus.UNPAID, nullable=False)
    
    # Status
    status = Column(Enum(ItemStatus), default=ItemStatus.PENDING, nullable=False)
    
    # Relationships
    booking = relationship("Booking", back_populates="booking_items")
    user = relationship("User", back_populates="booking_items")
    rate_card = relationship("RateCard", back_populates="booking_items")
    provider = relationship("Provider", back_populates="booking_items")
    address = relationship("Address", back_populates="booking_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_booking', 'booking_id'),
        Index('idx_user', 'user_id'),
        Index('idx_provider', 'provider_id', 'status'),
        Index('idx_payment', 'payment_status'),
        Index('idx_scheduled', 'scheduled_date'),
    )
    
    def __repr__(self):
        return f"<BookingItem(id={self.id}, booking_id={self.booking_id}, service={self.service_name}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'user_id': self.user_id,
            'rate_card_id': self.rate_card_id,
            'provider_id': self.provider_id,
            'address_id': self.address_id,
            'service_name': self.service_name,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else 0.00,
            'total_amount': float(self.total_amount) if self.total_amount else 0.00,
            'discount_amount': float(self.discount_amount) if self.discount_amount else 0.00,
            'final_amount': float(self.final_amount) if self.final_amount else 0.00,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'scheduled_time_from': self.scheduled_time_from.isoformat() if self.scheduled_time_from else None,
            'scheduled_time_to': self.scheduled_time_to.isoformat() if self.scheduled_time_to else None,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'cancel_by': self.cancel_by.value if self.cancel_by else "",
            'cancel_reason': self.cancel_reason,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

