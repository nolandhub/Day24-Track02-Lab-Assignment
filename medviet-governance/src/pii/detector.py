# src/pii/detector.py
import re
from collections import namedtuple

# Mock RecognizerResult for compatibility
RecognizerResult = namedtuple('RecognizerResult', ['entity_type', 'start', 'end', 'score', 'text'])

class SimpleAnalyzer:
    """Simple regex-based PII analyzer."""
    pass

def build_vietnamese_analyzer():
    """Build simple analyzer without NLP dependency."""
    return SimpleAnalyzer()

def detect_pii(text: str, analyzer) -> list:
    """
    Detect PII using regex patterns.
    """
    results = []

    # CCCD: 12 digits
    for match in re.finditer(r'\b\d{12}\b', text):
        results.append(RecognizerResult(
            entity_type='VN_CCCD',
            start=match.start(),
            end=match.end(),
            score=0.9,
            text=match.group()
        ))

    # Phone: 0[3|5|7|8|9]xxxxxxxx
    for match in re.finditer(r'0[35789]\d{8}', text):
        results.append(RecognizerResult(
            entity_type='VN_PHONE',
            start=match.start(),
            end=match.end(),
            score=0.85,
            text=match.group()
        ))

    # Email
    for match in re.finditer(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
        results.append(RecognizerResult(
            entity_type='EMAIL_ADDRESS',
            start=match.start(),
            end=match.end(),
            score=0.85,
            text=match.group()
        ))

    return results
