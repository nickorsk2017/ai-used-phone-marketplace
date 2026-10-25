/**
 * Frontend Regex layer of Guardrail 1: docs/ai/GUARDRAILS.md#guardrail-1-phone-saving.
 * The Backend repeats the check, this layer only saves a request.
 */
export type GuardrailViolation = "card_number" | "phone_number" | "link";

const DIGIT_GROUP = /\+?\d[\d\s().-]{5,}\d/g;

const LINK_PATTERNS = [
  /\b[a-z][a-z0-9+.-]*:\/\/\S+/i,
  /\bwww\.\S+/i,
  /\b[\w.+-]+@[\w-]+\.[\w.-]+\b/i,
  /\b(?:t\.me|wa\.me|bit\.ly|goo\.gl)\/\S*/i,
  /\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|net|org|io|co|us|info|biz|me|app|shop|store|xyz|link|site|online|ru|ly)\b(?:\/\S*)?/i,
];

function passesLuhn(digits: string): boolean {
  let sum = 0;
  let double = false;
  for (let index = digits.length - 1; index >= 0; index -= 1) {
    let digit = Number(digits[index]);
    if (double) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    sum += digit;
    double = !double;
  }
  return sum % 10 === 0;
}

export function findGuardrailViolations(text: string): GuardrailViolation[] {
  const found = new Set<GuardrailViolation>();

  for (const match of text.matchAll(DIGIT_GROUP)) {
    const digits = match[0].replace(/\D/g, "");
    if (digits.length >= 13 && digits.length <= 19 && passesLuhn(digits)) {
      found.add("card_number");
    } else if (digits.length >= 7 && digits.length <= 15) {
      found.add("phone_number");
    } else if (digits.length >= 16 && digits.length <= 19) {
      found.add("card_number");
    }
  }

  if (LINK_PATTERNS.some((pattern) => pattern.test(text))) {
    found.add("link");
  }

  return [...found];
}

export function hasGuardrailViolations(text: string): boolean {
  return findGuardrailViolations(text).length > 0;
}
