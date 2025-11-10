"""
Custom exceptions for the guardrails system.

This module defines all custom exceptions used throughout the guardrails system
for error handling and violation reporting.
"""


class GuardrailException(Exception):
    """
    Base exception for all guardrail-related errors.
    
    This is the parent class for all guardrail exceptions and should be used
    for catching any guardrail-related error.
    """
    
    def __init__(self, message: str, guardrail_name: str = None):
        """
        Initialize GuardrailException.
        
        Args:
            message: Error message describing the exception
            guardrail_name: Name of the guardrail that raised the exception
        """
        self.message = message
        self.guardrail_name = guardrail_name
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.guardrail_name:
            return f"[{self.guardrail_name}] {self.message}"
        return self.message


class GuardrailViolationException(GuardrailException):
    """
    Exception raised when a guardrail detects a violation.
    
    This exception is raised when user input or AI output violates a guardrail
    policy (e.g., contains PII, toxic content, prompt injection, etc.).
    """
    
    def __init__(
        self,
        message: str,
        guardrail_name: str,
        violation_type: str,
        severity: str = "MEDIUM",
        details: dict = None
    ):
        """
        Initialize GuardrailViolationException.
        
        Args:
            message: Error message describing the violation
            guardrail_name: Name of the guardrail that detected the violation
            violation_type: Type of violation (e.g., "PII_DETECTED", "TOXIC_CONTENT")
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            details: Additional details about the violation
        """
        super().__init__(message, guardrail_name)
        self.violation_type = violation_type
        self.severity = severity
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """
        Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": "GuardrailViolation",
            "guardrail_name": self.guardrail_name,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "message": self.message,
            "details": self.details
        }


class GuardrailTimeoutException(GuardrailException):
    """
    Exception raised when a guardrail check exceeds the timeout limit.
    
    This exception is raised when a guardrail takes too long to execute,
    preventing it from blocking the request indefinitely.
    """
    
    def __init__(
        self,
        message: str,
        guardrail_name: str,
        timeout_seconds: float
    ):
        """
        Initialize GuardrailTimeoutException.
        
        Args:
            message: Error message describing the timeout
            guardrail_name: Name of the guardrail that timed out
            timeout_seconds: Timeout limit that was exceeded
        """
        super().__init__(message, guardrail_name)
        self.timeout_seconds = timeout_seconds
    
    def to_dict(self) -> dict:
        """
        Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": "GuardrailTimeout",
            "guardrail_name": self.guardrail_name,
            "timeout_seconds": self.timeout_seconds,
            "message": self.message
        }


class GuardrailConfigurationException(GuardrailException):
    """
    Exception raised when there's a configuration error in a guardrail.
    
    This exception is raised when a guardrail is misconfigured or missing
    required configuration parameters.
    """
    
    def __init__(
        self,
        message: str,
        guardrail_name: str,
        config_key: str = None
    ):
        """
        Initialize GuardrailConfigurationException.
        
        Args:
            message: Error message describing the configuration issue
            guardrail_name: Name of the guardrail with configuration error
            config_key: Configuration key that caused the error (optional)
        """
        super().__init__(message, guardrail_name)
        self.config_key = config_key
    
    def to_dict(self) -> dict:
        """
        Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": "GuardrailConfiguration",
            "guardrail_name": self.guardrail_name,
            "config_key": self.config_key,
            "message": self.message
        }


class GuardrailInitializationException(GuardrailException):
    """
    Exception raised when a guardrail fails to initialize.
    
    This exception is raised when a guardrail cannot be initialized due to
    missing dependencies, invalid configuration, or other initialization errors.
    """
    
    def __init__(
        self,
        message: str,
        guardrail_name: str,
        cause: Exception = None
    ):
        """
        Initialize GuardrailInitializationException.
        
        Args:
            message: Error message describing the initialization failure
            guardrail_name: Name of the guardrail that failed to initialize
            cause: Original exception that caused the initialization failure
        """
        super().__init__(message, guardrail_name)
        self.cause = cause
    
    def to_dict(self) -> dict:
        """
        Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": "GuardrailInitialization",
            "guardrail_name": self.guardrail_name,
            "message": self.message,
            "cause": str(self.cause) if self.cause else None
        }

