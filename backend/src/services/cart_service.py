"""
Cart Service
Business logic for cart management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from typing import Optional
import logging

from src.core.models import User, Cart, CartItem, RateCard, Subcategory
from src.schemas.customer import (
    AddToCartRequest,
    UpdateCartItemRequest,
    CartResponse,
    CartItemResponse,
)

logger = logging.getLogger(__name__)


class CartService:
    """Service class for cart management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_cart(self, user_id: int) -> Cart:
        """
        Get user's cart or create if doesn't exist
        
        Args:
            user_id: User ID
            
        Returns:
            Cart object
        """
        result = await self.db.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)
            logger.info(f"Cart created: user_id={user_id}")
        
        return cart
    
    async def get_cart(self, user: User) -> CartResponse:
        """
        Get user's cart with items

        Args:
            user: Current user

        Returns:
            CartResponse with cart items
        """
        logger.info(f"Getting cart for user_id: {user.id}")

        # Get or create cart
        logger.debug("Getting or creating cart")
        cart = await self.get_or_create_cart(user.id)
        logger.debug(f"Cart found/created: cart_id={cart.id}")

        # Get cart items with rate card and subcategory details
        logger.debug("Fetching cart items with rate card and subcategory details")
        result = await self.db.execute(
            select(CartItem, RateCard, Subcategory)
            .join(RateCard, CartItem.rate_card_id == RateCard.id)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(CartItem.cart_id == cart.id)
        )
        items = result.all()
        logger.debug(f"Found {len(items)} cart items")

        # Calculate total
        total_amount = sum(item[0].total_price for item in items)
        logger.debug(f"Total amount: {total_amount}")
        
        # Build response
        cart_items = [
            CartItemResponse(
                id=item[0].id,
                rate_card_id=item[0].rate_card_id,
                rate_card_name=item[1].name,
                subcategory_id=item[2].id,
                subcategory_name=item[2].name,
                quantity=item[0].quantity,
                unit_price=item[0].unit_price,
                total_price=item[0].total_price
            )
            for item in items
        ]

        return CartResponse(
            items=cart_items,
            total_items=len(cart_items),
            total_amount=total_amount
        )
    
    async def add_to_cart(
        self, 
        request: AddToCartRequest, 
        user: User
    ) -> CartItemResponse:
        """
        Add item to cart
        
        Args:
            request: Add to cart request
            user: Current user
            
        Returns:
            CartItemResponse with added item
            
        Raises:
            ValueError: If rate card not found or inactive
        """
        # Get or create cart
        cart = await self.get_or_create_cart(user.id)
        
        # Verify rate card exists and is active
        rate_card_result = await self.db.execute(
            select(RateCard, Subcategory)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(
                RateCard.id == request.rate_card_id,
                RateCard.is_active == True
            )
        )
        rate_card_data = rate_card_result.one_or_none()
        
        if not rate_card_data:
            raise ValueError("Rate card not found or inactive")
        
        rate_card, subcategory = rate_card_data
        
        # Check if item already in cart
        existing_result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.rate_card_id == request.rate_card_id
            )
        )
        existing_item = existing_result.scalar_one_or_none()
        
        if existing_item:
            # Update quantity
            existing_item.quantity += request.quantity
            existing_item.total_price = existing_item.unit_price * existing_item.quantity
            await self.db.commit()
            await self.db.refresh(existing_item)
            
            logger.info(
                f"Cart item updated: id={existing_item.id}, "
                f"quantity={existing_item.quantity}"
            )
            
            return CartItemResponse(
                id=existing_item.id,
                rate_card_id=existing_item.rate_card_id,
                rate_card_name=rate_card.name,
                subcategory_id=subcategory.id,
                subcategory_name=subcategory.name,
                quantity=existing_item.quantity,
                unit_price=existing_item.unit_price,
                total_price=existing_item.total_price
            )
        else:
            # Create new cart item
            unit_price = rate_card.price
            total_price = unit_price * request.quantity
            
            cart_item = CartItem(
                cart_id=cart.id,
                rate_card_id=request.rate_card_id,
                quantity=request.quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            
            self.db.add(cart_item)
            await self.db.commit()
            await self.db.refresh(cart_item)
            
            logger.info(
                f"Cart item added: id={cart_item.id}, "
                f"rate_card_id={request.rate_card_id}"
            )
            
            return CartItemResponse(
                id=cart_item.id,
                rate_card_id=cart_item.rate_card_id,
                rate_card_name=rate_card.name,
                subcategory_id=subcategory.id,
                subcategory_name=subcategory.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price
            )
    
    async def update_cart_item(
        self,
        item_id: int,
        request: UpdateCartItemRequest,
        user: User
    ) -> CartItemResponse:
        """
        Update cart item quantity
        
        Args:
            item_id: Cart item ID
            request: Update request
            user: Current user
            
        Returns:
            CartItemResponse with updated item
            
        Raises:
            ValueError: If cart item not found
        """
        # Get cart
        cart = await self.get_or_create_cart(user.id)
        
        # Get cart item with rate card and subcategory
        result = await self.db.execute(
            select(CartItem, RateCard, Subcategory)
            .join(RateCard, CartItem.rate_card_id == RateCard.id)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            )
        )
        item_data = result.one_or_none()
        
        if not item_data:
            raise ValueError("Cart item not found")
        
        cart_item, rate_card, subcategory = item_data
        
        # Update quantity and total
        cart_item.quantity = request.quantity
        cart_item.total_price = cart_item.unit_price * request.quantity
        
        await self.db.commit()
        await self.db.refresh(cart_item)
        
        logger.info(
            f"Cart item updated: id={cart_item.id}, quantity={request.quantity}"
        )
        
        return CartItemResponse(
            id=cart_item.id,
            rate_card_id=cart_item.rate_card_id,
            rate_card_name=rate_card.name,
            subcategory_id=subcategory.id,
            subcategory_name=subcategory.name,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.total_price
        )
    
    async def remove_cart_item(self, item_id: int, user: User) -> None:
        """
        Remove item from cart
        
        Args:
            item_id: Cart item ID
            user: Current user
            
        Raises:
            ValueError: If cart item not found
        """
        # Get cart
        cart = await self.get_or_create_cart(user.id)
        
        # Get cart item
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if not cart_item:
            raise ValueError("Cart item not found")
        
        await self.db.delete(cart_item)
        await self.db.commit()
        
        logger.info(f"Cart item removed: id={item_id}")
    
    async def clear_cart(self, user: User) -> None:
        """
        Clear all items from cart
        
        Args:
            user: Current user
        """
        # Get cart
        cart = await self.get_or_create_cart(user.id)
        
        # Delete all cart items
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        cart_items = result.scalars().all()
        
        for item in cart_items:
            await self.db.delete(item)
        
        await self.db.commit()
        
        logger.info(f"Cart cleared: user_id={user.id}")


# Export
__all__ = ["CartService"]

