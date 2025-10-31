"""
Multi-Intent Classifier

Hybrid approach for intent classification:
1. Quick pattern matching (regex/keywords) for high-confidence cases
2. LLM-based classification for ambiguous cases
3. Fallback handling for unclear intents
"""

import json
import logging
import re
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from datetime import datetime, timezone

from .config import (
    IntentType,
    ClassificationThresholds,
    INTENT_CONFIGS
)
from .patterns import IntentPatterns
from src.llm.gemini.client import LLMClient

if TYPE_CHECKING:
    from src.schemas.intent import IntentResult, IntentClassificationResult
    from src.core.models import DialogState

logger = logging.getLogger(__name__)


class IntentClassifier:
    """
    Multi-intent classifier using hybrid approach.
    
    Detects and returns ALL intents present in a user query,
    not just the primary intent.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize intent classifier
        
        Args:
            llm_client: LLM client for classification (if None, will create one)
        """
        self.llm_client = llm_client or LLMClient.create_for_intent_classification()
        self.pattern_matcher = IntentPatterns()
        self.thresholds = ClassificationThresholds()
    
    async def classify(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        dialog_state: Optional["DialogState"] = None
    ) -> Tuple["IntentClassificationResult", str]:
        """
        Classify user message and detect all intents (context-aware)

        Args:
            message: User message to classify
            conversation_history: Optional list of previous messages
                Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            dialog_state: Optional active dialog state for additional context

        Returns:
            Tuple of (IntentClassificationResult, classification_method)
            classification_method: "pattern_match", "llm", "context_aware_llm", or "fallback"
        """
        from src.schemas.intent import IntentClassificationResult

        logger.info(f"Classifying message: {message[:100]}...")

        # Log context availability
        has_context = conversation_history or dialog_state
        if has_context:
            logger.info(f"Context available - History: {len(conversation_history) if conversation_history else 0} messages, Dialog State: {dialog_state.state.value if dialog_state else None}")
        
        # Step 1: Try pattern matching (fast path)
        pattern_results = self.pattern_matcher.match_intent(message)

        if pattern_results:
            # Check if we have high-confidence pattern matches
            high_confidence_intents = [
                (intent, confidence)
                for intent, confidence in pattern_results
                if confidence >= self.thresholds.PATTERN_MATCH_THRESHOLD
            ]

            # Only use pattern matching if there's a single clear intent
            # For potential multi-intent queries, pass to LLM
            if high_confidence_intents and len(high_confidence_intents) == 1:
                # Check if message might contain multiple intents (has "and", "also", etc.)
                # Exclude "day after tomorrow" from triggering multi-intent detection
                message_lower = message.lower()
                multi_intent_keywords = [' and ', ' also ', ' plus ', ' then ', ' after that ', ' and then ']
                has_multi_intent_signal = any(keyword in message_lower for keyword in multi_intent_keywords)

                # Special case: "day after tomorrow" should NOT trigger multi-intent
                if " after " in message_lower and "day after tomorrow" not in message_lower:
                    has_multi_intent_signal = True

                if not has_multi_intent_signal:
                    # IMPORTANT: Pattern matching takes precedence even when dialog_state is present
                    # This ensures that explicit questions like "what services do you give?" are
                    # correctly classified even during slot-filling
                    logger.info(f"High-confidence single intent pattern match: {high_confidence_intents}")
                    result = self._build_result_from_patterns(message, high_confidence_intents)

                    # If there's a dialog state and the matched intent is different, log it
                    if dialog_state is not None and dialog_state.intent is not None and str(dialog_state.intent) != high_confidence_intents[0][0].value:
                        logger.info(f"Pattern match overriding dialog state intent: {dialog_state.intent} → {high_confidence_intents[0][0].value}")

                    return result, "pattern_match"
                else:
                    logger.info(f"Multi-intent signal detected, passing to LLM: {message[:50]}...")
        
        # Step 2: Use LLM for classification (ambiguous cases)
        # Use context-aware classification if context is available
        classification_method = "context_aware_llm" if has_context else "llm"
        logger.info(f"Using LLM for classification (method: {classification_method})")

        try:
            llm_result = await self._classify_with_llm(
                message,
                conversation_history=conversation_history,
                dialog_state=dialog_state
            )

            # Check if LLM classification has sufficient confidence
            if llm_result.intents and llm_result.intents[0].confidence >= self.thresholds.LLM_CLASSIFICATION_THRESHOLD:
                logger.info(f"LLM classification successful: {llm_result.primary_intent}")
                return llm_result, classification_method
            
            # If confidence is low, mark as requiring clarification
            if llm_result.intents and llm_result.intents[0].confidence < self.thresholds.CLARIFICATION_THRESHOLD:
                llm_result.requires_clarification = True
                llm_result.clarification_reason = "Low confidence in intent classification"
                return llm_result, classification_method

            return llm_result, classification_method
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # Fall through to fallback
        
        # Step 3: Fallback - mark as unclear
        logger.warning("Falling back to unclear_intent")
        fallback_result = self._build_fallback_result(message)
        return fallback_result, "fallback"
    
    def _build_result_from_patterns(
        self,
        message: str,
        pattern_matches: List[Tuple[IntentType, float]]
    ) -> "IntentClassificationResult":
        """
        Build classification result from pattern matches

        Args:
            message: User message
            pattern_matches: List of (intent, confidence) tuples

        Returns:
            IntentClassificationResult
        """
        from src.schemas.intent import IntentResult, IntentClassificationResult

        # Extract entities using pattern matching
        entities = self.pattern_matcher.extract_entities_from_patterns(message)

        # Build intent results
        import json
        intent_results = []
        for intent, confidence in pattern_matches[:self.thresholds.MAX_INTENTS]:
            # Filter entities relevant to this intent
            relevant_entities = self._filter_entities_for_intent(intent, entities)

            intent_results.append(
                IntentResult(
                    intent=intent.value,
                    confidence=confidence,
                    entities_json=json.dumps(relevant_entities) if relevant_entities else None
                )
            )
        
        # Primary intent is the one with highest confidence
        primary_intent = pattern_matches[0][0].value
        
        return IntentClassificationResult(
            intents=intent_results,
            primary_intent=primary_intent,
            requires_clarification=False,
            clarification_reason=None
        )
    
    async def _classify_with_llm(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        dialog_state: Optional["DialogState"] = None
    ) -> "IntentClassificationResult":
        """
        Classify using LLM with structured output (context-aware)

        Args:
            message: User message
            conversation_history: Optional conversation history
            dialog_state: Optional dialog state

        Returns:
            IntentClassificationResult
        """
        from src.schemas.intent import IntentClassificationResult

        # Import prompts here to avoid circular import
        from src.llm.gemini.prompts import (
            build_intent_classification_prompt,
            build_context_aware_intent_prompt
        )

        # Build prompt (context-aware if context available)
        if conversation_history or dialog_state:
            prompt = build_context_aware_intent_prompt(
                message,
                conversation_history=conversation_history,
                dialog_state=dialog_state
            )
            logger.info("Using context-aware prompt for classification")
        else:
            prompt = build_intent_classification_prompt(message)
            logger.info("Using standard prompt for classification")

        # Get structured output from LLM
        structured_llm = self.llm_client.with_structured_output(IntentClassificationResult)  # type: ignore

        # Invoke LLM with retry logic
        from src.nlp.llm.gemini_client import with_retry

        @with_retry(max_retries=3, initial_delay=1.0, backoff_factor=2.0)
        def invoke_with_retry():
            return structured_llm.invoke(prompt)

        result = invoke_with_retry()

        # Normalize entities extracted by LLM (pass original message for fallback extraction)
        result = self._normalize_llm_entities(result, original_message=message)

        # Validate and filter intents
        result = self._validate_and_filter_intents(result)

        # Add context metadata
        if conversation_history or dialog_state:
            result.context_used = True
            result.context_summary = self._build_context_summary(conversation_history, dialog_state)

        return result

    def _normalize_llm_entities(
        self,
        result: "IntentClassificationResult",
        original_message: Optional[str] = None
    ) -> "IntentClassificationResult":
        """
        Normalize entities extracted by LLM using centralized normalizer
        Also adds fallback action extraction if LLM missed it

        Args:
            result: Classification result with raw entities from LLM
            original_message: Original user message for fallback extraction

        Returns:
            Result with normalized entities
        """
        from src.utils.entity_normalizer import normalize_entities
        import json

        for intent_result in result.intents:
            entities = intent_result.entities
            if not entities:
                continue

            # Use centralized normalizer
            normalized_entities = normalize_entities(entities)

            # For booking_management intent, always check pattern-based action extraction
            # This ensures we catch "list" actions that LLM might miss or misclassify
            if intent_result.intent == "booking_management" and original_message:
                pattern_action = self._extract_action_fallback(original_message)

                # If pattern extraction found an action, use it
                # Pattern extraction is more reliable for specific actions like "list"
                if pattern_action:
                    # If LLM extracted a different action, log it but prefer pattern match
                    if "action" in normalized_entities and normalized_entities["action"] != pattern_action:
                        logger.info(f"[_normalize_llm_entities] Overriding LLM action '{normalized_entities['action']}' with pattern-based action '{pattern_action}'")
                    normalized_entities["action"] = pattern_action
                    logger.info(f"[_normalize_llm_entities] Pattern extracted action: {pattern_action}")
                # If pattern extraction found nothing and LLM also found nothing, that's fine
                elif "action" not in normalized_entities:
                    logger.info(f"[_normalize_llm_entities] No action found by pattern or LLM")

            # Update entities with normalized values
            if normalized_entities:
                intent_result.entities_json = json.dumps(normalized_entities)
                logger.info(f"[_normalize_llm_entities] Normalized entities: {normalized_entities}")

        return result

    def _extract_action_fallback(self, message: str) -> Optional[str]:
        """
        Fallback method to extract action from message using pattern matching

        Priority order:
        1. List bookings (highest priority when "bookings" or "appointments" mentioned)
        2. Cancel
        3. Reschedule
        4. Modify
        5. Book (lowest priority)

        Args:
            message: User message

        Returns:
            Extracted action or None
        """
        message_lower = message.lower()

        # Check for "list" action first with specific patterns
        # This has highest priority when "bookings" or "appointments" is mentioned
        list_patterns = [
            r'\b(list|show|view|display)\s+(my|all|them)?\s*(bookings?|appointments?)?',  # "list them", "show my bookings"
            r'\b(check|see|get)\s+my\s+(bookings?|appointments?)',  # "check my bookings"
            r'\bmy\s+(bookings?|appointments?)',  # "my bookings"
            r'\ball\s+(bookings?|appointments?)',  # "all bookings"
            r'(bookings?|appointments?).*\b(list|show|view|display)',  # "bookings and list them"
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                return "list"

        # Check for booking-related phrases
        if re.search(r'\b(i want to|i need to|i would like to|i\'d like to)\s+(book|schedule|arrange)', message_lower):
            return "book"
        elif re.search(r'\b(i want|i need|i would like|i\'d like)\b', message_lower):
            # If followed by service keywords, assume booking intent
            service_keywords = ["ac", "air conditioning", "plumbing", "plumber", "cleaning",
                              "electrical", "electrician", "painting", "appliance", "repair", "service"]
            if any(keyword in message_lower for keyword in service_keywords):
                return "book"

        # Check for direct action keywords
        if re.search(r'\b(book|schedule|arrange|set up)\b', message_lower):
            return "book"
        elif re.search(r'\bcancel\b', message_lower):
            return "cancel"
        elif re.search(r'\b(reschedule|change date|move)\b', message_lower):
            return "reschedule"
        elif re.search(r'\b(modify|update|edit)\b', message_lower):
            return "modify"

        return None

    def _validate_and_filter_intents(
        self,
        result: "IntentClassificationResult"
    ) -> "IntentClassificationResult":
        """
        Validate and filter intent results

        Args:
            result: Raw classification result from LLM

        Returns:
            Validated and filtered result
        """
        # Filter intents by confidence threshold
        filtered_intents = [
            intent for intent in result.intents
            if intent.confidence >= self.thresholds.SECONDARY_INTENT_THRESHOLD
        ]
        
        # Limit to MAX_INTENTS
        filtered_intents = filtered_intents[:self.thresholds.MAX_INTENTS]
        
        # If no intents pass threshold, mark as unclear
        if not filtered_intents:
            return self._build_fallback_result("")
        
        # Sort by confidence
        filtered_intents.sort(key=lambda x: x.confidence, reverse=True)
        
        # Update result
        result.intents = filtered_intents
        result.primary_intent = filtered_intents[0].intent
        
        return result
    
    def _filter_entities_for_intent(
        self,
        intent: IntentType,
        entities: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Filter entities relevant to a specific intent
        
        Args:
            intent: Intent type
            entities: All extracted entities
            
        Returns:
            Filtered entities relevant to the intent
        """
        config = INTENT_CONFIGS.get(intent)
        if not config:
            return entities
        
        # Get required and optional entities for this intent
        relevant_entity_types = set(
            [e.value for e in config.required_entities] +
            [e.value for e in config.optional_entities]
        )
        
        # Filter entities
        filtered = {
            k: v for k, v in entities.items()
            if k in relevant_entity_types
        }
        
        return filtered

    def _build_context_summary(
        self,
        conversation_history: Optional[List[Dict[str, str]]],
        dialog_state: Optional["DialogState"]
    ) -> str:
        """
        Build a summary of the context used for classification

        Args:
            conversation_history: Conversation history
            dialog_state: Dialog state

        Returns:
            Human-readable context summary
        """
        summary_parts = []

        if conversation_history:
            summary_parts.append(f"{len(conversation_history)} previous messages")

        if dialog_state is not None:
            summary_parts.append(f"active dialog state ({dialog_state.state.value})")
            if dialog_state.intent is not None:
                summary_parts.append(f"intent: {dialog_state.intent}")

        return ", ".join(summary_parts) if summary_parts else "no context"

    def _build_fallback_result(self, message: str) -> "IntentClassificationResult":
        """
        Build fallback result for unclear intents

        Args:
            message: User message

        Returns:
            IntentClassificationResult with unclear_intent
        """
        from src.schemas.intent import IntentResult, IntentClassificationResult

        return IntentClassificationResult(
            intents=[
                IntentResult(
                    intent=IntentType.UNCLEAR_INTENT.value,
                    confidence=0.5,
                    entities_json=None  # No entities for unclear intent
                )
            ],
            primary_intent=IntentType.UNCLEAR_INTENT.value,
            requires_clarification=True,
            clarification_reason="Unable to determine user intent with sufficient confidence"
        )

