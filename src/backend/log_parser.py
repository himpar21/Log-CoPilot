import os
import json
import re
from typing import List, Dict, Any
from langchain_core.documents import Document

# Regex for Apache log format
APACHE_LOG_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+) - - \[(?P<timestamp>.*?)\] "(?P<request>.*?)" (?P<status>\d{3}) (?P<size>\d+) "(?P<referrer>.*?)" "(?P<level>.*?)"'
)

# Regex for key-value format logs (key1=value1 key2=value2 ...)
KEYVAL_PATTERN = re.compile(r'(\w+)=([\w\-\.:+]+)')

# Regex for single-line pipe-separated logs
# Example: 2025-09-13T00:15:44.209576+05:30 | orchestrator-eval-64 | DEBUG | event=dispatch | job=job-423 | to=python-infer | attempts=3
SINGLELINE_PATTERN = re.compile(
    r'^(?P<timestamp>[^\|]+)\s*\|\s*(?P<pod>[^\|]+)\s*\|\s*(?P<level>[^\|]+)\s*\|\s*(?P<details>.*)$'
)

def parse_apache_log_line(line: str) -> Dict[str, Any]:
    """Parses a single Apache log line into a structured dictionary."""
    match = APACHE_LOG_PATTERN.match(line)
    if match:
        return match.groupdict()
    return {"raw_log": line}

def parse_keyval_log_line(line: str) -> Dict[str, Any]:
    """Parses key=value style log lines."""
    matches = KEYVAL_PATTERN.findall(line)
    if matches:
        return {k: v for k, v in matches}
    return {"raw_log": line}

def parse_singleline_log_line(line: str) -> Dict[str, Any]:
    """Parses pipe-separated single line logs."""
    if not line:
        return {}

    match = SINGLELINE_PATTERN.match(line)
    if not match:
        return {"raw_log": line}

    data = {k: v.strip() if isinstance(v, str) else v for k, v in match.groupdict().items()}
    
    # Further split key=value pairs in the 'details' part
    details = dict((k.strip(), v.strip()) for k, v in KEYVAL_PATTERN.findall(data.pop("details", "")))
    
    return {**data, **details}

def parse_pretty_log_block(block: str) -> Dict[str, Any]:
    """
    Parses pretty formatted logs like:
        TIMESTAMP: 2025-09-13T00:16:22.209576+05:30
        POD: kube-agent-eval-195
        LEVEL: INFO
        EVENT: kube_event
        REASON: Evicted
        NODE: node-5
    """
    if not block or not block.strip():
        return {}

    data = {}
    for line in block.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().lower()] = value.strip()
    
    return data if data else {"raw_log": block}


def load_and_parse_logs(directory: str) -> List[Document]:
    """
    Loads and parses all log files from a directory, creating LangChain Documents.
    Handles .jsonl, .apache, .log, and other formats gracefully.
    """
    documents = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # JSON Lines logs
                    if file.endswith('.jsonl'):
                        for i, line in enumerate(content.splitlines()):
                            try:
                                data = json.loads(line)
                                documents.append(Document(
                                    page_content=json.dumps(data, indent=2),
                                    metadata={"source": file, "line": i + 1}
                                ))
                            except json.JSONDecodeError:
                                continue

                    # Apache logs
                    elif file.endswith('.apache') or "apache" in file:
                        for i, line in enumerate(content.splitlines()):
                            parsed = parse_apache_log_line(line)
                            documents.append(Document(
                                page_content=json.dumps(parsed, indent=2),
                                metadata={"source": file, "line": i + 1}
                            ))

                    # Pretty logs (multi-line blocks starting with TIMESTAMP:)
                    elif "pretty" in file:
                        blocks = re.split(r'\n\s*\n', content.strip())  # split by blank lines
                        for i, block in enumerate(blocks):
                            parsed = parse_pretty_log_block(block)
                            documents.append(Document(
                                page_content=json.dumps(parsed, indent=2),
                                metadata={"source": file, "block": i + 1}
                            ))

                    # Key-value logs
                    elif "keyval" in file:
                        for i, line in enumerate(content.splitlines()):
                            parsed = parse_keyval_log_line(line)
                            documents.append(Document(
                                page_content=json.dumps(parsed, indent=2),
                                metadata={"source": file, "line": i + 1}
                            ))

                    # Single-line pipe logs
                    elif "singleline" in file:
                        for i, line in enumerate(content.splitlines()):
                            parsed = parse_singleline_log_line(line)
                            documents.append(Document(
                                page_content=json.dumps(parsed, indent=2),
                                metadata={"source": file, "line": i + 1}
                            ))

                    # Fallback: generic line-by-line parsing
                    else:
                        for i, line in enumerate(content.splitlines()):
                            if line.strip():
                                documents.append(Document(
                                    page_content=line.strip(),
                                    metadata={"source": file, "line": i + 1}
                                ))

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    return documents
