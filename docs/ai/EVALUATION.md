# EVALUATION.md

Evaluation, Observability and cost of the LLM calls. Stack: see [DESIGN.md](DESIGN.md#stack).

v1.0 evaluates the steps where AI can fail regardless of the data volume: prompt parsing, model data generation, guardrails and filters. Ranking quality is measured with Hit Rate, Precision, Recall, MRR and NDCG on the seed: see [Ranking](#ranking).

## Offline and online

| | Offline | Online |
| --- | --- | --- |
| What | `make eval`: the datasets of the generation steps and ranking, see [Run](#run) | Production metrics: latency and cost, errors, reranker fallbacks, clarifications, user feedback on the search |
| Data | Test data only: the cases of the repository and the [seed](#data). Only `rag.search` uses a database, the evaluation database of `EVAL_DATABASE_*`: see [Evaluation database](#evaluation-database) | Production traffic |
| Tool | LangSmith experiments, or the local table of `make eval LOCAL=1` | LangSmith only: the traces of the production project, see [Tracing](#tracing), and feedback on the `rag.search` trace, see [TODO.md](../TODO.md#production-baseline) |

- `make eval` never runs on the working or production database, nor on the database of the tests: a run with `EVAL_DATABASE_*` pointing to the database of `POSTGRES_*` or of `TEST_DATABASE_*` stops before any change.
- Production data never becomes the expected output of a case: the expected results are known only on the fixed test data. Real prompts from the traces can become new cases, run on the test data.

## Data

- Purpose of the seed: a PoC without listings cannot be tested by hand. The seed lets a reviewer and the first users run searches right after `make seed`, and the evaluation test sets are built on the same known data, so the expected results of each prompt are known.
- Seed: 90 synthetic listings of 7 sellers, one listing per model (iOS and Android, 2020 to 2026 models, including Xiaomi, Huawei, Oppo, vivo, Honor, Realme and Nothing models of 2025 and 2026), with all three conditions and different prices. Files and the load script: see [STRUCTURE.md](../backend/STRUCTURE.md#seed).
- Test sets: 10 to 20 cases per group. This is a regression set, not a statistical benchmark.

## Metrics

| Step | Metric | Target | Tool |
| --- | --- | --- | --- |
| Prompt parsing: see [RAG.md](RAG.md#llm-output-structure) | Share of prompts where condition, price and OS match the expected values. Share of valid JSON | 100% valid JSON | LangSmith |
| Filters in the results | Share of results that violate the price or the condition from the prompt | 0% | Plain test |
| Model data generation: see [MY_LISTING.md](../features/MY_LISTING.md#description-response) | Share of cases where `model_code` and `os` match the expected values and the specifications are close to them. Share of valid JSON | 100% valid JSON | LangSmith |
| Clarification: see [RAG.md](RAG.md#clarification) | Share of prompts without phone criteria and of advice questions that return a clarification. Share of phone descriptions and listing requests that return a clarification by mistake | All vague prompts and advice questions answered in text, no false clarifications | LangSmith |
| Hallucinated models | A model that does not exist (for example, `iPhone 25`) returns HTTP 422 and no description | 100% | LangSmith |
| Guardrails: see [GUARDRAILS.md](GUARDRAILS.md) | Share of blocked toxic, fraud and prompt injection cases. Share of false blocks of clean texts | All bad cases blocked, no false blocks | Plain test |
| Reranker output: see [RERANKING.md](RERANKING.md#output-validation) | Share of reranker IDs that are not in the candidates. Share of results with a repeated `phone_id` | 0% in the result | Plain test |
| Latency and cost | p50 and p95 of the search time, cost of a search and of a listing creation | Measured, no target in v1.0 | LangSmith |
| Ranking: see [Ranking](#ranking) | Hit Rate@5, Precision@5, Recall@20, MRR and NDCG@10 against the relevant seed listings of each prompt | Measured, no target in v1.0 | LangSmith, code metrics |

## LangSmith

### Tracing

- Each LLM call is traced: prompt, response, latency, tokens and cost. An embedding call is traced with its latency only: LangChain sends no token usage for embeddings, so their cost is not in LangSmith. LangChain and LangGraph send the traces, the code only names the root runs and sets their tags.
- Root runs:

| Run name | Tag | Content |
| --- | --- | --- |
| `rag.search` | `rag` | The search graph. Each LangGraph node is a child span: see [RAG.md](RAG.md#orchestration-langgraph) |
| `phones.description` | `phones` | Model data generation: see [MY_LISTING.md](../features/MY_LISTING.md#description-response) |
| `phones.guardrail` | `phones` | The LLM Guardrail of Guardrail 1: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-1-phone-saving) |
| `rag.embed_listing` | `rag` | The listing embedding: see [RAG.md](RAG.md#indexing) |
| `rag.parse` | `rag` | The prompt parsing alone, called by `make eval` only: see [RAG.md](RAG.md#module-interface) |

- Errors of the LLM calls and retries are visible in the traces: see [RAG.md](RAG.md#errors-and-retries). A reranker fallback is marked on the `rerank` span with the metadata `rerank_fallback: true` and the error type: see [RERANKING.md](RERANKING.md#errors).
- The database session of the request is not sent to LangSmith: the trace metadata has no `configurable.session`.
- Tracing is optional. It is on only when `LANGSMITH_TRACING=true`. The API starts without LangSmith. Tests never send traces. Variables: see [DESIGN.md](../backend/DESIGN.md#configuration).
- Latency and cost: p50 and p95 of the search time and the cost of a search are the statistics of the `rag.search` runs in the LangSmith project. The cost of a listing creation is the sum of `phones.description` and `phones.guardrail`, without the embedding.

### Datasets

The cases are stored in the repository, one file per step in the folder of its module (`backend/eval/rag/parse.py`): see [STRUCTURE.md](../backend/STRUCTURE.md#eval). The dataset name is `<module>.<step>`. The repository is the source of truth: `make eval` uploads the cases to the LangSmith dataset `<LANGSMITH_PROJECT>.<dataset>` before the run. A changed set of cases replaces the examples of the dataset, the dataset and its experiments are kept, so the LangSmith dataset always matches the repository.

| Dataset | Target | Cases | Metrics |
| --- | --- | --- | --- |
| `rag.parse` | Prompt parsing: see [RAG.md](RAG.md#llm-output-structure) | Search prompts with the expected condition, price and OS | Valid output, condition match, price match, OS match |
| `rag.clarification` | Prompt parsing: see [RAG.md](RAG.md#clarification) | Prompts without phone criteria and advice questions (clarification expected), phone descriptions and listing requests (no clarification expected) | Clarification returned when expected and only then |
| `phones.description` | Model data generation: see [MY_LISTING.md](../features/MY_LISTING.md#description-response) | Model names of the seed with the model data of the seed listing as the expected output | Valid output, `model_code` match, `os` match, specifications close |
| `phones.hallucinated_models` | Model data generation | Names of models that do not exist, for example `iPhone 25` | No description returned: the endpoint returns HTTP 422 |
| `rag.search` | The whole search on the test database: see [Ranking](#ranking) | Search prompts with the relevant seed listings computed by rules | Hit Rate@5, Precision@5, Recall@20, MRR, NDCG@10 |

- 10 to 20 cases per dataset: see [Data](#data).
- A field that the case does not set is not checked. A field set to `null` must be absent in the output, for example no condition filter for `iPhone 13 under $300`. A price matches when the operator, the value and the maximum value are equal.
- Specifications are close: the camera megapixels are equal, the battery capacity differs by at most 5%, the display size differs by at most 0.1 inch.
- Metrics are code, no LLM judge. Each metric gives a score from 0 to 1 per case (1 or 0 for the checks of the generation steps), the experiment score is the mean.
- Targets call the public interface of `modules/rag` and `modules/phones` with the models from the configuration. Only `rag.search` uses the database: see [Evaluation database](#evaluation-database).
- Each run is a LangSmith experiment named after the dataset, with the model names in the experiment metadata. Runs are compared in LangSmith after a prompt or model change.

## Ranking

Dataset `rag.search`: the whole search (`rag.services.search`, see [RAG.md](RAG.md#module-interface)) on the seed, measured against the relevant seed listings of each prompt. Why rank metrics and not an LLM judge: see [Tradeoffs](#rank-metrics-instead-of-an-llm-judge).

### Evaluation database

- The search runs on the evaluation database of `EVAL_DATABASE_*` (see [DESIGN.md](../backend/DESIGN.md#configuration)) with the [seed](#data) loaded into it. It is a database of its own: not the working database of `POSTGRES_*`, and not the test database of `TEST_DATABASE_*`, which `make backend-test` rolls back and truncates. So `make backend-test` and `make eval` can run at the same time, and the seed stays loaded between runs. Why: see [Tradeoffs](#evaluation-database-separate-from-the-tests).
- Before a run that includes `rag.search`, `make eval` creates the database when it does not exist and applies the migrations.
- The seed is reloaded (`seed-reset`) only when the seed fingerprint changed: a hash of the seed users and listings, the embedding model and the migration files. The fingerprint of the loaded seed is stored as the comment of the evaluation database. A database without the comment, or a comment that cannot be read or written, gets a full reload. The seed embeddings are not traced.

### Relevant listings

- A case is the prompt and two rules over the seed listings: `relevant` (grade 1) and `highly_relevant` (grade 2, a subset of `relevant`). The expected output is computed from the seed by the rules: the `model_code` and the grade of each relevant listing. See [Tradeoffs](#rules-over-the-seed-instead-of-labeled-ids).
- A listing is identified by `model_code`: unique in the seed and stable across `seed-reset`, while the listing IDs change.
- The rules check what retrieval and reranking decide: preferences (battery, camera, display size), a brand or a model family, a named model, the intent of the prompt. Price and condition are applied in SQL, so every result already matches them: they are in a rule only together with other criteria.
- Each case has 1 to 19 relevant listings: Recall@20 says something only below the limit of 20 results.
- The target returns the model codes of the results in the search order. A clarification or a blocked prompt returns no results, so all metrics of the case are 0.

### Metrics

Grades: 2 highly relevant, 1 relevant, 0 any other listing.

| Metric | Formula | Question |
| --- | --- | --- |
| Hit Rate@5 | 1 when the top 5 has a relevant listing, else 0 | Does the first screen have a match? |
| Precision@5 | Relevant listings in the top 5 divided by `min(5, relevant listings of the seed)` | How clean is the first screen? |
| Recall@20 | Relevant listings in the results divided by all relevant listings of the seed | How many relevant listings does the search find? |
| MRR | 1 divided by the rank of the first relevant listing, 0 when there is none | How high is the first match? |
| NDCG@10 | DCG of the top 10 divided by the DCG of the ideal order; gain `2^grade - 1`, discount `log2(rank + 1)`; the ideal order is built from all relevant listings of the seed | How close is the order to the ideal? |

- Precision@5 divides by `min(5, relevant)`, so a case with fewer than 5 relevant listings can score 1. It divides by the same value also when the search returns fewer than 5 results.
- The reranker is an LLM: the scores vary slightly between runs. The trend across experiments matters, not one run.
- The metric functions are code of the project, no library: see [Tradeoffs](#own-metric-functions-instead-of-a-library).

## Run

| Command | What it does | Requirements |
| --- | --- | --- |
| `make eval` | Runs all datasets and sends the results to LangSmith as experiments. The main command after a change of an AI step | `OPENAI_API_KEY`, `LANGSMITH_API_KEY`, PostgreSQL with pgvector for `rag.search` |
| `make eval LOCAL=1` | Runs all datasets without LangSmith: no upload, no experiments, no traces. Prints the table only. For CI and for a run without a LangSmith account | `OPENAI_API_KEY`, PostgreSQL with pgvector for `rag.search` |
| `make eval DATASET=rag.search` | Runs one dataset, for example after a change of the reranker. Combines with `LOCAL=1` | As for `make eval`; PostgreSQL only for `rag.search` |

- Every command prints a table: dataset, metric, score, cases, p50 and p95 latency of the target, errors, tokens and cost. Tokens and cost are `n/a` with `LOCAL=1`.
- `rag.search` runs one search at a time, so its p50 and p95 are the latency of one search request. The other datasets run 4 targets in parallel: their latency includes the wait under the parallel load.
- A full run makes about 100 OpenAI requests. The experiment traces are sent whatever the value of `LANGSMITH_TRACING`.
- The first run with `rag.search` creates the evaluation database and loads the seed. Next runs reuse it: see [Evaluation database](#evaluation-database).
- The plain tests of the [Metrics](#metrics) table are a part of `make backend-test`.
- v1.0 (PoC): the Engineer runs `make eval` manually after a change of an AI step (prompts, models, RAG, guardrails). It is not run on every commit and is not a part of the Validator checks.
- Production: LLM evaluation is a CI quality gate before deployment: see [TODO.md](../TODO.md#production-baseline).

## Results

To be filled after the implementation.

## Tradeoffs

### What is not measured in v1.0

- Statistical quality of the search: 10 to 20 prompts on 90 synthetic listings catch regressions but do not measure the quality level on real listings.
- Behavior on real prompts and online metrics (position of the clicked result, Phone details views and Deal clicks after a search): after the first users, see [TODO.md](../TODO.md#production-baseline).

### Rank metrics instead of an LLM judge

- A typical RAG retrieves text chunks for a generated answer. Teams usually have no labeled relevant chunks, and the answer matters more than the order of the chunks, so the LLM platforms (LangSmith, Langfuse, DeepEval, Ragas) offer LLM judge metrics: retrieval relevance, groundedness, correctness. None of them has built-in Hit Rate, Precision@k, Recall@k, MRR and NDCG for a ranked list with known IDs.
- This project returns a ranked list of listings, like the search of an online shop. The order is the product, so the classic ranking metrics are the key metrics.
- The relevant listings are known: the seed is fixed, and the rules compute the relevant listings of each prompt. So Recall is measured, the scores do not depend on a judge model, and the metrics cost no LLM calls.
- Downside: the metrics are only as good as the rules. Each case has a test that its rules select the expected number of seed listings.

### Rules over the seed instead of labeled IDs

- A rule reads as the requirement (`os == "android" and battery_capacity >= 5000`), so a reviewer sees why a listing is relevant.
- A change of the seed (new listings, other prices) recomputes the relevant listings: the cases do not go stale.
- Downside: a prompt whose relevance cannot be written as a rule (`a phone for my grandmother`) is not in the set. Such prompts need an LLM judge metric in the file of the step, if they are added later.

### Own metric functions instead of a library

- Five short formulas on 10 to 20 cases: the speed of ranx (Numba) or pytrec_eval (C extension) gives nothing, while their build depends on the Python version and the platform.
- The definitions of the project are visible in the code and in [Metrics](#metrics): Recall against all relevant seed listings, Precision@5 divided by `min(5, relevant)`, 0 for a case without results.
- The unit tests compare the functions with values computed by hand on edge cases: no results, no relevant listing found, relevant listings below the cut-off, fewer results than `k`.
- Considered: ranx, ir-measures, pytrec_eval (classic IR), torchmetrics (needs PyTorch), the evaluators of LlamaIndex and Haystack (other frameworks), Ragas (ID based precision and recall only, no MRR or NDCG).

### Cut-offs of the metrics

- Hit Rate and Precision on the top 5: the first screen that the user sees.
- NDCG on the top 10: the order below the first screen still matters, the tail of 20 results matters less.
- Recall on all 20 results: a relevant listing found at any position is found.

### Evaluation database separate from the tests

- The test database is rolled back and truncated by every `make backend-test`: a seed loaded there does not survive a test run, so `make eval` had to reload the seed (90 embedding calls) on every run, and the two commands could not run at the same time.
- The evaluation database keeps the seed: a run reloads it only after a change of the seed, the embedding model or the migrations.
- Downside: one more local database. `make eval` creates it, so no manual step is needed when the PostgreSQL user may create databases. On a managed PostgreSQL without that right, the database is created by hand once.

### Datasets in the repository

- Cases are reviewed in pull requests together with the prompt change that they test.
- Downside: a case added in the LangSmith UI is overwritten by the next `make eval`. New cases are added in the repository only.

### One evaluation tool: LangSmith

- LangSmith already traces every LLM call. Datasets, experiments and the comparison of runs work on the same traces, for the generation steps and for ranking.
- The metrics are plain functions: `make eval LOCAL=1` runs them without LangSmith, and a move to another platform (for example Langfuse) changes the runner, not the metrics.
- DeepEval and Ragas are not used: their LLM judge metrics (faithfulness, hallucination, answer relevancy) evaluate a generated answer, and the project generates no answer from the found listings. They are reconsidered if it does.
- Offline evaluation is `make eval`. Online evaluation on real users is a part of the production baseline: see [TODO.md](../TODO.md#production-baseline).


## Metrics and targets

| Dataset | Target step | Metrics | Target |
| --- | --- | --- | --- |
| `rag.parse` | Prompt parsing | `valid_output`, `condition`, `price`, `os` | 100% valid JSON |
| `rag.clarification` | Prompt parsing | `valid_output`, `clarification` | All vague prompts and advice questions answered in text, no false clarifications |
| `rag.search` | Whole search on the evaluation database | `hit_rate@5`, `precision@5`, `recall@20`, `mrr`, `ndcg@10` | Measured, no target in v1.0 |
| `phones.description` | Model data generation | `valid_output`, `model_code`, `os`, `specifications` | 100% valid JSON |
| `phones.hallucinated_models` | Model data generation | `no_description` | 100% |

Ranking metrics use grades 2 (highly relevant), 1 (relevant), 0 (other). Relevant listings are computed by rules over the seed, so Recall is measured without an LLM judge. Formulas: see [EVALUATION.md](EVALUATION.md#metrics-1).

### Metrics Result

Run of `make docker-eval` on 2026-10-27: real OpenAI calls, experiments in LangSmith.

| Dataset | Metric | Score | Cases |
| --- | --- | --- | --- |
| `rag.parse` | valid_output | 1.00 | 15 |
| | condition | 1.00 | 15 |
| | price | 1.00 | 15 |
| | os | 1.00 | 13 |
| `rag.clarification` | valid_output | 1.00 | 16 |
| | clarification | 1.00 | 16 |
| `rag.search` | hit_rate@5 | 1.00 | 15 |
| | precision@5 | 0.78 | 15 |
| | recall@20 | 0.74 | 15 |
| | mrr | 1.00 | 15 |
| | ndcg@10 | 0.84 | 15 |
| `phones.description` | valid_output | 1.00 | 15 |
| | model_code | 0.80 | 15 |
| | os | 0.80 | 15 |
| | specifications | 0.80 | 15 |
| `phones.hallucinated_models` | no_description | 1.00 | 10 |

Latency, errors, tokens and cost per dataset. `rag.search` runs one request at a time: its latency is the latency of one search (guardrail, parse, retrieval, rerank). The other datasets time one LLM step and run 4 requests in parallel.

| Dataset | p50 s | p95 s | Errors | Tokens | Cost $ |
| --- | --- | --- | --- | --- | --- |
| `rag.parse` | 3.27 | 5.00 | 0 | 17715 | 0.0034 |
| `rag.clarification` | 2.27 | 3.92 | 0 | 18068 | 0.0024 |
| `rag.search` | 13.22 | 15.25 | 0 | 105679 | 0.0371 |
| `phones.description` | 3.25 | 4.47 | 0 | 9829 | 0.0054 |
| `phones.hallucinated_models` | 1.39 | 1.87 | 0 | 2037 | 0.0006 |
| Total | | | 0 | 153328 | 0.0489 |

- Targets met: 100% valid JSON, all clarification cases, 100% hallucinated models rejected.
- The reranker is an LLM: scores vary slightly between runs. The trend across experiments matters, not one run.
- Search time 5 to 13 s, most of it is the rerank call.

Changes after the previous run:

- `os` in `rag.parse` 0.69 to 1.00: the parse prompt sets the OS from a brand or a model: see [RAG.md](RAG.md#llm-output-structure).
- Precision@5 divides by `min(5, relevant listings)`: 6 of 15 cases have fewer than 5 relevant listings in the seed.