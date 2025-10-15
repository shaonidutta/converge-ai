"""
Password management utilities
Secure password hashing, validation, and strength checking
"""

from passlib.context import CryptContext
from typing import Optional
import re
import secrets
import string


# Password hashing context using bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Cost factor for bcrypt (higher = more secure but slower)
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
        
    Example:
        >>> hashed = hash_password("MySecurePassword123!")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("MyPassword123!")
        >>> verify_password("MyPassword123!", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def check_password_strength(password: str) -> dict:
    """
    Check password strength and return detailed feedback
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to check
        
    Returns:
        dict: {
            "is_strong": bool,
            "score": int (0-5),
            "feedback": list of str,
            "requirements_met": dict
        }
        
    Example:
        >>> result = check_password_strength("Weak")
        >>> print(result["is_strong"])
        False
        >>> print(result["feedback"])
        ['Password must be at least 8 characters long', ...]
    """
    feedback = []
    score = 0
    requirements_met = {
        "min_length": False,
        "has_uppercase": False,
        "has_lowercase": False,
        "has_digit": False,
        "has_special": False,
    }
    
    # Check minimum length
    if len(password) >= 8:
        requirements_met["min_length"] = True
        score += 1
    else:
        feedback.append("Password must be at least 8 characters long")
    
    # Check for uppercase letter
    if re.search(r"[A-Z]", password):
        requirements_met["has_uppercase"] = True
        score += 1
    else:
        feedback.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letter
    if re.search(r"[a-z]", password):
        requirements_met["has_lowercase"] = True
        score += 1
    else:
        feedback.append("Password must contain at least one lowercase letter")
    
    # Check for digit
    if re.search(r"\d", password):
        requirements_met["has_digit"] = True
        score += 1
    else:
        feedback.append("Password must contain at least one digit")
    
    # Check for special character
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        requirements_met["has_special"] = True
        score += 1
    else:
        feedback.append("Password must contain at least one special character (!@#$%^&*...)")
    
    # Additional checks for very strong passwords
    if len(password) >= 12:
        score += 0.5
    if len(password) >= 16:
        score += 0.5
    
    is_strong = score >= 5
    
    return {
        "is_strong": is_strong,
        "score": int(score),
        "feedback": feedback if not is_strong else ["Password is strong"],
        "requirements_met": requirements_met,
    }


def validate_password(password: str, min_length: int = 8) -> tuple[bool, Optional[str]]:
    """
    Validate password meets minimum requirements
    
    Args:
        password: Password to validate
        min_length: Minimum password length (default: 8)
        
    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
        
    Example:
        >>> is_valid, error = validate_password("weak")
        >>> print(is_valid)
        False
        >>> print(error)
        'Password must be at least 8 characters long'
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    strength = check_password_strength(password)
    
    if not strength["is_strong"]:
        return False, "; ".join(strength["feedback"])
    
    return True, None


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure random password
    
    Args:
        length: Length of password (default: 16)
        
    Returns:
        str: Secure random password
        
    Example:
        >>> password = generate_secure_password(16)
        >>> print(len(password))
        16
        >>> strength = check_password_strength(password)
        >>> print(strength["is_strong"])
        True
    """
    if length < 8:
        length = 8
    
    # Ensure password contains all required character types
    uppercase = secrets.choice(string.ascii_uppercase)
    lowercase = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("!@#$%^&*")
    
    # Fill remaining length with random characters
    remaining_length = length - 4
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*"
    remaining = ''.join(secrets.choice(all_chars) for _ in range(remaining_length))
    
    # Combine and shuffle
    password_chars = list(uppercase + lowercase + digit + special + remaining)
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)


def generate_reset_token(length: int = 32) -> str:
    """
    Generate a secure token for password reset
    
    Args:
        length: Length of token (default: 32)
        
    Returns:
        str: Secure random token (URL-safe)
        
    Example:
        >>> token = generate_reset_token()
        >>> print(len(token))
        32
    """
    return secrets.token_urlsafe(length)


# Export
__all__ = [
    "hash_password",
    "verify_password",
    "check_password_strength",
    "validate_password",
    "generate_secure_password",
    "generate_reset_token",
]

