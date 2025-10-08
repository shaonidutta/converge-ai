"""
LLM Client - Model-Agnostic Implementation

Uses LangChain's init_chat_model for model-agnostic LLM integration.
Supports easy switching between different providers (Gemini, OpenAI, Claude, etc.)
"""

import os
from typing import Optional, Dict, Any
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Model-agnostic LLM client using LangChain's abstraction layer.
    
    Supports multiple providers:
    - Google Gemini (google_genai)
    - OpenAI (openai)
    - Anthropic Claude (anthropic)
    - And more...
    
    Configuration is done via environment variables or constructor parameters.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        model_provider: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize LLM client
        
        Args:
            model: Model name (e.g., "gemini-2.0-flash-exp", "gpt-4o", "claude-3-opus-20240229")
            model_provider: Provider name (e.g., "google_genai", "openai", "anthropic")
                           If None, will be inferred from model name
            temperature: Temperature for generation (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
        """
        # Get configuration from environment or use defaults
        self.model = model or os.getenv("LLM_MODEL", "gemini-2.0-flash-exp")
        self.model_provider = model_provider or os.getenv("LLM_PROVIDER", "google_genai")
        self.temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "8192"))
        
        # Initialize the chat model using LangChain's universal init
        try:
            self.chat_model: BaseChatModel = init_chat_model(
                model=self.model,
                model_provider=self.model_provider,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )
            logger.info(
                f"Initialized LLM client: provider={self.model_provider}, "
                f"model={self.model}, temperature={self.temperature}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
    
    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a simple text prompt
        
        Args:
            prompt: Text prompt
            
        Returns:
            Generated text response
        """
        try:
            response = self.chat_model.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking LLM: {e}")
            raise
    
    def invoke_with_messages(self, messages: list) -> str:
        """
        Invoke the LLM with a list of messages
        
        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            
        Returns:
            Generated text response
        """
        try:
            response = self.chat_model.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error invoking LLM with messages: {e}")
            raise
    
    def with_structured_output(self, schema):
        """
        Get a version of the model that returns structured output
        
        Args:
            schema: Pydantic model class defining the output structure
            
        Returns:
            Chat model configured for structured output
        """
        return self.chat_model.with_structured_output(schema=schema)
    
    def get_model(self) -> BaseChatModel:
        """
        Get the underlying LangChain chat model
        
        Returns:
            BaseChatModel instance
        """
        return self.chat_model
    
    @classmethod
    def create_for_intent_classification(cls) -> "LLMClient":
        """
        Create an LLM client optimized for intent classification
        
        Returns:
            LLMClient configured for intent classification
        """
        # Use faster, cheaper model for classification
        model = os.getenv("INTENT_CLASSIFICATION_MODEL", "gemini-2.0-flash-exp")
        provider = os.getenv("INTENT_CLASSIFICATION_PROVIDER", "google_genai")
        
        return cls(
            model=model,
            model_provider=provider,
            temperature=0.0,  # Deterministic for classification
            max_tokens=1024   # Classification doesn't need many tokens
        )
    
    @classmethod
    def create_for_generation(cls) -> "LLMClient":
        """
        Create an LLM client optimized for text generation
        
        Returns:
            LLMClient configured for generation
        """
        # Use more capable model for generation
        model = os.getenv("GENERATION_MODEL", "gemini-1.5-pro")
        provider = os.getenv("GENERATION_PROVIDER", "google_genai")
        
        return cls(
            model=model,
            model_provider=provider,
            temperature=0.7,  # More creative for generation
            max_tokens=8192   # More tokens for longer responses
        )


# Convenience function for quick LLM access
def get_llm_client(
    model: Optional[str] = None,
    model_provider: Optional[str] = None,
    **kwargs
) -> LLMClient:
    """
    Get an LLM client instance
    
    Args:
        model: Model name
        model_provider: Provider name
        **kwargs: Additional parameters
        
    Returns:
        LLMClient instance
    """
    return LLMClient(model=model, model_provider=model_provider, **kwargs)

