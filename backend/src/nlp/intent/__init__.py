"""
Intent Classification Module

Multi-intent classification system with hybrid approach:
- Pattern matching for quick classification
- LLM-based classification for ambiguous cases
- Entity extraction
"""

from .classifier import IntentClassifier
from .config import IntentType, EntityType, INTENT_CONFIGS
from .patterns import IntentPatterns
from .examples import get_examples_for_intent, get_all_examples

__all__ = [
    "IntentClassifier",
    "IntentType",
    "EntityType",
    "INTENT_CONFIGS",
    "IntentPatterns",
    "get_examples_for_intent",
    "get_all_examples",
]
