# PLAN — 2026-10-26-langsmith-eval-tracing

## v1
plan_version: 1

### Steps
- P1 (R1): `backend/pyproject.toml`: explicit `langsmith>=0.14` (already in `uv.lock` as a transitive dependency of `langchain-core`), `uv lock`. `core/tracing.py`: `TracingSettings` on `ENV_FILE` (fields of DESIGN.md#configuration, model validator: tracing on requires the key), `get_settings` with `lru_cache`, `config_errors`, `configure_tracing(force=False)`: writes `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_ENDPOINT` (only when set) to `os.environ`; `force=True` (eval) turns tracing on and requires the key. `modules/main/app.py`: `check_config` adds the tracing errors; `create_app` calls `configure_tracing()` right after `check_config`, before routers import clients. `.env.example`: the 4 variables with a comment line linking EVALUATION.md#tracing.
- P2 (R2, tests never trace): `conftest.py` sets `LANGSMITH_TRACING=false` and `LANGCHAIN_TRACING_V2=false` before the app import, next to `OPENAI_API_KEY`. `test_config.py`: `no_env` also clears the LangSmith variables and `TracingSettings.env_file`.
- P3 (R2): root runs with `langsmith.traceable(name=..., tags=[...])`: `phones.generate_description` -> `phones.description`, `phones.check_listing` -> `phones.guardrail`, `rag.embed_listing` -> `rag.embed_listing`. LangChain child runs nest under the traceable context. `rag.search`: `graph.run` passes `run_name="rag.search"`, `tags=["rag"]` in the run config; nodes stay child spans. `session` stays in `configurable`: LangChain copies only primitive configurable values to metadata, verified by a test (A2).
- P4 (R2): `graph.rerank` fallback branch: `langsmith.get_current_run_tree()`; when present, add metadata `rerank_fallback=True`, `rerank_error=<exception class name>`. No-op when tracing is off. Logging unchanged.
- P5 (R3): `modules/rag/services/ai.py`: `parse_prompt(prompt)` via `core.llm.llm_call` with `get_search_model()`, `ParsedPrompt`, `PARSE_SYSTEM`, `prompt_message(prompt)`; traced as `rag.parse` with tag `rag`. Re-exported in `rag/services/__init__.py`. Graph node `parse` unchanged (RetryPolicy), so the search pipeline behaviour does not change.
- P6 (R4): `backend/eval/`:
  - `schemas.py`: `ParseCase`, `ClarificationCase`, `DescriptionCase`, `HallucinatedCase` (Pydantic; expected fields optional, explicit `None` = must be absent via `model_fields_set`).
  - `datasets/parse.py` (15 cases: condition, price operators and ranges, OS, `null` cases), `datasets/clarification.py` (16: 6 no-criteria, 4 advice, 6 search prompts incl. listing questions), `datasets/description.py` (15 model names picked from `seed.run.LISTINGS` by `model_code`, expected data read from the seed, across brands and years), `datasets/hallucinated_models.py` (10 non-existent names).
  - `targets.py`: `parse` and `clarification` -> `rag.services.parse_prompt`; `description` and `hallucinated_models` -> `phones.services.generate_description`. Output dict; an invalid output after the retry is caught and returned as `{"error": <class>}` so `valid output` scores 0 instead of aborting the experiment.
  - `evaluators.py`: pure functions `(outputs, reference_outputs) -> {"key", "score"}` per EVALUATION.md#datasets: valid output, condition (set equality), price (operator, value, max_value), OS, clarification expected, `model_code`, `os`, specifications close (camera equal, battery <=5%, display <=0.1), no description.
  - `upload.py`: dataset `<project>.<name>`; create if missing; content hash of the cases in the dataset metadata; on a different hash delete the examples and create the new ones (dataset and experiments kept).
  - `run.py`: `python -m eval.run [--dataset NAME]`. `configure_tracing(force=True)`, upload, `langsmith.aevaluate(target, data=dataset, evaluators, experiment_prefix=<name>, metadata={models from phones/rag settings}, max_concurrency=4)`. Table to stdout: dataset, evaluator, score; target p50/p95 latency from run start/end of the results; tokens and cost from `client.read_project(<experiment>, include_stats=True)` after the results are flushed. Exit code 1 when an upload or experiment fails, 0 otherwise (scores are reported, not gated, EVALUATION.md#run).
  - `__init__.py` files; `eval` is a plain package like `seed`.
- P7 (R5): `Makefile`: `eval: backend-check`, `$(UV_RUN) python -m eval.run` with `--dataset $(DATASET)` when set; `.PHONY` and `help` line. `pyproject.toml` `testpaths` adds `eval`.
- P8 (A2, A3): tests. `core`/`main` tests: export, defaults, startup error, `force`. `phones/tests`, `rag/tests`: run names and tags via a stubbed `langsmith` client / `tracing_context` capture with a fake `LangChainTracer`-free collector (`langsmith.run_helpers.tracing_context(enabled=True, client=<mock>)`), no network; graph run config name; rerank fallback metadata with a stubbed run tree; `session` absent from captured metadata; `parse_prompt` happy path and one repeat on invalid output (existing `ai_stubs`). `eval/tests`: dataset sizes and validation, seed match of `description`, evaluator positive/negative cases incl. tolerances and `null`.
- P9 (R6): `rag/CLAUDE.md`: `parse_prompt` and tracing link (EVALUATION.md#tracing); `phones/CLAUDE.md`: tracing link.
- P10 (A1, A4): `ruff check`, `ruff format --check`, `pytest`, `uv lock --check`, anchor check.

### Order
P1 -> P2 -> P5 -> P3 -> P4 -> P6 -> P7 -> P8 -> P9 -> P10.

### Risks
- Trace capture in tests depends on the `langsmith` test hooks: if `tracing_context(client=mock)` does not collect LangChain child runs, tests assert on the root traceable runs and the graph run config only.
- `get_current_run_tree()` inside a LangGraph node may return the node run or `None` depending on the context propagation of `langgraph` 1.2: Executor verifies with a captured trace; fallback is a child `traceable` run `rerank_fallback` under the node with the same metadata (EVALUATION.md would then need an Engineer update: report as an issue, not silently).
- `make eval` makes real OpenAI calls: about 56 LLM calls per full run.
- Example replacement on change resets the example IDs: experiments before the change stay in LangSmith but are compared against the old dataset version.
