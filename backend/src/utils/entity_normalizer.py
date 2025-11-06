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
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def normalize_date(raw_value: str) -> Optional[str]:
    """
    Normalize date to ISO format (YYYY-MM-DD)

    Handles:
    - Relative dates: "today", "tomorrow", "day after tomorrow", "next week", "in 3 days", "in 2 weeks"
    - ISO format: "2025-10-26"
    - DD/MM/YYYY format: "26/10/2025", "15/12/2025"
    - MM/DD/YYYY format: "12/15/2025" (US format)
    - DD-MM-YYYY format: "26-10-2025", "15-12-2025"
    - MM-DD-YYYY format: "12-15-2025" (US format)
    - Month names: "30 october", "October 30", "30th October 2025", "December 15th, 2025", "15th Dec 2025", "Dec 15, 2025"
    - Weekday names: "monday", "next monday", "this friday"
    - Natural language: "in 3 days", "in 2 weeks", "next month", "after 5 days"

    Args:
        raw_value: Raw date string from user input or LLM

    Returns:
        ISO format date string (YYYY-MM-DD) or None if cannot normalize
    """
    if not raw_value:
        return None

    value_lower = str(raw_value).lower().strip()
    today = datetime.now().date()

    # Relative dates - exact matches
    if value_lower in ["today", "now"]:
        return today.isoformat()

    if value_lower in ["tomorrow", "tmrw", "tmr"]:
        return (today + timedelta(days=1)).isoformat()

    if "day after tomorrow" in value_lower or "overmorrow" in value_lower:
        return (today + timedelta(days=2)).isoformat()

    if "next week" in value_lower:
        return (today + timedelta(days=7)).isoformat()

    # "in X days" or "after X days" patterns
    in_days_match = re.search(r'(?:in|after)\s+(\d+)\s+days?', value_lower)
    if in_days_match:
        days = int(in_days_match.group(1))
        return (today + timedelta(days=days)).isoformat()

    # "in X weeks" or "after X weeks" patterns
    in_weeks_match = re.search(r'(?:in|after)\s+(\d+)\s+weeks?', value_lower)
    if in_weeks_match:
        weeks = int(in_weeks_match.group(1))
        return (today + timedelta(weeks=weeks)).isoformat()

    # "next month" pattern
    if "next month" in value_lower:
        return (today + relativedelta(months=1)).isoformat()

    # Weekday names: "monday", "next monday", "this friday"
    weekdays = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }

    for weekday_name, weekday_num in weekdays.items():
        if weekday_name in value_lower:
            current_weekday = today.weekday()

            if "next" in value_lower:
                # Next occurrence of this weekday (at least 7 days from now)
                days_ahead = (weekday_num - current_weekday + 7) % 7
                if days_ahead == 0:  # If it's the same weekday, go to next week
                    days_ahead = 7
                target_date = today + timedelta(days=days_ahead)
            else:
                # This week's occurrence or next week if already passed
                days_ahead = (weekday_num - current_weekday) % 7
                if days_ahead == 0:  # If it's today, return today
                    target_date = today
                else:
                    target_date = today + timedelta(days=days_ahead)

            return target_date.isoformat()

    # ISO format (YYYY-MM-DD) - already normalized
    iso_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', str(raw_value))
    if iso_match:
        return raw_value

    # DD/MM/YYYY or DD-MM-YYYY format (European/Indian format)
    # Check if it looks like DD/MM/YYYY (day <= 31, month <= 12)
    date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', str(raw_value))
    if date_match:
        first_num = int(date_match.group(1))
        second_num = int(date_match.group(2))
        year = date_match.group(3)

        # Heuristic: If first number > 12, it must be day (DD/MM/YYYY)
        # If second number > 12, it must be month (MM/DD/YYYY)
        # Otherwise, assume DD/MM/YYYY (more common internationally)
        if first_num > 12:
            # Must be DD/MM/YYYY
            day, month = first_num, second_num
        elif second_num > 12:
            # Must be MM/DD/YYYY
            month, day = first_num, second_num
        else:
            # Ambiguous - default to DD/MM/YYYY (international standard)
            day, month = first_num, second_num

        try:
            # Validate the date
            parsed_date = datetime(int(year), int(month), int(day)).date()
            return parsed_date.isoformat()
        except ValueError:
            # If DD/MM/YYYY failed, try MM/DD/YYYY
            try:
                parsed_date = datetime(int(year), int(day), int(month)).date()
                return parsed_date.isoformat()
            except ValueError:
                pass

    # Month names: "30 october", "October 30", "30th October 2025", "December 15th, 2025"
    # Try to parse using datetime.strptime with various formats
    month_formats = [
        "%d %B",  # "30 October"
        "%d %b",  # "30 Oct"
        "%B %d",  # "October 30"
        "%b %d",  # "Oct 30"
        "%d %B %Y",  # "30 October 2025"
        "%d %b %Y",  # "30 Oct 2025"
        "%B %d %Y",  # "October 30 2025"
        "%b %d %Y",  # "Oct 30 2025"
        "%B %d, %Y",  # "December 15, 2025" or "November 13, 2025"
        "%b %d, %Y",  # "Dec 15, 2025"
        "%d%s %B",  # "30th October" (with ordinal suffix)
        "%d%s %b",  # "30th Oct"
        "%d%s %B %Y",  # "30th October 2025"
        "%d%s %b %Y",  # "30th Oct 2025"
        "%d%s %B, %Y",  # "15th December, 2025" or "13th November, 2025"
        "%d%s %b, %Y",  # "15th Dec, 2025"
        "%B %d%s, %Y",  # "November 13th, 2025" or "December 15th, 2025"
        "%b %d%s, %Y",  # "Nov 13th, 2025" or "Dec 15th, 2025"
    ]

    # Remove ordinal suffixes (st, nd, rd, th) and extra spaces
    value_cleaned = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', value_lower)
    value_cleaned = re.sub(r'\s+', ' ', value_cleaned).strip()

    for fmt in month_formats:
        try:
            # Remove the %s placeholder for ordinal suffix
            fmt_clean = fmt.replace('%s', '')
            parsed_date = datetime.strptime(value_cleaned, fmt_clean)
            # If year is not provided, assume current year
            if parsed_date.year == 1900:  # Default year from strptime
                parsed_date = parsed_date.replace(year=today.year)
                # If the date is in the past, assume next year
                if parsed_date.date() < today:
                    parsed_date = parsed_date.replace(year=today.year + 1)
            return parsed_date.date().isoformat()
        except ValueError:
            continue

    # Fallback: Use dateutil parser for flexible parsing
    # This handles many natural language formats
    try:
        # Remove common words that might confuse the parser
        value_for_parsing = value_lower
        for word in ['on', 'the', 'of']:
            value_for_parsing = value_for_parsing.replace(f' {word} ', ' ')

        # Parse with dateutil (dayfirst=True for international format)
        parsed_date = dateutil_parser.parse(value_for_parsing, dayfirst=True, fuzzy=True)

        # If parsed date is in the past and no year was specified, assume next year
        if parsed_date.date() < today and parsed_date.year == today.year:
            # Check if year was explicitly mentioned in the original string
            if not re.search(r'\d{4}', str(raw_value)):
                parsed_date = parsed_date.replace(year=today.year + 1)

        return parsed_date.date().isoformat()
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"[normalize_date] dateutil parsing failed for '{raw_value}': {e}")

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
        "list": ["list", "listing", "show", "view", "display", "see", "get", "all", "my bookings", "check my"],
        "book": ["book", "booking", "schedule", "scheduling", "reserve", "reservation", "arrange", "set up"],
        "cancel": ["cancel", "cancellation", "remove", "delete"],
        "reschedule": ["reschedule", "rescheduling", "change date", "change time", "move"],
        "modify": ["modify", "modification", "update", "edit", "change"],
        "check_status": ["status", "check", "track", "where is", "tracking"],
    }
    
    # Check if value matches any mapping
    # IMPORTANT: Check for exact match first to avoid false matches
    # (e.g., "reschedule" should not match "schedule" from "book" variations)
    for standard_action, variations in action_mapping.items():
        if value_lower in variations:
            return standard_action

    # If no exact match, check for substring match (for phrases like "my bookings")
    for standard_action, variations in action_mapping.items():
        for variation in variations:
            # Skip single-word variations for substring matching to avoid false matches
            if ' ' in variation and variation in value_lower:
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
    - ORD6B4AB979, ord6b4ab979 → ORD6B4AB979 (8 alphanumeric characters)
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
    # Should be: BK + 6 digits, BOOK + 4-6 digits, BKG + 4-6 digits, ORD + 8 alphanumeric, or # + 6 digits
    valid_patterns = [
        r"^BK\d{6}$",  # BK123456
        r"^BOOK\d{4,6}$",  # BOOK12345
        r"^BKG\d{4,6}$",  # BKG12345
        r"^ORD[A-Z0-9]{8}$",  # ORD6B4AB979 (8 alphanumeric characters)
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

    # Preprocess: Map order_id to booking_id (LLM sometimes extracts as order_id)
    if "order_id" in entities and "booking_id" not in entities:
        entities["booking_id"] = entities.pop("order_id")
        logger.info(f"[normalize_entities] Mapped order_id to booking_id: {entities['booking_id']}")

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

