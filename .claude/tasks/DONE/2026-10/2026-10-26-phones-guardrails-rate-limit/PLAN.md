# PLAN — 2026-10-26-phones-guardrails-rate-limit

## v1
plan_version: 1

### Steps
- P1 (R1): `modules/phones/schemas/phone.py`: `ModelCode` with a before-validator (strip, uppercase) and the pattern of SCHEMAS.md; max length from the model constant. Migration not needed: column is `String(64)`, the rule is narrower.
- P2 (R2): `service.check_listing`: regex over `model_code` too; `prompts.listing_message` includes `Model code:`. `phones/CLAUDE.md`: checked fields link GUARDRAILS.md.
- P3 (R3): `modules/main/rate_limit.py`: two instances `phones_description_rate_limit`, `phones_create_rate_limit` (1 per 10 s). `routers/phones.py`: route-level `dependencies=[Depends(...)]` on each endpoint, resolved before `CurrentUserShortSession` and the LLM calls. `routers/my_listings.py` unchanged.
- P4 (A1, A2): tests. Existing tests that call `POST /api/phones` more than once per test override `phones_create_rate_limit` through `app.dependency_overrides`. New: `phones/tests` (model code conversion, format, guardrail on `model_code`, message content), `main/tests/test_rate_limit.py` (both endpoints, `Retry-After`, independent counters, `GET /api/my-listings` after publish).
- P5 (R4, A3): Frontend: `useAddPhoneFlow` maps 429 on generation to a rate-limit state and on publish to `SaveError` `rate_limited`; `AddPhoneModal` shows the MY_LISTING.md text. Status constant next to `VALIDATION_ERROR_STATUS`. `AddPhoneModal.test.tsx`: both 429 cases (file stays under 200 lines; otherwise split the 429 cases into `AddPhoneModalErrors.test.tsx`).
- P6 (R5): `rag/CLAUDE.md` link to RAG.md#module-interface; check against `rag.service` signatures.
- P7 (A1-A4): `ruff`, `pytest`, `uv lock --check`, `pnpm lint typecheck test build`, anchor check.

### Order
P1 -> P2 -> P3 -> P4 -> P5 -> P6 -> P7.

### Risks
- One request per 10 s on `POST /api/phones`: a fast retry after 422 or 503 gets 429. Accepted by INFRA.md; the 429 text tells the user to wait.
- Several Uvicorn workers keep separate counters (INFRA.md#application).
- A stricter `model_code` makes LLM output with a non-matching code invalid: one repeated call, then 503 (RAG.md#errors-and-retries).

## v2
plan_version: 2
change: Engineer feedback on R3: `GET /api/my-listings` limited to 3 requests per 10 s per client IP, own counter (docs/INFRA.md#application updated; docs win over TASK.md R3 "not limited"). Only P3, P4, P5 change, other steps as in v1.

### Steps
- P3 (R3): as v1, plus `my_listings_rate_limit` (3 per 10 s) on `routers/my_listings.py`.
- P4 (A1, A2): as v1; the A2 case "`GET /api/my-listings` after `POST /api/phones` not limited" becomes: page load + reload after publish pass, the 4th request within 10 s returns 429. Existing tests with more than 3 `GET /api/my-listings` per test override `my_listings_rate_limit`.
- P5 (R4, A3): as v1; `MyListingsPage` load error on 429 keeps the existing list error state (no new text in MY_LISTING.md).
