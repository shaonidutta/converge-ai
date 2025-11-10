"""
Text processing utilities for guardrails.

This module provides utilities for text normalization, tokenization, and cleaning.
"""

import re
from typing import List


def normalize_text(text: str) -> str:
    """
    Normalize text for processing.
    
    - Converts to lowercase
    - Removes extra whitespace
    - Strips leading/trailing whitespace
    
    Args:
        text: Text to normalize
    
    Returns:
        Normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def clean_text(text: str) -> str:
    """
    Clean text by removing special characters and extra whitespace.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    """
    # Remove special characters (keep alphanumeric, spaces, and basic punctuation)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def tokenize(text: str) -> List[str]:
    """
    Tokenize text into words.
    
    Args:
        text: Text to tokenize
    
    Returns:
        List of tokens (words)
    """
    # Simple word tokenization (split on whitespace and punctuation)
    tokens = re.findall(r'\b\w+\b', text.lower())
    return tokens


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
    
    Returns:
        Number of words
    """
    return len(tokenize(text))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated (default: "...")
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Truncate and add suffix
    return text[:max_length - len(suffix)] + suffix


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Text containing URLs
    
    Returns:
        Text with URLs removed
    """
    # Remove http/https URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove www URLs
    text = re.sub(r'www\.\S+', '', text)
    
    return text


def remove_extra_whitespace(text: str) -> str:
    """
    Remove extra whitespace from text.
    
    Args:
        text: Text with extra whitespace
    
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

