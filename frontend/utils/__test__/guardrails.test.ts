import { describe, expect, it } from "vitest";
import { findGuardrailViolations } from "@/utils/guardrails";

describe("findGuardrailViolations", () => {
  it.each([
    "iPhone 13 Pro with a 6.1-inch ProMotion display, A15 Bionic chip and a triple 12 MP camera system.",
    "Battery 3095 mAh, 120 Hz, 1080 x 2400, bought in 2023.",
    "There are scuffs and scratches. Screen 6.7 inches, 256 GB.",
    "Galaxy S23 Ultra, 5,000 mAh, 200 MP camera.",
  ])("passes a clean listing text: %s", (text) => {
    expect(findGuardrailViolations(text)).toEqual([]);
  });

  it.each([
    "Pay to 4111 1111 1111 1111",
    "card 5500-0000-0000-0004 only",
    "4111111111111111",
  ])("finds a card number: %s", (text) => {
    expect(findGuardrailViolations(text)).toContain("card_number");
  });

  it.each(["Call me (415) 555-2671", "+1 415 555 2671", "text 415.555.2671"])(
    "finds a phone number: %s",
    (text) => {
      expect(findGuardrailViolations(text)).toContain("phone_number");
    },
  );

  it.each([
    "See https://example.com/deal",
    "visit www.cheap-phones.net",
    "write to seller@mail.com",
    "t.me/seller",
    "Order on bestdeals.shop now",
  ])("finds a link: %s", (text) => {
    expect(findGuardrailViolations(text)).toContain("link");
  });
});
