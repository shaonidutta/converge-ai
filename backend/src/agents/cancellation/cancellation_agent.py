"""
CancellationAgent - Handles booking cancellations with policy-based refunds

This agent manages the complete cancellation workflow:
1. Validates booking eligibility for cancellation
2. Checks cancellation policy and calculates refund
3. Processes cancellation with appropriate refund
4. Provides detailed cancellation information
"""

import logging
from typing import Dict, Any
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.models import User, Booking, BookingItem, BookingStatus, PaymentStatus, PaymentMethod
from src.schemas.customer import CancelBookingRequest

logger = logging.getLogger(__name__)


class CancellationAgent:
    """
    CancellationAgent handles booking cancellations with policy-based refunds
    
    Cancellation Policy:
    - More than 24 hours before service: 100% refund
    - 12-24 hours before service: 50% refund
    - 6-12 hours before service: 25% refund
    - Less than 6 hours before service: No refund
    - After service started: No cancellation allowed
    """
    
    # Cancellation policy thresholds (in hours)
    FULL_REFUND_HOURS = 24
    HALF_REFUND_HOURS = 12
    QUARTER_REFUND_HOURS = 6
    
    def __init__(self, db: AsyncSession, dialog_state_manager=None):
        """
        Initialize CancellationAgent

        Args:
            db: Database session
            dialog_state_manager: DialogStateManager instance (optional, will be created if not provided)
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
        self.dialog_state_manager = dialog_state_manager
        if not self.dialog_state_manager:
            from src.services.dialog_state_manager import DialogStateManager
            self.dialog_state_manager = DialogStateManager(db)
    
    async def execute(
        self,
        message: str,
        user: User,
        session_id: str,
        entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute cancellation request

        Args:
            message: User message
            user: Current user
            session_id: Session ID
            entities: Extracted entities (booking_id, reason, service_type, booking_filter)

        Returns:
            {
                "response": str,  # User-friendly message
                "action_taken": str,  # Action identifier
                "metadata": dict  # Cancellation details
            }
        """
        try:
            booking_id = entities.get("booking_id")
            service_type = entities.get("service_type")
            booking_filter = entities.get("booking_filter")  # "latest", "recent", etc.
            reason = entities.get("reason", "Customer requested cancellation")

            # Enhanced logic: handle different cancellation scenarios
            if booking_id:
                # Scenario 1: Direct booking ID provided
                return await self._cancel_by_booking_id(booking_id, reason, user, session_id)

            elif booking_filter == "latest" or "latest" in message.lower():
                # Scenario 2: Cancel latest booking
                return await self._cancel_latest_booking(reason, user, session_id)

            elif service_type:
                # Scenario 3: Cancel by service type
                return await self._cancel_by_service_type(service_type, reason, user, session_id)

            elif any(keyword in message.lower() for keyword in ["latest", "recent", "last"]):
                # Scenario 4: Implicit latest booking request
                return await self._cancel_latest_booking(reason, user, session_id)

            else:
                # Scenario 5: No specific criteria provided
                return await self._request_clarification(user)

        except ValueError as e:
            self.logger.error(f"Cancellation validation error: {e}")
            return {
                "response": f"Cancellation failed: {str(e)}",
                "action_taken": "cancellation_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            self.logger.error(f"Cancellation error: {e}", exc_info=True)
            return {
                "response": "An unexpected error occurred while processing your cancellation. Please contact support.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def execute_confirmed_cancellation(
        self,
        pending_action: Dict[str, Any],
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a confirmed cancellation from pending action

        Args:
            pending_action: Pending action details from dialog state
            user: Current user
            session_id: Session ID

        Returns:
            Response dict with cancellation result
        """
        try:
            order_id = pending_action.get("order_id")
            reason = pending_action.get("reason", "Customer requested cancellation")

            if not order_id:
                return {
                    "response": "Unable to process cancellation: Order ID not found in pending action.",
                    "action_taken": "cancellation_failed",
                    "metadata": {"error": "Missing order_id"}
                }

            # Execute cancellation with confirmed=True to skip confirmation
            result = await self._cancel_by_booking_id(
                booking_id=str(order_id),
                reason=reason,
                user=user,
                session_id=session_id,
                confirmed=True
            )

            # Clear pending action from dialog state
            await self.dialog_state_manager.clear_pending_action(session_id)

            return result

        except Exception as e:
            self.logger.error(f"Error executing confirmed cancellation: {str(e)}", exc_info=True)
            return {
                "response": "An error occurred while processing your cancellation. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _cancel_by_booking_id(
        self,
        booking_id: str | int,
        reason: str,
        user: User,
        session_id: str,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Cancel booking by specific booking ID

        Args:
            booking_id: Booking ID or Order ID
            reason: Cancellation reason
            user: Current user
            session_id: Session ID for dialog state
            confirmed: If True, skip confirmation and proceed with cancellation
        """

        # Get booking details
        # booking_id can be either the internal ID (int) or order_id (string like "ORD123456")
        booking = await self._get_booking(booking_id, user)

        if not booking:
            self.logger.warning(f"[CANCEL] Booking {booking_id} not found for user {user.id}")
            return {
                "response": f"Order {booking_id} not found. Please check the Order ID and try again.",
                "action_taken": "booking_not_found",
                "metadata": {"order_id": booking_id}
            }

        self.logger.info(f"[CANCEL] Found booking: order_id={booking.order_id}, status={booking.status}, items={len(booking.booking_items) if hasattr(booking, 'booking_items') and booking.booking_items else 0}")

        # Check if booking can be cancelled
        can_cancel, cancel_message = await self._can_cancel_booking(booking)

        if not can_cancel:
            return {
                "response": f"{cancel_message}",
                "action_taken": "cancellation_not_allowed",
                "metadata": {
                    "booking_id": booking.id,
                    "order_id": booking.order_id,
                    "status": booking.status.value,
                    "reason": cancel_message
                }
            }

        # Calculate refund based on cancellation policy
        refund_info = await self._calculate_refund(booking)

        # If not confirmed, request confirmation
        if not confirmed:
            return await self._request_cancellation_confirmation(
                booking, refund_info, reason, user, session_id
            )

        # Process cancellation (confirmed)
        result = await self._process_cancellation(booking, reason, refund_info, user)

        return result

    async def _cancel_latest_booking(self, reason: str, user: User, session_id: str) -> Dict[str, Any]:
        """Cancel the user's latest booking"""

        # Get the latest booking for the user
        latest_booking = await self._get_latest_booking(user)

        if not latest_booking:
            return {
                "response": "You don't have any bookings to cancel.",
                "action_taken": "no_bookings_found",
                "metadata": {"user_id": user.id}
            }

        # Use the existing cancellation logic
        return await self._cancel_by_booking_id(str(latest_booking.order_id), reason, user, session_id)

    async def _cancel_by_service_type(self, service_type: str, reason: str, user: User, session_id: str) -> Dict[str, Any]:
        """Cancel bookings by service type"""

        # Get bookings for the specific service type
        bookings = await self._get_bookings_by_service_type(service_type, user)

        if not bookings:
            return {
                "response": f"You don't have any {service_type.replace('_', ' ')} bookings to cancel.",
                "action_taken": "no_bookings_found",
                "metadata": {"service_type": service_type, "user_id": user.id}
            }

        # For now, cancel the latest booking of that service type
        # In the future, this could be enhanced to show a list and let user choose
        latest_booking = bookings[0]  # Already ordered by date desc

        return await self._cancel_by_booking_id(str(latest_booking.order_id), reason, user, session_id)

    async def _request_cancellation_confirmation(
        self,
        booking: Booking,
        refund_info: Dict[str, Any],
        reason: str,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Request user confirmation before cancelling booking

        Args:
            booking: Booking to cancel
            refund_info: Refund calculation details
            reason: Cancellation reason
            user: Current user
            session_id: Session ID for dialog state

        Returns:
            Response dict with confirmation request
        """
        # Get service name from booking items
        service_name = "Service"
        if hasattr(booking, 'booking_items') and booking.booking_items:
            service_name = booking.booking_items[0].service_name
            self.logger.info(f"[CANCEL] Booking {booking.order_id} has {len(booking.booking_items)} items, first service: {service_name}")

        # Format booking details - convert SQLAlchemy types to Python types
        total_amount = 0.0
        if booking.total is not None:
            total_amount = float(booking.total)

        booking_details = {
            "booking_id": booking.id,
            "order_id": booking.order_id,
            "service_name": service_name,
            "preferred_date": str(booking.preferred_date),
            "preferred_time": str(booking.preferred_time),
            "total_amount": total_amount,
            "refund_info": refund_info,
            "reason": reason
        }

        # Store pending action in dialog state
        if self.dialog_state_manager:
            await self.dialog_state_manager.set_pending_cancellation(
                session_id=session_id,
                user_id=user.id,  # type: ignore
            booking_details=booking_details
        )

        # Build confirmation message
        refund_amount = refund_info.get("refund_amount", 0.0)
        refund_percentage = refund_info.get("refund_percentage", 0)
        policy_message = refund_info.get("policy_message", "")

        response = f"""📋 **Booking Cancellation Confirmation**

**Order ID:** {booking.order_id}
**Service:** {service_name}
**Date:** {booking.preferred_date}
**Time:** {booking.preferred_time}
**Total Amount:** ₹{booking.total or 0:.2f}

**Refund Details:**
- Refund Amount: ₹{refund_amount:.2f} ({refund_percentage}%)
- {policy_message}

⚠️ **Are you sure you want to cancel this booking?**

Reply with **'yes'** to confirm cancellation or **'no'** to keep the booking."""

        return {
            "response": response,
            "action_taken": "awaiting_confirmation",
            "requires_confirmation": True,
            "metadata": {
                "order_id": booking.order_id,
                "booking_id": booking.id,
                "refund_amount": refund_amount,
                "refund_percentage": refund_percentage
            }
        }

    async def _request_clarification(self, user: User) -> Dict[str, Any]:
        """Request clarification when cancellation criteria is unclear"""

        # Get user's recent bookings to help with clarification
        recent_bookings = await self._get_recent_bookings(user, limit=3)

        if not recent_bookings:
            return {
                "response": "You don't have any bookings to cancel.",
                "action_taken": "no_bookings_found",
                "metadata": {"user_id": user.id}
            }

        # Build response with booking options
        response_parts = [
            "I can help you cancel a booking. Here are your recent bookings:",
            ""
        ]

        for booking in recent_bookings:
            status_emoji = "📋" if booking.status.value == "pending" else "✅" if booking.status.value == "confirmed" else "❌"

            # Get service name from booking items
            service_name = "Service"
            if hasattr(booking, 'booking_items') and booking.booking_items:
                service_name = booking.booking_items[0].service_name

            response_parts.append(
                f"{status_emoji} {booking.order_id} - {service_name} on {booking.preferred_date} ({booking.status.value})"
            )

        response_parts.extend([
            "",
            "Please provide the Order ID you want to cancel (e.g., 'cancel ORD123456') or say 'cancel latest' for your most recent booking."
        ])

        return {
            "response": "\n".join(response_parts),
            "action_taken": "clarification_requested",
            "metadata": {
                "user_id": user.id,
                "recent_bookings": [b.order_id for b in recent_bookings]
            }
        }
    
    async def _get_booking(self, booking_identifier: str | int, user: User):
        """
        Get booking by ID or order ID for the current user

        Args:
            booking_identifier: Booking ID (int) or order ID (str like "ORD123456")
            user: Current user

        Returns:
            Booking object or None
        """
        # Try to determine if it's an ID (int) or order ID (string)
        if isinstance(booking_identifier, int):
            # Query by internal ID with eager loading of booking_items
            result = await self.db.execute(
                select(Booking)
                .options(selectinload(Booking.booking_items))
                .where(
                    Booking.id == booking_identifier,
                    Booking.user_id == user.id
                )
            )
        else:
            # Query by order ID (string like "ORD123456") with eager loading
            result = await self.db.execute(
                select(Booking)
                .options(selectinload(Booking.booking_items))
                .where(
                    Booking.order_id == str(booking_identifier).upper(),
                    Booking.user_id == user.id
                )
            )
        return result.scalar_one_or_none()

    async def _get_latest_booking(self, user: User):
        """
        Get the user's latest booking that can potentially be cancelled

        Args:
            user: Current user

        Returns:
            Latest booking or None
        """
        from src.core.models import BookingStatus

        # Get latest booking that's not completed or already cancelled
        result = await self.db.execute(
            select(Booking).where(
                Booking.user_id == user.id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            ).order_by(Booking.created_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def _get_bookings_by_service_type(self, service_type: str, user: User) -> list:
        """
        Get bookings by service type for the user

        Args:
            service_type: Service type (e.g., "ac_repair", "tv_repair")
            user: Current user

        Returns:
            List of bookings for that service type
        """
        from src.core.models import BookingStatus, BookingItem

        # Join with BookingItem to filter by service type
        result = await self.db.execute(
            select(Booking).join(BookingItem).where(
                Booking.user_id == user.id,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                BookingItem.service_name.ilike(f"%{service_type.replace('_', ' ')}%")
            ).order_by(Booking.created_at.desc()).limit(5)
        )
        return list(result.scalars().all())

    async def _get_recent_bookings(self, user: User, limit: int = 5) -> list:
        """
        Get user's recent bookings

        Args:
            user: Current user
            limit: Maximum number of bookings to return

        Returns:
            List of recent bookings
        """
        from sqlalchemy.orm import selectinload
        result = await self.db.execute(
            select(Booking).options(selectinload(Booking.booking_items)).where(
                Booking.user_id == user.id
            ).order_by(Booking.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
    
    async def _can_cancel_booking(self, booking: Booking) -> tuple[bool, str]:
        """
        Check if booking can be cancelled
        
        Args:
            booking: Booking object
        
        Returns:
            Tuple of (can_cancel: bool, message: str)
        """
        # Check booking status
        if booking.status.value == BookingStatus.CANCELLED.value:
            return False, "This booking is already cancelled."

        if booking.status.value == BookingStatus.COMPLETED.value:
            return False, "Cannot cancel a completed booking."

        if booking.status.value == BookingStatus.IN_PROGRESS.value:
            return False, "Cannot cancel a booking that is currently in progress."
        
        # Check if service has already started
        # Handle potential None values and convert to datetime
        if booking.preferred_date is None or booking.preferred_time is None:
            return True, "Booking can be cancelled (no scheduled time)"

        try:
            scheduled_datetime = datetime.combine(booking.preferred_date, booking.preferred_time)  # type: ignore
        except (TypeError, AttributeError):
            # If there's an issue with date/time conversion, allow cancellation
            return True, "Booking can be cancelled"
        
        now = datetime.now()
        
        if now >= scheduled_datetime:
            return False, "Cannot cancel a booking after the scheduled service time has passed."
        
        return True, "Booking can be cancelled."
    
    async def _calculate_refund(self, booking: Booking) -> Dict[str, Any]:
        """
        Calculate refund amount based on cancellation policy
        
        Args:
            booking: Booking object
        
        Returns:
            Dict with refund details
        """
        # Calculate hours until service
        try:
            scheduled_datetime = datetime.combine(booking.preferred_date, booking.preferred_time)  # type: ignore
        except (TypeError, AttributeError):
            # If there's an issue with date/time conversion, return 0 hours (no refund)
            total_amount = float(booking.total) if booking.total is not None else 0.0
            return {
                "refund_percentage": 0,
                "refund_amount": 0.0,
                "cancellation_fee": total_amount,
                "policy_message": "No refund (unable to determine service time)"
            }
        
        now = datetime.now()
        hours_until_service = (scheduled_datetime - now).total_seconds() / 3600
        
        # Determine refund percentage based on policy
        if hours_until_service >= self.FULL_REFUND_HOURS:
            refund_percentage = 100
            policy_message = f"Full refund (cancelled more than {self.FULL_REFUND_HOURS} hours before service)"
        elif hours_until_service >= self.HALF_REFUND_HOURS:
            refund_percentage = 50
            policy_message = f"50% refund (cancelled {self.HALF_REFUND_HOURS}-{self.FULL_REFUND_HOURS} hours before service)"
        elif hours_until_service >= self.QUARTER_REFUND_HOURS:
            refund_percentage = 25
            policy_message = f"25% refund (cancelled {self.QUARTER_REFUND_HOURS}-{self.HALF_REFUND_HOURS} hours before service)"
        else:
            refund_percentage = 0
            policy_message = f"No refund (cancelled less than {self.QUARTER_REFUND_HOURS} hours before service)"
        
        # Calculate refund amount
        try:
            total_amount = float(booking.total) if booking.total is not None else 0.0
        except (TypeError, ValueError):
            total_amount = 0.0
        refund_amount = (total_amount * refund_percentage) / 100
        cancellation_fee = total_amount - refund_amount
        
        return {
            "hours_until_service": round(hours_until_service, 2),
            "refund_percentage": refund_percentage,
            "total_amount": total_amount,
            "refund_amount": refund_amount,
            "cancellation_fee": cancellation_fee,
            "policy_message": policy_message
        }
    
    async def _process_cancellation(
        self,
        booking: Booking,
        reason: str,
        refund_info: Dict[str, Any],
        user: User
    ) -> Dict[str, Any]:
        """
        Process the cancellation and refund
        
        Args:
            booking: Booking object
            reason: Cancellation reason
            refund_info: Refund calculation details
            user: Current user
        
        Returns:
            Response dict with cancellation details
        """
        # Update booking status using SQLAlchemy update
        from sqlalchemy import update
        await self.db.execute(
            update(Booking).where(Booking.id == booking.id).values(
                status=BookingStatus.CANCELLED,
                cancellation_reason=reason,
                cancelled_at=datetime.now(timezone.utc)
            )
        )
        
        # Update booking items status using SQLAlchemy update
        from src.core.models.booking_item import ItemStatus, CancelBy
        await self.db.execute(
            update(BookingItem).where(BookingItem.booking_id == booking.id).values(
                status=ItemStatus.CANCELLED,
                cancel_by=CancelBy.CUSTOMER,
                cancel_reason=reason
            )
        )
        
        # Process refund if applicable
        refund_processed = False
        refund_method = "N/A"
        
        if refund_info["refund_amount"] > 0:
            # Check payment method and status using .value for enum comparison
            if (booking.payment_method.value == PaymentMethod.WALLET.value and
                booking.payment_status.value == PaymentStatus.PAID.value):
                # Refund to wallet using update statement
                from src.core.models import User
                await self.db.execute(
                    update(User).where(User.id == user.id).values(
                        wallet_balance=User.wallet_balance + Decimal(str(refund_info["refund_amount"]))
                    )
                )
                await self.db.execute(
                    update(Booking).where(Booking.id == booking.id).values(
                        payment_status=PaymentStatus.REFUNDED
                    )
                )
                refund_processed = True
                refund_method = "wallet"
                self.logger.info(f"Refunded Rs. {refund_info['refund_amount']} to wallet for booking {booking.id}")
            elif booking.payment_status.value == PaymentStatus.PAID.value:
                # Mark for refund (will be processed by payment gateway)
                await self.db.execute(
                    update(Booking).where(Booking.id == booking.id).values(
                        payment_status=PaymentStatus.REFUNDED
                    )
                )
                refund_processed = True
                refund_method = booking.payment_method.value
                self.logger.info(f"Marked booking {booking.id} for refund via {refund_method}")
        
        await self.db.commit()
        
        # Build response message
        response_parts = [
            f"Booking {booking.order_id} has been cancelled successfully.",
            f"\nCancellation Details:",
            f"   - Order ID: {booking.order_id}",
            f"   - Total Amount: Rs. {refund_info['total_amount']:.2f}",
            f"   - Refund Amount: Rs. {refund_info['refund_amount']:.2f} ({refund_info['refund_percentage']}%)",
        ]

        if refund_info['cancellation_fee'] > 0:
            response_parts.append(f"   - Cancellation Fee: Rs. {refund_info['cancellation_fee']:.2f}")

        response_parts.append(f"   - Policy: {refund_info['policy_message']}")

        if refund_processed and refund_info['refund_amount'] > 0:
            if refund_method == "wallet":
                response_parts.append(f"\nRefund of Rs. {refund_info['refund_amount']:.2f} has been credited to your wallet.")
            else:
                response_parts.append(f"\nRefund of Rs. {refund_info['refund_amount']:.2f} will be processed to your {refund_method} within 5-7 business days.")
        elif refund_info['refund_amount'] == 0:
            response_parts.append(f"\nNote: No refund applicable as per cancellation policy.")
        
        response = "\n".join(response_parts)
        
        return {
            "response": response,
            "action_taken": "booking_cancelled",
            "metadata": {
                "booking_id": booking.id,
                "order_id": booking.order_id,
                "status": booking.status.value,
                "cancelled_at": booking.cancelled_at.isoformat(),
                "refund_info": refund_info,
                "refund_processed": refund_processed,
                "refund_method": refund_method
            }
        }

