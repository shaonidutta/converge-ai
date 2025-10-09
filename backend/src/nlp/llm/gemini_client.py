"""
Gemini LLM Client

Provides initialized Gemini LLM client for use across the application.
Uses configuration from settings to initialize the client.
"""

import logging
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import settings

logger = logging.getLogger(__name__)


def get_gemini_client(
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None
) -> ChatGoogleGenerativeAI:
    """
    Get initialized Gemini LLM client
    
    Args:
        temperature: Override default temperature (0.0-1.0)
        max_tokens: Override default max tokens
        model: Override default model name
        
    Returns:
        ChatGoogleGenerativeAI instance configured with settings
        
    Raises:
        ValueError: If GEMINI_API_KEY is not set
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    # Use provided values or fall back to settings
    final_temperature = temperature if temperature is not None else settings.GEMINI_TEMPERATURE
    final_max_tokens = max_tokens if max_tokens is not None else settings.GEMINI_MAX_TOKENS
    final_model = model if model is not None else settings.GEMINI_MODEL
    
    logger.info(f"Initializing Gemini client: model={final_model}, temp={final_temperature}")
    
    try:
        client = ChatGoogleGenerativeAI(
            model=final_model,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=final_temperature,
            max_tokens=final_max_tokens,
            top_p=settings.GEMINI_TOP_P,
            top_k=settings.GEMINI_TOP_K,
        )
        
        logger.info("✅ Gemini client initialized successfully")
        return client
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gemini client: {e}")
        raise


def get_gemini_client_for_classification() -> ChatGoogleGenerativeAI:
    """
    Get Gemini client optimized for intent classification
    
    Uses lower temperature for more deterministic results
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return get_gemini_client(
        temperature=0.3,  # Lower temperature for classification
        max_tokens=512    # Shorter responses for classification
    )


def get_gemini_client_for_extraction() -> ChatGoogleGenerativeAI:
    """
    Get Gemini client optimized for entity extraction
    
    Uses lower temperature for more accurate extraction
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return get_gemini_client(
        temperature=0.2,  # Very low temperature for extraction
        max_tokens=256    # Short responses for extraction
    )


def get_gemini_client_for_generation() -> ChatGoogleGenerativeAI:
    """
    Get Gemini client optimized for response generation
    
    Uses higher temperature for more creative responses
    
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return get_gemini_client(
        temperature=0.7,  # Higher temperature for generation
        max_tokens=1024   # Longer responses for generation
    )

