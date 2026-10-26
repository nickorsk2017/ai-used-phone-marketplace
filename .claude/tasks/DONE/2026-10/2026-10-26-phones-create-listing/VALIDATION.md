# VALIDATION — 2026-10-26-phones-create-listing

## v1
validation_version: 1
result: FAIL

### Checks
- A1: `ruff check`, `ruff format --check`, `pytest` 132 passed (PostgreSQL 16, pgvector 0.8.1), no real OpenAI calls: PASS.
- A2: all listed cases present in `phones/tests`, `rag/tests`, `main/tests/test_phones.py`, `main/tests/test_transaction_retry.py`: PASS.
- A3: `downgrade base`, `upgrade head`, `check`, `downgrade base`, `upgrade head`: PASS.
- A4: `pnpm lint`, `typecheck`, `test` 84 passed, `build`; second `GET /api/my-listings` asserted: PASS.
- A5: 0 broken anchors: PASS.
- R1-R9: PASS except L1.

### Issues
- L1: {type: logic, severity: high, ref: docs/backend/DESIGN.md#database-connection, note: `POST /api/phones/description` and `POST /api/phones` depend on `CurrentUser` -> `DbSession`; the request transaction stays open (idle in transaction) during the LLM Guardrail, description and embedding calls. DESIGN.md: slow calls run so that the request does not hold a connection while it waits. Fix: authenticate these endpoints in a short transaction that is closed before the slow calls.}
- L2: {type: logic, severity: low, ref: docs/backend/STRUCTURE.md#domain-module, note: `modules/phones/pyproject.toml` declares `pydantic-settings`; a domain module has no settings. Remove the dependency.}

### Discrepancies (CLAUDE.md#1), non-blocking
- D1: CLAUDE.md#validator requires `make eval` for AI step changes; docs/ai/EVALUATION.md#run describes it, `Makefile` has no `eval` target and no eval suite exists. Not run. Fix (Engineer): a separate task for the eval suite, or mark `make eval` as planned in EVALUATION.md.
- D2: docs/ai/RAG.md#module-interface: `index(phone)`. Code: `index(session, phone, embedding)` (embedding computed before the transaction per DESIGN.md#transaction-retry). Fix: RAG.md `embed_listing(...)` + `index(session, phone, embedding)`.
- D3: docs/features/MY_LISTING.md#description-response: `model_code`, `model_name`, `os` "saved as returned". `POST /api/phones` takes them from the client, so a direct API call can store any model code. Fix (Engineer): note the limitation in MY_LISTING.md Tradeoffs, or a server-side cache of generated descriptions (ROADMAP.md#production-baseline).
- D4: docs/INFRA.md#application plans limits for `/api/phones/description` and `POST /api/phones`; none exist yet (out of scope of this task).

## v2
validation_version: 2
result: PASS

### Checks
- L1: `POST /api/phones/description`, `POST /api/phones` on `CurrentUserShortSession`; pool checked-out connections during the LLM calls = 0, the test fails with `CurrentUser`: PASS.
- L2: no `pydantic-settings` in `modules/phones`; `uv sync --locked`: PASS.
- A1: `ruff check`, `ruff format --check`, `pytest` 133 passed: PASS.
- A3: `downgrade base`, `upgrade head`, `check`, `downgrade base`, `upgrade head`: PASS.
- A4: `pnpm typecheck`, `pnpm test` 84 passed (Frontend unchanged since v1, lint and build PASS in v1): PASS.
- A5: 0 broken anchors: PASS.
- Module calls: `main` -> `phones.service`, `rag.service`; no imports between `phones` and `rag`: PASS.

### Discrepancies
- D1-D4 of v1 stay open for the Engineer.
