# Category and Subcategory models

from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.core.database.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """
    Category model - main service categories
    """
    __tablename__ = "categories"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(500), nullable=True)
    
    # Display
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan")
    rate_cards = relationship("RateCard", back_populates="category")
    
    # Indexes
    __table_args__ = (
        Index('idx_active', 'is_active', 'display_order'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image': self.image,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Subcategory(Base, TimestampMixin):
    """
    Subcategory model - service subcategories under categories
    """
    __tablename__ = "subcategories"
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # Foreign Key
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    
    # Basic Info
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image = Column(String(500), nullable=True)
    
    # Display
    display_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    category = relationship("Category", back_populates="subcategories")
    rate_cards = relationship("RateCard", back_populates="subcategory")
    
    # Indexes
    __table_args__ = (
        Index('idx_category', 'category_id', 'is_active'),
        Index('unique_slug', 'category_id', 'slug', unique=True),
    )
    
    def __repr__(self):
        return f"<Subcategory(id={self.id}, name={self.name}, category_id={self.category_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'image': self.image,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

