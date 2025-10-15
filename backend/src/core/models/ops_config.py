"""
OpsConfig model - Runtime configuration for ops features
"""

from sqlalchemy import Column, BigInteger, String, Text, Index
from src.core.database.base import Base, TimestampMixin


class OpsConfig(Base, TimestampMixin):
    """
    OpsConfig model - Runtime configuration for operational features
    
    Allows dynamic configuration of ops behavior without code deployment:
    - Default filters
    - SLA buffer times
    - Rate limits
    - Feature flags
    """
    __tablename__ = "ops_config"
    
    # Primary Key
    id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    
    # Configuration
    config_key = Column(String(100), unique=True, nullable=False)
    config_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_config_key', 'config_key'),
    )
    
    def __repr__(self):
        return f"<OpsConfig(key={self.config_key}, value={self.config_value})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

