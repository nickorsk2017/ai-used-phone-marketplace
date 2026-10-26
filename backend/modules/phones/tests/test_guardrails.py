"""Backend Regex layer of Guardrail 1: docs/ai/GUARDRAILS.md#guardrail-1-phone-saving.

The cases repeat `frontend/utils/__test__/guardrails.test.ts`: both layers apply the same rules.
"""

import pytest

from modules.phones.services.guardrails import find_violations, has_violations, passes_luhn

CLEAN = [
    "iPhone 13 Pro with a 6.1-inch ProMotion display, A15 Bionic chip and a triple 12 MP camera system.",
    "Battery 3095 mAh, 120 Hz, 1080 x 2400, bought in 2023.",
    "There are scuffs and scratches. Screen 6.7 inches, 256 GB.",
    "Galaxy S23 Ultra, 5,000 mAh, 200 MP camera.",
]
BLOCKED = [
    *[
        (text, "card_number")
        for text in ["Pay to 4111 1111 1111 1111", "card 5500-0000-0000-0004 only", "4111111111111111"]
    ],
    *[(text, "phone_number") for text in ["Call me (415) 555-2671", "+1 415 555 2671", "text 415.555.2671"]],
    *[
        (text, "link")
        for text in [
            "See https://example.com/deal",
            "visit www.cheap-phones.net",
            "write to seller@mail.com",
            "t.me/seller",
            "Order on bestdeals.shop now",
        ]
    ],
]


@pytest.mark.parametrize(("text", "violation"), BLOCKED)
def test_blocked_text(text: str, violation: str) -> None:
    assert violation in find_violations(text)


@pytest.mark.parametrize("text", CLEAN)
def test_clean_text(text: str) -> None:
    assert find_violations(text) == set()


def test_luhn() -> None:
    assert passes_luhn("4111111111111111")
    assert not passes_luhn("4111111111111112")


def test_has_violations_checks_every_text() -> None:
    assert has_violations("clean", "call +1 415 555 2671")
    assert not has_violations("clean", "also clean")
