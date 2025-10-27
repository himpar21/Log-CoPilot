import re

# Simple regex patterns for common sensitive data
PATTERNS = {
    "ip_address": r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "uuid": r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
}

def mask_sensitive_data(text: str) -> str:
    """Masks common sensitive data patterns in a string."""
    for key, pattern in PATTERNS.items():
        text = re.sub(pattern, f"[{key.upper()}_MASKED]", text)
    return text