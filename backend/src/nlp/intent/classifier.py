"""
Multi-Intent Classifier

Hybrid approach for intent classification:
1. Quick pattern matching (regex/keywords) for high-confidence cases
2. LLM-based classification for ambiguous cases
3. Fallback handling for unclear intents
"""

import json
import logging
from typing import List, Dict, Tuple, Optional, TYPE_CHECKING
from datetime import datetime, timezone

from .config import (
    IntentType,
    ClassificationThresholds,
    INTENT_CONFIGS
)
from .patterns import IntentPatterns
from src.llm.gemini.client import LLMClient
from src.llm.gemini.prompts import build_intent_classification_prompt, get_system_prompt

if TYPE_CHECKING:
    from src.schemas.intent import IntentResult, IntentClassificationResult

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
    
    async def classify(self, message: str) -> Tuple["IntentClassificationResult", str]:
        """
        Classify user message and detect all intents

        Args:
            message: User message to classify

        Returns:
            Tuple of (IntentClassificationResult, classification_method)
            classification_method: "pattern_match", "llm", or "fallback"
        """
        from src.schemas.intent import IntentClassificationResult

        logger.info(f"Classifying message: {message[:100]}...")
        
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
                multi_intent_keywords = [' and ', ' also ', ' plus ', ' then ', ' after ']
                has_multi_intent_signal = any(keyword in message.lower() for keyword in multi_intent_keywords)

                if not has_multi_intent_signal:
                    logger.info(f"High-confidence single intent pattern match: {high_confidence_intents}")
                    result = self._build_result_from_patterns(message, high_confidence_intents)
                    return result, "pattern_match"
                else:
                    logger.info(f"Multi-intent signal detected, passing to LLM: {message[:50]}...")
        
        # Step 2: Use LLM for classification (ambiguous cases)
        logger.info("Using LLM for classification")
        try:
            llm_result = await self._classify_with_llm(message)
            
            # Check if LLM classification has sufficient confidence
            if llm_result.intents and llm_result.intents[0].confidence >= self.thresholds.LLM_CLASSIFICATION_THRESHOLD:
                logger.info(f"LLM classification successful: {llm_result.primary_intent}")
                return llm_result, "llm"
            
            # If confidence is low, mark as requiring clarification
            if llm_result.intents and llm_result.intents[0].confidence < self.thresholds.CLARIFICATION_THRESHOLD:
                llm_result.requires_clarification = True
                llm_result.clarification_reason = "Low confidence in intent classification"
                return llm_result, "llm"
            
            return llm_result, "llm"
            
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
        intent_results = []
        for intent, confidence in pattern_matches[:self.thresholds.MAX_INTENTS]:
            # Filter entities relevant to this intent
            relevant_entities = self._filter_entities_for_intent(intent, entities)
            
            intent_results.append(
                IntentResult(
                    intent=intent.value,
                    confidence=confidence,
                    entities=relevant_entities
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
    
    async def _classify_with_llm(self, message: str) -> "IntentClassificationResult":
        """
        Classify using LLM with structured output

        Args:
            message: User message

        Returns:
            IntentClassificationResult
        """
        from src.schemas.intent import IntentClassificationResult

        # Build prompt
        prompt = build_intent_classification_prompt(message)
        
        # Get structured output from LLM
        structured_llm = self.llm_client.with_structured_output(IntentClassificationResult)
        
        # Invoke LLM
        result = structured_llm.invoke(prompt)
        
        # Validate and filter intents
        result = self._validate_and_filter_intents(result)
        
        return result
    
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
                    entities={}
                )
            ],
            primary_intent=IntentType.UNCLEAR_INTENT.value,
            requires_clarification=True,
            clarification_reason="Unable to determine user intent with sufficient confidence"
        )

