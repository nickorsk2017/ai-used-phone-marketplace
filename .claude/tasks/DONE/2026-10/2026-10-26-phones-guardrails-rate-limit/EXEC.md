# EXEC — 2026-10-26-phones-guardrails-rate-limit

## v1
exec_version: 1

### Summary
- P1: `phones/schemas/phone.py`: `ModelCode` = strip + uppercase, pattern `^[A-Z0-9-]{2,32}$`.
- P2: `phones/service.check_listing`: regex over `model_code`; `prompts.listing_message` adds `Model code:`. `phones/CLAUDE.md` links GUARDRAILS.md and SCHEMAS.md.
- P3: `main/rate_limit.py`: `phones_description_rate_limit` (1/10 s), `phones_create_rate_limit` (1/10 s), `my_listings_rate_limit` (3/10 s); route-level dependencies in `routers/phones.py`, router-level in `routers/my_listings.py`.
- P4: `phones/tests/test_service.py` (uppercase, format, regex on `model_code`, message content), `main/tests/test_phones.py` (`without_create_limit` for multi-publish tests, invalid `model_code` 422 without the LLM call), `main/tests/test_rate_limit.py` (description 429 + `Retry-After`, create 429 with an independent counter, my-listings: load + reload after publish pass, 4th request 429).
- P5: `useAddPhoneFlow.ts`: `GenerateError` and `SaveError` with `rate_limited` on 429; `AddPhoneModal.tsx`: memoized `generateErrorJSX`, static texts in JSX. `AddPhoneModal.test.tsx`: two 429 cases (170 lines).
- P6: `rag/CLAUDE.md` already links RAG.md#module-interface; signatures match `rag.service`.
- P7: `ruff check`, `ruff format --check`, `pytest` 147 passed, `uv lock --check`; `pnpm lint`, `typecheck`, `test` 86 passed, `build`; anchors 0 broken.

### Changed files
- backend/modules/phones/{schemas/phone.py, service.py, prompts.py, CLAUDE.md, tests/test_service.py}
- backend/modules/main/{rate_limit.py, routers/phones.py, routers/my_listings.py, tests/test_phones.py, tests/test_rate_limit.py}
- frontend/features/my-listings/{useAddPhoneFlow.ts, AddPhoneModal.tsx}, frontend/features/__test__/my-listings/AddPhoneModal.test.tsx
