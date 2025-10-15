# Booking and BookingItem models

from sqlalchemy import Column, BigInteger, Integer, String, Numeric, Boolean, ForeignKey, Index, Enum, Date, Time, DateTime
from sqlalchemy.orm import relationship
from src.core.database.base import Base, TimestampMixin
import enum


class PaymentStatus(str, enum.Enum):
    """Payment status enum"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    """Payment method enum"""
    CARD = "card"
    UPI = "upi"
    WALLET = "wallet"
    CASH = "cash"


class SettlementStatus(str, enum.Enum):
    """Settlement status enum"""
    PENDING = "pending"
    COMPLETE = "complete"
    FAILED = "failed"
    INPROGRESS = "inprogress"


class BookingStatus(str, enum.Enum):
    """Booking status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base, TimestampMixin):
    """
    Booking model - order headers with payment info
    """
    __tablename__ = "bookings"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    address_id = Column(BigInteger, ForeignKey('addresses.id', ondelete='RESTRICT'), nullable=False)

    # Order
    order_id = Column(String(50), unique=True, nullable=False)
    booking_number = Column(String(50), unique=True, nullable=False)
    invoice_number = Column(String(100), nullable=True)
    
    # Payment
    payment_gateway_order_id = Column(String(100), nullable=True)
    transaction_id = Column(String(255), nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CARD, nullable=False)
    
    # Amounts
    subtotal = Column(Numeric(10, 2), nullable=False)
    discount = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # GST Details
    sgst = Column(Numeric(5, 2), default=0.00, nullable=False)
    cgst = Column(Numeric(5, 2), default=0.00, nullable=False)
    igst = Column(Numeric(5, 2), default=0.00, nullable=False)
    sgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    cgst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    igst_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    total_gst = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Additional Charges
    convenience_charge = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Total
    total = Column(Numeric(10, 2), nullable=False)
    
    # Partial Payment
    is_partial = Column(Boolean, default=False, nullable=False)
    partial_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    remaining_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    
    # Settlement
    is_settlement = Column(Enum(SettlementStatus), default=SettlementStatus.PENDING, nullable=False)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    # Scheduling
    preferred_date = Column(Date, nullable=False)
    preferred_time = Column(Time, nullable=False)

    # Additional Info
    special_instructions = Column(String(500), nullable=True)

    # Cancellation
    cancellation_reason = Column(String(500), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="bookings")
    address = relationship("Address")
    booking_items = relationship("BookingItem", back_populates="booking", cascade="all, delete-orphan")
    complaints = relationship("Complaint", back_populates="booking")
    
    # Indexes
    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_address', 'address_id'),
        Index('idx_booking_number', 'booking_number', unique=True),
        Index('idx_status', 'status'),
        Index('idx_payment', 'payment_status'),
        Index('idx_settlement', 'is_settlement'),
        Index('idx_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Booking(id={self.id}, order_id={self.order_id}, user_id={self.user_id}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'invoice_number': self.invoice_number,
            'payment_gateway_order_id': self.payment_gateway_order_id,
            'transaction_id': self.transaction_id,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'subtotal': float(self.subtotal) if self.subtotal else 0.00,
            'discount': float(self.discount) if self.discount else 0.00,
            'sgst': float(self.sgst) if self.sgst else 0.00,
            'cgst': float(self.cgst) if self.cgst else 0.00,
            'igst': float(self.igst) if self.igst else 0.00,
            'sgst_amount': float(self.sgst_amount) if self.sgst_amount else 0.00,
            'cgst_amount': float(self.cgst_amount) if self.cgst_amount else 0.00,
            'igst_amount': float(self.igst_amount) if self.igst_amount else 0.00,
            'total_gst': float(self.total_gst) if self.total_gst else 0.00,
            'convenience_charge': float(self.convenience_charge) if self.convenience_charge else 0.00,
            'total': float(self.total) if self.total else 0.00,
            'is_partial': self.is_partial,
            'partial_amount': float(self.partial_amount) if self.partial_amount else 0.00,
            'remaining_amount': float(self.remaining_amount) if self.remaining_amount else 0.00,
            'is_settlement': self.is_settlement.value if self.is_settlement else None,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

