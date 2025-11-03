"""
Entity Extractor Service

Extracts entity values from follow-up responses using pattern matching + LLM fallback.

Approach:
- Pattern matching (regex/rule-based) first for common cases (fast path)
- LLM fallback when confidence is low or patterns fail
- Context-aware extraction using conversation history
- Service name resolution for booking intents

Design Principles:
- Fast pattern matching for common formats
- LLM for ambiguous or complex cases
- High confidence scoring
- Normalized output values
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.nlp.intent.config import EntityType
from src.llm.gemini.client import LLMClient

logger = logging.getLogger(__name__)


class EntityExtractionResult(BaseModel):
    """Result of entity extraction"""
    entity_type: str
    entity_value: Any
    confidence: float
    normalized_value: Optional[Any] = None
    extraction_method: str  # "pattern", "llm", "heuristic", "service_name_resolver_*"
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata (e.g., resolved service info)


class EntityExtractor:
    """
    Extracts entity values from follow-up responses

    Features:
    - Pattern matching (fast path)
    - LLM fallback (accurate)
    - Context-aware extraction
    - Normalized output
    - Service name resolution for booking intents
    """

    def __init__(self, llm_client: Optional[LLMClient] = None, db: Optional[AsyncSession] = None):
        self.llm_client = llm_client
        self.db = db
        self.service_resolver = None

        # Initialize ServiceNameResolver if db is provided
        if db:
            try:
                from src.services.service_name_resolver import ServiceNameResolver
                self.service_resolver = ServiceNameResolver(db)
                logger.info("[EntityExtractor] ✅ ServiceNameResolver initialized successfully")
            except Exception as e:
                logger.error(f"[EntityExtractor] ❌ Failed to initialize ServiceNameResolver: {e}")
                logger.exception(e)
                self.service_resolver = None
        else:
            logger.warning("[EntityExtractor] ⚠️ No db provided, ServiceNameResolver will not be available")
    
    async def extract_multiple_entities(
        self,
        message: str,
        expected_entities: List[EntityType],
        context: Dict[str, Any]
    ) -> Dict[str, EntityExtractionResult]:
        """
        Extract multiple entities from a single message

        Args:
            message: User's message
            expected_entities: List of entity types we're expecting
            context: Conversation context

        Returns:
            Dict mapping entity type to EntityExtractionResult
        """
        logger.info(f"[EntityExtractor] Extracting multiple entities {[e.value for e in expected_entities]} from: '{message}'")

        results = {}

        # First, try to extract combined date-time patterns
        if EntityType.DATE in expected_entities and EntityType.TIME in expected_entities:
            combined_results = self._extract_combined_date_time(message)
            if combined_results:
                for entity_type, result in combined_results.items():
                    results[entity_type] = result
                    logger.info(f"[EntityExtractor] Successfully extracted combined {entity_type}: {result.entity_value}")

                # Remove date and time from expected entities since we found them
                expected_entities = [e for e in expected_entities if e not in [EntityType.DATE, EntityType.TIME]]

        # Try to extract remaining entity types
        for entity_type in expected_entities:
            if entity_type.value not in results:  # Don't re-extract already found entities
                result = await self.extract_from_follow_up(message, entity_type, context)
                if result:
                    results[entity_type.value] = result
                    logger.info(f"[EntityExtractor] Successfully extracted {entity_type.value}: {result.entity_value}")

        return results

    async def extract_from_follow_up(
        self,
        message: str,
        expected_entity: EntityType,
        context: Dict[str, Any]
    ) -> Optional[EntityExtractionResult]:
        """
        Extract entity value from follow-up response

        Args:
            message: User's follow-up message
            expected_entity: Entity type we're expecting
            context: Conversation context (collected entities, last question, etc.)

        Returns:
            EntityExtractionResult or None if extraction failed
        """
        logger.info(f"[EntityExtractor] Extracting {expected_entity.value} from: '{message}'")

        # Try pattern-based extraction first (fast path)
        pattern_result = await self._extract_with_patterns(message, expected_entity, context)
        if pattern_result and pattern_result.confidence >= 0.7:
            logger.info(f"[EntityExtractor] Pattern match successful: {pattern_result.entity_value} (confidence: {pattern_result.confidence})")
            return pattern_result
        
        # Fall back to LLM extraction if available
        if self.llm_client:
            llm_result = await self._extract_with_llm(message, expected_entity, context)
            if llm_result:
                # Check if LLM returned "NOT_FOUND" or very low confidence
                if llm_result.entity_value == "NOT_FOUND" or llm_result.confidence < 0.5:
                    logger.info(f"[EntityExtractor] LLM could not extract {expected_entity.value} (confidence: {llm_result.confidence})")
                    return None
                logger.info(f"[EntityExtractor] LLM extraction successful: {llm_result.entity_value} (confidence: {llm_result.confidence})")
                return llm_result

        # Return pattern result even if low confidence (better than nothing)
        if pattern_result:
            logger.warning(f"[EntityExtractor] Returning low-confidence pattern result: {pattern_result.confidence}")
            return pattern_result

        logger.warning(f"[EntityExtractor] Failed to extract {expected_entity.value}")
        return None
    
    def _clean_conversational_prefixes(self, message: str) -> str:
        """
        Remove conversational prefixes and filler words to extract core content

        Examples:
        - "ok details on texture painting" -> "texture painting"
        - "tell me about ac repair" -> "ac repair"
        - "i want to book plumbing" -> "plumbing"
        - "show me information on cleaning" -> "cleaning"
        """
        message_lower = message.lower().strip()

        # Define conversational prefixes to remove (order matters - more specific first)
        prefixes_to_remove = [
            # Information request patterns
            r'^(?:ok\s+)?(?:show\s+me\s+)?(?:give\s+me\s+)?(?:tell\s+me\s+)?(?:details?\s+)?(?:on|about|for|of)\s+',
            r'^(?:ok\s+)?(?:i\s+want\s+)?(?:to\s+)?(?:see|know|get|view)\s+(?:details?\s+)?(?:on|about|for|of)\s+',
            r'^(?:ok\s+)?(?:can\s+you\s+)?(?:show|tell|give)\s+(?:me\s+)?(?:details?\s+)?(?:on|about|for|of)\s+',
            r'^(?:ok\s+)?(?:what\s+about|how\s+about)\s+',

            # Booking intent patterns
            r'^(?:ok\s+)?(?:i\s+)?(?:want\s+to|wanna|would\s+like\s+to)\s+(?:book|schedule|get)\s+(?:a\s+)?',
            r'^(?:ok\s+)?(?:book|schedule|get)\s+(?:me\s+)?(?:a\s+)?',

            # General filler patterns
            r'^(?:ok|okay|alright|sure|yes|yeah)\s+',
            r'^(?:please\s+)?(?:i\s+need|i\s+want)\s+',
        ]

        cleaned = message_lower
        for pattern in prefixes_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        return cleaned.strip()

    async def _extract_with_patterns(
        self,
        message: str,
        expected_entity: EntityType,
        context: Dict[str, Any]
    ) -> Optional[EntityExtractionResult]:
        """
        Try to extract entity using regex patterns (fast path)
        """
        message_lower = message.lower().strip()

        # Clean conversational prefixes for better entity extraction
        cleaned_message = self._clean_conversational_prefixes(message)

        # ACTION patterns
        if expected_entity == EntityType.ACTION:
            return self._extract_action(message_lower)

        # Date patterns
        if expected_entity == EntityType.DATE:
            return self._extract_date(message, message_lower)

        # Time patterns
        if expected_entity == EntityType.TIME:
            return self._extract_time(message, message_lower)

        # Location patterns (pincode or city)
        if expected_entity == EntityType.LOCATION:
            return self._extract_location(message, message_lower)

        # Booking ID pattern
        if expected_entity == EntityType.BOOKING_ID:
            return self._extract_booking_id(message)

        # Service type patterns - use cleaned message for better extraction
        if expected_entity == EntityType.SERVICE_TYPE:
            # NEW: Try service name resolution first (handles specific service names + typos)
            logger.info(f"[EntityExtractor] SERVICE_TYPE extraction - service_resolver: {self.service_resolver is not None}")
            if self.service_resolver:
                logger.info(f"[EntityExtractor] Attempting service name resolution for: '{cleaned_message}'")
                service_name_result = await self._extract_service_name(cleaned_message, context)
                logger.info(f"[EntityExtractor] Service name resolution result: {service_name_result}")
                if service_name_result and service_name_result.confidence >= 0.7:
                    logger.info(f"[EntityExtractor] Service name resolved: {service_name_result.entity_value}")
                    return service_name_result
                else:
                    logger.info(f"[EntityExtractor] Service name resolution failed or low confidence")
            else:
                logger.warning(f"[EntityExtractor] service_resolver is None, skipping service name resolution")

            # Fall back to traditional service_type extraction
            logger.info(f"[EntityExtractor] Falling back to traditional service_type extraction")
            return self._extract_service_type(cleaned_message)

        # Service subcategory patterns - use cleaned message for better extraction
        if expected_entity == EntityType.SERVICE_SUBCATEGORY:
            return self._extract_service_subcategory(cleaned_message, context)

        # Issue type patterns
        if expected_entity == EntityType.ISSUE_TYPE:
            return self._extract_issue_type(message_lower)

        # Payment type patterns
        if expected_entity == EntityType.PAYMENT_TYPE:
            return self._extract_payment_type(message_lower)

        # Description patterns (for complaints)
        if expected_entity == EntityType.DESCRIPTION:
            return self._extract_description(message, context)

        # Status filter patterns
        if expected_entity == EntityType.STATUS_FILTER:
            return self._extract_status_filter(message_lower)

        # Booking filter patterns
        if expected_entity == EntityType.BOOKING_FILTER:
            return self._extract_booking_filter(message_lower)

        # Date/Time patterns
        if expected_entity == EntityType.DATE:
            return self._extract_date(message, message_lower)

        if expected_entity == EntityType.TIME:
            return self._extract_time(message, message_lower)

        # New date/time for rescheduling
        if expected_entity == EntityType.NEW_DATE:
            return self._extract_new_date(message, message_lower)

        if expected_entity == EntityType.NEW_TIME:
            return self._extract_new_time(message, message_lower)

        # Sort by patterns
        if expected_entity == EntityType.SORT_BY:
            return self._extract_sort_by(message_lower)

        return None
    
    def _extract_action(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract action (book, cancel, reschedule, modify, list, check_status)"""
        import re

        # FIRST: Check for explicit action keywords (higher priority)
        # This ensures "cancel my booking" matches "cancel" before "my booking" matches "list"
        action_keywords = {
            "cancel": [r'\bcancel\b', r'\bdelete\b', r'\bremove\b'],
            "reschedule": [r'\breschedule\b', r'\bchange date\b', r'\bchange time\b', r'\bmove\b'],
            "modify": [r'\bmodify\b', r'\bupdate\b', r'\bchange\b', r'\bedit\b'],
            "book": [r'\bbook\b', r'\bschedule\b', r'\breserve\b', r'\bappointment\b'],
            "check_status": [r'\bstatus\b', r'\btrack\b', r'\bwhere is\b']
        }

        for action, patterns in action_keywords.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return EntityExtractionResult(
                        entity_type=EntityType.ACTION.value,
                        entity_value=action,
                        confidence=0.9,
                        normalized_value=action,
                        extraction_method="pattern"
                    )

        # SECOND: Check for "list" action patterns (lower priority)
        # Only if no explicit action keywords were found
        list_patterns = [
            r'\b(list|show|view|display)\s+(my|all|them)?\s*(bookings?|appointments?)?',  # "list them", "show my bookings"
            r'\b(check|see|get)\s+my\s+(bookings?|appointments?)',  # "check my bookings"
            r'\bmy\s+(bookings?|appointments?)$',  # "my bookings" (end of message only)
            r'^\s*(my|all)\s+(bookings?|appointments?)\s*$',  # "my bookings" or "all bookings" (standalone)
            r'(bookings?|appointments?).*\b(list|show|view|display)',  # "bookings and list them"
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                return EntityExtractionResult(
                    entity_type=EntityType.ACTION.value,
                    entity_value="list",
                    confidence=0.95,
                    normalized_value="list",
                    extraction_method="pattern"
                )

        return None

    def _extract_status_filter(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract booking status filter (pending, confirmed, completed, cancelled)"""
        status_keywords = {
            "pending": ["pending", "upcoming", "scheduled", "active"],
            "confirmed": ["confirmed", "approved"],
            "completed": ["completed", "finished", "done", "past"],
            "cancelled": ["cancelled", "canceled", "deleted", "removed"]
        }

        for status, keywords in status_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.STATUS_FILTER.value,
                        entity_value=status,
                        confidence=0.9,
                        normalized_value=status,
                        extraction_method="pattern"
                    )

        return None

    def _extract_booking_filter(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract booking filter (latest, recent, last, first, oldest)"""
        filter_keywords = {
            "latest": ["latest", "most recent", "newest", "last"],
            "recent": ["recent", "recent ones"],
            "last": ["last", "previous"],
            "first": ["first", "earliest", "oldest"],
            "all": ["all", "every", "entire"]
        }

        for filter_type, keywords in filter_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.BOOKING_FILTER.value,
                        entity_value=filter_type,
                        confidence=0.9,
                        normalized_value=filter_type,
                        extraction_method="pattern"
                    )

        return None

    def _extract_sort_by(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract sort preference (date, status, amount)"""
        sort_keywords = {
            "date": ["date", "time", "when", "chronological", "recent", "latest"],
            "status": ["status", "state"],
            "amount": ["amount", "price", "cost", "expensive", "cheap"]
        }

        for sort_field, keywords in sort_keywords.items():
            for keyword in keywords:
                if f"sort by {keyword}" in message_lower or f"order by {keyword}" in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.SORT_BY.value,
                        entity_value=sort_field,
                        confidence=0.9,
                        normalized_value=sort_field,
                        extraction_method="pattern"
                    )

        return None

    def _extract_date(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract date using centralized normalizer"""
        from src.utils.entity_normalizer import normalize_date

        # Try to extract raw date value
        raw_value = None
        confidence = 0.0

        # Relative dates - word boundary matches
        if re.search(r'\b(today|now)\b', message_lower):
            match = re.search(r'\b(today|now)\b', message_lower)
            raw_value = match.group(0)
            confidence = 0.95
        elif re.search(r'\b(tomorrow|tmrw|tmr)\b', message_lower):
            match = re.search(r'\b(tomorrow|tmrw|tmr)\b', message_lower)
            raw_value = match.group(0)
            confidence = 0.95
        elif "day after tomorrow" in message_lower or "overmorrow" in message_lower:
            if "day after tomorrow" in message_lower:
                raw_value = "day after tomorrow"
            else:
                raw_value = "overmorrow"
            confidence = 0.9
        elif "next week" in message_lower:
            raw_value = "next week"
            confidence = 0.8
        elif "next month" in message_lower:
            raw_value = "next month"
            confidence = 0.8
        # "in X days" or "after X days" patterns
        elif re.search(r'(?:in|after)\s+\d+\s+days?', message_lower):
            match = re.search(r'(?:in|after)\s+\d+\s+days?', message_lower)
            raw_value = match.group(0)
            confidence = 0.9
        # "in X weeks" or "after X weeks" patterns
        elif re.search(r'(?:in|after)\s+\d+\s+weeks?', message_lower):
            match = re.search(r'(?:in|after)\s+\d+\s+weeks?', message_lower)
            raw_value = match.group(0)
            confidence = 0.9
        # Weekday names: "monday", "next monday", "this friday"
        elif re.search(r'\b(?:next\s+|this\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\b', message_lower):
            match = re.search(r'\b(?:next\s+|this\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\b', message_lower)
            raw_value = match.group(0)
            confidence = 0.9
        else:
            # Natural date formats with year: "December 15th, 2025", "15th Dec, 2025"
            natural_date_with_year_patterns = [
                r'(\d{1,2})(st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december),?\s+\d{4}',
                r'(\d{1,2})(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec),?\s+\d{4}',
                r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(st|nd|rd|th)?,?\s+\d{4}',
                r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(st|nd|rd|th)?,?\s+\d{4}'
            ]

            for pattern in natural_date_with_year_patterns:
                date_match = re.search(pattern, message_lower)
                if date_match:
                    raw_value = date_match.group(0)
                    confidence = 0.95
                    break

            if not raw_value:
                # Natural date formats without year: "31st October", "October 31st", "31 Oct"
                natural_date_patterns = [
                    r'(\d{1,2})(st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
                    r'(\d{1,2})(st|nd|rd|th)?\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
                    r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(st|nd|rd|th)?',
                    r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2})(st|nd|rd|th)?'
                ]

                for pattern in natural_date_patterns:
                    date_match = re.search(pattern, message_lower)
                    if date_match:
                        raw_value = date_match.group(0)
                        confidence = 0.9
                        break

            if not raw_value:
                # ISO format (YYYY-MM-DD)
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', message)
                if date_match:
                    raw_value = date_match.group(0)
                    confidence = 0.95
                # DD/MM/YYYY or MM/DD/YYYY or DD-MM-YYYY or MM-DD-YYYY format
                else:
                    date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', message)
                    if date_match:
                        raw_value = date_match.group(0)
                        confidence = 0.9

        if raw_value:
            # Use centralized normalizer
            normalized = normalize_date(raw_value)
            if normalized:
                logger.info(f"[EntityExtractor] Extracted date: '{raw_value}' → normalized: '{normalized}'")
                return EntityExtractionResult(
                    entity_type=EntityType.DATE.value,
                    entity_value=raw_value,
                    confidence=confidence,
                    normalized_value=normalized,
                    extraction_method="pattern"
                )

        return None

    def _extract_combined_date_time(self, message: str) -> Optional[Dict[str, EntityExtractionResult]]:
        """
        Extract combined date-time patterns like 'tomorrow 4pm', 'next Monday at 2pm'

        Args:
            message: User's message

        Returns:
            Dict with 'date' and 'time' EntityExtractionResult or None
        """
        from src.utils.entity_normalizer import normalize_date, normalize_time

        message_lower = message.lower().strip()
        logger.info(f"[EntityExtractor] Trying to extract combined date-time from: '{message}'")

        # Combined patterns for date + time
        combined_patterns = [
            # "tomorrow 4pm", "today 3pm"
            r'(today|tomorrow|tmrw|tmr)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "tomorrow at 4pm", "today at 3:30pm"
            r'(today|tomorrow|tmrw|tmr)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "in 3 days at 2pm", "after 5 days at 3pm"
            r'((?:in|after)\s+\d+\s+days?)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "December 15th, 2025 at 2pm", "15th Dec, 2025 at 3pm"
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec),?\s+\d{4})\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "31st October 4pm", "December 25th at 2pm"
            r'(\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "Monday 4pm", "next Friday at 3pm"
            r'(?:next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
            # "2025-12-15 at 3pm", "15/12/2025 at 2pm"
            r'(\d{4}-\d{2}-\d{2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))',
        ]

        for pattern in combined_patterns:
            match = re.search(pattern, message_lower)
            if match:
                date_part = match.group(1).strip()
                time_part = match.group(2).strip()

                logger.info(f"[EntityExtractor] Found combined pattern - Date: '{date_part}', Time: '{time_part}'")

                # Normalize date and time
                normalized_date = normalize_date(date_part)
                normalized_time = normalize_time(time_part)

                if normalized_date and normalized_time:
                    results = {}

                    results['date'] = EntityExtractionResult(
                        entity_type=EntityType.DATE.value,
                        entity_value=date_part,
                        confidence=0.9,
                        normalized_value=normalized_date,
                        extraction_method="combined_pattern"
                    )

                    results['time'] = EntityExtractionResult(
                        entity_type=EntityType.TIME.value,
                        entity_value=time_part,
                        confidence=0.9,
                        normalized_value=normalized_time,
                        extraction_method="combined_pattern"
                    )

                    logger.info(f"[EntityExtractor] Successfully extracted combined date-time: {normalized_date} at {normalized_time}")
                    return results

        return None

    def _extract_time(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract time using centralized normalizer"""
        from src.utils.entity_normalizer import normalize_time

        # Try to extract raw time value
        raw_value = None
        confidence = 0.0

        # 12-hour format
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)', message_lower)
        if time_match:
            raw_value = time_match.group(0)
            confidence = 0.95
        else:
            # 24-hour format
            time_match = re.search(r'(\d{1,2}):(\d{2})', message)
            if time_match:
                raw_value = time_match.group(0)
                confidence = 0.95
            else:
                # Time of day keywords
                if "morning" in message_lower:
                    raw_value = "morning"
                    confidence = 0.7
                elif "afternoon" in message_lower:
                    raw_value = "afternoon"
                    confidence = 0.7
                elif "evening" in message_lower:
                    raw_value = "evening"
                    confidence = 0.7
                elif "night" in message_lower:
                    raw_value = "night"
                    confidence = 0.6

        if raw_value:
            # Use centralized normalizer
            normalized = normalize_time(raw_value)
            if normalized:
                return EntityExtractionResult(
                    entity_type=EntityType.TIME.value,
                    entity_value=raw_value,
                    confidence=confidence,
                    normalized_value=normalized,
                    extraction_method="pattern"
                )

        return None

    def _extract_new_date(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract new date for rescheduling (uses same logic as _extract_date)"""
        # Look for keywords like "to", "for", "on" before the date
        # Examples: "reschedule to tomorrow", "change to next Monday", "move to 2025-11-05"

        # Try to extract date using the existing date extraction logic
        date_result = self._extract_date(message, message_lower)

        if date_result:
            # Change entity type to NEW_DATE
            return EntityExtractionResult(
                entity_type=EntityType.NEW_DATE.value,
                entity_value=date_result.entity_value,
                confidence=date_result.confidence,
                normalized_value=date_result.normalized_value,
                extraction_method=date_result.extraction_method
            )

        return None

    def _extract_new_time(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract new time for rescheduling (uses same logic as _extract_time)"""
        # Look for keywords like "to", "for", "at" before the time
        # Examples: "reschedule to 2pm", "change to 14:00", "move to afternoon"

        # Try to extract time using the existing time extraction logic
        time_result = self._extract_time(message, message_lower)

        if time_result:
            # Change entity type to NEW_TIME
            return EntityExtractionResult(
                entity_type=EntityType.NEW_TIME.value,
                entity_value=time_result.entity_value,
                confidence=time_result.confidence,
                normalized_value=time_result.normalized_value,
                extraction_method=time_result.extraction_method
            )

        return None

    def _extract_location(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """
        Extract location (full address, pincode, or city name)

        Priority:
        1. Full address with pincode (e.g., "123 Main St, Bangalore, Karnataka, 560001")
        2. City + pincode (e.g., "Bangalore, 560001")
        3. Pincode only (e.g., "560001")
        4. City name (e.g., "Bangalore")

        Strategy: Check for comma-separated patterns first (indicates full address),
        then fall back to pincode-only or city-only extraction.
        """
        # Check if message contains commas (indicates structured address)
        if ',' in message:
            # Check for full address pattern (street, city, state, pincode)
            # Pattern: any text, comma, city name, comma, state/text, comma/space, 6-digit pincode
            full_address_pattern = r'.+,\s*.+,\s*.+,?\s*\d{6}'
            if re.search(full_address_pattern, message):
                # Return the entire message as the address
                full_address = message.strip()
                logger.info(f"[EntityExtractor] Extracted full address: {full_address}")
                return EntityExtractionResult(
                    entity_type=EntityType.LOCATION.value,
                    entity_value=full_address,
                    confidence=0.98,
                    normalized_value=full_address,
                    extraction_method="pattern"
                )

            # Check for city + pincode pattern (e.g., "Bangalore, 560001")
            city_pincode_pattern = r'[a-zA-Z\s]+,\s*\d{6}'
            if re.search(city_pincode_pattern, message):
                location = message.strip()
                logger.info(f"[EntityExtractor] Extracted city + pincode: {location}")
                return EntityExtractionResult(
                    entity_type=EntityType.LOCATION.value,
                    entity_value=location,
                    confidence=0.95,
                    normalized_value=location,
                    extraction_method="pattern"
                )

        # Pincode pattern (6 digits only) - only if no commas found
        pincode_match = re.search(r'\b(\d{6})\b', message)
        if pincode_match:
            logger.info(f"[EntityExtractor] Extracted pincode only: {pincode_match.group(1)}")
            return EntityExtractionResult(
                entity_type=EntityType.LOCATION.value,
                entity_value=pincode_match.group(1),
                confidence=0.90,
                normalized_value=pincode_match.group(1),
                extraction_method="pattern"
            )

        # Common Indian cities
        cities = [
            "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
            "kolkata", "pune", "ahmedabad", "jaipur", "surat", "lucknow",
            "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam",
            "pimpri", "patna", "vadodara", "ghaziabad", "ludhiana", "agra"
        ]

        for city in cities:
            if city in message_lower:
                return EntityExtractionResult(
                    entity_type=EntityType.LOCATION.value,
                    entity_value=city.title(),
                    confidence=0.85,
                    normalized_value=city.title(),
                    extraction_method="pattern"
                )

        # If message is short and doesn't match patterns, assume it's a city name
        if len(message.split()) <= 2:
            return EntityExtractionResult(
                entity_type=EntityType.LOCATION.value,
                entity_value=message.strip(),
                confidence=0.6,
                normalized_value=message.strip().title(),
                extraction_method="heuristic"
            )

        return None

    def _extract_booking_id(self, message: str) -> Optional[EntityExtractionResult]:
        """
        Extract booking ID (Order ID)

        Supports formats:
        - ORD followed by 8 alphanumeric characters: ORDA5D9F532
        - Legacy formats with hyphens: BOOK-12345, BKG-12345, ORD-12345
        - Just numbers: 12345
        """
        # Pattern 1: ORD followed by 8 alphanumeric characters (current format)
        # Example: ORDA5D9F532, ORD4E33BB94
        order_id_match = re.search(r'\b(ORD[A-Z0-9]{8})\b', message, re.IGNORECASE)
        if order_id_match:
            order_id = order_id_match.group(1).upper()
            return EntityExtractionResult(
                entity_type=EntityType.BOOKING_ID.value,
                entity_value=order_id_match.group(1),
                confidence=0.98,
                normalized_value=order_id,
                extraction_method="pattern"
            )

        # Pattern 2: Legacy formats with hyphens (BOOK-12345, BKG-12345, ORD-12345)
        booking_match = re.search(r'\b(BOOK|BKG|ORD)[-_]?(\d{4,6})\b', message, re.IGNORECASE)
        if booking_match:
            booking_id = booking_match.group(0).upper()
            return EntityExtractionResult(
                entity_type=EntityType.BOOKING_ID.value,
                entity_value=booking_match.group(0),
                confidence=0.95,
                normalized_value=booking_id,
                extraction_method="pattern"
            )

        # Pattern 3: Just numbers (4-6 digits) - lower confidence
        number_match = re.search(r'\b(\d{4,6})\b', message)
        if number_match:
            return EntityExtractionResult(
                entity_type=EntityType.BOOKING_ID.value,
                entity_value=number_match.group(1),
                confidence=0.6,
                normalized_value=f"BOOK-{number_match.group(1)}",
                extraction_method="heuristic"
            )

        return None

    async def _extract_service_name(
        self,
        message: str,
        context: Dict[str, Any]
    ) -> Optional[EntityExtractionResult]:
        """
        Extract and resolve service name from message using ServiceNameResolver

        This handles cases like:
        - "i want to book texture painting" (specific service name)
        - "book texture pianting" (with typo)
        - "details on texture painting" (after seeing it in search)
        - "that one" (context reference)

        Returns:
            EntityExtractionResult with resolved service metadata, or None if not resolved
        """
        if not self.service_resolver:
            logger.warning("[EntityExtractor] ServiceNameResolver not initialized - skipping service name resolution")
            return None

        logger.info(f"[EntityExtractor] Attempting service name resolution for: '{message}'")

        try:
            # Resolve service name using ServiceNameResolver
            resolution = await self.service_resolver.resolve(message, context)

            logger.info(f"[EntityExtractor] ServiceNameResolver result: resolved={resolution.resolved}, error={resolution.error_message}")

            if not resolution.resolved:
                logger.info(f"[EntityExtractor] Service name not resolved: {resolution.error_message}")
                return None

            logger.info(f"[EntityExtractor] ✅ Service name resolved: {resolution.service_name or resolution.subcategory_name or resolution.category_name} (confidence: {resolution.confidence}, method: {resolution.method}, category_id={resolution.category_id}, subcategory_id={resolution.subcategory_id})")

            # Build metadata to pass to booking flow
            metadata = {
                "_resolved_service": {
                    "rate_card_id": resolution.rate_card_id,
                    "category_id": resolution.category_id,
                    "subcategory_id": resolution.subcategory_id,
                    "service_name": resolution.service_name,
                    "category_name": resolution.category_name,
                    "subcategory_name": resolution.subcategory_name,
                    "price": resolution.price
                }
            }

            # If we have category_id, use it as service_type
            # This allows the booking flow to work with existing logic
            if resolution.category_id:
                return EntityExtractionResult(
                    entity_type=EntityType.SERVICE_TYPE.value,
                    entity_value=str(resolution.category_id),  # Use category_id as service_type
                    confidence=resolution.confidence,
                    normalized_value=str(resolution.category_id),
                    extraction_method=f"service_name_resolver_{resolution.method}",
                    metadata=metadata
                )

            return None

        except Exception as e:
            logger.error(f"[EntityExtractor] Error in service name resolution: {e}", exc_info=True)
            return None

    def _extract_service_type(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract service type"""
        service_keywords = {
            # Repair services (more specific patterns first)
            "ac_repair": ["ac repair", "air conditioning repair", "hvac repair", "air conditioner repair"],
            "tv_repair": ["tv repair", "television repair", "tv service", "television service", "tv", "television"],
            "appliance_repair": ["washing machine", "refrigerator", "fridge", "appliance", "microwave", "geyser"],
            "bathroom_fitting": ["bathroom fitting", "bathroom installation", "bathroom renovation"],

            # General services
            "ac": ["ac", "air conditioning", "hvac", "air conditioner", "cooling"],
            "plumbing": ["plumbing", "plumber", "pipe", "leak", "tap", "faucet", "drain"],
            "cleaning": ["house cleaning", "home cleaning", "deep cleaning", "sanitization"],
            "electrical": ["electrical", "electrician", "wiring", "switch", "light", "power"],
            "painting": ["painting", "paint", "painter", "wall painting"],
            "pest_control": ["pest control", "pest", "pest service", "general pest control", "pest control service", "exterminator", "fumigation"],
            "carpentry": ["carpentry", "carpenter", "furniture", "wood work", "cabinet", "door repair", "furniture repair"],
            "water_purifier": ["water purifier", "ro", "water filter", "purifier", "water treatment", "ro service"],
            "car_care": ["car care", "car wash", "car cleaning", "car service", "vehicle cleaning", "auto detailing"],
            "salon_for_women": ["salon", "beauty salon", "women salon", "ladies salon", "beauty parlor", "hair salon"],
            "salon_for_men": ["men salon", "barber", "gents salon", "male grooming", "men's salon"],
            "packers_and_movers": ["packers", "movers", "packing", "moving", "relocation", "shifting", "packers and movers"]
        }

        # Check for specific subcategory names first
        # Map subcategory keywords to their parent categories
        subcategory_to_category = {
            "kitchen cleaning": ("cleaning", "Kitchen Cleaning"),
            "bathroom cleaning": ("cleaning", "Bathroom Cleaning"),
            "sofa cleaning": ("cleaning", "Sofa Cleaning"),
            "carpet cleaning": ("cleaning", "Carpet Cleaning"),
            "window cleaning": ("cleaning", "Window Cleaning"),
            "move-in cleaning": ("cleaning", "Move-in/Move-out Cleaning"),
            "move-out cleaning": ("cleaning", "Move-in/Move-out Cleaning"),
            "regular cleaning": ("cleaning", "Regular Cleaning"),
            "deep cleaning": ("cleaning", "Deep Cleaning")
        }

        for subcategory, (category, subcategory_name) in subcategory_to_category.items():
            if subcategory in message_lower:
                # Extract category but add metadata indicating specific subcategory
                logger.info(f"[_extract_service_type] Found subcategory keyword '{subcategory}', extracting category '{category}' with subcategory hint")
                return EntityExtractionResult(
                    entity_type=EntityType.SERVICE_TYPE.value,
                    entity_value=category,
                    confidence=0.95,  # High confidence for exact subcategory match
                    normalized_value=category,
                    extraction_method="pattern_subcategory",
                    metadata={"subcategory_hint": subcategory_name}
                )

        for service_type, keywords in service_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.SERVICE_TYPE.value,
                        entity_value=service_type,
                        confidence=0.9,
                        normalized_value=service_type,
                        extraction_method="pattern"
                    )

        return None

    def _extract_service_subcategory(self, message_lower: str, context: Dict[str, Any]) -> Optional[EntityExtractionResult]:
        """
        Extract service subcategory from user message

        This method matches the user's input against available subcategories from the context.
        The context should contain 'available_subcategories' from the validation metadata.

        Args:
            message_lower: User message in lowercase
            context: Context containing available_subcategories and collected_entities

        Returns:
            EntityExtractionResult if a match is found, None otherwise
        """
        logger.info(f"[EntityExtractor] Extracting service_subcategory from: '{message_lower}'")

        # Get available subcategories from context (set by validation when service_type requires subcategory)
        collected_entities = context.get('collected_entities', {})

        # Try to get available subcategories from dialog state metadata
        # This is set by the slot-filling graph when service_type validation fails
        available_subcategories = context.get('available_subcategories', [])

        if not available_subcategories:
            logger.warning(f"[EntityExtractor] No available_subcategories in context, cannot extract subcategory")
            # Fall back to generic extraction - just return the message as-is
            # The validator will check if it's valid
            return EntityExtractionResult(
                entity_type=EntityType.SERVICE_SUBCATEGORY.value,
                entity_value=message_lower,
                confidence=0.5,
                normalized_value=message_lower,
                extraction_method="fallback"
            )

        logger.info(f"[EntityExtractor] Available subcategories: {[sub.get('name', '') for sub in available_subcategories]}")

        # Check if user input is a numeric selection (e.g., "3" to select option 3)
        if message_lower.strip().isdigit():
            selection_index = int(message_lower.strip()) - 1  # Convert to 0-based index
            if 0 <= selection_index < len(available_subcategories):
                selected_subcategory = available_subcategories[selection_index]
                subcategory_name = selected_subcategory.get('name', '')
                subcategory_id = selected_subcategory.get('id')
                logger.info(f"[EntityExtractor] Numeric selection: {message_lower} -> {subcategory_name} (ID: {subcategory_id})")
                return EntityExtractionResult(
                    entity_type=EntityType.SERVICE_SUBCATEGORY.value,
                    entity_value=subcategory_name.lower(),
                    confidence=0.95,
                    normalized_value=subcategory_name.lower(),
                    extraction_method="numeric_selection",
                    metadata={"subcategory_id": subcategory_id, "subcategory_name": subcategory_name}
                )
            else:
                logger.warning(f"[EntityExtractor] Numeric selection {message_lower} is out of range (1-{len(available_subcategories)})")

        # Try to match user input against available subcategories
        # Use fuzzy matching to handle variations like "deep clean" vs "deep cleaning"
        best_match = None
        best_score = 0.0

        for subcategory in available_subcategories:
            subcategory_name = subcategory.get('name', '').lower()
            subcategory_id = subcategory.get('id')

            # Exact match (highest confidence)
            if subcategory_name == message_lower:
                logger.info(f"[EntityExtractor] Exact match found: {subcategory_name}")
                return EntityExtractionResult(
                    entity_type=EntityType.SERVICE_SUBCATEGORY.value,
                    entity_value=message_lower,
                    confidence=0.95,
                    normalized_value=subcategory_name,
                    extraction_method="pattern",
                    metadata={"subcategory_id": subcategory_id, "subcategory_name": subcategory.get('name')}
                )

            # Partial match (check if user input is contained in subcategory name or vice versa)
            if subcategory_name in message_lower or message_lower in subcategory_name:
                # Calculate match score based on length ratio
                score = min(len(message_lower), len(subcategory_name)) / max(len(message_lower), len(subcategory_name))
                if score > best_score:
                    best_score = score
                    best_match = subcategory

        # If we found a good partial match (score > 0.7), return it
        if best_match and best_score > 0.7:
            subcategory_name = best_match.get('name', '').lower()
            subcategory_id = best_match.get('id')
            logger.info(f"[EntityExtractor] Partial match found: {subcategory_name} (score: {best_score})")
            return EntityExtractionResult(
                entity_type=EntityType.SERVICE_SUBCATEGORY.value,
                entity_value=message_lower,
                confidence=0.85 * best_score,  # Adjust confidence based on match quality
                normalized_value=subcategory_name,
                extraction_method="pattern",
                metadata={"subcategory_id": subcategory_id, "subcategory_name": best_match.get('name')}
            )

        # No good match found - return low confidence result
        # The validator will reject it and ask the user to try again
        logger.warning(f"[EntityExtractor] No good match found for '{message_lower}' in available subcategories")
        return EntityExtractionResult(
            entity_type=EntityType.SERVICE_SUBCATEGORY.value,
            entity_value=message_lower,
            confidence=0.3,
            normalized_value=message_lower,
            extraction_method="fallback"
        )

    def _extract_issue_type(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract issue type for complaints"""
        # First check for numbered responses (1, 2, 3, etc.)
        number_mappings = {
            "1": "no_show",
            "2": "quality",
            "3": "behavior",
            "4": "damage",
            "5": "late",
            "6": "other"
        }

        # Check if message is just a number
        stripped_message = message_lower.strip()
        if stripped_message in number_mappings:
            issue_type = number_mappings[stripped_message]
            return EntityExtractionResult(
                entity_type=EntityType.ISSUE_TYPE.value,
                entity_value=issue_type,
                confidence=0.95,  # High confidence for numbered selection
                normalized_value=issue_type,
                extraction_method="numbered_option"
            )

        # Then check for keyword patterns
        issue_keywords = {
            "no_show": ["no show", "no-show", "didn't come", "didn't arrive", "not arrived", "missed", "didn't show up", "not show up"],
            "quality": ["quality", "poor quality", "bad quality", "not satisfied", "unsatisfied", "poor service", "bad service"],
            "behavior": ["behavior", "behaviour", "rude", "unprofessional", "misbehave", "attitude", "inappropriate"],
            "damage": ["damage", "damaged", "broke", "broken", "destroyed", "property damage", "something damaged"],
            "late": ["late", "delayed", "delay", "waiting", "not on time", "late arrival"],
            "other": ["other", "different", "something else", "not listed"]
        }

        for issue_type, keywords in issue_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.ISSUE_TYPE.value,
                        entity_value=issue_type,
                        confidence=0.85,
                        normalized_value=issue_type,
                        extraction_method="pattern"
                    )

        return None

    def _extract_description(self, message: str, context: Dict[str, Any]) -> Optional[EntityExtractionResult]:
        """Extract description for complaints and other detailed explanations"""
        # Clean the message
        cleaned_message = message.strip()

        # For complaints, be very liberal in accepting descriptions
        # Any message with reasonable content should be accepted as description
        if len(cleaned_message) >= 5:  # Lowered from 10 to 5 characters
            word_count = len(cleaned_message.split())

            # Accept almost any multi-word message as description
            if word_count >= 2:  # Lowered from 3 to 2 words
                return EntityExtractionResult(
                    entity_type=EntityType.DESCRIPTION.value,
                    entity_value=cleaned_message,
                    confidence=0.95,  # High confidence for description extraction
                    normalized_value=cleaned_message,
                    extraction_method="pattern"
                )

        # Even single words can be descriptions if they're meaningful
        if len(cleaned_message) >= 3:  # At least 3 characters
            return EntityExtractionResult(
                entity_type=EntityType.DESCRIPTION.value,
                entity_value=cleaned_message,
                confidence=0.80,  # Lower confidence for very short descriptions
                normalized_value=cleaned_message,
                extraction_method="fallback"
            )

        return None

    def _extract_payment_type(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract payment issue type"""
        payment_keywords = {
            "failed": ["failed", "failure", "not processed", "didn't go through"],
            "double_charged": ["double charge", "charged twice", "duplicate charge", "two times"],
            "wrong_amount": ["wrong amount", "incorrect amount", "overcharged", "more than expected"],
        }

        for payment_type, keywords in payment_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.PAYMENT_TYPE.value,
                        entity_value=payment_type,
                        confidence=0.85,
                        normalized_value=payment_type,
                        extraction_method="pattern"
                    )

        return None

    async def _extract_with_llm(
        self,
        message: str,
        expected_entity: EntityType,
        context: Dict[str, Any]
    ) -> Optional[EntityExtractionResult]:
        """
        Extract entity using LLM with context

        Used as fallback when pattern matching fails or has low confidence
        """
        if not self.llm_client:
            return None

        prompt = self._build_extraction_prompt(message, expected_entity, context)

        # Define output schema
        class ExtractionOutput(BaseModel):
            entity_value: str
            confidence: float
            normalized_value: Optional[str] = None

        try:
            structured_llm = self.llm_client.with_structured_output(ExtractionOutput)

            # Invoke LLM with retry logic
            from src.nlp.llm.gemini_client import with_retry

            @with_retry(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
            def invoke_with_retry():
                return structured_llm.invoke(prompt)

            result = invoke_with_retry()

            return EntityExtractionResult(
                entity_type=expected_entity.value,
                entity_value=result.entity_value,
                confidence=result.confidence,
                normalized_value=result.normalized_value or result.entity_value,
                extraction_method="llm"
            )
        except Exception as e:
            logger.error(f"[EntityExtractor] LLM extraction failed: {e}")
            return None

    def _build_extraction_prompt(
        self,
        message: str,
        expected_entity: EntityType,
        context: Dict[str, Any]
    ) -> str:
        """
        Build prompt for LLM entity extraction
        """
        today = datetime.now().date().isoformat()
        current_time = datetime.now().strftime("%H:%M")

        collected_entities = context.get("collected_entities", {})
        last_question = context.get("last_question", "")

        # Special instructions for location extraction
        location_instructions = ""
        if expected_entity == EntityType.LOCATION:
            location_instructions = """
**IMPORTANT for Location Extraction:**
- ONLY extract if the message contains a CLEAR location indicator:
  * A 6-digit pincode (e.g., "400001", "110001")
  * A city name (e.g., "Mumbai", "Delhi", "Bangalore")
  * A specific area/locality name
- DO NOT extract if the message:
  * Is a general statement (e.g., "I want to book a service")
  * Contains service types or actions (e.g., "AC repair service")
  * Is asking a question
  * Does not mention any location
- If NO clear location is found, set confidence to 0.0 and entity_value to "NOT_FOUND"
"""

        prompt = f"""You are an expert entity extractor for a home services platform.

**Context:**
- Today's date: {today}
- Current time: {current_time}
- Last question asked: "{last_question}"
- Already collected: {collected_entities}

**Task:**
Extract the **{expected_entity.value}** from the user's response.

**User's Response:** "{message}"

**Instructions:**
1. Extract the {expected_entity.value} value from the message
2. Normalize the value to a standard format:
   - Dates: YYYY-MM-DD format
   - Times: HH:MM format (24-hour)
   - Locations: City name or 6-digit pincode ONLY
   - Service types: Lowercase (e.g., "ac", "plumbing")
3. Provide a confidence score (0.0 to 1.0)
4. If the message is ambiguous or doesn't contain the entity, set confidence to 0.0 and entity_value to "NOT_FOUND"
{location_instructions}
**Examples:**
- "tomorrow" → date: {(datetime.now().date() + timedelta(days=1)).isoformat()}, confidence: 0.9
- "2 PM" → time: "14:00", confidence: 0.9
- "Mumbai" → location: "Mumbai", confidence: 0.85
- "400001" → location: "400001", confidence: 0.95
- "I want to book AC service" (when expecting location) → location: "NOT_FOUND", confidence: 0.0
- "yes" (when expecting confirmation) → confirmation: "yes", confidence: 0.95

Return the extracted entity value, normalized value, and confidence score.
"""

        return prompt

