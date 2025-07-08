# app/utils/password.py
"""Password security utilities."""

import bcrypt
import secrets
import string
import re
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class PasswordError(Exception):
    """Password related error."""
    pass


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    try:
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise PasswordError("Failed to hash password")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def validate_password_strength(password: str) -> Tuple[bool, list]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Length check
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    
    # Uppercase letter check
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Lowercase letter check
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Digit check
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    # Special character check
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append("Password must contain at least one special character")
    
    # Common password patterns (basic check)
    common_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
        r'admin',
        r'letmein'
    ]
    
    password_lower = password.lower()
    for pattern in common_patterns:
        if re.search(pattern, password_lower):
            errors.append("Password contains common patterns and is not secure")
            break
    
    # Sequential characters check
    if has_sequential_chars(password):
        errors.append("Password should not contain sequential characters")
    
    # Repeated characters check
    if has_repeated_chars(password):
        errors.append("Password should not contain too many repeated characters")
    
    return len(errors) == 0, errors


def has_sequential_chars(password: str, min_length: int = 3) -> bool:
    """
    Check for sequential characters in password.
    
    Args:
        password: Password to check
        min_length: Minimum length of sequential characters
        
    Returns:
        True if sequential characters found
    """
    password_lower = password.lower()
    
    # Check for sequential letters
    for i in range(len(password_lower) - min_length + 1):
        is_sequential = True
        for j in range(min_length - 1):
            if ord(password_lower[i + j + 1]) - ord(password_lower[i + j]) != 1:
                is_sequential = False
                break
        if is_sequential:
            return True
    
    # Check for sequential numbers
    for i in range(len(password) - min_length + 1):
        if password[i:i + min_length].isdigit():
            nums = [int(c) for c in password[i:i + min_length]]
            is_sequential = True
            for j in range(len(nums) - 1):
                if nums[j + 1] - nums[j] != 1:
                    is_sequential = False
                    break
            if is_sequential:
                return True
    
    return False


def has_repeated_chars(password: str, max_repeat: int = 3) -> bool:
    """
    Check for too many repeated characters.
    
    Args:
        password: Password to check
        max_repeat: Maximum allowed repeated characters
        
    Returns:
        True if too many repeated characters found
    """
    char_count = 1
    prev_char = password[0] if password else ''
    
    for char in password[1:]:
        if char.lower() == prev_char.lower():
            char_count += 1
            if char_count > max_repeat:
                return True
        else:
            char_count = 1
            prev_char = char
    
    return False


def generate_secure_password(length: int = 12) -> str:
    """
    Generate a secure random password.
    
    Args:
        length: Password length (minimum 8)
        
    Returns:
        Generated secure password
    """
    if length < 8:
        length = 8
    
    # Ensure password contains all required character types
    password_chars = []
    
    # Add at least one of each required type
    password_chars.append(secrets.choice(string.ascii_uppercase))
    password_chars.append(secrets.choice(string.ascii_lowercase))
    password_chars.append(secrets.choice(string.digits))
    password_chars.append(secrets.choice('!@#$%^&*()_+-=[]{}|;:,.<>?'))
    
    # Fill remaining length with random characters
    all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
    for _ in range(length - 4):
        password_chars.append(secrets.choice(all_chars))
    
    # Shuffle the password
    secrets.SystemRandom().shuffle(password_chars)
    
    return ''.join(password_chars)


def estimate_password_strength(password: str) -> dict:
    """
    Estimate password strength and provide score.
    
    Args:
        password: Password to analyze
        
    Returns:
        Dictionary with strength analysis
    """
    score = 0
    feedback = []
    
    # Length scoring
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    # Character variety scoring
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        score += 1
    
    # Penalty for common patterns
    if has_sequential_chars(password):
        score -= 1
        feedback.append("Avoid sequential characters")
    
    if has_repeated_chars(password):
        score -= 1
        feedback.append("Avoid repeated characters")
    
    # Determine strength level
    if score <= 2:
        strength = "weak"
        color = "red"
    elif score <= 4:
        strength = "fair"
        color = "orange"
    elif score <= 6:
        strength = "good"
        color = "yellow"
    else:
        strength = "strong"
        color = "green"
    
    return {
        "score": max(0, score),
        "max_score": 7,
        "strength": strength,
        "color": color,
        "feedback": feedback,
        "percentage": int((max(0, score) / 7) * 100)
    }