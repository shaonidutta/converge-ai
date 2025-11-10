"""
Toxic content detector guardrail for output.

This guardrail detects toxic, offensive, or inappropriate content in AI responses
using keyword matching and pattern detection.
"""

from typing import Dict, Any
from src.guardrails.core.base_guardrail import BaseGuardrail
from src.guardrails.core.guardrail_result import GuardrailResult, Action, Severity
from src.guardrails.config.patterns import get_toxic_content_patterns


class ToxicContentDetector(BaseGuardrail):
    """
    Detects toxic content in AI responses.
    
    This guardrail uses keyword matching to detect:
    - Profanity
    - Hate speech
    - Discriminatory language
    - Offensive content
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize ToxicContentDetector.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.threshold = config.get('threshold', 1)  # Number of matches to trigger
        self.toxic_patterns = get_toxic_content_patterns()
    
    async def check(self, text: str, context: Dict[str, Any]) -> GuardrailResult:
        """
        Check for toxic content in AI response.
        
        Args:
            text: AI-generated response text
            context: Additional context
        
        Returns:
            GuardrailResult indicating toxic content detection outcome
        """
        # Check for toxic patterns
        matches = []
        for pattern in self.toxic_patterns:
            found = pattern.findall(text)
            if found:
                matches.extend(found)
        
        # If no toxic content detected, allow
        if len(matches) < self.threshold:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.ALLOW,
                passed=True,
                severity=Severity.LOW,
                message="No toxic content detected",
                details={}
            )
        
        # Toxic content detected in output - block and use fallback
        return GuardrailResult(
            guardrail_name=self.name,
            action=Action.BLOCK,
            passed=False,
            severity=Severity.CRITICAL,
            message=self.get_fallback_response('toxic_content'),
            details={
                "toxic_matches": len(matches),
                "threshold": self.threshold
            }
        )

