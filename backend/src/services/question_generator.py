"""
Question Generator Service

Generates natural, context-aware questions for missing entities in slot-filling conversations.

Approach:
- LLM-generated questions for natural, context-aware phrasing
- Template fallback for edge cases or LLM failures
- Context-aware phrasing based on collected entities

Design Principles:
- User-friendly language
- Clear examples when helpful
- Reference previously collected information
- Conversational tone
"""

import logging
from typing import Dict, Any, Optional, List
from src.nlp.intent.config import EntityType, IntentType
from src.llm.gemini.client import LLMClient

logger = logging.getLogger(__name__)


# ============================================================
# QUESTION TEMPLATES (Core Slot-Filling)
# ============================================================

ENTITY_QUESTION_TEMPLATES = {
    EntityType.SERVICE_TYPE: {
        IntentType.BOOKING_MANAGEMENT: [
            "What type of service do you need? (e.g., AC repair, plumbing, cleaning, electrical)",
            "Which service would you like to book?",
            "What service are you looking for?"
        ],
        IntentType.PRICING_INQUIRY: [
            "Which service would you like to know the price for?",
            "What service pricing are you interested in?"
        ],
        IntentType.AVAILABILITY_CHECK: [
            "Which service are you checking availability for?",
            "What type of service do you need?"
        ],
    },
    EntityType.DATE: {
        IntentType.BOOKING_MANAGEMENT: [
            "What date would you like to schedule the service?",
            "When would you like us to come? (e.g., today, tomorrow, 2025-10-15)",
            "Which date works best for you?"
        ],
        IntentType.AVAILABILITY_CHECK: [
            "Which date are you checking availability for?",
            "What date are you interested in?"
        ],
    },
    EntityType.TIME: {
        IntentType.BOOKING_MANAGEMENT: [
            "What time works best for you? (e.g., 10 AM, 2 PM, evening)",
            "What time slot would you prefer?",
            "When during the day would you like the service?"
        ],
    },
    EntityType.LOCATION: {
        IntentType.BOOKING_MANAGEMENT: [
            "What's your location or pincode?",
            "Where do you need the service? (city or pincode)",
            "What's your address or pincode?"
        ],
        IntentType.PRICING_INQUIRY: [
            "Which area are you located in?",
            "What's your pincode? (pricing may vary by location)"
        ],
    },
    EntityType.BOOKING_ID: {
        IntentType.BOOKING_MANAGEMENT: [
            "What's your booking ID? (e.g., BOOK-12345)",
            "Could you provide your booking reference number?",
            "What's the booking ID you'd like to modify?"
        ],
    },
    EntityType.ISSUE_TYPE: {
        IntentType.COMPLAINT: [
            "What type of issue are you facing? (quality issue, technician behavior, damage, late arrival, no-show)",
            "Could you describe the problem you're experiencing?",
            "What went wrong with your service?"
        ],
    },
    EntityType.PAYMENT_TYPE: {
        IntentType.PAYMENT_ISSUE: [
            "What kind of payment issue are you experiencing? (failed payment, double charge, wrong amount)",
            "Could you describe the payment problem?",
            "What happened with your payment?"
        ],
    },
    EntityType.ACTION: {
        IntentType.BOOKING_MANAGEMENT: [
            "What would you like to do? (book, cancel, reschedule, modify)",
            "How can I help you with your booking?",
            "What action would you like to take?"
        ],
    },
}


# ============================================================
# CONFIRMATION TEMPLATES (High-Impact Actions)
# ============================================================

CONFIRMATION_TEMPLATES = {
    "booking_management": {
        "book": "Let me confirm: You want to book {service_type} servicing on {date} at {time} in {location}. Should I proceed with this booking?",
        "cancel": "You want to cancel booking {booking_id}. This action cannot be undone. Should I proceed with the cancellation?",
        "reschedule": "You want to reschedule booking {booking_id} to {date} at {time}. Should I proceed with this change?",
        "modify": "You want to modify booking {booking_id}. Should I proceed with this change?",
    },
    "complaint": "Let me confirm: You're filing a complaint about {issue_type} for booking {booking_id}. Should I proceed?",
    "payment_issue": "You're reporting a {payment_type} issue. Should I create a support ticket for this?",
    "refund_request": "You're requesting a refund for booking {booking_id}. Should I proceed with the refund request?",
}


class QuestionGenerator:
    """
    Generates questions for missing entities in slot-filling conversations

    Features:
    - LLM-generated questions (natural, context-aware)
    - Template fallback (for LLM failures)
    - Context-aware phrasing
    - Confirmation message generation
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client or LLMClient()
        self.templates = ENTITY_QUESTION_TEMPLATES  # Fallback templates
        self.confirmation_templates = CONFIRMATION_TEMPLATES
        self.question_count = {}  # Track question attempts per session
    
    def generate(
        self,
        entity_type: EntityType,
        intent: IntentType,
        collected_entities: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        attempt_number: int = 0
    ) -> str:
        """
        Generate question for missing entity using LLM

        Args:
            entity_type: Type of entity to ask for
            intent: Current intent
            collected_entities: Already collected entities (for context)
            context: Additional context (session_id, user preferences, etc.)
            attempt_number: Number of times we've asked for this entity (0-indexed)

        Returns:
            Question string
        """
        logger.info(f"[QuestionGenerator] Generating question for {entity_type.value}, intent: {intent.value}, attempt: {attempt_number}")

        # Try LLM-generated question first
        try:
            question = self._generate_llm_question(
                entity_type,
                intent,
                collected_entities,
                context,
                attempt_number
            )
            logger.info(f"[QuestionGenerator] LLM Generated: {question[:100]}...")
            return question
        except Exception as e:
            logger.warning(f"[QuestionGenerator] LLM generation failed: {e}, falling back to template")
            # Fallback to template
            question = self._get_template_question(entity_type, intent, attempt_number)

            # Add context if available
            if collected_entities:
                question = self._add_context_to_question(
                    question,
                    entity_type,
                    collected_entities
                )

            logger.info(f"[QuestionGenerator] Template Generated: {question[:100]}...")
            return question
    
    def _generate_llm_question(
        self,
        entity_type: EntityType,
        intent: IntentType,
        collected_entities: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        attempt_number: int = 0
    ) -> str:
        """
        Generate question using LLM for natural, context-aware phrasing
        """
        # Build context string
        context_str = ""
        if collected_entities:
            context_items = [f"{k}: {v}" for k, v in collected_entities.items()]
            context_str = f"\nAlready collected information: {', '.join(context_items)}"

        # Build prompt
        entity_name = entity_type.value.replace('_', ' ')
        intent_name = intent.value.replace('_', ' ')

        prompt = f"""You are Lisa, a friendly AI assistant helping users with home services.

Current conversation context:
- User intent: {intent_name}
- Missing information: {entity_name}{context_str}
- Attempt number: {attempt_number + 1}

Generate a natural, conversational question to ask the user for the {entity_name}.

Requirements:
1. Be friendly and conversational
2. Keep it concise (1-2 sentences max)
3. Include helpful examples if appropriate
4. Reference already collected information if relevant
5. If this is a retry (attempt > 0), rephrase differently
6. Do not use emojis
7. Do not add any extra text, just the question

Examples of good questions:
- "What's your location or pincode?"
- "Which date works best for you? (e.g., today, tomorrow, or a specific date)"
- "What time would you prefer? (e.g., 10 AM, 2 PM, evening)"

Generate the question:"""

        # Call LLM
        response = self.llm_client.invoke(prompt)
        question = response.strip()

        # Validate response
        if not question or len(question) > 200:
            raise ValueError(f"Invalid LLM response: {question}")

        return question

    def _get_template_question(
        self,
        entity_type: EntityType,
        intent: IntentType,
        attempt_number: int
    ) -> str:
        """
        Get template question from predefined templates (fallback)

        Uses attempt_number to vary phrasing (avoid repetition)
        """
        if entity_type in self.templates:
            intent_templates = self.templates[entity_type]

            if intent in intent_templates:
                templates = intent_templates[intent]
            else:
                # Fallback to first available template for this entity
                templates = list(intent_templates.values())[0]

            # Use attempt_number to cycle through variations
            if isinstance(templates, list):
                template_index = attempt_number % len(templates)
                return templates[template_index]
            else:
                return templates
        else:
            # Generic fallback
            entity_name = entity_type.value.replace('_', ' ')
            return f"Could you please provide the {entity_name}?"
    
    def _add_context_to_question(
        self,
        question: str,
        entity_type: EntityType,
        collected_entities: Dict[str, Any]
    ) -> str:
        """
        Add context from collected entities to make question more natural
        
        Examples:
        - If service_type="AC" collected, asking for date:
          "What date would you like to schedule the AC service?"
        - If date="2025-10-10" collected, asking for time:
          "What time works best for you on October 10th?"
        """
        # Add service type to question if available
        if "service_type" in collected_entities and entity_type != EntityType.SERVICE_TYPE:
            service = collected_entities["service_type"]
            question = question.replace("the service", f"the {service} service")
            question = question.replace("your service", f"your {service} service")
        
        # Add date context when asking for time
        if entity_type == EntityType.TIME and "date" in collected_entities:
            date_str = collected_entities["date"]
            # Simple date formatting (can be enhanced)
            question = question.replace("?", f" on {date_str}?")
        
        # Add location context when asking for date/time
        if entity_type in [EntityType.DATE, EntityType.TIME] and "location" in collected_entities:
            location = collected_entities["location"]
            if "?" in question:
                question = question.replace("?", f" in {location}?")
        
        return question
    
    def generate_confirmation(
        self,
        intent: IntentType,
        collected_entities: Dict[str, Any]
    ) -> str:
        """
        Generate confirmation message with all collected entities
        
        Used for high-impact actions (bookings, cancellations, refunds, payments)
        
        Args:
            intent: Current intent
            collected_entities: All collected entities
            
        Returns:
            Confirmation message string
        """
        logger.info(f"[QuestionGenerator] Generating confirmation for {intent.value}")
        
        intent_str = intent.value
        
        # Get confirmation template
        if intent_str in self.confirmation_templates:
            template_config = self.confirmation_templates[intent_str]
            
            # For booking_management, select template based on action
            if intent_str == "booking_management":
                action = collected_entities.get("action", "book")
                template = template_config.get(action, template_config["book"])
            else:
                template = template_config
            
            # Format template with collected entities
            try:
                confirmation = template.format(**collected_entities)
            except KeyError as e:
                logger.warning(f"[QuestionGenerator] Missing entity in template: {e}")
                # Fallback to generic confirmation
                confirmation = self._generate_generic_confirmation(intent, collected_entities)
        else:
            # Generic confirmation
            confirmation = self._generate_generic_confirmation(intent, collected_entities)
        
        logger.info(f"[QuestionGenerator] Confirmation: {confirmation[:100]}...")
        return confirmation
    
    def _generate_generic_confirmation(
        self,
        intent: IntentType,
        collected_entities: Dict[str, Any]
    ) -> str:
        """
        Generate generic confirmation when no template available
        """
        entities_str = ", ".join([f"{k}: {v}" for k, v in collected_entities.items()])
        return f"Let me confirm these details: {entities_str}. Should I proceed?"
    
    def generate_validation_error_message(
        self,
        entity_type: EntityType,
        error_message: str,
        suggestions: Optional[List[str]] = None
    ) -> str:
        """
        Generate user-friendly error message for validation failures
        
        Args:
            entity_type: Entity that failed validation
            error_message: Technical error message
            suggestions: Suggested valid values
            
        Returns:
            User-friendly error message
        """
        entity_name = entity_type.value.replace('_', ' ')
        
        message = f"Sorry, {error_message}."
        
        if suggestions:
            suggestions_str = ", ".join(suggestions[:3])  # Limit to 3 suggestions
            message += f" Here are some suggestions: {suggestions_str}."
        
        message += f" Could you please provide a valid {entity_name}?"
        
        return message
    
    def should_escalate(
        self,
        session_id: str,
        entity_type: EntityType,
        attempt_count: int,
        max_attempts: int = 3
    ) -> bool:
        """
        Determine if we should escalate (stop asking, offer alternative)
        
        Args:
            session_id: Session ID
            entity_type: Entity we're asking for
            attempt_count: Number of attempts so far
            max_attempts: Maximum attempts before escalation
            
        Returns:
            True if should escalate, False otherwise
        """
        return attempt_count >= max_attempts
    
    def generate_escalation_message(
        self,
        entity_type: EntityType,
        intent: IntentType
    ) -> str:
        """
        Generate message when escalating (too many failed attempts)
        
        Offers alternative UX (e.g., "Would you like to speak with a human agent?")
        """
        entity_name = entity_type.value.replace('_', ' ')
        
        return (
            f"I'm having trouble understanding the {entity_name}. "
            "Would you like to:\n"
            "1. Try again with a different format\n"
            "2. Skip this for now and continue\n"
            "3. Speak with a human agent"
        )

