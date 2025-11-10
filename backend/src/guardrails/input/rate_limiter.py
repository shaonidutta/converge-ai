"""
Rate limiter guardrail for input.

This guardrail implements token bucket rate limiting to prevent abuse
and ensure fair usage of the system.
"""

from typing import Dict, Any
import time
from src.guardrails.core.base_guardrail import BaseGuardrail
from src.guardrails.core.guardrail_result import GuardrailResult, Action, Severity

# In-memory rate limiting (for simplicity - should use Redis in production)
_rate_limit_buckets: Dict[int, Dict[str, Any]] = {}


class RateLimiter(BaseGuardrail):
    """
    Rate limits user requests using token bucket algorithm.
    
    This guardrail prevents abuse by limiting the number of requests
    a user can make per minute and per hour.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize RateLimiter.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(config)
        self.max_requests_per_minute = config.get('max_requests_per_minute', 20)
        self.max_requests_per_hour = config.get('max_requests_per_hour', 100)
        self.burst_size = config.get('burst_size', 5)
    
    async def check(self, text: str, context: Dict[str, Any]) -> GuardrailResult:
        """
        Check if user has exceeded rate limits.
        
        Args:
            text: User input text (not used for rate limiting)
            context: Additional context (must contain user_id)
        
        Returns:
            GuardrailResult indicating rate limit status
        """
        user_id = context.get('user_id')
        if user_id is None:
            # No user_id - allow (shouldn't happen)
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.ALLOW,
                passed=True,
                severity=Severity.LOW,
                message="No user_id provided",
                details={}
            )
        
        current_time = time.time()
        
        # Get or create bucket for user
        if user_id not in _rate_limit_buckets:
            _rate_limit_buckets[user_id] = {
                'minute_tokens': self.max_requests_per_minute,
                'minute_last_refill': current_time,
                'hour_tokens': self.max_requests_per_hour,
                'hour_last_refill': current_time,
                'total_requests': 0
            }
        
        bucket = _rate_limit_buckets[user_id]
        
        # Refill minute bucket
        time_since_minute_refill = current_time - bucket['minute_last_refill']
        if time_since_minute_refill >= 60:
            # Refill minute bucket
            bucket['minute_tokens'] = self.max_requests_per_minute
            bucket['minute_last_refill'] = current_time
        
        # Refill hour bucket
        time_since_hour_refill = current_time - bucket['hour_last_refill']
        if time_since_hour_refill >= 3600:
            # Refill hour bucket
            bucket['hour_tokens'] = self.max_requests_per_hour
            bucket['hour_last_refill'] = current_time
        
        # Check if user has tokens available
        if bucket['minute_tokens'] <= 0:
            # Rate limit exceeded (per minute)
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.MEDIUM,
                message=self.get_fallback_response('rate_limit_exceeded'),
                details={
                    "reason": "minute_limit_exceeded",
                    "max_requests_per_minute": self.max_requests_per_minute,
                    "retry_after_seconds": int(60 - time_since_minute_refill)
                }
            )
        
        if bucket['hour_tokens'] <= 0:
            # Rate limit exceeded (per hour)
            return GuardrailResult(
                guardrail_name=self.name,
                action=Action.BLOCK,
                passed=False,
                severity=Severity.MEDIUM,
                message=self.get_fallback_response('rate_limit_exceeded'),
                details={
                    "reason": "hour_limit_exceeded",
                    "max_requests_per_hour": self.max_requests_per_hour,
                    "retry_after_seconds": int(3600 - time_since_hour_refill)
                }
            )
        
        # Consume tokens
        bucket['minute_tokens'] -= 1
        bucket['hour_tokens'] -= 1
        bucket['total_requests'] += 1
        
        # Allow request
        return GuardrailResult(
            guardrail_name=self.name,
            action=Action.ALLOW,
            passed=True,
            severity=Severity.LOW,
            message="Rate limit check passed",
            details={
                "minute_tokens_remaining": bucket['minute_tokens'],
                "hour_tokens_remaining": bucket['hour_tokens'],
                "total_requests": bucket['total_requests']
            }
        )

