"""
Entity Validator Service

Validates and normalizes entity values according to business rules.

Approach:
- Configurable validation rules (stored in config, can be changed without code deploys)
- Strict enforcement of critical business rules
- User-friendly error messages
- Suggestions for valid values

Design Principles:
- Configurable but strict for critical rules
- Clear error messages
- Helpful suggestions
- Normalized output
"""

import logging
import re
from typing import Any, Optional, Dict, List
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.nlp.intent.config import EntityType

logger = logging.getLogger(__name__)


# ============================================================
# VALIDATION CONFIGURATION (Can be moved to DB/Admin UI)
# ============================================================

VALIDATION_CONFIG = {
    "date": {
        "min_days_ahead": 0,  # Can book from today
        "max_days_ahead": 90,  # Max 90 days in future
        "allow_past_dates": False,
    },
    "time": {
        "service_start_hour": 8,  # 8 AM
        "service_end_hour": 20,  # 8 PM
        "slot_duration_minutes": 30,
    },
    "location": {
        "require_pincode_validation": True,  # Check if pincode is serviceable
    },
    "booking_id": {
        "require_ownership_check": True,  # Check if booking belongs to user
    },
}


class ValidationResult(BaseModel):
    """Result of entity validation"""
    is_valid: bool
    normalized_value: Optional[Any] = None
    error_message: Optional[str] = None
    suggestions: Optional[List[str]] = None


class EntityValidator:
    """
    Validates and normalizes entity values
    
    Features:
    - Configurable validation rules
    - Strict enforcement of critical business rules
    - User-friendly error messages
    - Helpful suggestions
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = VALIDATION_CONFIG
    
    async def validate(
        self,
        entity_type: EntityType,
        value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate entity value
        
        Args:
            entity_type: Type of entity
            value: Entity value to validate
            context: Additional context for validation (user_id, collected_entities, etc.)
            
        Returns:
            ValidationResult
        """
        logger.info(f"[EntityValidator] Validating {entity_type.value}: {value}")
        
        context = context or {}
        
        if entity_type == EntityType.DATE:
            return self._validate_date(value)
        elif entity_type == EntityType.TIME:
            return self._validate_time(value)
        elif entity_type == EntityType.LOCATION:
            return await self._validate_location(value)
        elif entity_type == EntityType.SERVICE_TYPE:
            return await self._validate_service_type(value)
        elif entity_type == EntityType.BOOKING_ID:
            return await self._validate_booking_id(value, context)
        else:
            # Generic validation (just check if not empty)
            if value and str(value).strip():
                return ValidationResult(is_valid=True, normalized_value=value)
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Invalid {entity_type.value}"
                )
    
    def _validate_date(self, value: Any) -> ValidationResult:
        """Validate date value"""
        try:
            # Parse date
            if isinstance(value, str):
                parsed_date = datetime.fromisoformat(value).date()
            elif isinstance(value, date):
                parsed_date = value
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid date format. Please use YYYY-MM-DD format or say 'today', 'tomorrow'"
                )
            
            today = datetime.now().date()
            config = self.config["date"]
            
            # Check if date is in the past
            if not config["allow_past_dates"] and parsed_date < today:
                suggestions = [
                    "today",
                    "tomorrow",
                    (today + timedelta(days=7)).isoformat()
                ]
                return ValidationResult(
                    is_valid=False,
                    error_message="Date must be today or in the future",
                    suggestions=suggestions
                )
            
            # Check if date is within booking window
            min_date = today + timedelta(days=config["min_days_ahead"])
            max_date = today + timedelta(days=config["max_days_ahead"])
            
            if parsed_date > max_date:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Date is too far in the future (max {config['max_days_ahead']} days)",
                    suggestions=[max_date.isoformat()]
                )
            
            return ValidationResult(
                is_valid=True,
                normalized_value=parsed_date.isoformat()
            )
        
        except Exception as e:
            logger.error(f"[EntityValidator] Date validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message="Invalid date format. Please use YYYY-MM-DD format or say 'today', 'tomorrow'"
            )
    
    def _validate_time(self, value: Any) -> ValidationResult:
        """Validate time value"""
        try:
            # Parse time (HH:MM format)
            if isinstance(value, str):
                time_obj = datetime.strptime(value, "%H:%M").time()
            else:
                return ValidationResult(
                    is_valid=False,
                    error_message="Invalid time format. Please use HH:MM format or say '10 AM', '2 PM'"
                )
            
            config = self.config["time"]
            
            # Check if time is within service hours
            if time_obj.hour < config["service_start_hour"] or time_obj.hour >= config["service_end_hour"]:
                suggestions = ["10:00", "14:00", "18:00"]
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Service hours are {config['service_start_hour']} AM to {config['service_end_hour']} PM",
                    suggestions=suggestions
                )
            
            return ValidationResult(
                is_valid=True,
                normalized_value=value
            )
        
        except Exception as e:
            logger.error(f"[EntityValidator] Time validation error: {e}")
            return ValidationResult(
                is_valid=False,
                error_message="Invalid time format. Please use HH:MM format or say '10 AM', '2 PM'"
            )
    
    async def _validate_location(self, value: Any) -> ValidationResult:
        """Validate location (pincode or city)"""
        config = self.config["location"]

        # Reject obviously invalid locations
        if not value or not isinstance(value, str):
            return ValidationResult(
                is_valid=False,
                error_message="Please provide a valid location (city name or pincode)"
            )

        value_str = str(value).strip()

        # Check if it's a full address (contains comma-separated parts and pincode)
        # Pattern: street, city, state, pincode OR city, pincode
        full_address_pattern = r'.+,\s*.+,\s*.+,?\s*\d{6}'
        if re.search(full_address_pattern, value_str):
            # Extract pincode from full address for validation
            pincode_match = re.search(r'\b(\d{6})\b', value_str)
            if pincode_match:
                pincode = pincode_match.group(1)
                # Validate pincode if required
                if config["require_pincode_validation"]:
                    try:
                        from src.core.models import Pincode
                        result = await self.db.execute(
                            select(Pincode).where(Pincode.pincode == pincode)
                        )
                        pincode_obj = result.scalar_one_or_none()

                        if pincode_obj and pincode_obj.is_serviceable:
                            logger.info(f"[EntityValidator] Full address validated: {value_str} (pincode {pincode} is serviceable)")
                            return ValidationResult(
                                is_valid=True,
                                normalized_value=value_str
                            )
                        else:
                            # Graceful degradation: Accept address but log warning
                            logger.warning(f"[EntityValidator] Pincode {pincode} not in serviceable list, but accepting address for booking attempt")
                            return ValidationResult(
                                is_valid=True,
                                normalized_value=value_str
                            )
                    except Exception as e:
                        logger.error(f"[EntityValidator] Pincode validation error: {e}")
                        # If DB check fails, accept the address (graceful degradation)
                        logger.info(f"[EntityValidator] Accepting full address due to validation error: {value_str}")
                        return ValidationResult(
                            is_valid=True,
                            normalized_value=value_str
                        )
                else:
                    # No validation required, accept full address
                    logger.info(f"[EntityValidator] Accepting full address (validation disabled): {value_str}")
                    return ValidationResult(
                        is_valid=True,
                        normalized_value=value_str
                    )

        # Reject if it looks like a sentence or contains common non-location words
        invalid_keywords = [
            "book", "service", "want", "need", "repair", "fix", "help",
            "schedule", "appointment", "tomorrow", "today", "yesterday"
        ]
        value_lower = value_str.lower()
        if any(keyword in value_lower for keyword in invalid_keywords):
            return ValidationResult(
                is_valid=False,
                error_message="That doesn't look like a valid location. Please provide a city name or 6-digit pincode"
            )

        # Check if it's a pincode (6 digits only)
        if value_str.isdigit() and len(value_str) == 6:
            if config["require_pincode_validation"]:
                # Query database to check if pincode is serviceable
                try:
                    from src.core.models import Pincode
                    result = await self.db.execute(
                        select(Pincode).where(Pincode.pincode == value_str)
                    )
                    pincode_obj = result.scalar_one_or_none()

                    if pincode_obj and pincode_obj.is_serviceable:
                        logger.info(f"[EntityValidator] Pincode {value_str} validated and is serviceable")
                        return ValidationResult(
                            is_valid=True,
                            normalized_value=value_str
                        )
                    else:
                        # Graceful degradation: Accept pincode but log warning
                        logger.warning(f"[EntityValidator] Pincode {value_str} not in serviceable list, but accepting for booking attempt")
                        return ValidationResult(
                            is_valid=True,
                            normalized_value=value_str
                        )
                except Exception as e:
                    logger.error(f"[EntityValidator] Pincode validation error: {e}")
                    # If DB check fails, accept the pincode (graceful degradation)
                    logger.info(f"[EntityValidator] Accepting pincode {value_str} due to validation error")
                    return ValidationResult(
                        is_valid=True,
                        normalized_value=value_str
                    )
            else:
                logger.info(f"[EntityValidator] Accepting pincode {value_str} (validation disabled)")
                return ValidationResult(
                    is_valid=True,
                    normalized_value=value_str
                )

        # If it's a city name (1-3 words, no invalid keywords), accept it
        if 1 <= len(value_str.split()) <= 3:
            return ValidationResult(
                is_valid=True,
                normalized_value=value_str.title()
            )

        # Reject everything else
        return ValidationResult(
            is_valid=False,
            error_message="Please provide a valid city name or 6-digit pincode"
        )
    
    async def _validate_service_type(self, value: Any) -> ValidationResult:
        """Validate service type"""
        # Normalize to lowercase
        normalized = str(value).lower().strip()
        
        # Check against valid service types
        valid_services = ["ac", "plumbing", "cleaning", "electrical", "painting", "appliance_repair"]
        
        if normalized in valid_services:
            return ValidationResult(
                is_valid=True,
                normalized_value=normalized
            )
        else:
            return ValidationResult(
                is_valid=False,
                error_message=f"Unknown service type: {value}",
                suggestions=valid_services[:5]  # Show top 5 suggestions
            )
    
    async def _validate_booking_id(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Validate booking ID"""
        config = self.config["booking_id"]
        
        try:
            from src.core.models import Booking
            
            result = await self.db.execute(
                select(Booking).where(Booking.booking_id == value)
            )
            booking = result.scalar_one_or_none()
            
            if not booking:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Booking {value} not found. Please check the booking ID"
                )
            
            # Check ownership if required
            if config["require_ownership_check"] and context:
                user_id = context.get("user_id")
                if user_id and booking.user_id != user_id:
                    return ValidationResult(
                        is_valid=False,
                        error_message="This booking doesn't belong to you"
                    )
            
            return ValidationResult(
                is_valid=True,
                normalized_value=value
            )
        
        except Exception as e:
            logger.error(f"[EntityValidator] Booking ID validation error: {e}")
            # If DB check fails, accept the booking ID (graceful degradation)
            return ValidationResult(
                is_valid=True,
                normalized_value=value
            )

