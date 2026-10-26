# TASK — 2026-10-26-langsmith-eval-tracing
owner: Engineer
immutable: true

## Requirements
- R1: LangSmith settings per docs/backend/DESIGN.md#configuration: `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_ENDPOINT` in `core/tracing.py`, exported to the process environment on startup before the first LLM client. `LANGSMITH_TRACING=true` without `LANGSMITH_API_KEY` is a configuration error of the startup check. `backend/.env.example` lists the variables.
- R2: Tracing per docs/ai/EVALUATION.md#tracing: root runs `rag.search`, `phones.description`, `phones.guardrail`, `rag.embed_listing` with their tags; LangGraph nodes are child spans of `rag.search`; reranker fallback sets `rerank_fallback: true` and the error type on the `rerank` span; no `session` in the trace metadata; tests never send traces.
- R3: `rag.services.parse_prompt(prompt)` per docs/ai/RAG.md#module-interface.
- R4: `backend/eval/` per docs/backend/STRUCTURE.md#eval and docs/ai/EVALUATION.md#datasets: 4 datasets of 10 to 20 cases, targets, code evaluators, upload to `<LANGSMITH_PROJECT>.<dataset>` with example replacement on change, LangSmith experiments, results table per docs/ai/EVALUATION.md#run.
- R5: `make eval` and `make eval DATASET=<name>` per docs/ai/EVALUATION.md#run, listed in `make help`. `eval/tests` run in `make backend-test`.
- R6: `backend/modules/rag/CLAUDE.md`, `backend/modules/phones/CLAUDE.md` link the changed docs where needed.

## Acceptance
- A1: `make backend-test` passes. `ruff check`, `ruff format --check` pass.
- A2: Backend tests: settings export to the environment; tracing on without the key fails the startup check; tracing off by default; root run names and tags of R2 (LangSmith calls stubbed, no network); rerank fallback metadata; `parse_prompt` returns `ParsedPrompt` and repeats once on an invalid output.
- A3: `eval/tests`: every dataset has 10 to 20 valid cases; `description` cases match the seed listings; each evaluator gives the documented 1/0 on positive and negative examples, including `null` = absent and the specification tolerances.
- A4: All Markdown anchor links in `docs/`, `CLAUDE.md` and `backend/modules/*/CLAUDE.md` resolve.

## Constraints
- docs/ are already updated and are the source of truth for this task.
- `make eval` is not run by the Validator (CLAUDE.md#validator). The Engineer runs it with real keys.
- No API, schema, prompt or frontend changes.
- Out of scope: DeepEval ranking metrics, CI eval gate, trace sampling.
