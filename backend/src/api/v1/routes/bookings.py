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
    RescheduleBookingRequest,
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
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Create booking request: user_id={current_user.id}, address_id={request.address_id}")
        logger.debug(f"Booking data: {request.model_dump()}")

        booking_service = BookingService(db)
        result = await booking_service.create_booking(request, current_user)

        logger.info(f"Booking created successfully: booking_id={result.id}")
        return result
    except ValueError as e:
        logger.warning(f"Create booking failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create booking failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
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
    import logging
    import traceback
    logger = logging.getLogger(__name__)

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
        logger.error(f"List bookings error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch bookings: {str(e)}"
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
    "/{booking_id}/reschedule",
    response_model=BookingResponse,
    summary="Reschedule booking"
)
async def reschedule_booking(
    booking_id: int,
    request: RescheduleBookingRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Reschedule a booking to a new date and time"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Reschedule booking request: booking_id={booking_id}, user_id={current_user.id}")
        booking_service = BookingService(db)
        result = await booking_service.reschedule_booking(booking_id, request, current_user)
        logger.info(f"Booking rescheduled successfully: booking_id={booking_id}")
        return result
    except ValueError as e:
        logger.warning(f"Reschedule failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Reschedule failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reschedule booking: {str(e)}"
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
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Cancel booking request: booking_id={booking_id}, user_id={current_user.id}")
        booking_service = BookingService(db)
        await booking_service.cancel_booking(booking_id, request, current_user)
        logger.info(f"Booking cancelled successfully: booking_id={booking_id}")
        return MessageResponse(message="Booking cancelled successfully")
    except ValueError as e:
        logger.warning(f"Cancel failed - ValueError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Cancel failed - Exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )

