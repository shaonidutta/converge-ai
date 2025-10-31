"""
RescheduleAgent - Handles booking rescheduling requests

This agent manages all booking rescheduling scenarios:
1. Reschedule by specific Order ID
2. Reschedule latest booking automatically
3. Reschedule by service type (e.g., "reschedule my AC repair")
4. Request clarification when no specifics provided

Follows the same pattern as CancellationAgent for consistency.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, time
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Booking, User, BookingStatus
from src.services.booking_service import BookingService
from src.schemas.customer import RescheduleBookingRequest

logger = logging.getLogger(__name__)


class RescheduleAgent:
    """
    RescheduleAgent handles booking rescheduling with multiple scenarios
    
    Responsibilities:
    - Reschedule bookings by Order ID
    - Reschedule latest booking automatically
    - Reschedule bookings by service type
    - Validate reschedule eligibility
    - Validate new date/time
    - Process rescheduling through BookingService
    """
    
    def __init__(self, db: AsyncSession, dialog_state_manager=None):
        """
        Initialize RescheduleAgent

        Args:
            db: Database session
            dialog_state_manager: DialogStateManager instance (optional, will be created if not provided)
        """
        self.db = db
        self.booking_service = BookingService(db)
        self.logger = logger
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
        Execute reschedule request
        
        Args:
            message: User message
            user: Current user
            session_id: Session ID
            entities: Extracted entities
        
        Returns:
            Response dict with rescheduling details
        """
        try:
            # Extract entities
            booking_id = entities.get("booking_id")
            service_type = entities.get("service_type")
            booking_filter = entities.get("booking_filter")  # "latest", "recent", etc.
            new_date = entities.get("new_date") or entities.get("date")
            new_time = entities.get("new_time") or entities.get("time")
            reason = entities.get("reason", "Customer requested reschedule")
            
            self.logger.info(
                f"[RescheduleAgent] Processing reschedule request: "
                f"booking_id={booking_id}, service_type={service_type}, "
                f"booking_filter={booking_filter}, new_date={new_date}, new_time={new_time}"
            )
            
            # Enhanced logic: handle different reschedule scenarios
            if booking_id:
                # Scenario 1: Direct booking ID provided
                return await self._reschedule_by_booking_id(
                    booking_id, new_date, new_time, reason, user, session_id
                )

            elif booking_filter == "latest" or "latest" in message.lower():
                # Scenario 2: Reschedule latest booking
                return await self._reschedule_latest_booking(
                    new_date, new_time, reason, user, session_id
                )

            elif service_type:
                # Scenario 3: Reschedule by service type
                return await self._reschedule_by_service_type(
                    service_type, new_date, new_time, reason, user, session_id
                )

            elif any(keyword in message.lower() for keyword in ["latest", "recent", "last"]):
                # Scenario 4: Implicit latest booking request
                return await self._reschedule_latest_booking(
                    new_date, new_time, reason, user, session_id
                )
            
            else:
                # Scenario 5: No specific criteria provided
                return await self._request_clarification(user)
        
        except Exception as e:
            self.logger.error(f"[RescheduleAgent] Error: {e}", exc_info=True)
            return {
                "response": f"❌ An error occurred while processing your reschedule request: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def execute_confirmed_reschedule(
        self,
        pending_action: Dict[str, Any],
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Execute a confirmed reschedule from pending action

        Args:
            pending_action: Pending action details from dialog state
            user: Current user
            session_id: Session ID

        Returns:
            Response dict with reschedule result
        """
        try:
            order_id = pending_action.get("order_id")
            new_date = pending_action.get("new_date")
            new_time = pending_action.get("new_time")
            reason = pending_action.get("reason", "Customer requested reschedule")

            # Execute reschedule with confirmed=True to skip confirmation
            result = await self._reschedule_by_booking_id(
                booking_id=order_id,
                new_date=new_date,
                new_time=new_time,
                reason=reason,
                user=user,
                session_id=session_id,
                confirmed=True
            )

            # Clear pending action from dialog state
            await self.dialog_state_manager.clear_pending_action(session_id)

            return result

        except Exception as e:
            self.logger.error(f"Error executing confirmed reschedule: {str(e)}", exc_info=True)
            return {
                "response": "An error occurred while processing your reschedule. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
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
        from sqlalchemy.orm import selectinload
        from src.core.models import BookingItem

        # Try to determine if it's an ID (int) or order ID (string)
        if isinstance(booking_identifier, int):
            # Query by internal ID with eager loading of booking_items
            result = await self.db.execute(
                select(Booking)
                .options(selectinload(Booking.booking_items))
                .where(
                    and_(
                        Booking.id == booking_identifier,
                        Booking.user_id == user.id
                    )
                )
            )
        else:
            # Query by order ID (string like "ORD123456") with eager loading of booking_items
            result = await self.db.execute(
                select(Booking)
                .options(selectinload(Booking.booking_items))
                .where(
                    and_(
                        Booking.order_id == str(booking_identifier).upper(),
                        Booking.user_id == user.id
                    )
                )
            )
        return result.scalar_one_or_none()

    async def _reschedule_by_booking_id(
        self,
        booking_id: str | int,
        new_date: Optional[str],
        new_time: Optional[str],
        reason: str,
        user: User,
        session_id: str,
        confirmed: bool = False
    ) -> Dict[str, Any]:
        """
        Reschedule booking by Order ID

        Args:
            booking_id: Order ID (e.g., "ORD123456") or internal booking ID (int)
            new_date: New preferred date
            new_time: New preferred time
            reason: Reason for rescheduling
            user: Current user
            session_id: Session ID for dialog state
            confirmed: If True, skip confirmation and proceed with reschedule

        Returns:
            Response dict
        """
        self.logger.info(f"[RescheduleAgent] Rescheduling by booking_id: {booking_id}")

        # Get booking using helper method (handles both int ID and string order_id)
        booking = await self._get_booking(booking_id, user)

        if not booking:
            return {
                "response": f"❌ I couldn't find a booking with Order ID {booking_id}. Please check the Order ID and try again.",
                "action_taken": "booking_not_found",
                "metadata": {"order_id": booking_id}
            }

        # Check if new date and time are provided
        if not new_date or not new_time:
            return {
                "response": f"📅 To reschedule Order {booking.order_id}, I need the new date and time. "
                           f"Please provide both (e.g., 'reschedule to 2025-11-05 at 14:00').",
                "action_taken": "missing_datetime",
                "metadata": {
                    "order_id": booking.order_id,
                    "missing": "new_date" if not new_date else "new_time"
                }
            }

        # If not confirmed, request confirmation
        if not confirmed:
            return await self._request_reschedule_confirmation(
                booking, new_date, new_time, reason, user, session_id
            )

        # Process reschedule (confirmed)
        return await self._process_reschedule(booking, new_date, new_time, reason, user)
    
    async def _reschedule_latest_booking(
        self,
        new_date: Optional[str],
        new_time: Optional[str],
        reason: str,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Reschedule user's latest booking

        Args:
            new_date: New preferred date
            new_time: New preferred time
            reason: Reason for rescheduling
            user: Current user
            session_id: Session ID for dialog state

        Returns:
            Response dict
        """
        self.logger.info(f"[RescheduleAgent] Rescheduling latest booking for user {user.id}")

        # Find latest booking
        result = await self.db.execute(
            select(Booking)
            .where(
                and_(
                    Booking.user_id == user.id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                )
            )
            .order_by(desc(Booking.created_at))
            .limit(1)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return {
                "response": "❌ You don't have any active bookings to reschedule.",
                "action_taken": "no_bookings",
                "metadata": {}
            }

        # Check if new date and time are provided
        if not new_date or not new_time:
            return {
                "response": f"📅 To reschedule your latest booking (Order {booking.order_id}), "
                           f"I need the new date and time. Please provide both.",
                "action_taken": "missing_datetime",
                "metadata": {"booking_id": booking.order_id}
            }

        # Use the existing reschedule logic with confirmation
        return await self._reschedule_by_booking_id(
            booking.order_id, new_date, new_time, reason, user, session_id
        )

    async def _reschedule_by_service_type(
        self,
        service_type: str,
        new_date: Optional[str],
        new_time: Optional[str],
        reason: str,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Reschedule booking by service type

        Args:
            service_type: Service type (e.g., "ac_repair", "plumbing")
            new_date: New preferred date
            new_time: New preferred time
            reason: Reason for rescheduling
            user: Current user
            session_id: Session ID for dialog state

        Returns:
            Response dict
        """
        self.logger.info(f"[RescheduleAgent] Rescheduling by service_type: {service_type}")

        # Find booking by service type
        result = await self.db.execute(
            select(Booking)
            .where(
                and_(
                    Booking.user_id == user.id,
                    Booking.service_name.ilike(f"%{service_type}%"),
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                )
            )
            .order_by(desc(Booking.created_at))
            .limit(1)
        )
        booking = result.scalar_one_or_none()

        if not booking:
            return {
                "response": f"❌ You don't have any active {service_type} bookings to reschedule.",
                "action_taken": "no_service_bookings",
                "metadata": {"service_type": service_type}
            }

        # Check if new date and time are provided
        if not new_date or not new_time:
            return {
                "response": f"📅 To reschedule your {service_type} booking (Order {booking.order_id}), "
                           f"I need the new date and time. Please provide both.",
                "action_taken": "missing_datetime",
                "metadata": {
                    "booking_id": booking.order_id,
                    "service_type": service_type
                }
            }

        # Use the existing reschedule logic with confirmation
        return await self._reschedule_by_booking_id(
            booking.order_id, new_date, new_time, reason, user, session_id
        )
    
    async def _request_reschedule_confirmation(
        self,
        booking: Booking,
        new_date: str,
        new_time: str,
        reason: str,
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Request user confirmation before rescheduling booking

        Args:
            booking: Booking to reschedule
            new_date: New preferred date
            new_time: New preferred time
            reason: Reschedule reason
            user: Current user
            session_id: Session ID for dialog state

        Returns:
            Response dict with confirmation request
        """
        # Get service name from booking items
        service_name = "Service"
        if hasattr(booking, 'booking_items') and booking.booking_items:
            service_name = booking.booking_items[0].service_name

        # Format booking details
        booking_details = {
            "booking_id": booking.id,
            "order_id": booking.order_id,
            "service_name": service_name,
            "preferred_date": str(booking.preferred_date),
            "preferred_time": str(booking.preferred_time)
        }

        # Store pending action in dialog state
        await self.dialog_state_manager.set_pending_reschedule(
            session_id=session_id,
            user_id=user.id,
            booking_details=booking_details,
            new_date=new_date,
            new_time=new_time,
            reason=reason
        )

        # Build confirmation message
        response = f"""📅 **Booking Reschedule Confirmation**

**Order ID:** {booking.order_id}
**Service:** {service_name}

**Current Schedule:**
- Date: {booking.preferred_date}
- Time: {booking.preferred_time}

**New Schedule:**
- Date: {new_date}
- Time: {new_time}

⚠️ **Do you want to proceed with this reschedule?**

Reply with **'yes'** to confirm reschedule or **'no'** to cancel."""

        return {
            "response": response,
            "action_taken": "awaiting_confirmation",
            "requires_confirmation": True,
            "metadata": {
                "order_id": booking.order_id,
                "booking_id": booking.id,
                "old_date": str(booking.preferred_date),
                "old_time": str(booking.preferred_time),
                "new_date": new_date,
                "new_time": new_time
            }
        }

    async def _request_clarification(self, user: User) -> Dict[str, Any]:
        """
        Request clarification when no specific booking is identified
        
        Args:
            user: Current user
        
        Returns:
            Response dict with booking list
        """
        self.logger.info(f"[RescheduleAgent] Requesting clarification for user {user.id}")
        
        # Get user's active bookings
        result = await self.db.execute(
            select(Booking)
            .where(
                and_(
                    Booking.user_id == user.id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                )
            )
            .order_by(desc(Booking.created_at))
            .limit(5)
        )
        bookings = result.scalars().all()
        
        if not bookings:
            return {
                "response": "❌ You don't have any active bookings to reschedule.",
                "action_taken": "no_bookings",
                "metadata": {}
            }
        
        # Format booking list
        booking_list = "\n\n".join([
            f"📋 {booking.order_id} - {booking.service_name} - {booking.preferred_date} at {booking.preferred_time} "
            f"(Status: {booking.status.value})"
            for booking in bookings
        ])
        
        return {
            "response": f"I can help you reschedule a booking. Here are your active bookings:\n\n{booking_list}\n\n"
                       f"Please provide the Order ID and new date/time you'd like to reschedule to.",
            "action_taken": "clarification_requested",
            "metadata": {
                "booking_count": len(bookings),
                "bookings": [b.order_id for b in bookings]
            }
        }

    async def _process_reschedule(
        self,
        booking: Booking,
        new_date: str,
        new_time: str,
        reason: str,
        user: User
    ) -> Dict[str, Any]:
        """
        Process the actual rescheduling

        Args:
            booking: Booking to reschedule
            new_date: New preferred date
            new_time: New preferred time
            reason: Reason for rescheduling
            user: Current user

        Returns:
            Response dict
        """
        try:
            # Validate reschedule eligibility
            can_reschedule, message = await self._validate_reschedule_eligibility(booking)
            if not can_reschedule:
                return {
                    "response": f"❌ {message}",
                    "action_taken": "reschedule_not_allowed",
                    "metadata": {
                        "order_id": booking.order_id,
                        "reason": message
                    }
                }

            # Validate new date and time
            is_valid, validation_message = await self._validate_new_datetime(new_date, new_time)
            if not is_valid:
                return {
                    "response": f"❌ {validation_message}",
                    "action_taken": "invalid_datetime",
                    "metadata": {
                        "order_id": booking.order_id,
                        "new_date": new_date,
                        "new_time": new_time
                    }
                }

            # Create reschedule request
            reschedule_request = RescheduleBookingRequest(
                preferred_date=new_date,
                preferred_time=new_time,
                reason=reason
            )

            # Reschedule booking using BookingService
            result = await self.booking_service.reschedule_booking(
                booking.id,
                reschedule_request,
                user
            )

            self.logger.info(
                f"[RescheduleAgent] Successfully rescheduled booking {booking.order_id} "
                f"to {new_date} at {new_time}"
            )

            # Get service name from booking items
            service_name = "Service"
            if result.items and len(result.items) > 0:
                service_name = result.items[0].service_name

            return {
                "response": f"✅ Your booking (Order {result.order_id}) has been successfully rescheduled!\n\n"
                           f"📅 New Date: {new_date}\n"
                           f"🕐 New Time: {new_time}\n"
                           f"📋 Service: {service_name}\n\n"
                           f"You will receive a confirmation shortly.",
                "action_taken": "booking_rescheduled",
                "metadata": {
                    "booking_id": result.id,
                    "order_id": result.order_id,
                    "old_date": str(booking.preferred_date),
                    "old_time": str(booking.preferred_time),
                    "new_date": new_date,
                    "new_time": new_time,
                    "service_name": service_name
                }
            }

        except ValueError as e:
            self.logger.error(f"[RescheduleAgent] ValueError: {e}")
            return {
                "response": f"❌ Rescheduling failed: {str(e)}",
                "action_taken": "reschedule_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            self.logger.error(f"[RescheduleAgent] Error processing reschedule: {e}", exc_info=True)
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _validate_reschedule_eligibility(self, booking: Booking) -> tuple[bool, str]:
        """
        Validate if booking can be rescheduled

        Args:
            booking: Booking to validate

        Returns:
            Tuple of (can_reschedule, message)
        """
        # Check booking status
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            return False, f"Cannot reschedule booking with status: {booking.status.value}. Only PENDING or CONFIRMED bookings can be rescheduled."

        # Check if service has already started
        if booking.preferred_date is None or booking.preferred_time is None:
            return True, "Booking can be rescheduled (no scheduled time)"

        try:
            scheduled_datetime = datetime.combine(booking.preferred_date, booking.preferred_time)
        except (TypeError, AttributeError):
            # If there's an issue with date/time conversion, allow rescheduling
            return True, "Booking can be rescheduled"

        now = datetime.now()

        if now >= scheduled_datetime:
            return False, "Cannot reschedule a booking after the scheduled service time has passed."

        return True, "Booking can be rescheduled."

    async def _validate_new_datetime(self, new_date: str, new_time: str) -> tuple[bool, str]:
        """
        Validate new date and time

        Args:
            new_date: New preferred date (YYYY-MM-DD format)
            new_time: New preferred time (HH:MM format)

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Parse date
            parsed_date = datetime.strptime(new_date, "%Y-%m-%d").date()

            # Parse time
            parsed_time = datetime.strptime(new_time, "%H:%M").time()

            # Check if new date is in the future
            if parsed_date < datetime.now().date():
                return False, "The new date must be in the future."

            # Check if new datetime is at least 2 hours from now
            new_datetime = datetime.combine(parsed_date, parsed_time)
            now = datetime.now()

            if new_datetime < now:
                return False, "The new date and time must be in the future."

            # Check if it's at least 2 hours from now
            time_diff = (new_datetime - now).total_seconds() / 3600  # hours
            if time_diff < 2:
                return False, "Please schedule at least 2 hours in advance."

            return True, "Valid date and time"

        except ValueError as e:
            return False, f"Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time. Error: {str(e)}"

