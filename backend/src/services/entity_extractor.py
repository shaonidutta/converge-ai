"""
Entity Extractor Service

Extracts entity values from follow-up responses using pattern matching + LLM fallback.

Approach:
- Pattern matching (regex/rule-based) first for common cases (fast path)
- LLM fallback when confidence is low or patterns fail
- Context-aware extraction using conversation history

Design Principles:
- Fast pattern matching for common formats
- LLM for ambiguous or complex cases
- High confidence scoring
- Normalized output values
"""

import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from src.nlp.intent.config import EntityType
from src.llm.gemini.client import LLMClient

logger = logging.getLogger(__name__)


class EntityExtractionResult(BaseModel):
    """Result of entity extraction"""
    entity_type: str
    entity_value: Any
    confidence: float
    normalized_value: Optional[Any] = None
    extraction_method: str  # "pattern", "llm", "heuristic"


class EntityExtractor:
    """
    Extracts entity values from follow-up responses
    
    Features:
    - Pattern matching (fast path)
    - LLM fallback (accurate)
    - Context-aware extraction
    - Normalized output
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
    
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
        pattern_result = self._extract_with_patterns(message, expected_entity, context)
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
    
    def _extract_with_patterns(
        self,
        message: str,
        expected_entity: EntityType,
        context: Dict[str, Any]
    ) -> Optional[EntityExtractionResult]:
        """
        Try to extract entity using regex patterns (fast path)
        """
        message_lower = message.lower().strip()

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

        # Service type patterns
        if expected_entity == EntityType.SERVICE_TYPE:
            return self._extract_service_type(message_lower)

        # Issue type patterns
        if expected_entity == EntityType.ISSUE_TYPE:
            return self._extract_issue_type(message_lower)

        # Payment type patterns
        if expected_entity == EntityType.PAYMENT_TYPE:
            return self._extract_payment_type(message_lower)

        return None
    
    def _extract_action(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract action (book, cancel, reschedule, modify, check_status)"""
        action_keywords = {
            "book": ["book", "schedule", "reserve", "appointment"],
            "cancel": ["cancel", "delete", "remove"],
            "reschedule": ["reschedule", "change date", "change time", "move"],
            "modify": ["modify", "update", "change", "edit"],
            "check_status": ["status", "check", "track", "where is"]
        }

        for action, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return EntityExtractionResult(
                        entity_type=EntityType.ACTION.value,
                        entity_value=action,
                        confidence=0.9,
                        normalized_value=action,
                        extraction_method="pattern"
                    )

        return None
    
    def _extract_date(self, message: str, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract date using centralized normalizer"""
        from src.utils.entity_normalizer import normalize_date

        # Try to extract raw date value
        raw_value = None
        confidence = 0.0

        # Relative dates
        if message_lower in ["today", "now"]:
            raw_value = message
            confidence = 0.95
        elif message_lower in ["tomorrow", "tmrw", "tmr"]:
            raw_value = message
            confidence = 0.95
        elif "day after tomorrow" in message_lower:
            raw_value = message
            confidence = 0.9
        elif "next week" in message_lower:
            raw_value = message
            confidence = 0.8
        else:
            # ISO or DD/MM/YYYY format
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', message)
            if date_match:
                raw_value = date_match.group(0)
                confidence = 0.95
            else:
                date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', message)
                if date_match:
                    raw_value = date_match.group(0)
                    confidence = 0.9

        if raw_value:
            # Use centralized normalizer
            normalized = normalize_date(raw_value)
            if normalized:
                return EntityExtractionResult(
                    entity_type=EntityType.DATE.value,
                    entity_value=raw_value,
                    confidence=confidence,
                    normalized_value=normalized,
                    extraction_method="pattern"
                )

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
        """Extract booking ID"""
        # Pattern: BOOK-12345, BKG-12345, ORD-12345
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

        # Just numbers (4-6 digits) - lower confidence
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

    def _extract_service_type(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract service type"""
        service_keywords = {
            "ac": ["ac", "air conditioning", "hvac", "air conditioner", "cooling"],
            "plumbing": ["plumbing", "plumber", "pipe", "leak", "tap", "faucet", "drain"],
            "cleaning": ["cleaning", "clean", "house cleaning", "deep cleaning", "sanitization"],
            "electrical": ["electrical", "electrician", "wiring", "switch", "light", "power"],
            "painting": ["painting", "paint", "painter", "wall painting"],
            "appliance_repair": ["washing machine", "refrigerator", "fridge", "appliance", "microwave"],
        }

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

    def _extract_issue_type(self, message_lower: str) -> Optional[EntityExtractionResult]:
        """Extract issue type for complaints"""
        issue_keywords = {
            "quality": ["quality", "poor quality", "bad quality", "not satisfied", "unsatisfied"],
            "behavior": ["behavior", "behaviour", "rude", "unprofessional", "misbehave"],
            "damage": ["damage", "damaged", "broke", "broken", "destroyed"],
            "late": ["late", "delayed", "delay", "waiting", "not on time"],
            "no_show": ["no show", "didn't come", "didn't arrive", "not arrived", "missed"],
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

