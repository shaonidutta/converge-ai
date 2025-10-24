"""
Entity Normalization Utility

Centralized entity normalization functions to ensure consistency across:
- Pattern-based extraction (patterns.py)
- Follow-up extraction (entity_extractor.py)
- LLM extraction (classifier.py)

All entity extraction paths should use these functions to normalize raw values.
"""

import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def normalize_date(raw_value: str) -> Optional[str]:
    """
    Normalize date to ISO format (YYYY-MM-DD)
    
    Handles:
    - Relative dates: "today", "tomorrow", "day after tomorrow", "next week"
    - ISO format: "2025-10-26"
    - DD/MM/YYYY format: "26/10/2025"
    - DD-MM-YYYY format: "26-10-2025"
    
    Args:
        raw_value: Raw date string from user input or LLM
        
    Returns:
        ISO format date string (YYYY-MM-DD) or None if cannot normalize
    """
    if not raw_value:
        return None
    
    value_lower = str(raw_value).lower().strip()
    today = datetime.now().date()
    
    # Relative dates
    if value_lower in ["today", "now"]:
        return today.isoformat()
    
    if value_lower in ["tomorrow", "tmrw", "tmr"]:
        return (today + timedelta(days=1)).isoformat()
    
    if "day after tomorrow" in value_lower:
        return (today + timedelta(days=2)).isoformat()
    
    if "next week" in value_lower:
        return (today + timedelta(days=7)).isoformat()
    
    # ISO format (YYYY-MM-DD) - already normalized
    iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', str(raw_value))
    if iso_match:
        return raw_value
    
    # DD/MM/YYYY or DD-MM-YYYY format
    date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', str(raw_value))
    if date_match:
        day, month, year = date_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # Could not normalize
    logger.warning(f"[normalize_date] Could not normalize date: {raw_value}")
    return None


def normalize_time(raw_value: str) -> Optional[str]:
    """
    Normalize time to 24-hour format (HH:MM)
    
    Handles:
    - 12-hour format: "2 PM", "10:30 AM", "2pm", "10:30am"
    - 24-hour format: "14:00", "09:30"
    - Time of day: "morning" → "10:00", "afternoon" → "14:00", "evening" → "18:00"
    
    Args:
        raw_value: Raw time string from user input or LLM
        
    Returns:
        24-hour format time string (HH:MM) or None if cannot normalize
    """
    if not raw_value:
        return None
    
    value_str = str(raw_value).strip()
    value_lower = value_str.lower()
    
    # 12-hour format (2 PM, 10:30 AM, 2pm, 10:30am)
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)', value_lower)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = time_match.group(3).replace('.', '').replace(' ', '')
        
        # Convert to 24-hour format
        if period in ["pm", "pm"]:
            if hour != 12:
                hour += 12
        elif period in ["am", "am"]:
            if hour == 12:
                hour = 0
        
        return f"{hour:02d}:{minute:02d}"
    
    # 24-hour format (14:00, 09:30) - already normalized
    time_24h_match = re.match(r'^(\d{1,2}):(\d{2})$', value_str)
    if time_24h_match:
        hour = int(time_24h_match.group(1))
        minute = int(time_24h_match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"
    
    # Time of day keywords
    if "morning" in value_lower:
        return "10:00"
    if "afternoon" in value_lower:
        return "14:00"
    if "evening" in value_lower:
        return "18:00"
    if "night" in value_lower:
        return "20:00"
    
    # Could not normalize
    logger.warning(f"[normalize_time] Could not normalize time: {raw_value}")
    return None


def normalize_location(raw_value: str) -> Optional[str]:
    """
    Normalize location to standardized format
    
    Handles:
    - Full address: "123 Main Street, Agra, Uttar Pradesh, 282002"
    - City + pincode: "Bangalore, 560001"
    - Pincode only: "560001"
    - City name: "Mumbai", "Delhi", "Bangalore"
    
    Args:
        raw_value: Raw location string from user input or LLM
        
    Returns:
        Normalized location string or None if cannot normalize
    """
    if not raw_value:
        return None
    
    value_str = str(raw_value).strip()
    
    # If it's already a full address or city+pincode, return as-is
    if len(value_str) > 5:
        return value_str
    
    # Pincode only (6 digits)
    pincode_match = re.search(r'\b(\d{6})\b', value_str)
    if pincode_match:
        return pincode_match.group(1)
    
    # Could not normalize
    logger.warning(f"[normalize_location] Could not normalize location: {raw_value}")
    return None


def normalize_service_type(raw_value: str) -> Optional[str]:
    """
    Normalize service type to lowercase standard format
    
    Handles:
    - "AC service" → "ac"
    - "Plumbing Service" → "plumbing"
    - "Air Conditioning" → "ac"
    
    Args:
        raw_value: Raw service type string from user input or LLM
        
    Returns:
        Normalized service type string or None if cannot normalize
    """
    if not raw_value:
        return None
    
    value_lower = str(raw_value).lower().strip()
    
    # Remove "service" suffix
    value_lower = value_lower.replace(" service", "").replace("service", "").strip()
    
    # Map common variations to standard service types
    service_mapping = {
        "air conditioning": "ac",
        "air conditioner": "ac",
        "hvac": "ac",
        "plumber": "plumbing",
        "pipe": "plumbing",
        "electrician": "electrical",
        "wiring": "electrical",
        "painter": "painting",
        "house cleaning": "cleaning",
        "deep cleaning": "cleaning",
        "washing machine": "appliance_repair",
        "refrigerator": "appliance_repair",
        "fridge": "appliance_repair",
    }
    
    # Check if value matches any mapping
    for key, standard_type in service_mapping.items():
        if key in value_lower:
            return standard_type
    
    # Return as-is if no mapping found (already normalized)
    return value_lower


def normalize_action(raw_value: str) -> Optional[str]:
    """
    Normalize action to standard format
    
    Handles:
    - "booking" → "book"
    - "schedule" → "book"
    - "cancellation" → "cancel"
    
    Args:
        raw_value: Raw action string from user input or LLM
        
    Returns:
        Normalized action string or None if cannot normalize
    """
    if not raw_value:
        return None
    
    value_lower = str(raw_value).lower().strip()
    
    # Map variations to standard actions
    action_mapping = {
        "book": ["book", "booking", "schedule", "scheduling", "reserve", "reservation", "arrange", "set up"],
        "cancel": ["cancel", "cancellation", "remove", "delete"],
        "reschedule": ["reschedule", "rescheduling", "change date", "change time", "move"],
        "modify": ["modify", "modification", "update", "edit", "change"],
        "check_status": ["status", "check", "track", "where is", "tracking"],
    }
    
    # Check if value matches any mapping
    for standard_action, variations in action_mapping.items():
        for variation in variations:
            if variation in value_lower:
                return standard_action
    
    # Return as-is if no mapping found
    return value_lower


def normalize_booking_id(raw_value: str) -> Optional[str]:
    """
    Normalize booking ID to standard format

    Handles:
    - BK123456, bk123456 → BK123456
    - BK-123456, BK_123456 → BK123456
    - BOOK12345, book-12345 → BOOK12345
    - #123456 → #123456

    Args:
        raw_value: Raw booking ID string from user input or LLM

    Returns:
        Normalized booking ID (uppercase, no separators) or None if invalid
    """
    if not raw_value:
        return None

    value = str(raw_value).strip()

    # Remove common separators (-, _)
    value_clean = value.replace("-", "").replace("_", "")

    # Convert to uppercase
    value_upper = value_clean.upper()

    # Validate format
    # Should be: BK + 6 digits, BOOK + 4-6 digits, BKG + 4-6 digits, ORD + 4-6 digits, or # + 6 digits
    valid_patterns = [
        r"^BK\d{6}$",  # BK123456
        r"^BOOK\d{4,6}$",  # BOOK12345
        r"^BKG\d{4,6}$",  # BKG12345
        r"^ORD\d{4,6}$",  # ORD12345
        r"^#\d{6}$",  # #123456
    ]

    for pattern in valid_patterns:
        if re.match(pattern, value_upper):
            return value_upper

    # If doesn't match any pattern, return as-is (might be valid in database)
    return value_upper


def normalize_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize all entities in a dictionary

    Args:
        entities: Dictionary of entity_type -> raw_value

    Returns:
        Dictionary of entity_type -> normalized_value
    """
    if not entities:
        return {}

    # Preprocess: Split combined date-time values
    # e.g., "tomorrow morning" → date: "tomorrow", time: "morning"
    if "date" in entities and entities["date"]:
        date_value = str(entities["date"]).lower().strip()
        time_keywords = ["morning", "afternoon", "evening", "night"]

        for time_keyword in time_keywords:
            if time_keyword in date_value:
                # Split date and time
                date_part = date_value.replace(time_keyword, "").strip()
                if date_part:
                    entities["date"] = date_part
                    entities["time"] = time_keyword
                    logger.info(f"[normalize_entities] Split '{date_value}' into date='{date_part}' and time='{time_keyword}'")
                break

    normalized = {}

    for entity_type, raw_value in entities.items():
        if not raw_value or raw_value == "NOT_FOUND":
            continue

        # Normalize based on entity type
        if entity_type == "date":
            normalized_value = normalize_date(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        elif entity_type == "time":
            normalized_value = normalize_time(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        # Handle time_range by converting to time
        elif entity_type == "time_range":
            normalized_value = normalize_time(raw_value)
            if normalized_value:
                # Store as "time" not "time_range"
                normalized["time"] = normalized_value
                logger.info(f"[normalize_entities] Converted time_range '{raw_value}' to time '{normalized_value}'")

        elif entity_type == "location":
            normalized_value = normalize_location(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        elif entity_type == "service_type":
            normalized_value = normalize_service_type(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        elif entity_type == "action":
            normalized_value = normalize_action(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        elif entity_type == "booking_id":
            normalized_value = normalize_booking_id(raw_value)
            if normalized_value:
                normalized[entity_type] = normalized_value

        else:
            # Keep other entities as-is
            normalized[entity_type] = raw_value

    return normalized

