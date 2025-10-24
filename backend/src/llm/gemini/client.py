"""
LLM Client - Google GenAI SDK Implementation

Uses the new google.genai SDK to support all Gemini models including gemini-1.5-flash-8b.
This uses the stable v1 API instead of the deprecated v1beta API.
"""

import os
import json
from typing import Optional, Dict, Any, List
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Direct Google GenAI SDK client for Gemini models.

    This client uses google.generativeai directly to support all Gemini models
    including gemini-1.5-flash-8b which is not supported by LangChain's v1beta API.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        model_provider: Optional[str] = None,  # Kept for compatibility, ignored
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize LLM client

        Args:
            model: Model name (e.g., "gemini-1.5-flash-8b", "gemini-1.5-pro", "gemini-2.0-flash-exp")
            model_provider: Ignored (kept for compatibility)
            temperature: Temperature for generation (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters
        """
        # Get configuration from environment or use defaults
        # Note: gemini-1.5-flash-8b is not available in v1beta API, use gemini-2.0-flash instead
        self.model_name = model or os.getenv("LLM_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        self.temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "8192"))

        # Configure Google GenAI with API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        # Initialize the client
        try:
            self.client = genai.Client(api_key=api_key)
            self.generation_config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            logger.info(
                f"Initialized Gemini client with model: {self.model_name}, "
                f"temperature={self.temperature}, max_tokens={self.max_tokens}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise RuntimeError(f"Failed to initialize Gemini client: {e}")

    def invoke(self, prompt: str) -> str:
        """
        Invoke the LLM with a simple text prompt

        Args:
            prompt: Text prompt

        Returns:
            Generated text response
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Error invoking Gemini: {e}")
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
            # Extract system instruction if present
            system_instruction = None
            contents = []

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    system_instruction = content
                else:
                    contents.append(content)

            # Create config with system instruction if present
            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            if system_instruction:
                config.system_instruction = system_instruction

            # Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            return response.text
        except Exception as e:
            logger.error(f"Error invoking Gemini with messages: {e}")
            raise

    def with_structured_output(self, schema: BaseModel):
        """
        Get a version of the model that returns structured output

        Args:
            schema: Pydantic model class defining the output structure

        Returns:
            StructuredOutputModel instance
        """
        return StructuredOutputModel(self.client, schema, self.model_name, self.generation_config)

    def get_client(self):
        """
        Get the underlying Gemini client

        Returns:
            genai.Client instance
        """
        return self.client

    @classmethod
    def create_for_intent_classification(cls) -> "LLMClient":
        """
        Create an LLM client optimized for intent classification

        Returns:
            LLMClient configured for intent classification
        """
        # Use faster, cheaper model for classification
        # Default to gemini-2.0-flash (gemini-1.5-flash-8b is not available in v1beta)
        model = os.getenv("INTENT_CLASSIFICATION_MODEL", os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))

        return cls(
            model=model,
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

        return cls(
            model=model,
            temperature=0.7,  # More creative for generation
            max_tokens=8192   # More tokens for longer responses
        )


class StructuredOutputModel:
    """
    Wrapper for Gemini client that returns structured output matching a Pydantic schema.
    """

    def __init__(self, client: genai.Client, schema: BaseModel, model_name: str, generation_config: types.GenerateContentConfig):
        """
        Initialize structured output model

        Args:
            client: Gemini Client instance
            schema: Pydantic model class defining the output structure
            model_name: Name of the model
            generation_config: Generation configuration
        """
        self.client = client
        self.schema = schema
        self.model_name = model_name
        self.generation_config = generation_config

    def invoke(self, prompt: str):
        """
        Invoke the model and parse output to match schema

        Args:
            prompt: Text prompt (should include JSON schema instructions)

        Returns:
            Instance of the Pydantic schema with parsed data
        """
        try:
            # Get JSON schema and remove additionalProperties
            schema_dict = self.schema.model_json_schema()
            schema_dict = self._remove_additional_properties(schema_dict)

            # Create config with JSON response schema
            config = types.GenerateContentConfig(
                temperature=self.generation_config.temperature,
                max_output_tokens=self.generation_config.max_output_tokens,
                response_mime_type='application/json',
                response_schema=schema_dict,
            )

            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            # Parse JSON and validate with Pydantic
            response_data = json.loads(response.text)
            return self.schema(**response_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Response text: {response.text}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")
        except Exception as e:
            logger.error(f"Error in structured output: {e}")
            raise

    def _remove_additional_properties(self, schema: dict) -> dict:
        """
        Recursively remove additionalProperties from JSON schema

        Args:
            schema: JSON schema dict

        Returns:
            Modified schema without additionalProperties
        """
        if isinstance(schema, dict):
            # Remove additionalProperties key
            if "additionalProperties" in schema:
                del schema["additionalProperties"]

            # Recursively process nested schemas
            for key, value in schema.items():
                if isinstance(value, dict):
                    schema[key] = self._remove_additional_properties(value)
                elif isinstance(value, list):
                    schema[key] = [self._remove_additional_properties(item) if isinstance(item, dict) else item for item in value]

        return schema


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
        model_provider: Ignored (kept for compatibility)
        **kwargs: Additional parameters

    Returns:
        LLMClient instance
    """
    return LLMClient(model=model, **kwargs)
