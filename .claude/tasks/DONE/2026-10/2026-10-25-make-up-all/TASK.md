# TASK — 2026-10-25-make-up-all
owner: Engineer
immutable: true

## Requirements
- R1: `make up-all` starts the Frontend dev server and the Backend dev server together in one terminal. Ctrl+C stops both.

## Acceptance
- A1: `make up-all` serves `http://localhost:3000` and `http://localhost:8000/api/health`.
- A2: Ctrl+C leaves no running server on ports 3000 and 8000.
- A3: Works with GNU Make 3.81 (macOS default).

## Constraints
- Reuses the `frontend-dev` and `backend-dev` targets. No new dependencies.
