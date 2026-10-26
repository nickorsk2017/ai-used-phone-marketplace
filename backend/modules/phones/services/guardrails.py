"""Backend Regex layer of Guardrail 1: docs/ai/GUARDRAILS.md#guardrail-1-phone-saving.

Same rules and thresholds as `frontend/utils/guardrails.ts`: the Backend does not trust the Frontend.
"""

import re
from typing import Literal

GuardrailViolation = Literal["card_number", "phone_number", "link"]

FLAGS = re.IGNORECASE | re.ASCII
DIGIT_GROUP = re.compile(r"\+?\d[\d\s().-]{5,}\d")
NON_DIGIT = re.compile(r"\D")
LINK_PATTERNS = (
    re.compile(r"\b[a-z][a-z0-9+.-]*://\S+", FLAGS),
    re.compile(r"\bwww\.\S+", FLAGS),
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", FLAGS),
    re.compile(r"\b(?:t\.me|wa\.me|bit\.ly|goo\.gl)/\S*", FLAGS),
    re.compile(
        r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|net|org|io|co|us|info|biz|me|app|shop|store|xyz|link|site|online|ru|ly)"
        r"\b(?:/\S*)?",
        FLAGS,
    ),
)


def passes_luhn(digits: str) -> bool:
    total = 0
    for position, character in enumerate(reversed(digits)):
        digit = int(character)
        if position % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def find_violations(text: str) -> set[GuardrailViolation]:
    found: set[GuardrailViolation] = set()
    for match in DIGIT_GROUP.finditer(text):
        digits = NON_DIGIT.sub("", match.group())
        if 13 <= len(digits) <= 19 and passes_luhn(digits):
            found.add("card_number")
        elif 7 <= len(digits) <= 15:
            found.add("phone_number")
        elif 16 <= len(digits) <= 19:
            found.add("card_number")
    if any(pattern.search(text) for pattern in LINK_PATTERNS):
        found.add("link")
    return found


def has_violations(*texts: str) -> bool:
    return any(find_violations(text) for text in texts)
