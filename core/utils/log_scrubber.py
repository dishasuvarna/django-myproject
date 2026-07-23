import re

# Lightweight, regex-based PII scrubber for LOGGING/DEBUG OUTPUT ONLY.
#
# This does NOT touch data stored in the database, shown to doctors, or
# sent to Ollama - it only sanitizes text right before it gets printed to
# the terminal/logs, so accidental debug prints never leak real patient
# details (phone numbers, emails, etc.) into log files.
#
# This is intentionally simple (not full Presidio) because extraction and
# AI summarization both run 100% locally via Ollama - no data leaves this
# machine, so the main real-world risk is accidental console/log exposure,
# not third-party data sharing.

_PATTERNS = [
    # Phone numbers (10-digit, with optional separators/country code)
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\d{10}\b"), "[PHONE_REDACTED]"),

    # Email addresses
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL_REDACTED]"),

    # Common ID patterns: sequences of 6+ digits (e.g. patient IDs, Aadhaar-like numbers)
    (re.compile(r"\b\d{6,}\b"), "[ID_REDACTED]"),
]


def scrub_for_log(value):
    """
    Returns a version of `value` with obvious PII patterns replaced by
    placeholders. Safe to use in print()/logging calls. Does NOT modify
    the original value - only use the return value for logging.
    """
    if value is None:
        return value

    text = str(value)
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)

    return text