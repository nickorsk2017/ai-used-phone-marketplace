"""Search prompt delimiters, shared by the guardrail and parse prompts."""

PROMPT_DELIMITER = "<<<SEARCH_PROMPT>>>"


def prompt_message(prompt: str) -> str:
    return f"{PROMPT_DELIMITER}\n{prompt}\n{PROMPT_DELIMITER}"
