"""
PII (Personally Identifiable Information) detection and masking utilities.

This module provides utilities for detecting and masking various types of PII
in text, including emails, phone numbers, SSNs, credit cards, etc.
"""

import re
from typing import List, Dict, Tuple
from src.guardrails.config.patterns import (
    EMAIL_PATTERN,
    PHONE_PATTERNS,
    SSN_PATTERNS,
    CREDIT_CARD_PATTERNS,
    AADHAAR_PATTERN,
    PAN_PATTERN,
    get_all_pii_patterns
)


def detect_email(text: str) -> List[str]:
    """
    Detect email addresses in text.
    
    Args:
        text: Text to search for emails
    
    Returns:
        List of detected email addresses
    """
    return EMAIL_PATTERN.findall(text)


def detect_phone(text: str) -> List[str]:
    """
    Detect phone numbers in text.
    
    Args:
        text: Text to search for phone numbers
    
    Returns:
        List of detected phone numbers
    """
    phones = []
    for pattern in PHONE_PATTERNS:
        phones.extend(pattern.findall(text))
    return phones


def detect_ssn(text: str) -> List[str]:
    """
    Detect SSN (Social Security Numbers) in text.
    
    Args:
        text: Text to search for SSNs
    
    Returns:
        List of detected SSNs
    """
    ssns = []
    for pattern in SSN_PATTERNS:
        ssns.extend(pattern.findall(text))
    return ssns


def detect_credit_card(text: str) -> List[str]:
    """
    Detect credit card numbers in text.
    
    Args:
        text: Text to search for credit cards
    
    Returns:
        List of detected credit card numbers
    """
    cards = []
    for pattern in CREDIT_CARD_PATTERNS:
        cards.extend(pattern.findall(text))
    return cards


def detect_aadhaar(text: str) -> List[str]:
    """
    Detect Aadhaar numbers (India) in text.
    
    Args:
        text: Text to search for Aadhaar numbers
    
    Returns:
        List of detected Aadhaar numbers
    """
    return AADHAAR_PATTERN.findall(text)


def detect_pan(text: str) -> List[str]:
    """
    Detect PAN card numbers (India) in text.
    
    Args:
        text: Text to search for PAN numbers
    
    Returns:
        List of detected PAN numbers
    """
    return PAN_PATTERN.findall(text)


def detect_all_pii(text: str, pii_types: List[str] = None) -> Dict[str, List[str]]:
    """
    Detect all types of PII in text.
    
    Args:
        text: Text to search for PII
        pii_types: List of PII types to detect (None = all types)
    
    Returns:
        Dictionary mapping PII type to list of detected values
    """
    results = {}
    
    # Define detection functions
    detectors = {
        'email': detect_email,
        'phone': detect_phone,
        'ssn': detect_ssn,
        'credit_card': detect_credit_card,
        'aadhaar': detect_aadhaar,
        'pan': detect_pan,
    }
    
    # Detect specified types or all types
    types_to_check = pii_types if pii_types else detectors.keys()
    
    for pii_type in types_to_check:
        if pii_type in detectors:
            detected = detectors[pii_type](text)
            if detected:
                results[pii_type] = detected
    
    return results


def mask_email(email: str) -> str:
    """
    Mask an email address.
    
    Args:
        email: Email address to mask
    
    Returns:
        Masked email (e.g., j***@example.com)
    """
    if '@' not in email:
        return '[EMAIL]'
    
    local, domain = email.split('@', 1)
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """
    Mask a phone number.
    
    Args:
        phone: Phone number to mask
    
    Returns:
        Masked phone (e.g., ***-***-1234)
    """
    # Extract digits only
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) < 4:
        return '[PHONE]'
    
    # Show last 4 digits
    return f"***-***-{digits[-4:]}"


def mask_ssn(ssn: str) -> str:
    """
    Mask an SSN.
    
    Args:
        ssn: SSN to mask
    
    Returns:
        Masked SSN (e.g., ***-**-1234)
    """
    # Extract digits only
    digits = re.sub(r'\D', '', ssn)
    
    if len(digits) != 9:
        return '[SSN]'
    
    # Show last 4 digits
    return f"***-**-{digits[-4:]}"


def mask_credit_card(card: str) -> str:
    """
    Mask a credit card number.
    
    Args:
        card: Credit card number to mask
    
    Returns:
        Masked card (e.g., ****-****-****-1234)
    """
    # Extract digits only
    digits = re.sub(r'\D', '', card)
    
    if len(digits) < 4:
        return '[CARD]'
    
    # Show last 4 digits
    return f"****-****-****-{digits[-4:]}"


def mask_aadhaar(aadhaar: str) -> str:
    """
    Mask an Aadhaar number.
    
    Args:
        aadhaar: Aadhaar number to mask
    
    Returns:
        Masked Aadhaar (e.g., ****-****-1234)
    """
    # Extract digits only
    digits = re.sub(r'\D', '', aadhaar)
    
    if len(digits) != 12:
        return '[AADHAAR]'
    
    # Show last 4 digits
    return f"****-****-{digits[-4:]}"


def mask_pan(pan: str) -> str:
    """
    Mask a PAN card number.
    
    Args:
        pan: PAN number to mask
    
    Returns:
        Masked PAN (e.g., ***********C)
    """
    if len(pan) < 2:
        return '[PAN]'
    
    # Show last character
    return '*' * (len(pan) - 1) + pan[-1]


def mask_pii_in_text(text: str, pii_types: List[str] = None) -> Tuple[str, Dict[str, int]]:
    """
    Mask all PII in text.
    
    Args:
        text: Text containing PII
        pii_types: List of PII types to mask (None = all types)
    
    Returns:
        Tuple of (masked_text, counts_dict)
        - masked_text: Text with PII masked
        - counts_dict: Dictionary mapping PII type to count of masked items
    """
    masked_text = text
    counts = {}
    
    # Define masking functions
    maskers = {
        'email': (EMAIL_PATTERN, mask_email),
        'phone': (PHONE_PATTERNS, mask_phone),
        'ssn': (SSN_PATTERNS, mask_ssn),
        'credit_card': (CREDIT_CARD_PATTERNS, mask_credit_card),
        'aadhaar': (AADHAAR_PATTERN, mask_aadhaar),
        'pan': (PAN_PATTERN, mask_pan),
    }
    
    # Mask specified types or all types
    types_to_mask = pii_types if pii_types else maskers.keys()
    
    for pii_type in types_to_mask:
        if pii_type not in maskers:
            continue
        
        patterns, mask_func = maskers[pii_type]
        
        # Handle single pattern or list of patterns
        if not isinstance(patterns, list):
            patterns = [patterns]
        
        count = 0
        for pattern in patterns:
            matches = pattern.findall(masked_text)
            for match in matches:
                masked_value = mask_func(match)
                masked_text = masked_text.replace(match, masked_value, 1)
                count += 1
        
        if count > 0:
            counts[pii_type] = count
    
    return masked_text, counts


def has_pii(text: str, pii_types: List[str] = None) -> bool:
    """
    Check if text contains any PII.
    
    Args:
        text: Text to check
        pii_types: List of PII types to check (None = all types)
    
    Returns:
        True if PII detected, False otherwise
    """
    detected = detect_all_pii(text, pii_types)
    return len(detected) > 0

