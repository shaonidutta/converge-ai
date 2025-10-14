"""
Cart model
Shopping cart for users
"""

from sqlalchemy import Column, Integer, BigInteger, ForeignKey, DECIMAL, DateTime, func
from sqlalchemy.orm import relationship
from backend.src.core.database.base import Base, TimestampMixin


class Cart(Base, TimestampMixin):
    """
    Cart model - User shopping cart

    Stores cart items for users before booking
    """
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, items={len(self.items) if self.items else 0})>"


class CartItem(Base, TimestampMixin):
    """
    Cart Item model - Individual items in cart

    Stores rate card, quantity, and pricing
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    rate_card_id = Column(Integer, ForeignKey("rate_cards.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    rate_card = relationship("RateCard")
    
    def __repr__(self):
        return f"<CartItem(id={self.id}, cart_id={self.cart_id}, rate_card_id={self.rate_card_id}, quantity={self.quantity})>"

