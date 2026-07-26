"""
Sensitive data masking.

Before any retrieved chunk is sent to the Gemini API, it passes through this
module so that PII / secrets never leave the local system in plaintext.

This is a regex-based masker suitable for a prototype. In production this
would typically be backed by a dedicated PII-detection model (e.g. Presidio)
for higher recall, especially on names and addresses.
"""
import re
from dataclasses import dataclass, field


@dataclass
class MaskResult:
    masked_text: str
    redaction_count: int = 0
    categories_found: set = field(default_factory=set)


# Order matters: more specific patterns first so we don't get partial /
# overlapping matches (e.g. credit card before generic long-number patterns).
_PATTERNS = [
    ("EMAIL", re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")),
    (
        "CREDIT_CARD",
        re.compile(r"\b(?:\d[ -]?){13,16}\b"),
    ),
    (
        "SSN",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    ),
    (
        "PHONE",
        re.compile(
            r"(\+?\d{1,3}[-.\s]?)?(\(?\d{2,4}\)?[-.\s]?)\d{3,4}[-.\s]?\d{3,4}\b"
        ),
    ),
    (
        "CLIENT_ID",
        re.compile(r"\b(?:client|cust(?:omer)?|acct|account)[\s_-]?id\s*[:#]?\s*[A-Za-z0-9-]{4,}\b", re.IGNORECASE),
    ),
    (
        "PASSWORD",
        re.compile(r"\bpassword\s*[:=]\s*\S+", re.IGNORECASE),
    ),
    (
        "API_KEY",
        re.compile(r"\b(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9\-_.]{8,}\b", re.IGNORECASE),
    ),
    (
        "IP_ADDRESS",
        re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    ),
    (
        "DOB",
        re.compile(r"\b(0?[1-9]|1[0-2])[/-](0?[1-9]|[12]\d|3[01])[/-](\d{4}|\d{2})\b"),
    ),
]


def mask_text(text: str) -> MaskResult:
    """Replace sensitive substrings with category-labelled placeholders."""
    result_text = text
    categories = set()
    count = 0

    for label, pattern in _PATTERNS:
        def _replace(match, label=label):
            nonlocal count
            count += 1
            categories.add(label)
            return f"[MASKED_{label}]"

        result_text = pattern.sub(_replace, result_text)

    return MaskResult(masked_text=result_text, redaction_count=count, categories_found=categories)


def mask_chunks(chunks: list) -> list:
    """Apply masking to a list of retrieved chunk dicts (in-place safe copy)."""
    masked = []
    for chunk in chunks:
        r = mask_text(chunk.get("text", ""))
        new_chunk = dict(chunk)
        new_chunk["text"] = r.masked_text
        new_chunk["redactions"] = r.redaction_count
        masked.append(new_chunk)
    return masked
