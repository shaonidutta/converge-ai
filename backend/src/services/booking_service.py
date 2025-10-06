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
        logger.info(f"Creating booking for user_id: {user.id}, address_id: {request.address_id}")

        # Verify address exists and belongs to user
        logger.debug("Verifying address")
        address_result = await self.db.execute(
            select(Address).where(
                Address.id == request.address_id,
                Address.user_id == user.id
            )
        )
        address = address_result.scalar_one_or_none()

        if not address:
            logger.warning(f"Address not found: address_id={request.address_id}")
            raise ValueError("Address not found")

        logger.debug(f"Address verified: {address.city}, {address.state}")
        
        # Get user's cart
        logger.debug("Fetching user cart")
        cart_result = await self.db.execute(
            select(Cart).where(Cart.user_id == user.id)
        )
        cart = cart_result.scalar_one_or_none()

        if not cart:
            logger.warning(f"Cart not found for user_id: {user.id}")
            raise ValueError("Cart is empty")

        logger.debug(f"Cart found: cart_id={cart.id}")

        # Get cart items
        logger.debug("Fetching cart items")
        cart_items_result = await self.db.execute(
            select(CartItem, RateCard, Subcategory)
            .join(RateCard, CartItem.rate_card_id == RateCard.id)
            .join(Subcategory, RateCard.subcategory_id == Subcategory.id)
            .where(CartItem.cart_id == cart.id)
        )
        cart_items = cart_items_result.all()

        if not cart_items:
            logger.warning(f"No items in cart: cart_id={cart.id}")
            raise ValueError("Cart is empty")

        logger.debug(f"Found {len(cart_items)} items in cart")

        # Calculate total amount
        total_amount = sum(item[0].total_price for item in cart_items)
        logger.debug(f"Total amount: {total_amount}")

        # Check wallet balance if payment method is wallet
        if request.payment_method == "wallet":
            logger.debug(f"Checking wallet balance: required={total_amount}, available={user.wallet_balance}")
            if user.wallet_balance < total_amount:
                logger.warning(f"Insufficient wallet balance: user_id={user.id}")
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
        logger.debug(f"Creating {len(cart_items)} booking items")
        booking_items = []

        for cart_item, rate_card, subcategory in cart_items:
            # Calculate scheduled time (add 2 hours to start time for end time)
            from datetime import timedelta
            scheduled_time_from = preferred_datetime.time()
            scheduled_time_to = (preferred_datetime + timedelta(hours=2)).time()

            booking_item = BookingItem(
                booking_id=booking.id,
                user_id=user.id,
                rate_card_id=cart_item.rate_card_id,
                address_id=request.address_id,
                service_name=rate_card.name,
                quantity=cart_item.quantity,
                price=cart_item.unit_price,
                total_amount=cart_item.total_price,
                discount_amount=Decimal('0.00'),
                final_amount=cart_item.total_price,
                scheduled_date=preferred_datetime.date(),
                scheduled_time_from=scheduled_time_from,
                scheduled_time_to=scheduled_time_to,
                payment_status="unpaid",
                status="pending"
            )
            self.db.add(booking_item)
            booking_items.append((booking_item, rate_card, subcategory))

        logger.debug(f"Booking items created successfully")
        
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
            is_default=address.is_default
        )
        
        item_responses = []
        for booking_item, rate_card, subcategory in booking_items:
            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=booking_item.service_name,
                rate_card_name=rate_card.name,
                quantity=booking_item.quantity,
                unit_price=float(booking_item.price),
                total_price=float(booking_item.final_amount)
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
            select(BookingItem, RateCard)
            .join(RateCard, BookingItem.rate_card_id == RateCard.id)
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
            is_default=address.is_default
        )

        item_responses = [
            BookingItemResponse(
                id=item[0].id,
                service_name=item[0].service_name,
                rate_card_name=item[1].name,
                quantity=item[0].quantity,
                unit_price=float(item[0].price),
                total_price=float(item[0].final_amount)
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


    async def reschedule_booking(
        self,
        booking_id: int,
        request,  # RescheduleBookingRequest
        user: User
    ):
        """
        Reschedule a booking

        Args:
            booking_id: Booking ID
            request: Reschedule request with new date and time
            user: Current user

        Returns:
            BookingResponse with updated booking

        Raises:
            ValueError: If booking cannot be rescheduled
        """
        from src.schemas.customer import BookingResponse

        logger.info(f"Rescheduling booking: booking_id={booking_id}, user_id={user.id}")

        # Get booking
        result = await self.db.execute(
            select(Booking).where(
                Booking.id == booking_id,
                Booking.user_id == user.id
            )
        )
        booking = result.scalar_one_or_none()

        if not booking:
            logger.warning(f"Booking not found: booking_id={booking_id}")
            raise ValueError("Booking not found")

        # Check if booking can be rescheduled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            logger.warning(
                f"Cannot reschedule booking with status: {booking.status.value}"
            )
            raise ValueError(
                f"Cannot reschedule booking with status: {booking.status.value}"
            )

        # Validate new date and time
        try:
            from datetime import datetime as dt
            new_date = dt.strptime(request.preferred_date, "%Y-%m-%d").date()
            new_time = dt.strptime(request.preferred_time, "%H:%M").time()

            # Check if new date is in the future
            if new_date < dt.now().date():
                raise ValueError("Preferred date must be in the future")
        except ValueError as e:
            logger.warning(f"Invalid date/time format: {str(e)}")
            raise ValueError(f"Invalid date or time format: {str(e)}")

        # Update booking
        old_date = booking.preferred_date
        old_time = booking.preferred_time

        booking.preferred_date = request.preferred_date
        booking.preferred_time = request.preferred_time

        # Add reschedule note to special instructions
        reschedule_note = f"\n[Rescheduled from {old_date} {old_time}"
        if request.reason:
            reschedule_note += f" - Reason: {request.reason}"
        reschedule_note += "]"

        if booking.special_instructions:
            booking.special_instructions += reschedule_note
        else:
            booking.special_instructions = reschedule_note.strip()

        await self.db.commit()
        await self.db.refresh(booking)

        logger.info(
            f"Booking rescheduled: id={booking.id}, "
            f"new_date={request.preferred_date}, new_time={request.preferred_time}"
        )

        # Get address and items for response
        address_result = await self.db.execute(
            select(Address).where(Address.id == booking.address_id)
        )
        address = address_result.scalar_one()

        items_result = await self.db.execute(
            select(BookingItem, RateCard)
            .join(RateCard, BookingItem.rate_card_id == RateCard.id)
            .where(BookingItem.booking_id == booking.id)
        )
        items = items_result.all()

        # Build response
        address_response = AddressResponse(
            id=address.id,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            pincode=address.pincode,
            is_default=address.is_default
        )

        item_responses = []
        for booking_item, rate_card in items:
            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=booking_item.service_name,
                rate_card_name=rate_card.name,
                quantity=booking_item.quantity,
                unit_price=float(booking_item.price),
                total_price=float(booking_item.final_amount)
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

