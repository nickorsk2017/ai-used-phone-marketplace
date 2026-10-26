# TASK — 2026-10-26-phones-guardrails-rate-limit
owner: Engineer
immutable: true

## Requirements
- R1: `model_code` per docs/backend/SCHEMAS.md#phones-modulesphones: uppercase conversion and format `^[A-Z0-9-]{2,32}$` in `PhoneDescription` (description response and `POST /api/phones` body).
- R2: Guardrail 1 per docs/ai/GUARDRAILS.md#guardrail-1-phone-saving: `model_code` added to the Backend Regex check and to the LLM Guardrail message.
- R3: Rate limits per docs/INFRA.md#application: `POST /api/phones/description` and `POST /api/phones`, 1 request per 10 seconds per client IP, one counter per endpoint, 429 with `Retry-After`. `GET /api/my-listings` not limited.
- R4: Frontend per docs/features/MY_LISTING.md#add-phone-flow: HTTP 429 on the description generation and on publish shows `Too many requests. Wait 10 seconds and try again.`, the entered data is kept.
- R5: `backend/modules/phones/CLAUDE.md` and `backend/modules/rag/CLAUDE.md` link the changed docs where needed. docs/ai/RAG.md#module-interface matches `rag.service`.

## Acceptance
- A1: `make backend-test` passes. `ruff check`, `ruff format --check` pass.
- A2: Backend tests: lowercase `model_code` converted, invalid `model_code` 422 on `POST /api/phones`, `model_code` with a link or a phone number blocked by Guardrail 1, `model_code` present in the LLM Guardrail message, second request within 10 s 429 with `Retry-After` on each limited endpoint, counters of the two endpoints independent, `GET /api/my-listings` after `POST /api/phones` not limited.
- A3: Frontend `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build` pass. Tests: 429 texts on generation and on publish.
- A4: All Markdown anchor links in `docs/`, `CLAUDE.md` and `backend/modules/*/CLAUDE.md` resolve.

## Constraints
- docs/ and CLAUDE.md#validator are already updated and are the source of truth for this task.
- `make eval` is not run (CLAUDE.md#validator).
- Out of scope: rate limits of `/api/search` and `/api/phones/{id}/contact`, shared counter storage.
