"""
Configuration for all guardrails.

This module contains the configuration settings for all guardrails including
enabled status, timeouts, thresholds, and fallback messages.
"""

from typing import Dict, Any


# Global guardrails configuration
GUARDRAILS_CONFIG: Dict[str, Any] = {
    # Input Guardrails
    "input_validator": {
        "enabled": True,
        "timeout": 1.0,  # 1 second
        "max_length": 10000,  # Maximum input length in characters
        "min_length": 1,  # Minimum input length
        "allowed_encodings": ["utf-8", "ascii"],
        "fallback_messages": {
            "too_long": "Your message is too long. Please keep it under 10,000 characters.",
            "too_short": "Your message is too short. Please provide more details.",
            "invalid_encoding": "Your message contains invalid characters. Please use standard text.",
            "default": "I'm sorry, but I can't process that message format."
        }
    },
    
    "pii_detector": {
        "enabled": True,
        "timeout": 2.0,  # 2 seconds
        "detect_email": True,
        "detect_phone": True,
        "detect_ssn": True,
        "detect_credit_card": True,
        "detect_address": True,
        "detect_aadhaar": True,
        "detect_pan": True,
        "detect_passport": False,  # Less common
        "detect_drivers_license": False,  # Less common
        "detect_bank_account": False,  # Less common
        "mask_pii": True,  # Whether to mask detected PII
        "fallback_messages": {
            "pii_detected": "I noticed your message contains personal information. For your privacy and security, please avoid sharing sensitive details like phone numbers, email addresses, or identification numbers in our chat.",
            "default": "I'm sorry, but I can't process messages containing personal information."
        }
    },
    
    "toxic_content_detector": {
        "enabled": True,
        "timeout": 2.0,  # 2 seconds
        "threshold": 1,  # Number of toxic keywords to trigger (1 = any match)
        "fallback_messages": {
            "toxic_content": "I'm here to help, but I can only respond to respectful messages. Please rephrase your request in a polite manner.",
            "default": "I'm sorry, but I can't process that type of message."
        }
    },
    
    "rate_limiter": {
        "enabled": True,
        "timeout": 1.0,  # 1 second
        "max_requests_per_minute": 20,  # Maximum requests per user per minute
        "max_requests_per_hour": 100,  # Maximum requests per user per hour
        "burst_size": 5,  # Allow burst of 5 requests
        "fallback_messages": {
            "rate_limit_exceeded": "You're sending messages too quickly. Please wait a moment before trying again.",
            "default": "Please slow down and try again in a moment."
        }
    },
    
    # Output Guardrails
    "pii_leakage_detector": {
        "enabled": True,
        "timeout": 2.0,  # 2 seconds
        "detect_email": True,
        "detect_phone": True,
        "detect_ssn": True,
        "detect_credit_card": True,
        "detect_address": True,
        "detect_aadhaar": True,
        "detect_pan": True,
        "mask_pii": True,  # Whether to mask detected PII in output
        "fallback_messages": {
            "pii_leakage": "I apologize, but I can't provide that information as it may contain sensitive data.",
            "default": "I'm sorry, but I can't provide that response."
        }
    },
    
    "toxic_content_detector_output": {
        "enabled": True,
        "timeout": 2.0,  # 2 seconds
        "threshold": 1,  # Number of toxic keywords to trigger
        "fallback_messages": {
            "toxic_content": "I apologize, but I need to rephrase my response. How else can I help you?",
            "default": "I apologize, but I need to provide a different response."
        }
    },
    
    # Phase 2 Guardrails (Should-Have) - Disabled by default
    "prompt_injection_detector": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 5.0,  # 5 seconds
        "use_llm": False,  # Use LLM for detection (slower but more accurate)
        "cache_ttl": 3600,  # Cache results for 1 hour
        "fallback_messages": {
            "prompt_injection": "I detected an attempt to manipulate my behavior. I can only respond to genuine service requests.",
            "default": "I'm sorry, but I can't process that type of request."
        }
    },
    
    "policy_compliance_checker": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 3.0,  # 3 seconds
        "check_pricing": True,
        "check_commitments": True,
        "check_unauthorized_offers": True,
        "fallback_messages": {
            "policy_violation": "I can't make that commitment. Please contact our support team for specific pricing and offers.",
            "default": "I'm sorry, but I can't provide that information."
        }
    },
    
    # Phase 3 Guardrails (Nice-to-Have) - Disabled by default
    "jailbreak_detector": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 5.0,  # 5 seconds
        "use_llm": False,
        "fallback_messages": {
            "jailbreak_attempt": "I detected an attempt to bypass my safety guidelines. I can only respond to legitimate service requests.",
            "default": "I'm sorry, but I can't process that request."
        }
    },
    
    "hallucination_detector": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 3.0,  # 3 seconds
        "verify_against_db": True,
        "fallback_messages": {
            "hallucination_detected": "I apologize, but I need to verify that information. Let me provide you with accurate details.",
            "default": "Let me provide you with accurate information."
        }
    },
    
    "commitment_detector": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 2.0,  # 2 seconds
        "flag_only": True,  # Only flag, don't block
        "fallback_messages": {
            "commitment_detected": "I should clarify that I can't make definitive commitments. Let me provide you with the information you need.",
            "default": "Let me provide you with accurate information."
        }
    },
    
    "quality_assurance_checker": {
        "enabled": False,  # Disabled in Phase 1
        "timeout": 2.0,  # 2 seconds
        "min_response_length": 10,
        "max_response_length": 5000,
        "check_coherence": True,
        "fallback_messages": {
            "quality_issue": "I apologize, but my response didn't meet quality standards. Let me try again.",
            "default": "Let me provide you with a better response."
        }
    }
}


def get_guardrail_config(guardrail_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific guardrail.
    
    Args:
        guardrail_name: Name of the guardrail
    
    Returns:
        Configuration dictionary for the guardrail
    
    Raises:
        KeyError: If guardrail name not found in configuration
    """
    if guardrail_name not in GUARDRAILS_CONFIG:
        raise KeyError(f"Guardrail '{guardrail_name}' not found in configuration")
    
    return GUARDRAILS_CONFIG[guardrail_name].copy()


def is_guardrail_enabled(guardrail_name: str) -> bool:
    """
    Check if a guardrail is enabled.
    
    Args:
        guardrail_name: Name of the guardrail
    
    Returns:
        True if enabled, False otherwise
    """
    config = get_guardrail_config(guardrail_name)
    return config.get("enabled", False)


def get_all_enabled_guardrails() -> Dict[str, Dict[str, Any]]:
    """
    Get all enabled guardrails and their configurations.
    
    Returns:
        Dictionary mapping guardrail names to their configurations
    """
    return {
        name: config
        for name, config in GUARDRAILS_CONFIG.items()
        if config.get("enabled", False)
    }


def get_phase1_guardrails() -> Dict[str, Dict[str, Any]]:
    """
    Get Phase 1 (must-have) guardrails.
    
    Returns:
        Dictionary of Phase 1 guardrail configurations
    """
    phase1_names = [
        "input_validator",
        "pii_detector",
        "toxic_content_detector",
        "rate_limiter",
        "pii_leakage_detector",
        "toxic_content_detector_output"
    ]
    
    return {
        name: GUARDRAILS_CONFIG[name]
        for name in phase1_names
        if name in GUARDRAILS_CONFIG
    }


def update_guardrail_config(guardrail_name: str, updates: Dict[str, Any]):
    """
    Update configuration for a specific guardrail.
    
    Args:
        guardrail_name: Name of the guardrail
        updates: Dictionary of configuration updates
    
    Raises:
        KeyError: If guardrail name not found in configuration
    """
    if guardrail_name not in GUARDRAILS_CONFIG:
        raise KeyError(f"Guardrail '{guardrail_name}' not found in configuration")
    
    GUARDRAILS_CONFIG[guardrail_name].update(updates)


def enable_guardrail(guardrail_name: str):
    """
    Enable a specific guardrail.
    
    Args:
        guardrail_name: Name of the guardrail to enable
    """
    update_guardrail_config(guardrail_name, {"enabled": True})


def disable_guardrail(guardrail_name: str):
    """
    Disable a specific guardrail.
    
    Args:
        guardrail_name: Name of the guardrail to disable
    """
    update_guardrail_config(guardrail_name, {"enabled": False})

