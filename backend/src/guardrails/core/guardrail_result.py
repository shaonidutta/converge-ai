"""
Result classes for guardrail checks.

This module defines the data structures used to represent the results of
guardrail checks, including individual guardrail results and aggregated reports.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


class Action(Enum):
    """
    Action to take based on guardrail check result.
    
    Attributes:
        ALLOW: Allow the message to proceed without modification
        SANITIZE: Sanitize the message (e.g., mask PII) and proceed
        BLOCK: Block the message and return fallback response
        FLAG: Flag the message for review but allow it to proceed
    """
    ALLOW = "allow"
    SANITIZE = "sanitize"
    BLOCK = "block"
    FLAG = "flag"


class Severity(Enum):
    """
    Severity level of a guardrail violation.
    
    Attributes:
        LOW: Low severity - informational only
        MEDIUM: Medium severity - should be reviewed
        HIGH: High severity - requires immediate attention
        CRITICAL: Critical severity - immediate action required
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GuardrailResult:
    """
    Result of a single guardrail check.
    
    This class represents the outcome of running a single guardrail on a piece
    of text (user input or AI output).
    
    Attributes:
        guardrail_name: Name of the guardrail that produced this result
        action: Action to take (ALLOW, SANITIZE, BLOCK, FLAG)
        passed: Whether the check passed (True) or failed (False)
        severity: Severity level of any violation detected
        message: Human-readable message describing the result
        details: Additional details about the check (e.g., what was detected)
        sanitized_text: Sanitized version of the text (if action is SANITIZE)
        latency_ms: Time taken to run the guardrail check (in milliseconds)
        timestamp: When the check was performed
    """
    guardrail_name: str
    action: Action
    passed: bool
    severity: Severity = Severity.LOW
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    sanitized_text: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_blocking(self) -> bool:
        """
        Check if this result should block the message.
        
        Returns:
            True if action is BLOCK, False otherwise
        """
        return self.action == Action.BLOCK
    
    def requires_sanitization(self) -> bool:
        """
        Check if this result requires sanitization.
        
        Returns:
            True if action is SANITIZE, False otherwise
        """
        return self.action == Action.SANITIZE
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the result
        """
        return {
            "guardrail_name": self.guardrail_name,
            "action": self.action.value,
            "passed": self.passed,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "has_sanitized_text": self.sanitized_text is not None,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class GuardrailReport:
    """
    Aggregated report from multiple guardrail checks.
    
    This class represents the combined results of running multiple guardrails
    on a piece of text. It determines the final action to take based on all
    individual guardrail results.
    
    Attributes:
        results: List of individual guardrail results
        original_text: Original text that was checked
        final_action: Final action to take (most restrictive action wins)
        final_text: Final text after sanitization (if applicable)
        is_blocked: Whether the message should be blocked
        total_latency_ms: Total time taken for all guardrail checks
        timestamp: When the report was generated
    """
    results: List[GuardrailResult]
    original_text: str
    final_action: Action = Action.ALLOW
    final_text: Optional[str] = None
    is_blocked: bool = False
    total_latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """
        Post-initialization processing.
        
        Calculates final action, final text, and blocking status based on
        individual guardrail results.
        """
        self._calculate_final_action()
        self._calculate_final_text()
        self._calculate_total_latency()
    
    def _calculate_final_action(self):
        """
        Calculate the final action based on all guardrail results.
        
        The most restrictive action wins:
        BLOCK > SANITIZE > FLAG > ALLOW
        """
        if not self.results:
            self.final_action = Action.ALLOW
            self.is_blocked = False
            return
        
        # Check for BLOCK (highest priority)
        for result in self.results:
            if result.action == Action.BLOCK:
                self.final_action = Action.BLOCK
                self.is_blocked = True
                return
        
        # Check for SANITIZE (second priority)
        for result in self.results:
            if result.action == Action.SANITIZE:
                self.final_action = Action.SANITIZE
                self.is_blocked = False
                return
        
        # Check for FLAG (third priority)
        for result in self.results:
            if result.action == Action.FLAG:
                self.final_action = Action.FLAG
                self.is_blocked = False
                return
        
        # Default to ALLOW
        self.final_action = Action.ALLOW
        self.is_blocked = False
    
    def _calculate_final_text(self):
        """
        Calculate the final text after applying all sanitizations.
        
        If any guardrail requires sanitization, apply all sanitizations
        in sequence. Otherwise, use the original text.
        """
        if self.final_action != Action.SANITIZE:
            self.final_text = self.original_text
            return
        
        # Apply all sanitizations in sequence
        text = self.original_text
        for result in self.results:
            if result.requires_sanitization() and result.sanitized_text:
                text = result.sanitized_text
        
        self.final_text = text
    
    def _calculate_total_latency(self):
        """
        Calculate total latency from all guardrail checks.
        
        Since guardrails run in parallel, the total latency is the maximum
        latency among all guardrails (not the sum).
        """
        if not self.results:
            self.total_latency_ms = 0.0
            return
        
        # Total latency is the max (since guardrails run in parallel)
        self.total_latency_ms = max(
            (result.latency_ms for result in self.results),
            default=0.0
        )
    
    def get_violations(self) -> List[GuardrailResult]:
        """
        Get all guardrail results that detected violations.
        
        Returns:
            List of GuardrailResult objects where passed is False
        """
        return [result for result in self.results if not result.passed]
    
    def get_blocking_violations(self) -> List[GuardrailResult]:
        """
        Get all guardrail results that require blocking.
        
        Returns:
            List of GuardrailResult objects with action BLOCK
        """
        return [result for result in self.results if result.is_blocking()]
    
    def get_fallback_response(self) -> str:
        """
        Get fallback response for blocked messages.
        
        Returns the message from the first blocking guardrail, or a default
        message if no blocking guardrails are found.
        
        Returns:
            Fallback response message
        """
        blocking_violations = self.get_blocking_violations()
        if blocking_violations:
            return blocking_violations[0].message
        return "I'm sorry, but I can't process that request."
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert report to dictionary for logging/serialization.
        
        Returns:
            Dictionary representation of the report
        """
        return {
            "final_action": self.final_action.value,
            "is_blocked": self.is_blocked,
            "total_latency_ms": self.total_latency_ms,
            "num_results": len(self.results),
            "num_violations": len(self.get_violations()),
            "num_blocking_violations": len(self.get_blocking_violations()),
            "results": [result.to_dict() for result in self.results],
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_results(
        cls,
        results: List[GuardrailResult],
        original_text: str
    ) -> "GuardrailReport":
        """
        Create a GuardrailReport from a list of GuardrailResult objects.
        
        Args:
            results: List of individual guardrail results
            original_text: Original text that was checked
        
        Returns:
            GuardrailReport instance
        """
        return cls(results=results, original_text=original_text)

