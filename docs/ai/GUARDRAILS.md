# GUARDRAILS.md

Protection of user input: toxic content, fraud and Prompt Injection. Antifraud requirement: see [TASK.md](../../TASK.md#business-requirements).

| Guardrail | Where | Blocks |
| --- | --- | --- |
| [Guardrail 1](#guardrail-1-phone-saving) | Phone saving, before the listing is saved | Toxic content, fraud and Prompt Injection |
| [Guardrail 2](#guardrail-2-search-prompt) | Search prompt, before the search LLM call | Prompt Injection |

## Model

The LLM layer of both guardrails uses the OpenAI `gpt-5.6-luna` model. The model is set in the configuration. The final choice is made by the guardrail metrics: see [EVALUATION.md](EVALUATION.md) and [Tradeoffs](#model-choice).

## Guardrail 1: Phone Saving

Applied when a listing is created or updated, before the listing is saved: see [MY_LISTING.md](../features/MY_LISTING.md#add-phone-flow) and [API.md](../backend/API.md). It prevents toxic content, fraud and Prompt Injection from being saved in listings. The listing text is later passed to the search LLM (reranking), so Prompt Injection in a listing would affect the search. If any layer blocks the text, the listing is not saved.

Three layers (rationale: [Tradeoffs](#three-layers-for-phone-saving)):

1. Frontend Regex. Checks for credit card numbers, phone numbers and links to other services.
2. Backend Regex. Checks for credit card numbers, phone numbers and links to other services.
3. LLM Guardrail (OpenAI `gpt-5.6-luna`). Checks for toxic content, for fraud cases that Regex did not catch and for Prompt Injection.

- Checked text: `model_name`, `description` and `condition_note`. `model_code` has a fixed format and `os` is an enum: both are validated by the schema before the guardrails and are not checked by the Regex layers, see [SCHEMAS.md](../backend/SCHEMAS.md#phones-modulesphones). The LLM Guardrail also receives `model_code` as context. The Backend Regex rules are the same as the Frontend Regex rules (`frontend/utils/guardrails.ts`).
- The Backend Regex runs first. A blocked text does not reach the LLM Guardrail.
- LLM output: `{"allowed": false, "category": "toxic" | "fraud" | "prompt_injection" | null}`. The listing text is passed inside delimiters as data.
- A blocked listing returns HTTP 422. The response does not name the layer or the category.
- Fail closed: if the LLM Guardrail call fails after its retries ([RAG.md](RAG.md#errors-and-retries)), the listing is not saved and the endpoint returns HTTP 503.

## Guardrail 2: Search Prompt

The user prompt on the Search page passes Guardrail 2 before the search LLM call: see [RAG.md](RAG.md#architecture). The LLM Guardrail (OpenAI `gpt-5.6-luna`) detects Prompt Injection. A prompt with Prompt Injection is not passed to the search LLM.

- Owned by `modules/rag`, the first node of the search graph.
- LLM output: `{"allowed": false, "category": "prompt_injection" | null}`. The prompt is passed inside delimiters as data.
- A question to the assistant that asks for advice about phones (`What do you think is better, a good camera or a good screen?`) is not Prompt Injection and is allowed: see [RAG.md](RAG.md#clarification).
- A blocked prompt returns HTTP 422. The response does not name the category.
- Fail closed: if the call fails after its retries ([RAG.md](RAG.md#errors-and-retries)), the search is not run and the endpoint returns HTTP 503.

## Tradeoffs

### Three layers for phone saving

The 3 layers remove unnecessary calls and increase reliability if one of the layers fails by mistake. Backend Regex is needed because we cannot trust the Frontend, and API calls can also be made directly without the Frontend app.

### Model choice

OpenAI `gpt-5.6-luna` is the starting model for v1.0. It is replaced if the guardrail metrics in [EVALUATION.md](EVALUATION.md) show missed bad cases or false blocks of clean texts.
