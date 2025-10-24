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
    
    def __init__(self, db: AsyncSession):
        """
        Initialize CancellationAgent
        
        Args:
            db: Database session
        """
        self.db = db
        self.logger = logging.getLogger(__name__)
    
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
            entities: Extracted entities (booking_id, reason)
        
        Returns:
            {
                "response": str,  # User-friendly message
                "action_taken": str,  # Action identifier
                "metadata": dict  # Cancellation details
            }
        """
        try:
            booking_id = entities.get("booking_id")
            reason = entities.get("reason", "Customer requested cancellation")
            
            if not booking_id:
                return {
                    "response": "I need the booking ID to process the cancellation. Could you provide your booking number?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "booking_id"}
                }
            
            # Get booking details
            # booking_id can be either the internal ID (int) or booking_number (string like "BK123456")
            booking = await self._get_booking(booking_id, user)

            if not booking:
                return {
                    "response": f"❌ Booking {booking_id} not found. Please check the booking number and try again.",
                    "action_taken": "booking_not_found",
                    "metadata": {"booking_id": booking_id}
                }
            
            # Check if booking can be cancelled
            can_cancel, cancel_message = await self._can_cancel_booking(booking)
            
            if not can_cancel:
                return {
                    "response": f"❌ {cancel_message}",
                    "action_taken": "cancellation_not_allowed",
                    "metadata": {
                        "booking_id": booking.id,
                        "booking_number": booking.booking_number,
                        "status": booking.status.value,
                        "reason": cancel_message
                    }
                }
            
            # Calculate refund based on cancellation policy
            refund_info = await self._calculate_refund(booking)
            
            # Process cancellation
            result = await self._process_cancellation(booking, reason, refund_info, user)
            
            return result
            
        except ValueError as e:
            self.logger.error(f"Cancellation validation error: {e}")
            return {
                "response": f"❌ Cancellation failed: {str(e)}",
                "action_taken": "cancellation_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            self.logger.error(f"Cancellation error: {e}", exc_info=True)
            return {
                "response": "❌ An unexpected error occurred while processing your cancellation. Please contact support.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _get_booking(self, booking_identifier: str | int, user: User) -> Booking:
        """
        Get booking by ID or booking number for the current user

        Args:
            booking_identifier: Booking ID (int) or booking number (str like "BK123456")
            user: Current user

        Returns:
            Booking object or None
        """
        # Try to determine if it's an ID (int) or booking number (string)
        if isinstance(booking_identifier, int):
            # Query by internal ID
            result = await self.db.execute(
                select(Booking).where(
                    Booking.id == booking_identifier,
                    Booking.user_id == user.id
                )
            )
        else:
            # Query by booking number (string like "BK123456")
            result = await self.db.execute(
                select(Booking).where(
                    Booking.booking_number == str(booking_identifier).upper(),
                    Booking.user_id == user.id
                )
            )
        return result.scalar_one_or_none()
    
    async def _can_cancel_booking(self, booking: Booking) -> tuple[bool, str]:
        """
        Check if booking can be cancelled
        
        Args:
            booking: Booking object
        
        Returns:
            Tuple of (can_cancel: bool, message: str)
        """
        # Check booking status
        if booking.status == BookingStatus.CANCELLED:
            return False, "This booking is already cancelled."
        
        if booking.status == BookingStatus.COMPLETED:
            return False, "Cannot cancel a completed booking."
        
        if booking.status == BookingStatus.IN_PROGRESS:
            return False, "Cannot cancel a booking that is currently in progress."
        
        # Check if service has already started
        scheduled_datetime = datetime.combine(
            booking.preferred_date,
            booking.preferred_time
        )
        
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
        scheduled_datetime = datetime.combine(
            booking.preferred_date,
            booking.preferred_time
        )
        
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
        total_amount = float(booking.total)
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
            from src.core.models.booking_item import ItemStatus, CancelBy
            item.status = ItemStatus.CANCELLED
            item.cancel_by = CancelBy.CUSTOMER
            item.cancel_reason = reason
        
        # Process refund if applicable
        refund_processed = False
        refund_method = "N/A"
        
        if refund_info["refund_amount"] > 0:
            if booking.payment_method == PaymentMethod.WALLET and booking.payment_status == PaymentStatus.PAID:
                # Refund to wallet
                user.wallet_balance += Decimal(str(refund_info["refund_amount"]))
                booking.payment_status = PaymentStatus.REFUNDED
                refund_processed = True
                refund_method = "wallet"
                self.logger.info(f"Refunded ₹{refund_info['refund_amount']} to wallet for booking {booking.id}")
            elif booking.payment_status == PaymentStatus.PAID:
                # Mark for refund (will be processed by payment gateway)
                booking.payment_status = PaymentStatus.REFUNDED
                refund_processed = True
                refund_method = booking.payment_method.value
                self.logger.info(f"Marked booking {booking.id} for refund via {refund_method}")
        
        await self.db.commit()
        
        # Build response message
        response_parts = [
            f"✅ Booking {booking.booking_number} has been cancelled successfully.",
            f"\n📋 Cancellation Details:",
            f"   • Booking ID: {booking.booking_number}",
            f"   • Total Amount: ₹{refund_info['total_amount']:.2f}",
            f"   • Refund Amount: ₹{refund_info['refund_amount']:.2f} ({refund_info['refund_percentage']}%)",
        ]
        
        if refund_info['cancellation_fee'] > 0:
            response_parts.append(f"   • Cancellation Fee: ₹{refund_info['cancellation_fee']:.2f}")
        
        response_parts.append(f"   • Policy: {refund_info['policy_message']}")
        
        if refund_processed and refund_info['refund_amount'] > 0:
            if refund_method == "wallet":
                response_parts.append(f"\n💰 Refund of ₹{refund_info['refund_amount']:.2f} has been credited to your wallet.")
            else:
                response_parts.append(f"\n💰 Refund of ₹{refund_info['refund_amount']:.2f} will be processed to your {refund_method} within 5-7 business days.")
        elif refund_info['refund_amount'] == 0:
            response_parts.append(f"\n⚠️ No refund applicable as per cancellation policy.")
        
        response = "\n".join(response_parts)
        
        return {
            "response": response,
            "action_taken": "booking_cancelled",
            "metadata": {
                "booking_id": booking.id,
                "booking_number": booking.booking_number,
                "status": booking.status.value,
                "cancelled_at": booking.cancelled_at.isoformat(),
                "refund_info": refund_info,
                "refund_processed": refund_processed,
                "refund_method": refund_method
            }
        }

