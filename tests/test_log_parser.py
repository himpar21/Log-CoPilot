import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.backend.log_parser import (
    parse_apache_log_line,
    parse_keyval_log_line,
    parse_singleline_log_line,
    parse_pretty_log_block
)

# --- 1. Tests for Apache Log Parser ---

def test_parse_valid_apache_log():
    """Tests parsing of the provided Apache log sample."""
    log_line = '10.253.3.41 - - [12/Sep/2025:23:47:22 +0530] "PUT /health HTTP/1.1" 200 1746 "angular-ui-eval-833" "INFO"'
    parsed = parse_apache_log_line(log_line)
    
    assert parsed['ip'] == '10.253.3.41'
    assert parsed['timestamp'] == '12/Sep/2025:23:47:22 +0530'
    assert parsed['request'] == 'PUT /health HTTP/1.1'
    assert parsed['status'] == '200'
    assert parsed['size'] == '1746'
    assert parsed['referrer'] == 'angular-ui-eval-833'
    assert parsed['level'] == 'INFO'

def test_parse_invalid_apache_log():
    """Tests that a non-matching Apache line is returned as raw log."""
    log_line = "This is not a valid apache log"
    parsed = parse_apache_log_line(log_line)
    assert parsed == {"raw_log": log_line}

# --- 2. Tests for Key-Value (logfmt) Parser ---

def test_parse_valid_keyval_log():
    """Tests parsing of the provided key=value log sample."""
    log_line = 'ts=2025-09-13T00:31:43.209576+05:30 pod=dotnet-svc-eval-202 level=WARN event=db_save req=17b75fde-a5e0-4625-893d-2afaf1391cf6 rows=676 status=503'
    parsed = parse_keyval_log_line(log_line)
    
    assert parsed['ts'] == '2025-09-13T00:31:43.209576+05:30'
    assert parsed['pod'] == 'dotnet-svc-eval-202'
    assert parsed['level'] == 'WARN'
    assert parsed['event'] == 'db_save'
    assert parsed['req'] == '17b75fde-a5e0-4625-893d-2afaf1391cf6'
    assert parsed['rows'] == '676'
    assert parsed['status'] == '503'

def test_parse_invalid_keyval_log():
    """Tests that a non-matching key=value line is returned as raw log."""
    log_line = "This is not a keyval log"
    parsed = parse_keyval_log_line(log_line)
    assert parsed == {"raw_log": log_line}

# --- 3. Tests for Single-Line Pipe Parser ---

def test_parse_valid_singleline_log():
    """Tests parsing of the provided pipe-separated log sample."""
    log_line = '2025-09-13T00:15:44.209576+05:30 | orchestrator-eval-64 | DEBUG | event=dispatch | job=job-423 | to=python-infer | attempts=3'
    parsed = parse_singleline_log_line(log_line)
    
    # Check the main fields
    assert parsed['timestamp'] == '2025-09-13T00:15:44.209576+05:30'
    assert parsed['pod'] == 'orchestrator-eval-64'
    assert parsed['level'] == 'DEBUG'
    
    # Check the details that were also parsed from the last part
    assert parsed['event'] == 'dispatch'
    assert parsed['job'] == 'job-423'
    assert parsed['to'] == 'python-infer'
    assert parsed['attempts'] == '3'

def test_parse_invalid_singleline_log():
    """Tests that a non-matching pipe-separated line is returned as raw log."""
    log_line = "This is not a pipe separated log"
    parsed = parse_singleline_log_line(log_line)
    assert parsed == {"raw_log": log_line}

# --- 4. Tests for Pretty Multi-line Block Parser ---

def test_parse_valid_pretty_log_block():
    """Tests parsing of the provided multi-line pretty log block."""
    log_block = """TIMESTAMP: 2025-09-13T00:16:22.209576+05:30
POD: kube-agent-eval-195
LEVEL: INFO
EVENT: kube_event
REASON: Evicted
NODE: node-5"""
    parsed = parse_pretty_log_block(log_block)
    
    # Check for lowercase keys as defined in the parser
    assert parsed['timestamp'] == '2025-09-13T00:16:22.209576+05:30'
    assert parsed['pod'] == 'kube-agent-eval-195'
    assert parsed['level'] == 'INFO'
    assert parsed['event'] == 'kube_event'
    assert parsed['reason'] == 'Evicted'
    assert parsed['node'] == 'node-5'

def test_parse_invalid_pretty_log_block():
    """Tests that a non-matching pretty block is returned as raw log."""
    log_block = "This is not a pretty log block"
    parsed = parse_pretty_log_block(log_block)
    assert parsed == {"raw_log": log_block}

def test_parse_empty_pretty_log_block():
    """Tests that an empty or whitespace-only block is handled."""
    log_block = "\n   \n"
    parsed = parse_pretty_log_block(log_block)
    # The parser returns an empty dict for an empty block, which is correct.
    assert parsed == {}