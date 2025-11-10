"""
Guardrail factory for creating and initializing guardrails.

This module provides a factory for creating guardrail instances
based on configuration.
"""

from typing import List
from src.guardrails.core.base_guardrail import BaseGuardrail
from src.guardrails.core.guardrail_manager import GuardrailManager
from src.guardrails.config.guardrail_config import get_phase1_guardrails, is_guardrail_enabled

# Import input guardrails
from src.guardrails.input.input_validator import InputValidator
from src.guardrails.input.pii_detector import PIIDetector
from src.guardrails.input.toxic_content_detector import ToxicContentDetector as InputToxicContentDetector
from src.guardrails.input.rate_limiter import RateLimiter

# Import output guardrails
from src.guardrails.output.pii_leakage_detector import PIILeakageDetector
from src.guardrails.output.toxic_content_detector import ToxicContentDetector as OutputToxicContentDetector


def create_input_guardrails() -> List[BaseGuardrail]:
    """
    Create all enabled input guardrails.
    
    Returns:
        List of input guardrail instances
    """
    guardrails = []
    phase1_config = get_phase1_guardrails()
    
    # InputValidator
    if is_guardrail_enabled('input_validator'):
        config = phase1_config['input_validator']
        guardrails.append(InputValidator(config))
    
    # PIIDetector
    if is_guardrail_enabled('pii_detector'):
        config = phase1_config['pii_detector']
        guardrails.append(PIIDetector(config))
    
    # ToxicContentDetector
    if is_guardrail_enabled('toxic_content_detector'):
        config = phase1_config['toxic_content_detector']
        guardrails.append(InputToxicContentDetector(config))
    
    # RateLimiter
    if is_guardrail_enabled('rate_limiter'):
        config = phase1_config['rate_limiter']
        guardrails.append(RateLimiter(config))
    
    return guardrails


def create_output_guardrails() -> List[BaseGuardrail]:
    """
    Create all enabled output guardrails.
    
    Returns:
        List of output guardrail instances
    """
    guardrails = []
    phase1_config = get_phase1_guardrails()
    
    # PIILeakageDetector
    if is_guardrail_enabled('pii_leakage_detector'):
        config = phase1_config['pii_leakage_detector']
        guardrails.append(PIILeakageDetector(config))
    
    # ToxicContentDetector (output)
    if is_guardrail_enabled('toxic_content_detector_output'):
        config = phase1_config['toxic_content_detector_output']
        guardrails.append(OutputToxicContentDetector(config))
    
    return guardrails


def create_guardrail_manager() -> GuardrailManager:
    """
    Create and initialize a GuardrailManager with all enabled guardrails.
    
    Returns:
        Initialized GuardrailManager instance
    """
    manager = GuardrailManager()
    
    # Register input guardrails
    input_guardrails = create_input_guardrails()
    for guardrail in input_guardrails:
        manager.register_input_guardrail(guardrail)
    
    # Register output guardrails
    output_guardrails = create_output_guardrails()
    for guardrail in output_guardrails:
        manager.register_output_guardrail(guardrail)
    
    return manager

