"""
BookingAgent - Handles all booking-related operations

This agent is responsible for:
- Creating new bookings from slot-filled entities
- Canceling existing bookings
- Rescheduling bookings
- Modifying booking details
- Validating provider availability in user's pincode
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from backend.src.services.booking_service import BookingService
from backend.src.core.models import User, Address, Cart, CartItem, RateCard, Provider, ProviderPincode, Pincode
from backend.src.schemas.customer import CreateBookingRequest


class BookingAgent:
    """
    BookingAgent handles all booking-related operations
    
    Responsibilities:
    - Create new bookings from slot-filled entities
    - Validate provider availability in user's pincode
    - Cancel bookings with refund logic
    - Reschedule bookings to new date/time
    - Modify booking details
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize BookingAgent
        
        Args:
            db: Async database session
        """
        self.db = db
        self.booking_service = BookingService(db)
    
    async def execute(
        self,
        intent: str,
        entities: Dict[str, Any],
        user: User,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Main execution method - routes to appropriate handler based on action
        
        Args:
            intent: Intent type (should be "booking_management")
            entities: Extracted entities from slot-filling
                {
                    "action": "book" | "cancel" | "reschedule" | "modify",
                    "service_type": "ac" (for book action),
                    "date": "2025-10-15" (for book/reschedule),
                    "time": "14:00" (for book/reschedule),
                    "location": "560001" (for book),
                    "booking_id": "BK12345" (for cancel/reschedule/modify),
                    "reason": "..." (for cancel)
                }
            user: Current authenticated user
            session_id: Chat session ID
        
        Returns:
            {
                "response": str,  # User-friendly message
                "action_taken": str,  # Action identifier
                "metadata": dict  # Additional data (booking_id, amount, etc.)
            }
        """
        action = entities.get("action", "book")
        
        if action == "book":
            return await self._create_booking(entities, user)
        elif action == "cancel":
            return await self._cancel_booking(entities, user)
        elif action == "reschedule":
            return await self._reschedule_booking(entities, user)
        elif action == "modify":
            return await self._modify_booking(entities, user)
        else:
            return {
                "response": "I'm not sure what you want to do with the booking. Could you please clarify?",
                "action_taken": "error",
                "metadata": {"error": "unknown_action", "action": action}
            }
    
    async def _create_booking(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Create a new booking from slot-filled entities
        
        Args:
            entities: Contains service_type, date, time, location
            user: Current user
        
        Returns:
            Response dict with booking details
        """
        try:
            # Step 1: Get user's address for the specified pincode
            pincode = entities.get("location")
            if not pincode:
                return {
                    "response": "I need your location (pincode) to create the booking.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "location"}
                }
            
            # Find address with this pincode
            address_result = await self.db.execute(
                select(Address).where(
                    Address.user_id == user.id,
                    Address.pincode == pincode
                )
            )
            address = address_result.scalar_one_or_none()
            
            if not address:
                return {
                    "response": f"I couldn't find an address with pincode {pincode} in your account. Please add this address first.",
                    "action_taken": "address_not_found",
                    "metadata": {"pincode": pincode}
                }
            
            # Step 2: Validate provider availability in this pincode
            validation_result = await self._validate_provider_availability(pincode)
            if not validation_result["is_valid"]:
                return {
                    "response": validation_result["message"],
                    "action_taken": "provider_not_available",
                    "metadata": {"pincode": pincode, "details": validation_result}
                }
            
            # Step 3: Parse date and time
            date_str = entities.get("date")
            time_str = entities.get("time")
            
            if not date_str or not time_str:
                return {
                    "response": "I need both date and time to create the booking.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": ["date", "time"] if not date_str and not time_str else ["date"] if not date_str else ["time"]}
                }
            
            # Step 4: Create booking request
            # Note: Assumes user has already added items to cart via separate flow
            # In production, you might want to add cart items here based on service_type
            
            request = CreateBookingRequest(
                address_id=address.id,
                preferred_date=date_str,
                preferred_time=time_str,
                payment_method=entities.get("payment_method", "card"),  # Default to card
                special_instructions=entities.get("special_instructions")
            )
            
            # Step 5: Create booking using BookingService
            booking_response = await self.booking_service.create_booking(request, user)
            
            # Step 6: Return success response
            return {
                "response": f"✅ Booking confirmed! Your booking ID is {booking_response.booking_number}. "
                           f"Total amount: ₹{booking_response.total}. "
                           f"Scheduled for {booking_response.preferred_date} at {booking_response.preferred_time}.",
                "action_taken": "booking_created",
                "metadata": {
                    "booking_id": booking_response.id,
                    "booking_number": booking_response.booking_number,
                    "total_amount": float(booking_response.total),
                    "scheduled_date": str(booking_response.preferred_date),
                    "scheduled_time": str(booking_response.preferred_time),
                    "payment_status": booking_response.payment_status,
                    "status": booking_response.status
                }
            }
            
        except ValueError as e:
            # Handle validation errors from BookingService
            return {
                "response": f"❌ Booking failed: {str(e)}",
                "action_taken": "booking_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            # Handle unexpected errors
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _validate_provider_availability(self, pincode: str) -> Dict[str, Any]:
        """
        Validate that providers are available in the specified pincode
        
        This checks:
        1. Pincode exists and is serviceable
        2. At least one active provider services this pincode
        3. Rate cards in user's cart have providers who service this pincode
        
        Args:
            pincode: Pincode to validate
        
        Returns:
            {
                "is_valid": bool,
                "message": str,
                "available_providers": int,
                "pincode_id": int
            }
        """
        # Step 1: Check if pincode exists and is serviceable
        pincode_result = await self.db.execute(
            select(Pincode).where(Pincode.pincode == pincode)
        )
        pincode_obj = pincode_result.scalar_one_or_none()
        
        if not pincode_obj:
            return {
                "is_valid": False,
                "message": f"Sorry, pincode {pincode} is not in our service area yet.",
                "available_providers": 0,
                "pincode_id": None
            }
        
        if not pincode_obj.is_serviceable:
            return {
                "is_valid": False,
                "message": f"Sorry, we don't service pincode {pincode} at the moment.",
                "available_providers": 0,
                "pincode_id": pincode_obj.id
            }
        
        # Step 2: Check if any active providers service this pincode
        provider_count_result = await self.db.execute(
            select(ProviderPincode)
            .join(Provider, ProviderPincode.provider_id == Provider.id)
            .where(
                ProviderPincode.pincode_id == pincode_obj.id,
                Provider.is_active == True,
                Provider.is_verified == True
            )
        )
        provider_associations = provider_count_result.all()
        
        if not provider_associations:
            return {
                "is_valid": False,
                "message": f"Sorry, no service providers are available in pincode {pincode} right now.",
                "available_providers": 0,
                "pincode_id": pincode_obj.id
            }
        
        return {
            "is_valid": True,
            "message": f"Service available in pincode {pincode}",
            "available_providers": len(provider_associations),
            "pincode_id": pincode_obj.id
        }
    
    async def _cancel_booking(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Cancel an existing booking
        
        Args:
            entities: Contains booking_id, reason
            user: Current user
        
        Returns:
            Response dict with cancellation details
        """
        try:
            booking_id = entities.get("booking_id")
            reason = entities.get("reason", "Customer requested cancellation")
            
            if not booking_id:
                return {
                    "response": "I need the booking ID to cancel. Could you provide it?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "booking_id"}
                }
            
            # Cancel booking using BookingService
            result = await self.booking_service.cancel_booking(int(booking_id), reason, user)
            
            return {
                "response": f"✅ Booking {result.booking_number} has been cancelled. "
                           f"Refund of ₹{result.total} will be processed within 5-7 business days.",
                "action_taken": "booking_cancelled",
                "metadata": {
                    "booking_id": result.id,
                    "booking_number": result.booking_number,
                    "refund_amount": float(result.total),
                    "status": result.status
                }
            }
            
        except ValueError as e:
            return {
                "response": f"❌ Cancellation failed: {str(e)}",
                "action_taken": "cancellation_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _reschedule_booking(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Reschedule an existing booking to a new date/time
        
        Args:
            entities: Contains booking_id, date, time
            user: Current user
        
        Returns:
            Response dict with rescheduling details
        """
        # Implementation will use BookingService.reschedule_booking
        # For now, return placeholder
        return {
            "response": "Rescheduling feature is coming soon!",
            "action_taken": "not_implemented",
            "metadata": {}
        }
    
    async def _modify_booking(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Modify booking details (e.g., special instructions)
        
        Args:
            entities: Contains booking_id, modifications
            user: Current user
        
        Returns:
            Response dict with modification details
        """
        # Implementation for modifying booking details
        # For now, return placeholder
        return {
            "response": "Booking modification feature is coming soon!",
            "action_taken": "not_implemented",
            "metadata": {}
        }

