"""
Booking Routes (Thin Controllers)
Booking management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from src.core.database.connection import get_db
from src.core.security.dependencies import get_current_user
from src.core.models import User
from src.schemas.customer import (
    CreateBookingRequest,
    BookingResponse,
    CancelBookingRequest,
)
from src.schemas.auth import MessageResponse
from src.services import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create booking"
)
async def create_booking(
    request: CreateBookingRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Create a new booking from cart"""
    try:
        booking_service = BookingService(db)
        return await booking_service.create_booking(request, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )


@router.get(
    "",
    response_model=List[BookingResponse],
    summary="List bookings"
)
async def list_bookings(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """List user's bookings with optional status filter"""
    try:
        booking_service = BookingService(db)
        return await booking_service.list_bookings(
            current_user,
            status_filter,
            skip,
            limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch bookings"
        )


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Get booking details"
)
async def get_booking(
    booking_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get booking details by ID"""
    try:
        booking_service = BookingService(db)
        return await booking_service.get_booking(booking_id, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch booking"
        )


@router.post(
    "/{booking_id}/cancel",
    response_model=MessageResponse,
    summary="Cancel booking"
)
async def cancel_booking(
    booking_id: int,
    request: CancelBookingRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Cancel a booking"""
    try:
        booking_service = BookingService(db)
        await booking_service.cancel_booking(booking_id, request, current_user)
        return MessageResponse(message="Booking cancelled successfully")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel booking"
        )

