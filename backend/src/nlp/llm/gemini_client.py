"""
Gemini LLM Client

Provides initialized Gemini LLM client for use across the application.
Uses configuration from settings to initialize the client.
"""

import logging
import time
import asyncio
from typing import Optional, Any, Callable
from functools import wraps
from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import settings

logger = logging.getLogger(__name__)

# Rate limiting: Track last API call time to avoid hitting rate limits
_last_api_call_time = 0
_min_delay_between_calls = 0.5  # 500ms between calls = max 120 RPM (well under 15 RPM limit)


def with_retry(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator to add exponential backoff retry logic to LLM calls

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e)

                    # Check if it's a retryable error (503, 429, or rate limit)
                    is_retryable = (
                        "503" in error_msg or
                        "429" in error_msg or
                        "overloaded" in error_msg.lower() or
                        "rate limit" in error_msg.lower() or
                        "quota" in error_msg.lower()
                    )

                    if not is_retryable or attempt == max_retries:
                        # Not retryable or max retries reached
                        logger.error(f"LLM call failed after {attempt + 1} attempts: {error_msg}")
                        raise

                    # Log retry attempt
                    logger.warning(
                        f"LLM call failed (attempt {attempt + 1}/{max_retries + 1}): {error_msg}. "
                        f"Retrying in {delay:.1f}s..."
                    )

                    # Wait before retry
                    time.sleep(delay)
                    delay *= backoff_factor

            # Should never reach here, but just in case
            raise last_exception

        return wrapper
    return decorator


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

