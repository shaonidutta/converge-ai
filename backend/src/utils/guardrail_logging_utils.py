"""
Logging utilities for guardrail violations and metrics.

This module provides utilities for logging guardrail violations, metrics,
and performance data.
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def log_violation(
    guardrail_name: str,
    violation_type: str,
    severity: str,
    user_id: int,
    text_preview: str,
    details: Dict[str, Any] = None
):
    """
    Log a guardrail violation.
    
    Args:
        guardrail_name: Name of the guardrail that detected the violation
        violation_type: Type of violation
        severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        user_id: ID of the user
        text_preview: Preview of the text (first 100 chars)
        details: Additional details about the violation
    """
    log_data = {
        "event": "guardrail_violation",
        "guardrail": guardrail_name,
        "violation_type": violation_type,
        "severity": severity,
        "user_id": user_id,
        "text_preview": text_preview[:100] if text_preview else "",
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Log at appropriate level based on severity
    if severity == "CRITICAL":
        logger.critical(f"Guardrail violation: {log_data}")
    elif severity == "HIGH":
        logger.error(f"Guardrail violation: {log_data}")
    elif severity == "MEDIUM":
        logger.warning(f"Guardrail violation: {log_data}")
    else:
        logger.info(f"Guardrail violation: {log_data}")


def log_guardrail_check(
    guardrail_name: str,
    check_type: str,
    passed: bool,
    latency_ms: float,
    user_id: int
):
    """
    Log a guardrail check (for metrics).
    
    Args:
        guardrail_name: Name of the guardrail
        check_type: Type of check (input/output)
        passed: Whether the check passed
        latency_ms: Latency in milliseconds
        user_id: ID of the user
    """
    log_data = {
        "event": "guardrail_check",
        "guardrail": guardrail_name,
        "check_type": check_type,
        "passed": passed,
        "latency_ms": latency_ms,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Guardrail check: {log_data}")


def log_guardrail_report(
    check_type: str,
    final_action: str,
    is_blocked: bool,
    total_latency_ms: float,
    num_violations: int,
    user_id: int
):
    """
    Log a complete guardrail report.
    
    Args:
        check_type: Type of check (input/output)
        final_action: Final action taken (ALLOW, SANITIZE, BLOCK, FLAG)
        is_blocked: Whether the message was blocked
        total_latency_ms: Total latency in milliseconds
        num_violations: Number of violations detected
        user_id: ID of the user
    """
    log_data = {
        "event": "guardrail_report",
        "check_type": check_type,
        "final_action": final_action,
        "is_blocked": is_blocked,
        "total_latency_ms": total_latency_ms,
        "num_violations": num_violations,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    if is_blocked:
        logger.warning(f"Guardrail report (BLOCKED): {log_data}")
    else:
        logger.info(f"Guardrail report: {log_data}")


def log_guardrail_error(
    guardrail_name: str,
    error_message: str,
    user_id: int,
    details: Dict[str, Any] = None
):
    """
    Log a guardrail error.
    
    Args:
        guardrail_name: Name of the guardrail
        error_message: Error message
        user_id: ID of the user
        details: Additional error details
    """
    log_data = {
        "event": "guardrail_error",
        "guardrail": guardrail_name,
        "error_message": error_message,
        "user_id": user_id,
        "details": details or {},
        "timestamp": datetime.now().isoformat()
    }
    
    logger.error(f"Guardrail error: {log_data}")


def log_cache_hit(guardrail_name: str, user_id: int):
    """
    Log a cache hit.
    
    Args:
        guardrail_name: Name of the guardrail
        user_id: ID of the user
    """
    log_data = {
        "event": "cache_hit",
        "guardrail": guardrail_name,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.debug(f"Cache hit: {log_data}")


def log_cache_miss(guardrail_name: str, user_id: int):
    """
    Log a cache miss.
    
    Args:
        guardrail_name: Name of the guardrail
        user_id: ID of the user
    """
    log_data = {
        "event": "cache_miss",
        "guardrail": guardrail_name,
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.debug(f"Cache miss: {log_data}")

