# RateCard model

from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from src.core.database.base import Base, TimestampMixin


class RateCard(Base, TimestampMixin):
    """
    RateCard model - pricing for services with variants
    """
    __tablename__ = "rate_cards"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    subcategory_id = Column(Integer, ForeignKey('subcategories.id', ondelete='CASCADE'), nullable=False)
    
    # Pricing
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    strike_price = Column(Numeric(10, 2), nullable=True)

    # Availability - Now managed through rate_card_pincodes junction table
    # available_pincodes = Column(JSON, nullable=True)  # REMOVED - use pincodes relationship instead

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="rate_cards")
    subcategory = relationship("Subcategory", back_populates="rate_cards")
    booking_items = relationship("BookingItem", back_populates="rate_card")

    # New pincode relationships (optimized)
    pincode_associations = relationship(
        'RateCardPincode',
        back_populates='rate_card',
        cascade='all, delete-orphan'
    )

    pincodes = relationship(
        'Pincode',
        secondary='rate_card_pincodes',
        back_populates='rate_cards',
        viewonly=True
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_category_sub', 'category_id', 'subcategory_id', 'is_active'),
    )
    
    def __repr__(self):
        return f"<RateCard(id={self.id}, name={self.name}, price={self.price})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'subcategory_id': self.subcategory_id,
            'name': self.name,
            'price': float(self.price) if self.price else 0.00,
            'strike_price': float(self.strike_price) if self.strike_price else None,
            'available_pincodes': [p.pincode for p in self.pincodes] if self.pincodes else [],  # Get from relationship
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

