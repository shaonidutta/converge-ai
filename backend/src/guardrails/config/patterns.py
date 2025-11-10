"""
Regex patterns for PII detection and content filtering.

This module contains all regex patterns used by guardrails for detecting
personally identifiable information (PII) and other sensitive content.
"""

import re

# Email patterns
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    re.IGNORECASE
)

# Phone number patterns (various formats)
PHONE_PATTERNS = [
    re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),  # 123-456-7890, 123.456.7890, 123 456 7890
    re.compile(r'\b\(\d{3}\)\s?\d{3}[-.\s]?\d{4}\b'),  # (123) 456-7890
    re.compile(r'\b\+\d{1,3}[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'),  # +1-123-456-7890
    re.compile(r'\b\d{10}\b'),  # 1234567890
]

# SSN patterns (US Social Security Number)
SSN_PATTERNS = [
    re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),  # 123-45-6789
    re.compile(r'\b\d{9}\b'),  # 123456789 (only if context suggests SSN)
]

# Credit card patterns (major card types)
CREDIT_CARD_PATTERNS = [
    re.compile(r'\b4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # Visa
    re.compile(r'\b5[1-5]\d{2}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # Mastercard
    re.compile(r'\b3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5}\b'),  # American Express
    re.compile(r'\b6(?:011|5\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # Discover
]

# Address patterns (basic)
ADDRESS_PATTERNS = [
    re.compile(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Circle|Cir)\b', re.IGNORECASE),
]

# Zip code patterns
ZIP_CODE_PATTERNS = [
    re.compile(r'\b\d{5}(?:-\d{4})?\b'),  # 12345 or 12345-6789
]

# Date of birth patterns
DOB_PATTERNS = [
    re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'),  # MM/DD/YYYY, MM-DD-YYYY
    re.compile(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b', re.IGNORECASE),  # January 1, 2000
]

# IP address patterns
IP_ADDRESS_PATTERNS = [
    re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),  # IPv4: 192.168.1.1
    re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),  # IPv6
]

# Aadhaar number pattern (India)
AADHAAR_PATTERN = re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b')

# PAN card pattern (India)
PAN_PATTERN = re.compile(r'\b[A-Z]{5}\d{4}[A-Z]\b')

# Passport number patterns (generic)
PASSPORT_PATTERNS = [
    re.compile(r'\b[A-Z]{1,2}\d{6,9}\b'),  # Generic passport format
]

# Driver's license patterns (US - varies by state, this is generic)
DRIVERS_LICENSE_PATTERNS = [
    re.compile(r'\b[A-Z]{1,2}\d{6,8}\b'),
]

# Bank account number patterns (generic)
BANK_ACCOUNT_PATTERNS = [
    re.compile(r'\b\d{8,17}\b'),  # Generic bank account (8-17 digits)
]

# Toxic content keywords (basic list - should be expanded)
TOXIC_KEYWORDS = [
    # Profanity (basic examples - expand as needed)
    # Match word and its variations (fucking, fucked, etc.)
    r'\bfuck',
    r'\bshit',
    r'\bdamn',
    r'\bbitch',
    r'\basshole',
    r'\bbastard',

    # Hate speech indicators (basic examples - expand as needed)
    r'\b(?:hate|kill|murder|attack)\s+(?:all|every|those)\b',

    # Discriminatory language (basic examples - expand as needed)
    r'\b(?:racist|sexist|homophobic|transphobic)\b',
]

# Compile toxic content patterns
TOXIC_CONTENT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE) for pattern in TOXIC_KEYWORDS
]

# Prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    # Ignore previous instructions
    re.compile(r'ignore\s+(?:previous|all|above|prior)\s+(?:instructions|prompts|rules)', re.IGNORECASE),
    
    # System prompts
    re.compile(r'(?:system|admin|root)\s+(?:prompt|instruction|command|mode)', re.IGNORECASE),
    
    # Role manipulation
    re.compile(r'(?:you\s+are|act\s+as|pretend\s+to\s+be)\s+(?:a|an)\s+(?:admin|developer|system|root)', re.IGNORECASE),
    
    # Jailbreak attempts
    re.compile(r'(?:jailbreak|bypass|override|disable)\s+(?:safety|security|filter|guardrail)', re.IGNORECASE),
    
    # DAN (Do Anything Now) prompts
    re.compile(r'\bDAN\b.*(?:mode|prompt|instruction)', re.IGNORECASE),
]

# Jailbreak patterns (more sophisticated attempts)
JAILBREAK_PATTERNS = [
    # Hypothetical scenarios
    re.compile(r'(?:imagine|pretend|hypothetically|in\s+a\s+world\s+where)', re.IGNORECASE),
    
    # Character roleplay
    re.compile(r'(?:roleplay|character|persona).*(?:evil|malicious|harmful)', re.IGNORECASE),
    
    # Encoding tricks
    re.compile(r'(?:base64|rot13|hex|encode|decode)', re.IGNORECASE),
]

# Commitment/promise patterns (things AI shouldn't commit to)
COMMITMENT_PATTERNS = [
    re.compile(r'\b(?:I\s+will|I\s+promise|I\s+guarantee|I\s+assure\s+you)\b', re.IGNORECASE),
    re.compile(r'\b(?:definitely|certainly|absolutely)\s+(?:will|can|shall)\b', re.IGNORECASE),
]

# Pricing/discount patterns (unauthorized commitments)
UNAUTHORIZED_PRICING_PATTERNS = [
    re.compile(r'\b(?:free|discount|offer|deal)\b.*\b(?:\d+%|\$\d+)\b', re.IGNORECASE),
    re.compile(r'\b(?:special\s+price|limited\s+offer|exclusive\s+deal)\b', re.IGNORECASE),
]


def get_all_pii_patterns():
    """
    Get all PII detection patterns.
    
    Returns:
        Dictionary mapping PII type to list of patterns
    """
    return {
        'email': [EMAIL_PATTERN],
        'phone': PHONE_PATTERNS,
        'ssn': SSN_PATTERNS,
        'credit_card': CREDIT_CARD_PATTERNS,
        'address': ADDRESS_PATTERNS,
        'zip_code': ZIP_CODE_PATTERNS,
        'dob': DOB_PATTERNS,
        'ip_address': IP_ADDRESS_PATTERNS,
        'aadhaar': [AADHAAR_PATTERN],
        'pan': [PAN_PATTERN],
        'passport': PASSPORT_PATTERNS,
        'drivers_license': DRIVERS_LICENSE_PATTERNS,
        'bank_account': BANK_ACCOUNT_PATTERNS,
    }


def get_toxic_content_patterns():
    """
    Get all toxic content patterns.
    
    Returns:
        List of compiled regex patterns
    """
    return TOXIC_CONTENT_PATTERNS


def get_prompt_injection_patterns():
    """
    Get all prompt injection patterns.
    
    Returns:
        List of compiled regex patterns
    """
    return PROMPT_INJECTION_PATTERNS


def get_jailbreak_patterns():
    """
    Get all jailbreak patterns.
    
    Returns:
        List of compiled regex patterns
    """
    return JAILBREAK_PATTERNS


def get_commitment_patterns():
    """
    Get all commitment patterns.
    
    Returns:
        List of compiled regex patterns
    """
    return COMMITMENT_PATTERNS


def get_unauthorized_pricing_patterns():
    """
    Get all unauthorized pricing patterns.
    
    Returns:
        List of compiled regex patterns
    """
    return UNAUTHORIZED_PRICING_PATTERNS

