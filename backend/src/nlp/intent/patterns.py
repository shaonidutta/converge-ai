"""
Intent Pattern Matching

Quick pattern-based intent classification using keywords and regex.
This is the first step in the hybrid classification approach.
"""

import re
from typing import Dict, List, Tuple, Optional
from .config import IntentType, EntityType


class IntentPatterns:
    """Pattern-based intent classification for quick matching"""
    
    # Keyword patterns for each intent (lowercase)
    INTENT_KEYWORDS: Dict[IntentType, List[str]] = {
        IntentType.BOOKING_MANAGEMENT: [
            "book", "schedule", "appointment", "reserve", "arrange",
            "cancel", "reschedule", "modify", "change booking",
            "cancel booking", "cancel appointment", "cancel service"
        ],
        IntentType.PRICING_INQUIRY: [
            "price", "cost", "charge", "rate", "fee", "how much",
            "what's the price", "what is the cost", "pricing",
            "charges", "rates", "fees"
        ],
        IntentType.AVAILABILITY_CHECK: [
            "available", "availability", "when can", "free slot",
            "available slot", "available time", "check availability",
            "are you available", "do you have"
        ],
        IntentType.SERVICE_INFORMATION: [
            "what is", "tell me about", "information about", "details about",
            "how does", "what does", "explain", "describe",
            "service details", "service information", "what's included",
            "help with services", "services you offer", "what services",
            "available services", "service options", "types of services",
            "can you help with", "help me with services",
            "suggest", "recommend", "recommendation", "suggestions",
            "can you suggest", "can u suggest", "suggest me", "recommend me",
            "what do you recommend", "what would you suggest", "any suggestions",
            "which service", "what should i", "help me choose"
        ],
        IntentType.COMPLAINT: [
            "complaint", "complain", "issue", "problem", "not satisfied",
            "poor service", "bad service", "unhappy", "disappointed",
            "technician was rude", "damage", "broken", "not working"
        ],
        IntentType.PAYMENT_ISSUE: [
            "payment failed", "payment not working", "payment issue",
            "charged twice", "double charged", "wrong amount",
            "overcharged", "payment problem", "payment error",
            "transaction failed", "payment declined"
        ],
        IntentType.REFUND_REQUEST: [
            "refund", "money back", "return money", "get refund",
            "refund request", "want refund", "need refund",
            "refund status", "refund to wallet"
        ],
        IntentType.ACCOUNT_MANAGEMENT: [
            "update profile", "change phone", "change email",
            "update address", "manage account", "account settings",
            "delete account", "update details"
        ],
        IntentType.TRACK_SERVICE: [
            "track", "where is", "technician location", "eta",
            "when will arrive", "track technician", "service status",
            "track booking", "where is technician"
        ],
        IntentType.FEEDBACK: [
            "feedback", "review", "rating", "rate service",
            "write review", "give feedback", "compliment",
            "good service", "excellent service"
        ],
        IntentType.POLICY_INQUIRY: [
            "policy", "terms", "conditions", "cancellation policy",
            "refund policy", "warranty", "guarantee", "privacy policy",
            "terms and conditions"
        ],
        IntentType.GREETING: [
            "hello", "hi", "hey", "good morning", "good afternoon",
            "good evening", "greetings", "namaste", "hola"
        ],
    }
    
    # Regex patterns for specific intents
    REGEX_PATTERNS: Dict[IntentType, List[str]] = {
        IntentType.BOOKING_MANAGEMENT: [
            r"\b(book|schedule|cancel|reschedule)\s+(a|an|my)?\s*(service|appointment|booking)",
            r"\b(want|need)\s+to\s+(book|cancel|reschedule)",
            r"\bcancel\s+my\s+(booking|appointment|service)",
        ],
        IntentType.PRICING_INQUIRY: [
            r"\bhow\s+much\s+(does|is|for|to)",
            r"\bwhat('s| is)\s+the\s+(price|cost|charge|rate)",
            r"\b(price|cost|charge)\s+(for|of)",
        ],
        IntentType.REFUND_REQUEST: [
            r"\b(want|need|request)\s+(a|my)?\s*refund",
            r"\brefund\s+(request|status|to wallet)",
            r"\bget\s+my\s+money\s+back",
        ],
        IntentType.COMPLAINT: [
            r"\b(complaint|complain|issue|problem)\s+(about|with)",
            r"\b(poor|bad|terrible)\s+service",
            r"\btechnician\s+(was|is)\s+(rude|late|unprofessional)",
        ],
    }
    
    @classmethod
    def match_intent(cls, message: str) -> List[Tuple[IntentType, float]]:
        """
        Match intents using keyword and regex patterns
        
        Args:
            message: User message (will be lowercased)
            
        Returns:
            List of (intent, confidence) tuples sorted by confidence
        """
        message_lower = message.lower()
        intent_scores: Dict[IntentType, float] = {}
        
        # 1. Keyword matching
        for intent, keywords in cls.INTENT_KEYWORDS.items():
            score = 0.0
            matched_keywords = 0
            
            for keyword in keywords:
                if keyword in message_lower:
                    matched_keywords += 1
                    # Exact phrase match gets higher score
                    if f" {keyword} " in f" {message_lower} ":
                        score += 0.3
                    else:
                        score += 0.2
            
            if matched_keywords > 0:
                # Normalize score (cap at 0.95 for pattern matching)
                intent_scores[intent] = min(0.95, score)
        
        # 2. Regex matching (higher confidence)
        for intent, patterns in cls.REGEX_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    # Regex match gets higher confidence
                    current_score = intent_scores.get(intent, 0.0)
                    intent_scores[intent] = max(current_score, 0.95)
                    break
        
        # 3. Sort by confidence and return
        sorted_intents = sorted(
            intent_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_intents
    
    @classmethod
    def extract_entities_from_patterns(cls, message: str) -> Dict[str, str]:
        """
        Extract entities using pattern matching with centralized normalization

        Args:
            message: User message

        Returns:
            Dictionary of entity_type (string) -> normalized entity_value (string)
        """
        from src.utils.entity_normalizer import (
            normalize_date, normalize_time, normalize_location,
            normalize_service_type, normalize_action
        )

        message_lower = message.lower()
        raw_entities: Dict[str, str] = {}

        # Extract service types (raw extraction)
        service_keywords = {
            "ac": ["ac", "air conditioning", "hvac", "air conditioner"],
            "plumbing": ["plumbing", "plumber", "pipe", "leak", "tap", "faucet"],
            "cleaning": ["cleaning", "clean", "house cleaning", "deep cleaning"],
            "electrical": ["electrical", "electrician", "wiring", "switch", "light"],
            "painting": ["painting", "paint", "painter"],
            "appliance_repair": ["washing machine", "refrigerator", "fridge", "appliance"],
        }

        for service_type, keywords in service_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    raw_entities[EntityType.SERVICE_TYPE.value] = service_type
                    break
            if EntityType.SERVICE_TYPE.value in raw_entities:
                break

        # Extract actions (raw extraction)
        # Check for intent phrases first (higher priority)
        if re.search(r'\b(i want to|i need to|i would like to|i\'d like to)\s+(book|schedule|arrange)', message_lower):
            raw_entities[EntityType.ACTION.value] = "book"
        elif re.search(r'\b(i want|i need|i would like|i\'d like)\b', message_lower):
            # If followed by service type, assume booking intent
            if any(keyword in message_lower for keywords in [
                ["ac", "air conditioning", "hvac"],
                ["plumbing", "plumber"],
                ["cleaning", "clean"],
                ["electrical", "electrician"],
                ["painting", "paint"],
                ["appliance", "washing machine", "refrigerator"]
            ] for keyword in keywords):
                raw_entities[EntityType.ACTION.value] = "book"

        # If not found, check action keywords
        if EntityType.ACTION.value not in raw_entities:
            action_keywords = {
                "cancel": ["cancel", "remove", "delete"],
                "reschedule": ["reschedule", "change date", "move"],
                "modify": ["modify", "update", "edit"],
                "book": ["book", "schedule", "arrange", "set up"],
            }

            for action, keywords in action_keywords.items():
                for keyword in keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, message_lower):
                        raw_entities[EntityType.ACTION.value] = action
                        break
                if EntityType.ACTION.value in raw_entities:
                    break

        # Extract DATE (raw extraction - will be normalized)
        if "today" in message_lower or " now" in message_lower:
            raw_entities[EntityType.DATE.value] = "today"
        elif "tomorrow" in message_lower or "tmrw" in message_lower or "tmr" in message_lower:
            raw_entities[EntityType.DATE.value] = "tomorrow"
        elif "day after tomorrow" in message_lower:
            raw_entities[EntityType.DATE.value] = "day after tomorrow"
        elif "next week" in message_lower:
            raw_entities[EntityType.DATE.value] = "next week"
        else:
            # ISO or DD/MM/YYYY format
            date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', message)
            if date_match:
                raw_entities[EntityType.DATE.value] = date_match.group(0)
            else:
                date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', message)
                if date_match:
                    raw_entities[EntityType.DATE.value] = date_match.group(0)

        # Extract TIME (raw extraction - will be normalized)
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|a\.m\.|p\.m\.)', message_lower)
        if time_match:
            raw_entities[EntityType.TIME.value] = time_match.group(0)
        else:
            time_match = re.search(r'(\d{1,2}):(\d{2})', message)
            if time_match:
                raw_entities[EntityType.TIME.value] = time_match.group(0)
            elif "morning" in message_lower:
                raw_entities[EntityType.TIME.value] = "morning"
            elif "afternoon" in message_lower:
                raw_entities[EntityType.TIME.value] = "afternoon"
            elif "evening" in message_lower:
                raw_entities[EntityType.TIME.value] = "evening"
            elif "night" in message_lower:
                raw_entities[EntityType.TIME.value] = "night"

        # Extract LOCATION (raw extraction - will be normalized)
        if ',' in message:
            full_address_pattern = r'.+,\s*.+,\s*.+,?\s*\d{6}'
            if re.search(full_address_pattern, message):
                raw_entities[EntityType.LOCATION.value] = message.strip()
            else:
                city_pincode_pattern = r'[a-zA-Z\s]+,\s*\d{6}'
                city_pincode_match = re.search(city_pincode_pattern, message)
                if city_pincode_match:
                    raw_entities[EntityType.LOCATION.value] = city_pincode_match.group(0).strip()

        if EntityType.LOCATION.value not in raw_entities:
            pincode_match = re.search(r'\b(\d{6})\b', message)
            if pincode_match:
                raw_entities[EntityType.LOCATION.value] = pincode_match.group(1)

        if EntityType.LOCATION.value not in raw_entities:
            cities = [
                "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
                "kolkata", "pune", "ahmedabad", "jaipur", "surat", "lucknow",
                "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam",
                "pimpri", "patna", "vadodara", "ghaziabad", "ludhiana", "agra"
            ]
            for city in cities:
                if city in message_lower:
                    raw_entities[EntityType.LOCATION.value] = city.title()
                    break

        # Extract issue types (no normalization needed)
        issue_keywords = {
            "quality": ["poor quality", "bad service", "not satisfied"],
            "behavior": ["rude", "unprofessional", "behavior"],
            "damage": ["damage", "broken", "damaged"],
            "late": ["late", "delayed", "not on time"],
            "no_show": ["no show", "didn't come", "missed"],
        }

        for issue_type, keywords in issue_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    raw_entities[EntityType.ISSUE_TYPE.value] = issue_type
                    break
            if EntityType.ISSUE_TYPE.value in raw_entities:
                break

        # Extract payment issues (no normalization needed)
        payment_keywords = {
            "failed": ["failed", "declined", "not working"],
            "double_charged": ["double charged", "charged twice"],
            "wrong_amount": ["wrong amount", "overcharged", "incorrect"],
        }

        for payment_type, keywords in payment_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    raw_entities[EntityType.PAYMENT_TYPE.value] = payment_type
                    break
            if EntityType.PAYMENT_TYPE.value in raw_entities:
                break

        # Extract booking ID (no normalization needed)
        # Support multiple booking ID formats:
        # - BK66A80A35 (BK + 8 alphanumeric characters) - ACTUAL FORMAT
        # - BK123456, BK-123456, BK_123456 (BK + 6 digits)
        # - BOOK12345, BOOK-12345, BOOK_12345
        # - BKG12345, BKG-12345, BKG_12345
        # - ORD12345, ORD-12345, ORD_12345
        # - #123456
        booking_id_patterns = [
            r"\bBK[A-Z0-9]{8}\b",  # BK66A80A35 (BK + 8 alphanumeric) - PRIMARY FORMAT
            r"\b(BK)[-_]?(\d{6})\b",  # BK123456, BK-123456, BK_123456
            r"\b(BOOK)[-_]?([A-Z0-9]{4,8})\b",  # BOOK12345, BOOK-12345
            r"\b(BKG)[-_]?([A-Z0-9]{4,8})\b",  # BKG12345, BKG-12345
            r"\b(ORD)[-_]?([A-Z0-9]{4,8})\b",  # ORD12345, ORD-12345
            r"#([A-Z0-9]{6,8})\b",  # #123456, #66A80A35
        ]

        for pattern in booking_id_patterns:
            booking_match = re.search(pattern, message, re.IGNORECASE)
            if booking_match:
                raw_entities[EntityType.BOOKING_ID.value] = booking_match.group(0).upper()
                break

        # Normalize all extracted entities using centralized normalizer
        normalized_entities: Dict[str, str] = {}

        for entity_type, raw_value in raw_entities.items():
            if entity_type == EntityType.DATE.value:
                normalized = normalize_date(raw_value)
                if normalized:
                    normalized_entities[entity_type] = normalized
            elif entity_type == EntityType.TIME.value:
                normalized = normalize_time(raw_value)
                if normalized:
                    normalized_entities[entity_type] = normalized
            elif entity_type == EntityType.LOCATION.value:
                normalized = normalize_location(raw_value)
                if normalized:
                    normalized_entities[entity_type] = normalized
            elif entity_type == EntityType.SERVICE_TYPE.value:
                normalized = normalize_service_type(raw_value)
                if normalized:
                    normalized_entities[entity_type] = normalized
            elif entity_type == EntityType.ACTION.value:
                normalized = normalize_action(raw_value)
                if normalized:
                    normalized_entities[entity_type] = normalized
            else:
                # Keep other entities as-is (issue_type, payment_type, booking_id)
                normalized_entities[entity_type] = raw_value

        return normalized_entities

