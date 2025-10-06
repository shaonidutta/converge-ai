"""
Booking Service
Business logic for booking management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
import logging
import uuid

from src.core.models import (
    User, Booking, BookingItem, Cart, CartItem, Address,
    RateCard, Subcategory, BookingStatus, PaymentStatus, PaymentMethod
)
from src.schemas.customer import (
    CreateBookingRequest,
    BookingResponse,
    BookingItemResponse,
    AddressResponse,
    CancelBookingRequest,
)

logger = logging.getLogger(__name__)


class BookingService:
    """Service class for booking management business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_booking(
        self, 
        request: CreateBookingRequest, 
        user: User
    ) -> BookingResponse:
        """
        Create a new booking from cart
        
        Args:
            request: Booking creation request
            user: Current user
            
        Returns:
            BookingResponse with booking details
            
        Raises:
            ValueError: If validation fails
        """
        # Verify address exists and belongs to user
        address_result = await self.db.execute(
            select(Address).where(
                Address.id == request.address_id,
                Address.user_id == user.id,
                Address.is_active == True
            )
        )
        address = address_result.scalar_one_or_none()
        
        if not address:
            raise ValueError("Address not found")
        
        # Get user's cart
        cart_result = await self.db.execute(
            select(Cart).where(Cart.user_id == user.id)
        )
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise ValueError("Cart is empty")
        
        # Get cart items
        cart_items_result = await self.db.execute(
            select(CartItem, RateCard, Subcategory)
            .join(RateCard, CartItem.rate_card_id == RateCard.id)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(CartItem.cart_id == cart.id)
        )
        cart_items = cart_items_result.all()
        
        if not cart_items:
            raise ValueError("Cart is empty")
        
        # Calculate total amount
        total_amount = sum(item[0].total_price for item in cart_items)
        
        # Check wallet balance if payment method is wallet
        if request.payment_method == "wallet":
            if user.wallet_balance < total_amount:
                raise ValueError(
                    f"Insufficient wallet balance. Required: {total_amount}, "
                    f"Available: {user.wallet_balance}"
                )
        
        # Parse preferred date and time
        try:
            preferred_datetime = datetime.strptime(
                f"{request.preferred_date} {request.preferred_time}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            raise ValueError("Invalid date or time format")
        
        # Create booking
        booking_number = f"BK{uuid.uuid4().hex[:8].upper()}"
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"
        
        booking = Booking(
            order_id=order_id,
            booking_number=booking_number,
            user_id=user.id,
            address_id=request.address_id,
            subtotal=total_amount,
            discount=Decimal('0.00'),
            sgst=Decimal('0.00'),
            cgst=Decimal('0.00'),
            igst=Decimal('0.00'),
            sgst_amount=Decimal('0.00'),
            cgst_amount=Decimal('0.00'),
            igst_amount=Decimal('0.00'),
            total_gst=Decimal('0.00'),
            convenience_charge=Decimal('0.00'),
            total=total_amount,
            is_partial=False,
            partial_amount=Decimal('0.00'),
            remaining_amount=Decimal('0.00'),
            payment_method=PaymentMethod[request.payment_method.upper()],
            payment_status=PaymentStatus.PENDING,
            status=BookingStatus.PENDING,
            preferred_date=preferred_datetime.date(),
            preferred_time=preferred_datetime.time(),
            special_instructions=request.special_instructions
        )
        
        self.db.add(booking)
        await self.db.flush()  # Get booking ID
        
        # Create booking items from cart items
        booking_items = []
        for cart_item, rate_card, subcategory in cart_items:
            booking_item = BookingItem(
                booking_id=booking.id,
                user_id=user.id,
                rate_card_id=cart_item.rate_card_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                status=BookingStatus.PENDING
            )
            self.db.add(booking_item)
            booking_items.append((booking_item, rate_card, subcategory))
        
        # Deduct from wallet if payment method is wallet
        if request.payment_method == "wallet":
            user.wallet_balance -= booking.total
            booking.payment_status = PaymentStatus.PAID
        
        # Clear cart
        for cart_item, _, _ in cart_items:
            await self.db.delete(cart_item)
        
        await self.db.commit()
        await self.db.refresh(booking)
        
        logger.info(
            f"Booking created: id={booking.id}, number={booking_number}, "
            f"user_id={user.id}"
        )
        
        # Prepare response
        address_response = AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            landmark=address.landmark,
            address_type=address.address_type,
            is_default=address.is_default,
            is_active=address.is_active
        )
        
        item_responses = []
        for booking_item, rate_card, subcategory in booking_items:
            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=subcategory.name,
                rate_card_name=rate_card.name,
                quantity=booking_item.quantity,
                unit_price=booking_item.unit_price,
                total_price=booking_item.total_price
            ))
        
        return BookingResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            status=booking.status.value,
            total_amount=booking.total,
            preferred_date=booking.preferred_date.isoformat(),
            preferred_time=booking.preferred_time.strftime("%H:%M"),
            address=address_response,
            items=item_responses,
            special_instructions=booking.special_instructions,
            created_at=booking.created_at.isoformat()
        )
    
    async def list_bookings(
        self,
        user: User,
        status_filter: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[BookingResponse]:
        """
        List user's bookings with optional status filter
        
        Args:
            user: Current user
            status_filter: Optional status filter
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of BookingResponse
            
        Raises:
            ValueError: If status filter is invalid
        """
        # Build query
        query = select(Booking).where(Booking.user_id == user.id)
        
        # Apply status filter
        if status_filter:
            status_upper = status_filter.upper()
            if status_upper in [s.name for s in BookingStatus]:
                query = query.where(Booking.status == BookingStatus[status_upper])
            else:
                raise ValueError(f"Invalid status filter: {status_filter}")
        
        # Order by created_at desc
        query = query.order_by(Booking.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        bookings = result.scalars().all()
        
        # Prepare response
        response = []
        for booking in bookings:
            booking_response = await self._build_booking_response(booking)
            response.append(booking_response)
        
        return response
    
    async def get_booking(self, booking_id: int, user: User) -> BookingResponse:
        """
        Get booking details by ID
        
        Args:
            booking_id: Booking ID
            user: Current user
            
        Returns:
            BookingResponse with booking details
            
        Raises:
            ValueError: If booking not found
        """
        # Get booking
        result = await self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user.id
            )
        )
        booking = result.scalar_one_or_none()
        
        if not booking:
            raise ValueError("Booking not found")
        
        return await self._build_booking_response(booking)
    
    async def _build_booking_response(self, booking: Booking) -> BookingResponse:
        """Helper method to build booking response"""
        # Get address
        address_result = await self.db.execute(
            select(Address).where(Address.id == booking.address_id)
        )
        address = address_result.scalar_one()
        
        # Get booking items
        items_result = await self.db.execute(
            select(BookingItem, RateCard, Subcategory)
            .join(RateCard, BookingItem.rate_card_id == RateCard.id)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(BookingItem.booking_id == booking.id)
        )
        items = items_result.all()
        
        address_response = AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            landmark=address.landmark,
            address_type=address.address_type,
            is_default=address.is_default,
            is_active=address.is_active
        )
        
        item_responses = [
            BookingItemResponse(
                id=item[0].id,
                service_name=item[2].name,
                rate_card_name=item[1].name,
                quantity=item[0].quantity,
                unit_price=item[0].unit_price,
                total_price=item[0].total_price
            )
            for item in items
        ]
        
        return BookingResponse(
            id=booking.id,
            booking_number=booking.booking_number,
            status=booking.status.value,
            total_amount=booking.total,
            preferred_date=booking.preferred_date.isoformat(),
            preferred_time=booking.preferred_time.strftime("%H:%M"),
            address=address_response,
            items=item_responses,
            special_instructions=booking.special_instructions,
            created_at=booking.created_at.isoformat()
        )


    async def cancel_booking(
        self,
        booking_id: int,
        request: CancelBookingRequest,
        user: User
    ) -> None:
        """
        Cancel a booking

        Args:
            booking_id: Booking ID
            request: Cancellation request
            user: Current user

        Raises:
            ValueError: If booking cannot be cancelled
        """
        # Get booking
        result = await self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user.id
            )
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError("Booking not found")

        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(
                f"Cannot cancel booking with status: {booking.status.value}"
            )

        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = request.reason
        booking.cancelled_at = datetime.now(timezone.utc)

        # Update booking items status
        items_result = await self.db.execute(
            select(BookingItem).where(BookingItem.booking_id == booking.id)
        )
        items = items_result.scalars().all()

        for item in items:
            item.status = BookingStatus.CANCELLED

        # Refund to wallet if paid via wallet
        if (booking.payment_method == PaymentMethod.WALLET and
            booking.payment_status == PaymentStatus.PAID):
            user.wallet_balance += booking.total
            booking.payment_status = PaymentStatus.REFUNDED

        await self.db.commit()

        logger.info(
            f"Booking cancelled: id={booking.id}, user_id={user.id}, "
            f"reason={request.reason}"
        )


# Export
__all__ = ["BookingService"]

