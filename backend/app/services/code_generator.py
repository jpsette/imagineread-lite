"""
Code Generator Service
Generates unique alphanumeric codes for file transfers.
"""
import secrets
import string
from datetime import datetime


def generate_code(length: int = 8) -> str:
    """
    Generate a unique alphanumeric code.
    
    Uses uppercase letters and digits, excluding ambiguous characters (0, O, I, 1, L)
    for better readability when manually typing.
    
    Args:
        length: Length of the code (default 8)
        
    Returns:
        Alphanumeric code string
    """
    # Remove ambiguous characters for easier manual entry
    alphabet = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_unique_code(existing_codes: set | None = None, length: int = 8) -> str:
    """
    Generate a unique code that doesn't exist in the provided set.
    
    Args:
        existing_codes: Set of existing codes to avoid
        length: Length of the code
        
    Returns:
        Unique alphanumeric code
    """
    if existing_codes is None:
        return generate_code(length)
    
    max_attempts = 100
    for _ in range(max_attempts):
        code = generate_code(length)
        if code not in existing_codes:
            return code
    
    # If we can't find a unique code after max attempts, increase length
    return generate_code(length + 2)


def format_code_for_display(code: str) -> str:
    """
    Format code for display (e.g., ABC1-23XY).
    
    Args:
        code: The raw code
        
    Returns:
        Formatted code with hyphens
    """
    if len(code) <= 4:
        return code
    
    mid = len(code) // 2
    return f"{code[:mid]}-{code[mid:]}"
