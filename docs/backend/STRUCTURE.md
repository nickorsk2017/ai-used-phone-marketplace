# Backend Structure

Module responsibilities: [DESIGN.md](DESIGN.md#modules).

## Folders

```
backend/
  core/
  schemas/
  modules/
    users/
    auth/
    phones/
    rag/
    main/
  migrations/
  seed/
  eval/
  alembic.ini
  main.py
  conftest.py
  pyproject.toml
  uv.lock
  Dockerfile
  .dockerignore
  .env.example
```

- `core`: shared infrastructure of the modules: database settings and connection (see [DESIGN.md](DESIGN.md#database-connection)), `llm.py`: the LangChain client factories (`chat_model`, `embeddings`) and `llm_call`, the structured LLM call with the repeat on an invalid output (see [RAG.md](../ai/RAG.md#errors-and-retries)), `tracing.py`: the LangSmith settings and their export to the process environment (see [EVALUATION.md](../ai/EVALUATION.md#tracing)).
- `schemas`: shared Pydantic schemas that combine the schemas of several modules, for example the response body of `POST /api/search` (`schemas/search.py`: `SearchResponse` with the listings of `phones.schemas`). Imported by `modules/main` only. Schemas of one module stay in the `schemas` of that module.
- `modules`: domain modules and `main`, one folder per module: see [Module structure](#module-structure).
- `migrations`: Alembic migrations of all modules, `alembic.ini`: their config. See [SCHEMAS.md](SCHEMAS.md#migrations).
- `seed`: synthetic seed data and the script that loads it: see [Seed](#seed).
- `eval`: LangSmith evaluation, one folder per module and one file per AI step, `make eval`: see [Eval](#eval).
- `main.py`: entry point.
- `conftest.py`: shared test fixtures (PostgreSQL from `TEST_DATABASE_*`).
- `pyproject.toml`, `uv.lock`: uv workspace of the modules, dev tools (pytest, ruff).
- `.env.example`: template of `backend/.env`. Variables: see [DESIGN.md](DESIGN.md#configuration).

## Module structure

There are two kinds of modules: domain modules and `modules/main`. Module rules: the `CLAUDE.md` of each module.

### Domain module

`modules/users`, `modules/auth`, `modules/phones`, `modules/rag`. A domain module has no HTTP endpoints.

- `models` - SQLAlchemy models, only in a module with tables
- `schemas` - Pydantic schemas for data structure validation, also the request and response bodies of the API
- `services` - public interface of the module. Other modules import only `services` and `schemas`. `services/__init__.py` re-exports the public functions, the files inside are split by dependency: `crud.py` has the database functions (take the session), `ai.py` has the LLM and embedding calls (`modules/phones`, `modules/rag`), `token.py` and `access.py` in `modules/auth`
- `services` internal files, not re-exported by `services/__init__.py` and imported only inside the module: `guardrails.py` in `modules/phones`, `graph.py` (search pipeline) and `ranking.py` (ranking rules, no I/O) in `modules/rag`
- `prompts` - system prompts of the LLM calls, one file per prompt (`modules/phones`: `description.py`, `guardrail.py`; `modules/rag`: `guardrail.py`, `parse.py`, `rerank.py`, and `delimiters.py` with the search prompt delimiter shared by `guardrail.py` and `parse.py`). User text goes to the LLM only inside the delimiters of these files. Internal, imported only inside the module
- `config.py` - settings of the module, only in a module with settings (`modules/phones`, `modules/rag`): see [DESIGN.md](DESIGN.md#configuration)
- `database.py` - declarative Base of the module tables (`UsersBase`), only in a module with tables
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code

### `modules/main`

The API for the Frontend. No tables and no models.

- `app.py` - app factory, configuration check, CORS, routers under the `/api` prefix
- `config.py` - settings of the module
- `dependencies.py` - session of the request (`DbSession`), the session cookie and access checks (`CurrentUser`, `owner_access`)
- `rate_limit.py` - rate limits of the modules
- `ai.py` - `AI_ERRORS`: errors of the AI calls of the domain modules left after the retries, mapped to 503
- `routers` - API endpoints, one file per resource (`users.py`, `health.py`, `phones.py`, `my_listings.py`, `search.py`)
- `tests` - unit tests, integration tests
- `pyproject.toml` - file describing dependencies and libraries
- `CLAUDE.md` - rules for AI coding agents: module architecture and code

## Seed

`backend/seed/` holds the synthetic data of the evaluation: see [EVALUATION.md](../ai/EVALUATION.md#data).

- `users/seed_1.py`: `USERS`, 7 seed sellers as `UserCreate`. A seed user is identified by the WhatsApp number.
- `schemas.py`: `SeedListing`, the seller index in `USERS` and the listing as `PhoneCreate`.
- `listing/seed_1.py`, `listing/seed_2.py`, `listing/seed_3.py`: `LISTINGS`, 20 listings each: Apple, Samsung, Google and OnePlus.
- `listing/seed_4.py`: `LISTINGS`, 14 listings: Xiaomi, POCO, Huawei and Honor. `listing/seed_5.py`: `LISTINGS`, 16 listings: Oppo, vivo, Realme, Nothing and CMF.
- One listing per model. Model data: the model code, the main camera, the battery and the display of the real model. The model code is the US code. A model without a US version has the global code, or the China code if the model is sold only in China: see [RAG.md](../ai/RAG.md#model-code-limitations). The battery and the display are the values of the version of this code; for a foldable, the display is the main display.
- `run.py`: the load script, `make seed`. It checks that `model_code` and `model_name` are unique, creates the missing users, computes the embeddings of the missing listings with `rag.services.embed_listing`, then creates the listings and their `search_index` records in one transaction with `phones.services.create_phone` and `rag.services.index`. Guardrail 1 is not called: the seed text is trusted.
- A repeated run adds only the missing users and listings: a listing is identified by its user and `model_code`. `make seed-reset` deletes the seed users, their listings and their index records first.
- The domain modules have no lookup of a user by WhatsApp and no delete of all listings of a user, so `run.py` reads the seed user IDs and deletes the seed rows with SQL directly. This is the only code outside a module that touches module tables, besides `migrations/`.

## Eval

`backend/eval/` holds the LangSmith evaluation: see [EVALUATION.md](../ai/EVALUATION.md#datasets).

```
eval/
  rag/
    parse.py
    clarification.py
    ranking.py
  phones/
    description.py
    hallucinated_models.py
  metrics.py
  schemas.py
  upload.py
  run.py
  tests/
```

- One folder per backend module, one file per evaluated AI step. The file holds everything about the step: the cases, the target and the metrics, and exports `DATASET` (`EvalDataset`). A new step is a new file in the folder of its module.
- `rag/__init__.py`, `phones/__init__.py`: `DATASETS`, the datasets of the module in the run order.
- The target calls only the public `services` of its module. A step file may reuse the target of another step of the same module (`clarification.py` uses the target of `parse.py`).
- `metrics.py`: metrics shared by several steps (`valid_output`). A metric of one step stays in the file of that step.
- `schemas.py`: `EvalDataset` (name, cases, target, metrics) and `Example`.
- `upload.py`: creates the LangSmith dataset or replaces its examples when the cases changed.
- `rag/ranking.py`: the only step on the database: the rank metrics and the relevance rules over the seed, see [EVALUATION.md](../ai/EVALUATION.md#ranking).
- `database.py`: prepares the evaluation database of `EVAL_DATABASE_*` for a run with `rag.search`: creates it when missing, applies the migrations, reloads the seed when its fingerprint changed. `python -m eval.database` (`make docker-seed-test`) runs only this preparation.
- `run.py`: `make eval`. Collects the datasets of all modules, uploads the cases, runs the experiments and prints the results table. `--local` (`make eval LOCAL=1`) runs the targets and the metrics without LangSmith.
- `tests/`: unit tests of the cases and the metrics, no LLM and no LangSmith calls. A part of `make backend-test`.
- `eval` is not a module: it imports only the `services` and `schemas` of the modules, and the settings of `modules/phones` and `modules/rag` for the model names in the experiment metadata.
