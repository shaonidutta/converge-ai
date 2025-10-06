# Address model

from sqlalchemy import Column, BigInteger, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.core.database.base import Base, TimestampMixin


class Address(Base, TimestampMixin):
    """
    Address model - user delivery/service addresses
    """
    __tablename__ = "addresses"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Address
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    
    # Contact
    contact_name = Column(String(100), nullable=True)
    contact_mobile = Column(String(15), nullable=True)
    
    # Flags
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="addresses")
    booking_items = relationship("BookingItem", back_populates="address")
    
    # Indexes
    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_pincode', 'pincode'),
    )
    
    def __repr__(self):
        return f"<Address(id={self.id}, user_id={self.user_id}, city={self.city}, pincode={self.pincode})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'pincode': self.pincode,
            'contact_name': self.contact_name,
            'contact_mobile': self.contact_mobile,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

