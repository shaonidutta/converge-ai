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
            "cancel booking", "cancel appointment", "cancel service",
            "list bookings", "show bookings", "view bookings", "my bookings",
            "all bookings", "check bookings", "see bookings"
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
            "which service", "what should i", "help me choose",
            "what services do you", "what services do u", "services do you give",
            "services do u give", "what services you give", "what services u give",
            "what do you offer", "what do u offer", "what can you do",
            # Subcategory-specific patterns
            "subcategories", "sub-categories", "subcategories for", "sub-categories for",
            "types of", "options for", "what types", "show me options",
            "categories", "service categories", "all categories"
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
            r"\b(list|show|view|display|see|get|check)\s+(my|all)?\s*(bookings?|appointments?)",
            r"\b(can|could)\s+(you|u)\s+(list|show|view|check)\s+(my)?\s*(bookings?|appointments?)",
            r"\bmy\s+(bookings?|appointments?)",
        ],
        IntentType.SERVICE_INFORMATION: [
            r"\bwhat\s+services\s+(do|does|can)\s+(you|u|ya)",
            r"\bservices\s+(do|does)\s+(you|u)\s+(give|offer|provide|have)",
            r"\bwhat\s+(do|can)\s+(you|u)\s+(offer|provide|do|help)",
            r"\bwhat\s+services",
            r"\btell\s+me\s+about\s+(your\s+)?services",
            # Subcategory-specific regex patterns
            r"\b(subcategories|sub-categories)\s+for\s+[\w\s]+",
            r"\bwhat\s+[\w\s]+\s+(services|options)\s+do\s+you\s+have",
            r"\bshow\s+me\s+[\w\s]+\s+(services|options|subcategories)",
            r"\btypes?\s+of\s+[\w\s]+\s+services?",
            r"\blist\s+[\w\s]+\s+(services|options)",
            r"\b[\w\s]+\s+(subcategories|sub-categories)",
            r"\bwhat\s+categories\s+do\s+you\s+have",
            r"\bshow\s+me\s+all\s+(service\s+)?categories",
            r"\blist\s+all\s+categories"
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
        IntentType.POLICY_INQUIRY: [
            r"\b(what|tell|explain)\s+(is|are|me|about)?\s*(your|the)?\s*(cancellation|refund|warranty|privacy|return)\s+policy",
            r"\bpolicy\s+(on|for|about)\s+(cancellation|refund|warranty|returns)",
            r"\b(cancellation|refund|warranty|privacy)\s+(policy|terms|conditions)",
            r"\bterms\s+(and|&)?\s*conditions",
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
            "pest_control": ["pest control", "pest", "pest service", "general pest control", "pest control service", "exterminator", "fumigation"],
            "carpentry": ["carpentry", "carpenter", "furniture", "wood work", "cabinet", "door repair"],
            "water_purifier": ["water purifier", "ro", "water filter", "purifier", "water treatment"],
            "car_care": ["car care", "car wash", "car cleaning", "car service", "vehicle cleaning"],
            "salon_for_women": ["salon", "beauty salon", "women salon", "ladies salon", "beauty parlor"],
            "salon_for_men": ["men salon", "barber", "gents salon", "male grooming"],
            "packers_and_movers": ["packers", "movers", "packing", "moving", "relocation", "shifting"]
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
                ["appliance", "washing machine", "refrigerator"],
                ["pest control", "pest", "pest service", "exterminator"],
                ["carpentry", "carpenter", "furniture"],
                ["water purifier", "ro", "water filter"],
                ["car care", "car wash", "car cleaning"],
                ["salon", "beauty salon", "barber"],
                ["packers", "movers", "packing", "moving", "relocation"]
            ] for keyword in keywords):
                raw_entities[EntityType.ACTION.value] = "book"

        # If not found, check action keywords
        # IMPORTANT: Check specific action keywords FIRST (cancel, reschedule, modify, book)
        # before checking "list" patterns to avoid false matches
        if EntityType.ACTION.value not in raw_entities:
            action_keywords = {
                "cancel": ["cancel", "remove", "delete"],
                "reschedule": ["reschedule", "change date", "move booking", "move appointment"],
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

            # Only check for "list" action if no other action was found
            # List patterns should ONLY match when there's an explicit list/show/view action word
            if EntityType.ACTION.value not in raw_entities:
                list_patterns = [
                    r'\b(list|show|view|display)\s+(my|all|them)?\s*(bookings?|appointments?)?',  # "list my bookings", "show bookings"
                    r'\b(check|see|get)\s+my\s+(bookings?|appointments?)',  # "check my bookings"
                    r'(bookings?|appointments?).*\b(list|show|view|display)',  # "bookings and list them"
                ]

                for pattern in list_patterns:
                    if re.search(pattern, message_lower):
                        raw_entities[EntityType.ACTION.value] = "list"
                        break

        # Extract STATUS_FILTER (for list action)
        # Check for status keywords in queries like "show my pending bookings"
        if raw_entities.get(EntityType.ACTION.value) == "list":
            status_keywords = {
                "pending": ["pending", "upcoming", "scheduled", "active"],
                "confirmed": ["confirmed", "approved"],
                "completed": ["completed", "finished", "done", "past"],
                "cancelled": ["cancelled", "canceled", "deleted", "removed"]
            }

            # Check for status keywords appearing before "bookings" or "appointments"
            # Pattern: "show my [status] bookings"
            status_pattern = r'\b(' + '|'.join([kw for keywords in status_keywords.values() for kw in keywords]) + r')\s+(bookings?|appointments?)'
            status_match = re.search(status_pattern, message_lower)

            if status_match:
                status_word = status_match.group(1)
                # Find which status this keyword belongs to
                for status, keywords in status_keywords.items():
                    if status_word in keywords:
                        raw_entities[EntityType.STATUS_FILTER.value] = status
                        break
            else:
                # Fallback: check for status keywords anywhere in the message
                for status, keywords in status_keywords.items():
                    for keyword in keywords:
                        if keyword in message_lower:
                            raw_entities[EntityType.STATUS_FILTER.value] = status
                            break
                    if EntityType.STATUS_FILTER.value in raw_entities:
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

        # Extract order ID (no normalization needed)
        # Support order ID format:
        # - ORD12345678 (ORD + 8 alphanumeric characters) - PRIMARY FORMAT
        # - ORD123456, ORD-123456, ORD_123456 (ORD + 6+ digits)
        # - ORDER12345, ORDER-12345, ORDER_12345
        # - #123456
        booking_id_patterns = [
            r"\bORD[A-Z0-9]{8}\b",  # ORD12345678 (ORD + 8 alphanumeric) - PRIMARY FORMAT
            r"\b(ORD)[-_]?([A-Z0-9]{6,8})\b",  # ORD123456, ORD-123456, ORD_123456
            r"\b(ORDER)[-_]?([A-Z0-9]{4,8})\b",  # ORDER12345, ORDER-12345
            r"#([A-Z0-9]{6,8})\b",  # #123456, #12345678
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

