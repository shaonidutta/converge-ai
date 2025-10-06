"""
Pincode model for optimized pincode management
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from backend.src.core.database.base import Base


def get_current_timestamp():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


class Pincode(Base):
    """
    Pincode master table
    Stores all serviceable pincodes with city and state information
    """
    __tablename__ = 'pincodes'
    
    id = Column(Integer, primary_key=True, index=True)
    pincode = Column(String(6), unique=True, nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    is_serviceable = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    updated_at = Column(DateTime, default=get_current_timestamp, onupdate=get_current_timestamp, nullable=False)
    
    # Relationships
    rate_card_associations = relationship(
        'RateCardPincode',
        back_populates='pincode',
        cascade='all, delete-orphan'
    )
    
    provider_associations = relationship(
        'ProviderPincode',
        back_populates='pincode',
        cascade='all, delete-orphan'
    )
    
    # Many-to-many relationships through association tables
    rate_cards = relationship(
        'RateCard',
        secondary='rate_card_pincodes',
        back_populates='pincodes',
        viewonly=True
    )
    
    providers = relationship(
        'Provider',
        secondary='provider_pincodes',
        back_populates='pincodes',
        viewonly=True
    )
    
    def __repr__(self):
        return f"<Pincode(pincode='{self.pincode}', city='{self.city}', state='{self.state}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'pincode': self.pincode,
            'city': self.city,
            'state': self.state,
            'is_serviceable': self.is_serviceable,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class RateCardPincode(Base):
    """
    Junction table for rate_cards and pincodes (many-to-many)
    """
    __tablename__ = 'rate_card_pincodes'
    
    id = Column(Integer, primary_key=True, index=True)
    rate_card_id = Column(Integer, nullable=False, index=True)
    pincode_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    
    # Relationships
    rate_card = relationship('RateCard', back_populates='pincode_associations')
    pincode = relationship('Pincode', back_populates='rate_card_associations')
    
    # Indexes
    __table_args__ = (
        Index('idx_rate_card', 'rate_card_id'),
        Index('idx_pincode_rcp', 'pincode_id'),
        Index('unique_rate_card_pincode', 'rate_card_id', 'pincode_id', unique=True),
    )
    
    def __repr__(self):
        return f"<RateCardPincode(rate_card_id={self.rate_card_id}, pincode_id={self.pincode_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'rate_card_id': self.rate_card_id,
            'pincode_id': self.pincode_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ProviderPincode(Base):
    """
    Junction table for providers and pincodes (many-to-many)
    """
    __tablename__ = 'provider_pincodes'

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, nullable=False, index=True)  # BigInteger to match providers.id
    pincode_id = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=get_current_timestamp, nullable=False)
    
    # Relationships
    provider = relationship('Provider', back_populates='pincode_associations')
    pincode = relationship('Pincode', back_populates='provider_associations')
    
    # Indexes
    __table_args__ = (
        Index('idx_provider', 'provider_id'),
        Index('idx_pincode_pp', 'pincode_id'),
        Index('unique_provider_pincode', 'provider_id', 'pincode_id', unique=True),
    )
    
    def __repr__(self):
        return f"<ProviderPincode(provider_id={self.provider_id}, pincode_id={self.pincode_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'provider_id': self.provider_id,
            'pincode_id': self.pincode_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

