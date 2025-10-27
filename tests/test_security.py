
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest

from src.backend.security import mask_sensitive_data
from src.backend.log_parser import (
    parse_apache_log_line,
    parse_keyval_log_line,
    parse_singleline_log_line,
    parse_pretty_log_block
)
import json

def test_mask_sensitive_data_raw():
    """Test masking of IP, email, and UUID in plain text."""
    text = "User 192.168.1.1 with email test@example.com and ID f47ac10b-58cc-4372-a567-0e02b2c3d479"
    masked = mask_sensitive_data(text)

    assert "[IP_ADDRESS_MASKED]" in masked
    assert "[EMAIL_MASKED]" in masked
    assert "[UUID_MASKED]" in masked
    assert "192.168.1.1" not in masked
    assert "test@example.com" not in masked

def test_mask_in_apache_log():
    """Ensure masking works inside Apache log strings."""
    log_line = '192.168.1.1 - - [13/Sep/2025:12:01:44 +0530] "GET /api HTTP/1.1" 200 1234 "-" "test@example.com"'
    masked = mask_sensitive_data(log_line)

    assert "[IP_ADDRESS_MASKED]" in masked
    assert "[EMAIL_MASKED]" in masked
    assert "192.168.1.1" not in masked
    assert "test@example.com" not in masked

def test_mask_in_keyval_log():
    """Ensure masking works in key=value log format."""
    log_line = "user_id=f47ac10b-58cc-4372-a567-0e02b2c3d479 ip=192.168.1.1 email=test@example.com"
    masked = mask_sensitive_data(log_line)

    assert "[UUID_MASKED]" in masked
    assert "[IP_ADDRESS_MASKED]" in masked
    assert "[EMAIL_MASKED]" in masked

def test_mask_in_singleline_log():
    """Ensure masking works in single-line pipe logs."""
    log_line = "2025-09-13T00:15:44.209576+05:30 | orchestrator | INFO | email=test@example.com | ip=192.168.1.1"
    masked = mask_sensitive_data(log_line)

    assert "[EMAIL_MASKED]" in masked
    assert "[IP_ADDRESS_MASKED]" in masked

def test_mask_in_pretty_log():
    """Ensure masking works in pretty (multi-line) logs."""
    log_block = """
    TIMESTAMP: 2025-09-13T00:15:44.209576+05:30
    POD: pod-123
    USER_EMAIL: test@example.com
    CLIENT_IP: 192.168.1.1
    SESSION: f47ac10b-58cc-4372-a567-0e02b2c3d479
    """
    masked = mask_sensitive_data(log_block)

    assert "[EMAIL_MASKED]" in masked
    assert "[IP_ADDRESS_MASKED]" in masked
    assert "[UUID_MASKED]" in masked
