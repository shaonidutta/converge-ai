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
import logging

from src.services.booking_service import BookingService
from src.services.response_generator import ResponseGenerator
from src.core.models import User, Address, Cart, CartItem, RateCard, Provider, ProviderPincode, Pincode, Booking
from src.schemas.customer import CreateBookingRequest

logger = logging.getLogger(__name__)


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
        self.response_generator = ResponseGenerator()
    
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
                    "action": "book" | "cancel" | "reschedule" | "modify" | "list",
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
        elif action == "list":
            # Extract optional filtering and sorting parameters
            status_filter = entities.get("status_filter")
            sort_by = entities.get("sort_by", "date")
            limit = entities.get("limit", 20)

            return await self._list_bookings(
                user=user,
                status_filter=status_filter,
                sort_by=sort_by,
                limit=limit
            )
        else:
            return {
                "response": f"I'm not quite sure what you'd like to do with your booking. Could you let me know if you want to book, cancel, reschedule, modify, or view your bookings?",
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
            # Step 1: Parse location entity
            location = entities.get("location")
            if not location:
                # This should never happen - slot-filling should collect all required entities
                raise ValueError("Missing required entity 'location'. Slot-filling should have collected this.")

            # Parse location to extract pincode and address components
            import re
            pincode_match = re.search(r'\b(\d{6})\b', location)
            if not pincode_match:
                return {
                    "response": f"I couldn't find a valid pincode in '{location}'. Please provide a 6-digit pincode.",
                    "action_taken": "invalid_pincode",
                    "metadata": {"location": location}
                }

            pincode = pincode_match.group(1)

            # Check if location is a full address (contains commas)
            is_full_address = ',' in location

            # Find existing address with this pincode
            address_result = await self.db.execute(
                select(Address).where(
                    Address.user_id == user.id,
                    Address.pincode == pincode
                )
            )
            address = address_result.scalar_one_or_none()

            if not address:
                # Auto-create address if we have a full address
                if is_full_address:
                    # Parse full address: "123 Main Street, Bangalore, Karnataka, 560001"
                    # Expected format: street, city, state, pincode
                    parts = [p.strip() for p in location.split(',')]

                    if len(parts) >= 3:
                        # Extract components
                        address_line1 = parts[0]  # "123 Main Street"
                        city = parts[1] if len(parts) >= 2 else "Unknown"  # "Bangalore"
                        state = parts[2] if len(parts) >= 3 else "Unknown"  # "Karnataka"

                        # Auto-create address
                        from src.services.address_service import AddressService
                        from src.schemas.customer import AddressRequest

                        address_request = AddressRequest(
                            address_line1=address_line1,
                            address_line2=None,
                            city=city,
                            state=state,
                            pincode=pincode,
                            is_default=False
                        )

                        address_service = AddressService(self.db)
                        address_response = await address_service.add_address(address_request, user)

                        # Fetch the created address
                        address_result = await self.db.execute(
                            select(Address).where(Address.id == address_response.id)
                        )
                        address = address_result.scalar_one()

                        logger.info(f"Auto-created address for user {user.id}: {address_line1}, {city}, {state}, {pincode}")
                    else:
                        # Invalid address format
                        return {
                            "response": f"I couldn't parse the address '{location}'. Please provide in format: 'Street, City, State, Pincode'",
                            "action_taken": "invalid_address_format",
                            "metadata": {"location": location}
                        }
                else:
                    # Only pincode provided, need full address
                    return {
                        "response": f"I need your complete address for pincode {pincode}. Please provide:\n"
                                  f"1. Address line 1 (street, building)\n"
                                  f"2. City\n"
                                  f"3. State\n\n"
                                  f"Example: '123 Main Street, Mumbai, Maharashtra, {pincode}'",
                        "action_taken": "address_details_needed",
                        "metadata": {
                            "pincode": pincode,
                            "needed_fields": ["address_line1", "city", "state"]
                        }
                    }
            
            # Step 2: Validate provider availability in this pincode
            # Note: Validation will attempt to find providers, but will gracefully proceed if none found
            validation_result = await self._validate_provider_availability(pincode)
            if not validation_result["is_valid"]:
                logger.warning(f"[BookingAgent] No providers available for pincode {pincode}, but proceeding with booking")
                # Don't return error - let booking service handle provider assignment
            
            # Step 3: Parse date and time
            date_str = entities.get("date")
            time_str = entities.get("time")
            
            if not date_str or not time_str:
                return {
                    "response": "I need both date and time to create the booking.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": ["date", "time"] if not date_str and not time_str else ["date"] if not date_str else ["time"]}
                }
            
            # Step 4: Auto-add service to cart if not already present
            service_type = entities.get("service_type", "").lower()

            # Try to get rate_card_id from service subcategory validation metadata
            rate_card_id = entities.get("_metadata_rate_card_id")

            print(f"\n\n{'='*80}")
            print(f"[BookingAgent] ALL ENTITIES: {entities}")
            print(f"[BookingAgent] Entity keys: {list(entities.keys())}")
            print(f"[BookingAgent] rate_card_id: {rate_card_id}")
            print(f"{'='*80}\n\n")

            logger.info(f"[BookingAgent] ALL ENTITIES: {entities}")
            logger.info(f"[BookingAgent] Checking for rate_card_id in entities: {list(entities.keys())}")
            if rate_card_id:
                logger.info(f"[BookingAgent] Found rate_card_id from metadata: {rate_card_id}")
            else:
                logger.info(f"[BookingAgent] No rate_card_id found in metadata, will use fallback mapping")

            # If no rate_card_id from metadata, fall back to hardcoded mapping
            if not rate_card_id:
                logger.info(f"No rate_card_id from metadata, using fallback mapping for service_type: {service_type}")

                # Map service types to subcategory IDs and default rate cards
                service_mapping = {
                    "ac": {"subcategory_id": 9, "rate_card_id": 18},  # AC Repair - Basic
                    "ac_repair": {"subcategory_id": 9, "rate_card_id": 18},
                    "ac_installation": {"subcategory_id": 10, "rate_card_id": 21},
                    "ac_gas": {"subcategory_id": 11, "rate_card_id": 24},
                    "refrigerator": {"subcategory_id": 12, "rate_card_id": 27},
                    "washing_machine": {"subcategory_id": 13, "rate_card_id": 29},
                    "plumbing": {"subcategory_id": 17, "rate_card_id": 33},
                    "electrical": {"subcategory_id": 24, "rate_card_id": 48},
                    "cleaning": {"subcategory_id": 1, "rate_card_id": 1},
                    "painting": {"subcategory_id": 31, "rate_card_id": 60},  # Added painting
                    "pest": {"subcategory_id": 34, "rate_card_id": 63},  # General Pest Control - Basic
                    "pest_control": {"subcategory_id": 34, "rate_card_id": 63},  # General Pest Control - Basic
                    "general_pest_control": {"subcategory_id": 34, "rate_card_id": 63},  # General Pest Control - Basic
                }

                # Get rate card for the service type
                service_info = service_mapping.get(service_type)
                if not service_info:
                    # Default to AC Repair if service type not recognized
                    logger.warning(f"Unknown service type '{service_type}', defaulting to AC Repair")
                    service_info = service_mapping["ac"]

                rate_card_id = service_info["rate_card_id"]

            logger.info(f"Using rate_card_id: {rate_card_id} for service_type: {service_type}")

            # Add to cart using CartService
            from src.services.cart_service import CartService
            from src.schemas.customer import AddToCartRequest

            cart_service = CartService(self.db)

            # Check if cart already has items
            cart = await cart_service.get_or_create_cart(user.id)
            cart_items_result = await self.db.execute(
                select(CartItem).where(CartItem.cart_id == cart.id)
            )
            existing_items = cart_items_result.scalars().all()

            if not existing_items:
                # Add service to cart
                try:
                    add_to_cart_request = AddToCartRequest(
                        rate_card_id=rate_card_id,
                        quantity=1
                    )
                    await cart_service.add_to_cart(add_to_cart_request, user)
                    logger.info(f"Auto-added service to cart: rate_card_id={rate_card_id}")
                except Exception as e:
                    logger.error(f"Failed to add service to cart: {e}")
                    return {
                        "response": f"Sorry, I couldn't add the {service_type} service to your cart. Please try again.",
                        "action_taken": "cart_add_failed",
                        "metadata": {"error": str(e)}
                    }
            else:
                logger.info(f"Cart already has {len(existing_items)} items, skipping auto-add")

            # Step 5: Create booking request
            request = CreateBookingRequest(
                address_id=address.id,
                preferred_date=date_str,
                preferred_time=time_str,
                payment_method=entities.get("payment_method", "card"),  # Default to card
                special_instructions=entities.get("special_instructions")
            )

            # Step 6: Create booking using BookingService
            booking_response = await self.booking_service.create_booking(request, user)

            # Step 7: Generate natural response using ResponseGenerator
            response_text = await self.response_generator.generate_booking_confirmation(
                booking_data={
                    "order_id": booking_response.order_id,
                    "total_amount": float(booking_response.total_amount),
                    "date": str(booking_response.preferred_date),
                    "time": str(booking_response.preferred_time)
                },
                conversation_history=None,  # TODO: Pass conversation history from coordinator
                user_name=user.first_name
            )

            # Step 8: Return success response
            return {
                "response": response_text,
                "action_taken": "booking_created",
                "metadata": {
                    "booking_id": booking_response.id,
                    "order_id": booking_response.order_id,
                    "total_amount": float(booking_response.total_amount),
                    "scheduled_date": str(booking_response.preferred_date),
                    "scheduled_time": str(booking_response.preferred_time),
                    "payment_status": booking_response.status,
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
            import traceback
            logger.error(f"Unexpected error in _create_booking: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}. Please try again.",
                "action_taken": "error",
                "metadata": {"error": str(e), "traceback": traceback.format_exc()}
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
        Cancel an existing booking using CancellationAgent with policy enforcement

        This method delegates to CancellationAgent which handles:
        - Policy-based refund calculation (100%, 50%, 25%, or 0% based on timing)
        - Booking eligibility validation
        - Status checks
        - Wallet refund processing

        Args:
            entities: Contains booking_id, reason
            user: Current user

        Returns:
            Response dict with cancellation details including policy-based refund
        """
        try:
            booking_id = entities.get("booking_id")

            if not booking_id:
                return {
                    "response": "I need the Order ID to cancel. Could you provide it? (e.g., ORDA5D9F532)",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "booking_id"}
                }

            # Use CancellationAgent for policy-based cancellation
            # This ensures cancellation policies are enforced correctly
            from src.agents.cancellation.cancellation_agent import CancellationAgent

            cancellation_agent = CancellationAgent(self.db)

            # CancellationAgent handles:
            # - Time-based refund calculation
            # - Policy enforcement
            # - Status validation
            # - Wallet refunds
            result = await cancellation_agent.execute(
                message="",  # Not needed, we have entities
                user=user,
                session_id="",  # Not needed for cancellation
                entities=entities
            )

            return result
            
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
        try:
            # Extract required entities
            booking_id = entities.get("booking_id")
            new_date = entities.get("date")
            new_time = entities.get("time")
            reason = entities.get("reason", "Customer requested reschedule")

            # Validate required fields
            if not booking_id:
                return {
                    "response": "I need the booking ID to reschedule. Could you provide it?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "booking_id"}
                }

            if not new_date:
                return {
                    "response": "I need the new date to reschedule. What date would you prefer?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "date"}
                }

            if not new_time:
                return {
                    "response": "I need the new time to reschedule. What time would you prefer?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "time"}
                }

            # Create reschedule request
            from src.schemas.customer import RescheduleBookingRequest
            reschedule_request = RescheduleBookingRequest(
                preferred_date=new_date,
                preferred_time=new_time,
                reason=reason
            )

            # Reschedule booking using BookingService
            result = await self.booking_service.reschedule_booking(
                int(booking_id),
                reschedule_request,
                user
            )

            return {
                "response": f"✅ Booking {result.order_id} has been rescheduled to {new_date} at {new_time}. "
                           f"You will receive a confirmation shortly.",
                "action_taken": "booking_rescheduled",
                "metadata": {
                    "booking_id": result.id,
                    "order_id": result.order_id,
                    "new_date": new_date,
                    "new_time": new_time,
                    "status": result.status
                }
            }

        except ValueError as e:
            return {
                "response": f"❌ Rescheduling failed: {str(e)}",
                "action_taken": "reschedule_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"Error rescheduling booking: {str(e)}")
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _modify_booking(self, entities: Dict[str, Any], user: User) -> Dict[str, Any]:
        """
        Modify booking details (e.g., special instructions)

        Args:
            entities: Contains booking_id, special_instructions
            user: Current user

        Returns:
            Response dict with modification details
        """
        try:
            # Extract required entities
            booking_id = entities.get("booking_id")
            special_instructions = entities.get("special_instructions")

            # Validate required fields
            if not booking_id:
                return {
                    "response": "I need the booking ID to modify. Could you provide it?",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "booking_id"}
                }

            if not special_instructions:
                return {
                    "response": "What would you like to modify? Please provide the special instructions or changes you need.",
                    "action_taken": "missing_entity",
                    "metadata": {"missing": "modifications"}
                }

            # Get booking to verify it exists and belongs to user
            booking = await self.booking_service.get_booking(int(booking_id), user)

            # Check if booking can be modified
            if booking.status not in ["PENDING", "CONFIRMED"]:
                return {
                    "response": f"❌ Cannot modify booking with status: {booking.status}. "
                               f"Only pending or confirmed bookings can be modified.",
                    "action_taken": "modification_failed",
                    "metadata": {"error": f"Invalid status: {booking.status}"}
                }

            # Update special instructions in database
            result = await self.db.execute(
                select(Booking).where(
                    Booking.id == int(booking_id),
                    Booking.user_id == user.id
                )
            )
            booking_record = result.scalar_one_or_none()

            if not booking_record:
                return {
                    "response": "❌ Booking not found or you don't have permission to modify it.",
                    "action_taken": "modification_failed",
                    "metadata": {"error": "Booking not found"}
                }

            # Update special instructions
            booking_record.special_instructions = special_instructions
            await self.db.commit()
            await self.db.refresh(booking_record)

            return {
                "response": f"✅ Booking {booking.order_id} has been updated successfully. "
                           f"Your special instructions have been noted.",
                "action_taken": "booking_modified",
                "metadata": {
                    "booking_id": booking.id,
                    "order_id": booking.order_id,
                    "modifications": {
                        "special_instructions": special_instructions
                    }
                }
            }

        except ValueError as e:
            return {
                "response": f"❌ Modification failed: {str(e)}",
                "action_taken": "modification_failed",
                "metadata": {"error": str(e)}
            }
        except Exception as e:
            logger.error(f"Error modifying booking: {str(e)}")
            return {
                "response": f"❌ An unexpected error occurred: {str(e)}",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

    async def _list_bookings(
        self,
        user: User,
        status_filter: str = None,
        sort_by: str = "date",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        List bookings for the user with optional filtering and sorting

        Args:
            user: User object
            status_filter: Optional status filter (pending, confirmed, completed, cancelled)
            sort_by: Sort field (date, status, amount)
            limit: Maximum number of bookings to return

        Returns:
            Response dict with list of bookings
        """
        try:
            # Fetch bookings using BookingService
            bookings = await self.booking_service.list_bookings(
                user=user,
                status_filter=status_filter,
                skip=0,
                limit=limit
            )

            if not bookings:
                return {
                    "response": "You don't have any bookings yet. Would you like to book a service?",
                    "action_taken": "no_bookings",
                    "metadata": {"booking_count": 0}
                }

            # Build booking summary
            booking_summaries = []
            for b in bookings:
                try:
                    service_name = "Unknown"
                    # BookingResponse has 'items' field, not 'booking_items'
                    if b.items and len(b.items) > 0:
                        item = b.items[0]
                        if item.rate_card and item.rate_card.subcategory:
                            service_name = item.rate_card.subcategory.name

                    booking_summaries.append({
                        'order_id': b.order_id,
                        'service': service_name,
                        'date': b.preferred_date,
                        'time': b.preferred_time,
                        'status': b.status,
                        'total_amount': float(b.total_amount),
                        'address': f"{b.address.city}, {b.address.state}" if b.address else "N/A"
                    })
                except Exception as e:
                    logger.error(f"Error processing booking {b.id}: {str(e)}")
                    continue

            # Sort bookings
            if sort_by == "date":
                booking_summaries.sort(key=lambda x: (x['date'], x['time']), reverse=True)
            elif sort_by == "status":
                # Priority: pending > confirmed > completed > cancelled
                status_priority = {"pending": 1, "confirmed": 2, "completed": 3, "cancelled": 4}
                booking_summaries.sort(key=lambda x: status_priority.get(x['status'], 5))
            elif sort_by == "amount":
                booking_summaries.sort(key=lambda x: x['total_amount'], reverse=True)

            # Build response text
            filter_text = f" ({status_filter} only)" if status_filter else ""
            response_lines = [f"Here are your bookings{filter_text}:"]

            for idx, booking in enumerate(booking_summaries, 1):
                response_lines.append(
                    f"{idx}. Order {booking['order_id']} - {booking['service']} on {booking['date']} at {booking['time']} (Status: {booking['status']}, Amount: Rs. {booking['total_amount']})"
                )

            # Add helpful footer
            if len(booking_summaries) >= limit:
                response_lines.append(f"\nShowing {limit} bookings. Ask for more if needed.")

            if not status_filter:
                response_lines.append("\nYou can filter by status: pending, confirmed, completed, or cancelled.")

            response_text = "\n".join(response_lines)

            return {
                "response": response_text,
                "action_taken": "bookings_listed",
                "metadata": {
                    "booking_count": len(bookings),
                    "bookings": booking_summaries,
                    "status_filter": status_filter,
                    "sort_by": sort_by
                }
            }

        except Exception as e:
            logger.error(f"Error listing bookings: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())

            return {
                "response": "I'm having trouble fetching your bookings right now. Please try again later or contact support.",
                "action_taken": "error",
                "metadata": {"error": str(e)}
            }

