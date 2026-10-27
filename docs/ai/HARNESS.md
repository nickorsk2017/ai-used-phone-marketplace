# HARNESS.md

LLM Harness (RAG Harness): the code around every LLM call of the product. It defines what each call receives, what it may return, how the output is checked and what happens on failure. Modules: `backend/modules/rag` and `backend/modules/phones`. The development process with Claude agents is a separate harness: see [CLAUDE.md](CLAUDE.md).

## Principles

1. The LLM works only on free text: the search prompt, the listing text, the model name. Price, condition, listing IDs, access and the WhatsApp number are handled by deterministic code.
2. Each LLM call has a Pydantic contract (structured output through LangChain). An output that fails validation is not used.
3. Untrusted text (the search prompt, the listing text) is passed to the LLM inside delimiters as data. The system prompt states that instructions inside it are ignored.
4. Each failure has one defined outcome: fail closed for guardrails and generation, fail open for reranking.
5. Each LLM call is traced and has an evaluation dataset or a plain test.

## LLM calls

| Call | Module | Input | Output contract | On failure | Trace |
| --- | --- | --- | --- | --- | --- |
| Model data generation | `phones` | Model name | Description and model data, `model_found`: see [MY_LISTING.md](../features/MY_LISTING.md#description-response) | Unknown model: HTTP 422. Call failed: HTTP 503 | `phones.description` |
| Guardrail 1 | `phones` | `model_name`, `description`, `condition_note` inside delimiters | `allowed`, `category`: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-1-phone-saving) | Blocked: HTTP 422. Call failed: HTTP 503, fail closed | `phones.guardrail` |
| Listing embedding | `rag` | `model_name`, `description`, `condition_note` | Vector: see [RAG.md](RAG.md#indexing) | Listing not saved, HTTP 503 | `rag.embed_listing` |
| Guardrail 2 | `rag` | Search prompt inside delimiters | `allowed`, `category`: see [GUARDRAILS.md](GUARDRAILS.md#guardrail-2-search-prompt) | Blocked: HTTP 422. Call failed: HTTP 503, fail closed | `rag.search` node |
| Prompt parsing | `rag` | Search prompt | `filters`, `preferences`, `model_ids`, `query_for_embedding` or `clarification`: see [RAG.md](RAG.md#llm-output-structure) | HTTP 503 | `rag.search` node |
| Reranking | `rag` | `preferences`, candidates inside delimiters | `phone_id` and `relevance` per candidate: see [RERANKING.md](RERANKING.md#output) | Fail open: SQL order, `rerank_fallback` in the trace | `rag.search` node |

## Controls

| Control | Where | Document |
| --- | --- | --- |
| Input guardrails: Regex and LLM for listings, LLM for the search prompt | Before the listing is saved, first node of the search graph | [GUARDRAILS.md](GUARDRAILS.md) |
| Structured output and Pydantic validation | Every LLM call | [RAG.md](RAG.md#llm-output-structure) |
| Deterministic retrieval: exact model code match, price and condition in SQL `WHERE` | Search graph after parsing | [RAG.md](RAG.md#search-index-table) |
| Clarification instead of a search without criteria | Prompt parsing | [RAG.md](RAG.md#clarification) |
| Output validation in code: unknown and repeated IDs, threshold, diversity limit | After reranking | [RERANKING.md](RERANKING.md#output-validation) |
| Retries: network errors by the model client, validation errors by the LangGraph node, each in one place | Every LLM call | [RAG.md](RAG.md#errors-and-retries) |
| Tracing of prompt, response, latency, tokens and cost | Every LLM call and graph node | [EVALUATION.md](EVALUATION.md#tracing) |
| Evaluation datasets with code metrics, no LLM judge | `make eval`, run by the Engineer | [EVALUATION.md](EVALUATION.md#datasets) |

## Search pipeline

A LangGraph graph, `POST /api/search`: see [RAG.md](RAG.md#architecture).

| Step | Node | Input | Output | On failure |
| --- | --- | --- | --- | --- |
| 1 | Guardrail | Prompt inside delimiters | `allowed`, `category` | Blocked: HTTP 422. Call failed: HTTP 503, fail closed |
| 2 | Parse | Prompt | `filters` (price, condition), `preferences` (OS, camera, battery, display), up to 10 `model_ids`, `query_for_embedding` | Invalid JSON: one node retry, then HTTP 503 |
| 3 | Clarification | Parse output | Text answer when the prompt has no phone criteria or asks for advice | Ends the graph, no database query |
| 4 | Retrieval | `model_ids`, `filters` | SQL by exact model code with price and condition in `WHERE` | |
| 5 | Vector fallback | `query_for_embedding`, `filters` | pgvector with the same `WHERE`, only below 20 results | |
| 6 | Merge | Both paths | Dedup by `phone_id`, at most 40 candidates | |
| 7 | Rerank | `preferences`, candidates inside delimiters | `relevance` 0 to 1 per `phone_id` | Fail open: SQL order, `rerank_fallback` in the trace |
| 8 | Output check | Reranker output | Unknown and repeated IDs dropped, threshold 0.3, at most 5 listings per model, top 20 | |

Retries: network errors by the model client (`max_retries=2`, timeout 60 s), validation errors by the LangGraph node (2 attempts): see [RAG.md](RAG.md#errors-and-retries). Reranking: see [RERANKING.md](RERANKING.md).

## Listing creation

1. The seller enters the model name. The LLM returns the model code, OS, specifications and description. An unknown model (`iPhone 25`) returns HTTP 422 and no description: see [MY_LISTING.md](../features/MY_LISTING.md).
2. The seller edits the text, sets condition and price.
3. Guardrail 1 before saving: Frontend Regex, Backend Regex (card numbers, phone numbers, links), LLM check for toxic content, fraud and Prompt Injection. Fail closed: see [GUARDRAILS.md](GUARDRAILS.md).
4. The listing and its search index record with the embedding are saved in one transaction.

Guardrail 1 also protects the search: listing text is passed to the reranker, so Prompt Injection in a listing is blocked before it is stored.

## Right-sizing

The simplest version is one LLM call: prompt in, listing IDs out. Each component handles one failure of it.

| Failure of one LLM call | Handling |
| --- | --- |
| Invented listings or prices | The LLM returns filters and model codes, SQL selects listings |
| Broken hard limit ("under $400") | Price and condition are SQL filters |
| Rare or misspelled model | pgvector fallback below 20 results |
| Invalid JSON | Pydantic validation, node retry |

Guardrail and Parse fail closed (HTTP 503). Rerank fails open: it changes the order, not the content. Rejected alternatives: see [Tradeoffs](#tradeoffs).

## Quality

| Layer | What is checked | Tool |
| --- | --- | --- |
| Tracing | Each LLM call and each graph node: prompt, response, latency, tokens, cost | LangSmith: see [EVALUATION.md](EVALUATION.md#tracing) |
| Plain tests | Filters in the results, guardrails, reranker output validation | `make backend-test` |
| Evaluation datasets | Parsing, clarification, model data generation, hallucinated models, ranking. Code metrics, no LLM judge | `make eval`, LangSmith experiments: see [EVALUATION.md](EVALUATION.md#datasets) |

Offline evaluation runs on the fixed seed of 90 synthetic listings, 10 to 20 cases per dataset. Online metrics (latency, cost, errors, reranker fallbacks, clarifications, user feedback) come from the production traces: see [EVALUATION.md](EVALUATION.md#offline-and-online).

### Known limitations

- `model_code` 0.80 in `phones.description`: one model can get several codes, so the SQL match by model code misses listings. Plan: a model catalog with model ID variants.
- 90 synthetic listings and 15 cases per dataset: the numbers show a trend, not the quality on real traffic. Plan: a seed of 200 to 300 listings.
- Search latency p50 13.22 s: three sequential LLM calls. Plan: show the SQL results at once and load the reranked order after them, `reasoning_effort=low`, model per node through an AI router compared on the evaluation datasets. A model switch is accepted only if the evaluation scores hold.

## Models

Providers and models are set in the configuration and changed without changes in the pipeline code: see [DESIGN.md](DESIGN.md#stack). The model of each call is selected by its evaluation metrics: see [EVALUATION.md](EVALUATION.md#metrics).

## Tradeoffs

- Rejected: an agent with tools. Variable number of LLM calls, harder to evaluate, the request is one-shot.
- Rejected: vector search only. No exact model match, no price enforcement.
- Code metrics instead of an LLM judge: scores do not depend on a judge model and cost no LLM calls. Considered: DeepEval, Ragas. Details: see [EVALUATION.md](EVALUATION.md#rank-metrics-instead-of-an-llm-judge).
