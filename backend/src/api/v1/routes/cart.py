"""
Cart Routes (Thin Controllers)
Cart management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.customer import (
    AddToCartRequest,
    UpdateCartItemRequest,
    CartResponse,
    CartItemResponse,
)
from src.schemas.auth import MessageResponse
from src.services import CartService

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get(
    "",
    response_model=CartResponse,
    summary="Get cart"
)
async def get_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get user's cart with items"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Get cart request for user_id: {current_user.id}")
        cart_service = CartService(db)
        logger.debug("CartService instantiated")

        result = await cart_service.get_cart(current_user)
        logger.info(f"Cart fetched successfully for user_id: {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch cart - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch cart: {str(e)}"
        )


@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add to cart"
)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Add item to cart"""
    try:
        cart_service = CartService(db)
        return await cart_service.add_to_cart(request, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add to cart"
        )


@router.put(
    "/items/{item_id}",
    response_model=CartItemResponse,
    summary="Update cart item"
)
async def update_cart_item(
    item_id: int,
    request: UpdateCartItemRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update cart item quantity"""
    try:
        cart_service = CartService(db)
        return await cart_service.update_cart_item(item_id, request, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.delete(
    "/items/{item_id}",
    response_model=MessageResponse,
    summary="Remove cart item"
)
async def remove_cart_item(
    item_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Remove item from cart"""
    try:
        cart_service = CartService(db)
        await cart_service.remove_cart_item(item_id, current_user)
        return MessageResponse(message="Item removed from cart")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove cart item"
        )


@router.delete(
    "",
    response_model=MessageResponse,
    summary="Clear cart"
)
async def clear_cart(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Clear all items from cart"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Clear cart request for user_id: {current_user.id}")
        cart_service = CartService(db)
        await cart_service.clear_cart(current_user)
        logger.info(f"Cart cleared successfully for user_id: {current_user.id}")
        return MessageResponse(message="Cart cleared successfully")
    except Exception as e:
        logger.error(f"Failed to clear cart - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cart: {str(e)}"
        )

