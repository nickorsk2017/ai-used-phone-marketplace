# TASK — 2026-10-25-backend-fastapi-min-version
owner: Engineer
immutable: true

## Requirements
- R1: `modules/main` requires FastAPI from the second latest release: `fastapi>=0.161.1` (latest 0.162.0). Covers `Depends(scope="function")` (D2 of 2026-10-25-backend-shared-session-health).

## Acceptance
- A1: `uv lock --check` passes, resolved FastAPI version unchanged, `pytest` passes.

## Constraints
- No other dependency changes.
