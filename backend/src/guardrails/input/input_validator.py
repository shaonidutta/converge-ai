"""
Input validator guardrail.

This guardrail validates the format, encoding, and length of user input
to prevent malformed or invalid messages from being processed.
"""

from typing import Dict, Any
from src.guardrails.core.base_guardrail import BaseGuardrail
from src.guardrails.core.guardrail_result import GuardrailResult, Action, Severity


class InputValidator(BaseGuardrail):
    """
    Validates user input format, encoding, and length.
    
    This is a fast, rule-based guardrail that checks:
    - Input length (min/max)
    - Text encoding (UTF-8)
    - Empty/whitespace-only input
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize InputValidator.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.max_length = config.get('max_length', 10000)
        self.min_length = config.get('min_length', 1)
        self.allowed_encodings = config.get('allowed_encodings', ['utf-8', 'ascii'])
    
    async def check(self, text: str, context: Dict[str, Any]) -> GuardrailResult:
        """
        Validate input text.
        
        Args:
            text: User input text
            context: Additional context
        
        Returns:
            GuardrailResult indicating validation outcome
        """
        # Check if text is None or empty
        if text is None:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.HIGH,
                message=self.get_fallback_response('too_short'),
                details={"reason": "null_input"}
            )
        
        # Check if text is only whitespace
        if not text.strip():
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.MEDIUM,
                message=self.get_fallback_response('too_short'),
                details={"reason": "empty_input"}
            )
        
        # Check minimum length
        if len(text) < self.min_length:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.LOW,
                message=self.get_fallback_response('too_short'),
                details={"reason": "too_short", "length": len(text), "min_length": self.min_length}
            )
        
        # Check maximum length
        if len(text) > self.max_length:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.MEDIUM,
                message=self.get_fallback_response('too_long'),
                details={"reason": "too_long", "length": len(text), "max_length": self.max_length}
            )
        
        # Check encoding (try to encode as UTF-8)
        try:
            text.encode('utf-8')
        except UnicodeEncodeError:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.MEDIUM,
                message=self.get_fallback_response('invalid_encoding'),
                details={"reason": "invalid_encoding"}
            )
        
        # All checks passed
        return GuardrailResult(
            guardrail_name=self.name,
            action=Action.ALLOW,
            passed=True,
            severity=Severity.LOW,
            message="Input validation passed",
            details={"length": len(text)}
        )

