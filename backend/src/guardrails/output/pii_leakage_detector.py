"""
PII leakage detector guardrail for output.

This guardrail detects PII in AI-generated responses to prevent
accidental leakage of sensitive information.
"""

from typing import Dict, Any
from src.guardrails.core.base_guardrail import BaseGuardrail
from src.guardrails.core.guardrail_result import GuardrailResult, Action, Severity
from src.utils.pii_utils import detect_all_pii, mask_pii_in_text


class PIILeakageDetector(BaseGuardrail):
    """
    Detects PII leakage in AI responses.
    
    This guardrail uses regex patterns to detect various types of PII including:
    - Email addresses
    - Phone numbers
    - SSN (Social Security Numbers)
    - Credit card numbers
    - Aadhaar numbers (India)
    - PAN card numbers (India)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize PIILeakageDetector.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.mask_pii = config.get('mask_pii', True)
        
        # Determine which PII types to detect
        self.pii_types = []
        if config.get('detect_email', True):
            self.pii_types.append('email')
        if config.get('detect_phone', True):
            self.pii_types.append('phone')
        if config.get('detect_ssn', True):
            self.pii_types.append('ssn')
        if config.get('detect_credit_card', True):
            self.pii_types.append('credit_card')
        if config.get('detect_aadhaar', True):
            self.pii_types.append('aadhaar')
        if config.get('detect_pan', True):
            self.pii_types.append('pan')
    
    async def check(self, text: str, context: Dict[str, Any]) -> GuardrailResult:
        """
        Check for PII leakage in AI response.
        
        Args:
            text: AI-generated response text
            context: Additional context
        
        Returns:
            GuardrailResult indicating PII leakage detection outcome
        """
        # Detect PII
        detected_pii = detect_all_pii(text, self.pii_types)
        
        # If no PII detected, allow
        if not detected_pii:
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.ALLOW,
                passed=True,
                severity=Severity.LOW,
                message="No PII leakage detected",
                details={}
            )
        
        # PII detected in output
        pii_summary = {pii_type: len(values) for pii_type, values in detected_pii.items()}
        
        # If masking is enabled, sanitize the text
        if self.mask_pii:
            sanitized_text, mask_counts = mask_pii_in_text(text, self.pii_types)
            
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.SANITIZE,
                passed=False,
                severity=Severity.HIGH,
                message="PII leakage detected and masked",
                details={
                    "pii_detected": pii_summary,
                    "pii_masked": mask_counts
                },
                sanitized_text=sanitized_text
            )
        else:
            # Block if masking is disabled
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.CRITICAL,
                message=self.get_fallback_response('pii_leakage'),
                details={"pii_detected": pii_summary}
            )
    
    async def sanitize(self, text: str, context: Dict[str, Any]) -> str:
        """
        Sanitize text by masking PII.
        
        Args:
            text: Text containing PII
            context: Additional context
        
        Returns:
            Sanitized text with PII masked
        """
        sanitized_text, _ = mask_pii_in_text(text, self.pii_types)
        return sanitized_text

