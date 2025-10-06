# Provider model

from sqlalchemy import Column, BigInteger, String, Numeric, Integer, Boolean, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin


class Provider(Base, TimestampMixin):
    """
    Provider model - service providers
    """
    __tablename__ = "providers"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Basic Info
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    mobile = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    
    # Service Coverage (JSON array of pincodes)
    service_pincodes = Column(JSON, nullable=True)
    
    # Rating
    avg_rating = Column(Numeric(3, 2), default=0.00, nullable=False)
    total_bookings = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    booking_items = relationship("BookingItem", back_populates="provider")
    
    # Indexes
    __table_args__ = (
        Index('idx_mobile', 'mobile'),
        Index('idx_active', 'is_active', 'is_verified'),
    )
    
    def __repr__(self):
        return f"<Provider(id={self.id}, name={self.first_name} {self.last_name}, mobile={self.mobile})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile': self.mobile,
            'email': self.email,
            'service_pincodes': self.service_pincodes,
            'avg_rating': float(self.avg_rating) if self.avg_rating else 0.00,
            'total_bookings': self.total_bookings,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

