"""
Base guardrail abstract class.

This module defines the abstract base class that all guardrails must inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import asyncio
from .guardrail_result import GuardrailResult, Action, Severity
from .exceptions import GuardrailTimeoutException


class BaseGuardrail(ABC):
    """
    Abstract base class for all guardrails.
    
    All guardrails must inherit from this class and implement the check() method.
    The class provides common functionality for timeout handling, sanitization,
    and fallback responses.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the guardrail.
        
        Args:
            config: Configuration dictionary for the guardrail
        """
        self.config = config
        self.name = self.__class__.__name__
        self.enabled = config.get('enabled', True)
        self.timeout = config.get('timeout', 5.0)  # Default 5 seconds
        self.fallback_messages = config.get('fallback_messages', {})
    
    @abstractmethod
    async def check(self, text: str, context: Dict[str, Any]) -> GuardrailResult:
        """
        Check if text passes the guardrail.
        
        This is the main method that must be implemented by all guardrails.
        It should analyze the text and return a GuardrailResult indicating
        whether the text passes or fails the check.
        
        Args:
            text: Text to check (user input or AI output)
            context: Additional context (user_id, session_id, etc.)
        
        Returns:
            GuardrailResult indicating the outcome of the check
        """
        pass
    
    async def check_with_timeout(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> GuardrailResult:
        """
        Check text with timeout protection.
        
        Wraps the check() method with timeout handling to prevent guardrails
        from blocking indefinitely.
        
        Args:
            text: Text to check
            context: Additional context
        
        Returns:
            GuardrailResult from the check, or error result if timeout occurs
        """
        start_time = time.time()
        
        try:
            # Run check with timeout
            result = await asyncio.wait_for(
                self.check(text, context),
                timeout=self.timeout
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            result.latency_ms = latency_ms
            
            return result
            
        except asyncio.TimeoutError:
            # Timeout occurred - return error result
            latency_ms = (time.time() - start_time) * 1000
            
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.ALLOW,  # Allow on timeout (fail-open)
                passed=True,  # Don't block on timeout
                severity=Severity.MEDIUM,
                message=f"Guardrail check timed out after {self.timeout}s",
                details={"timeout": True, "timeout_seconds": self.timeout},
                latency_ms=latency_ms
            )
        
        except Exception as e:
            # Unexpected error - return error result
            latency_ms = (time.time() - start_time) * 1000
            
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.ALLOW,  # Allow on error (fail-open)
                passed=True,  # Don't block on error
                severity=Severity.HIGH,
                message=f"Guardrail check failed: {str(e)}",
                details={"error": True, "error_message": str(e)},
                latency_ms=latency_ms
            )
    
    async def sanitize(self, text: str, context: Dict[str, Any]) -> str:
        """
        Sanitize text if needed.
        
        This method can be overridden by guardrails that support sanitization
        (e.g., masking PII). The default implementation returns the text unchanged.
        
        Args:
            text: Text to sanitize
            context: Additional context
        
        Returns:
            Sanitized text
        """
        return text
    
    def get_fallback_response(self, violation_type: str) -> str:
        """
        Get fallback response for a specific violation type.
        
        Returns a user-friendly message to display when a guardrail blocks
        a message. The message can be customized per violation type.
        
        Args:
            violation_type: Type of violation (e.g., "PII_DETECTED", "TOXIC_CONTENT")
        
        Returns:
            Fallback response message
        """
        # Try to get specific message for this violation type
        if violation_type in self.fallback_messages:
            return self.fallback_messages[violation_type]
        
        # Try to get default message for this guardrail
        if 'default' in self.fallback_messages:
            return self.fallback_messages['default']
        
        # Return generic fallback message
        return "I'm sorry, but I can't process that request."
    
    def is_enabled(self) -> bool:
        """
        Check if the guardrail is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.enabled
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

