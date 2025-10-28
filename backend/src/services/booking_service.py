"""
Booking Service
Business logic for booking management
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal
import logging
import uuid

from src.core.models import (
    User, Booking, BookingItem, Cart, CartItem, Address,
    RateCard, Subcategory, Category, BookingStatus, PaymentStatus, PaymentMethod,
    Provider, Pincode, ProviderPincode
)
from src.schemas.customer import (
    CreateBookingRequest,
    BookingResponse,
    BookingItemResponse,
    AddressResponse,
    CancelBookingRequest,
    RateCardWithSubcategoryResponse,
    SubcategoryResponse,
    CategoryResponse,
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

        # Validate provider availability in user's pincode
        # Note: This will log warnings if no providers found, but won't block booking
        logger.debug("Validating provider availability")
        try:
            await self._validate_provider_availability(address.pincode, cart_items)
        except ValueError as e:
            # Log warning but don't block booking - let system assign provider later
            logger.warning(f"Provider validation warning for pincode {address.pincode}: {e}")
            logger.info("Proceeding with booking - provider will be assigned based on availability")

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
        order_id = f"ORD{uuid.uuid4().hex[:8].upper()}"

        booking = Booking(
            order_id=order_id,
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
            f"Booking created: id={booking.id}, order_id={booking.order_id}, "
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
            # Get category for the subcategory
            category_result = await self.db.execute(
                select(Category).where(Category.id == subcategory.category_id)
            )
            category = category_result.scalar_one()

            # Build rate card with subcategory response
            rate_card_response = RateCardWithSubcategoryResponse(
                id=rate_card.id,
                name=rate_card.name,
                subcategory=SubcategoryResponse(
                    id=subcategory.id,
                    name=subcategory.name,
                    slug=subcategory.slug,
                    description=subcategory.description,
                    image=subcategory.image,
                    category_id=subcategory.category_id,
                    category_name=category.name,
                    is_active=subcategory.is_active,
                    rate_card_count=0,  # Not needed for booking display
                    category=CategoryResponse(
                        id=category.id,
                        name=category.name,
                        slug=category.slug,
                        description=category.description,
                        image=category.image,
                        is_active=category.is_active,
                        subcategory_count=0  # Not needed for booking display
                    )
                )
            )

            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=booking_item.service_name,
                rate_card_name=rate_card.name,
                rate_card=rate_card_response,
                quantity=booking_item.quantity,
                unit_price=float(booking_item.price),
                total_price=float(booking_item.final_amount)
            ))
        
        return BookingResponse(
            id=booking.id,
            order_id=booking.order_id,
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

        Optimized with eager loading to prevent N+1 queries:
        - Uses selectinload to fetch related address and booking items in single queries
        - Reduces database round trips from O(n*2) to O(1) where n = number of bookings

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
        # Build query with eager loading for related entities
        # This prevents N+1 query problem by loading all related data in advance
        query = (
            select(Booking)
            .where(Booking.user_id == user.id)
            .options(
                selectinload(Booking.address),  # Eager load address
                selectinload(Booking.booking_items)
                    .selectinload(BookingItem.rate_card)
                    .selectinload(RateCard.subcategory)
                    .selectinload(Subcategory.category)  # Eager load items + rate cards + subcategory + category
            )
        )

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
        bookings = result.scalars().unique().all()  # unique() needed when using selectinload

        # Prepare response - now all data is already loaded, no additional queries
        response = []
        for booking in bookings:
            # Build response using already-loaded relationships
            address = booking.address

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
            for booking_item in booking.booking_items:
                rate_card = booking_item.rate_card
                subcategory = rate_card.subcategory
                category = subcategory.category

                # Build rate card with subcategory response
                rate_card_response = RateCardWithSubcategoryResponse(
                    id=rate_card.id,
                    name=rate_card.name,
                    subcategory=SubcategoryResponse(
                        id=subcategory.id,
                        name=subcategory.name,
                        slug=subcategory.slug,
                        description=subcategory.description,
                        image=subcategory.image,
                        category_id=subcategory.category_id,
                        category_name=category.name,
                        is_active=subcategory.is_active,
                        rate_card_count=0,  # Not needed for booking display
                        category=CategoryResponse(
                            id=category.id,
                            name=category.name,
                            slug=category.slug,
                            description=category.description,
                            image=category.image,
                            is_active=category.is_active,
                            subcategory_count=0  # Not needed for booking display
                        )
                    )
                )

                item_responses.append(BookingItemResponse(
                    id=booking_item.id,
                    service_name=booking_item.service_name,
                    rate_card_name=rate_card.name,
                    rate_card=rate_card_response,
                    quantity=booking_item.quantity,
                    unit_price=float(booking_item.price),
                    total_price=float(booking_item.final_amount)
                ))

            response.append(BookingResponse(
                id=booking.id,
                order_id=booking.order_id,
                status=booking.status.value,
                total_amount=booking.total,
                preferred_date=booking.preferred_date.isoformat(),
                preferred_time=booking.preferred_time.strftime("%H:%M"),
                address=address_response,
                items=item_responses,
                special_instructions=booking.special_instructions,
                created_at=booking.created_at.isoformat()
            ))

        return response
    
    async def get_booking(self, booking_id: int, user: User) -> BookingResponse:
        """
        Get booking details by ID

        Optimized with eager loading to prevent N+1 queries

        Args:
            booking_id: Booking ID
            user: Current user

        Returns:
            BookingResponse with booking details

        Raises:
            ValueError: If booking not found
        """
        # Get booking with eager loading
        result = await self.db.execute(
            select(Booking)
            .where(
                Booking.id == booking_id,
                Booking.user_id == user.id
            )
            .options(
                selectinload(Booking.address),
                selectinload(Booking.booking_items)
                    .selectinload(BookingItem.rate_card)
                    .selectinload(RateCard.subcategory)
                    .selectinload(Subcategory.category)
            )
        )
        booking = result.scalar_one_or_none()

        if not booking:
            raise ValueError("Booking not found")

        # Build response using already-loaded relationships
        address = booking.address

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
        for booking_item in booking.booking_items:
            rate_card = booking_item.rate_card
            subcategory = rate_card.subcategory
            category = subcategory.category

            # Build rate card with subcategory response
            rate_card_response = RateCardWithSubcategoryResponse(
                id=rate_card.id,
                name=rate_card.name,
                subcategory=SubcategoryResponse(
                    id=subcategory.id,
                    name=subcategory.name,
                    slug=subcategory.slug,
                    description=subcategory.description,
                    image=subcategory.image,
                    category_id=subcategory.category_id,
                    category_name=category.name,
                    is_active=subcategory.is_active,
                    rate_card_count=0,  # Not needed for booking display
                    category=CategoryResponse(
                        id=category.id,
                        name=category.name,
                        slug=category.slug,
                        description=category.description,
                        image=category.image,
                        is_active=category.is_active,
                        subcategory_count=0  # Not needed for booking display
                    )
                )
            )

            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=booking_item.service_name,
                rate_card_name=rate_card.name,
                rate_card=rate_card_response,
                quantity=booking_item.quantity,
                unit_price=float(booking_item.price),
                total_price=float(booking_item.final_amount)
            ))

        return BookingResponse(
            id=booking.id,
            order_id=booking.order_id,
            status=booking.status.value,
            total_amount=booking.total,
            preferred_date=booking.preferred_date.isoformat(),
            preferred_time=booking.preferred_time.strftime("%H:%M"),
            address=address_response,
            items=item_responses,
            special_instructions=booking.special_instructions,
            created_at=booking.created_at.isoformat()
        )

    # Note: _build_booking_response method removed - now using eager loading in list_bookings and get_booking
    # This eliminates N+1 query problem and improves performance significantly


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
            # Get subcategory and category for the rate card
            subcategory_result = await self.db.execute(
                select(Subcategory).where(Subcategory.id == rate_card.subcategory_id)
            )
            subcategory = subcategory_result.scalar_one()

            category_result = await self.db.execute(
                select(Category).where(Category.id == subcategory.category_id)
            )
            category = category_result.scalar_one()

            # Build rate card with subcategory response
            rate_card_response = RateCardWithSubcategoryResponse(
                id=rate_card.id,
                name=rate_card.name,
                subcategory=SubcategoryResponse(
                    id=subcategory.id,
                    name=subcategory.name,
                    slug=subcategory.slug,
                    description=subcategory.description,
                    image=subcategory.image,
                    category_id=subcategory.category_id,
                    category_name=category.name,
                    is_active=subcategory.is_active,
                    rate_card_count=0,  # Not needed for booking display
                    category=CategoryResponse(
                        id=category.id,
                        name=category.name,
                        slug=category.slug,
                        description=category.description,
                        image=category.image,
                        is_active=category.is_active,
                        subcategory_count=0  # Not needed for booking display
                    )
                )
            )

            item_responses.append(BookingItemResponse(
                id=booking_item.id,
                service_name=booking_item.service_name,
                rate_card_name=rate_card.name,
                rate_card=rate_card_response,
                quantity=booking_item.quantity,
                unit_price=float(booking_item.price),
                total_price=float(booking_item.final_amount)
            ))

        return BookingResponse(
            id=booking.id,
            order_id=booking.order_id,
            status=booking.status.value,
            total_amount=booking.total,
            preferred_date=booking.preferred_date.isoformat(),
            preferred_time=booking.preferred_time.strftime("%H:%M"),
            address=address_response,
            items=item_responses,
            special_instructions=booking.special_instructions,
            created_at=booking.created_at.isoformat()
        )

    async def get_booking_by_order_id(
        self,
        order_id: str,
        user: User
    ) -> Optional[Booking]:
        """
        Get booking by order ID

        Args:
            order_id: Order ID (e.g., "ORD123456")
            user: Current user

        Returns:
            Booking object or None if not found
        """
        result = await self.db.execute(
            select(Booking).where(
                Booking.order_id == order_id.upper(),
                Booking.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

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

    async def cancel_booking_by_order_id(
        self,
        order_id: str,
        reason: str,
        user: User
    ) -> BookingResponse:
        """
        Cancel a booking by order ID

        Args:
            order_id: Order ID (e.g., "ORD123456")
            reason: Cancellation reason
            user: Current user

        Returns:
            BookingResponse with cancelled booking details

        Raises:
            ValueError: If booking cannot be cancelled
        """
        # Get booking by order ID
        booking = await self.get_booking_by_order_id(order_id, user)

        if not booking:
            raise ValueError(f"Booking {order_id} not found")

        # Check if booking can be cancelled
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise ValueError(
                f"Cannot cancel booking with status: {booking.status.value}"
            )

        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
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
        await self.db.refresh(booking)

        logger.info(
            f"Booking cancelled: id={booking.id}, order_id={booking.order_id}, user_id={user.id}, reason={reason}"
        )

        # Return booking response
        return await self._build_booking_response(booking)

    async def _validate_provider_availability(
        self,
        pincode: str,
        cart_items: list
    ) -> None:
        """
        Validate that providers are available for all cart items in the specified pincode

        This checks:
        1. Pincode exists and is serviceable
        2. Each rate card in cart has a provider who services this pincode

        Args:
            pincode: User's pincode
            cart_items: List of (CartItem, RateCard, Subcategory) tuples

        Raises:
            ValueError: If validation fails
        """
        # Step 1: Check if pincode exists and is serviceable
        pincode_result = await self.db.execute(
            select(Pincode).where(Pincode.pincode == pincode)
        )
        pincode_obj = pincode_result.scalar_one_or_none()

        if not pincode_obj:
            logger.warning(f"Pincode not found: {pincode}")
            raise ValueError(f"Sorry, pincode {pincode} is not in our service area yet.")

        if not pincode_obj.is_serviceable:
            logger.warning(f"Pincode not serviceable: {pincode}")
            raise ValueError(f"Sorry, we don't service pincode {pincode} at the moment.")

        # Step 2: Validate each rate card's provider services this pincode
        for cart_item, rate_card, subcategory in cart_items:
            # Check if rate card's provider services this pincode
            provider_check = await self.db.execute(
                select(ProviderPincode)
                .join(Provider, ProviderPincode.provider_id == Provider.id)
                .where(
                    ProviderPincode.provider_id == rate_card.provider_id,
                    ProviderPincode.pincode_id == pincode_obj.id,
                    Provider.is_active == True,
                    Provider.is_verified == True
                )
            )
            provider_association = provider_check.scalar_one_or_none()

            if not provider_association:
                logger.warning(
                    f"Provider {rate_card.provider_id} does not service pincode {pincode} "
                    f"for rate_card {rate_card.id} ({rate_card.name})"
                )
                raise ValueError(
                    f"Sorry, the service '{rate_card.name}' is not available in pincode {pincode}. "
                    f"Please remove it from your cart or choose a different location."
                )

        logger.debug(f"Provider validation passed for pincode {pincode}")


# Export
__all__ = ["BookingService"]

