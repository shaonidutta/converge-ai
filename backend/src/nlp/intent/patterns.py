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
            "service details", "service information", "what's included"
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
    def extract_entities_from_patterns(cls, message: str) -> Dict[EntityType, str]:
        """
        Extract entities using pattern matching
        
        Args:
            message: User message
            
        Returns:
            Dictionary of entity_type -> entity_value
        """
        message_lower = message.lower()
        entities: Dict[EntityType, str] = {}
        
        # Extract service types
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
                    entities[EntityType.SERVICE_TYPE] = service_type
                    break
            if EntityType.SERVICE_TYPE in entities:
                break
        
        # Extract actions
        action_keywords = {
            "book": ["book", "schedule", "arrange", "set up"],
            "cancel": ["cancel", "remove", "delete"],
            "reschedule": ["reschedule", "change date", "move"],
            "modify": ["modify", "update", "edit"],
        }
        
        for action, keywords in action_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    entities[EntityType.ACTION] = action
                    break
            if EntityType.ACTION in entities:
                break
        
        # Extract issue types
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
                    entities[EntityType.ISSUE_TYPE] = issue_type
                    break
            if EntityType.ISSUE_TYPE in entities:
                break
        
        # Extract payment issues
        payment_keywords = {
            "failed": ["failed", "declined", "not working"],
            "double_charged": ["double charged", "charged twice"],
            "wrong_amount": ["wrong amount", "overcharged", "incorrect"],
        }
        
        for payment_type, keywords in payment_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    entities[EntityType.PAYMENT_TYPE] = payment_type
                    break
            if EntityType.PAYMENT_TYPE in entities:
                break
        
        # Extract booking ID (pattern: BOOK-XXXXX or similar)
        booking_id_pattern = r"\b(BOOK|BKG|ORD)[-_]?(\d{4,6})\b"
        booking_match = re.search(booking_id_pattern, message, re.IGNORECASE)
        if booking_match:
            entities[EntityType.BOOKING_ID] = booking_match.group(0)
        
        return entities

