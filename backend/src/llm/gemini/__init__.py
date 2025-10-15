"""
LLM Module - Model-Agnostic LLM Integration

Uses LangChain's init_chat_model for provider-agnostic LLM access.
"""

from .client import LLMClient, get_llm_client
from .prompts import (
    build_intent_classification_prompt,
    build_entity_extraction_prompt,
    get_system_prompt
)

__all__ = [
    "LLMClient",
    "get_llm_client",
    "build_intent_classification_prompt",
    "build_entity_extraction_prompt",
    "get_system_prompt",
]
