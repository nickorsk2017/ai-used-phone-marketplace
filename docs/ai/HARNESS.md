# HARNESS.md

LLM Harness (RAG Harness): the code around every LLM call of the product. It defines what each call receives, what it may return, how the output is checked and what happens on failure. Modules: `backend/modules/rag` and `backend/modules/phones`. The development process with Claude agents is a separate harness: see [CLAUDE-HARNESS.md](CLAUDE-HARNESS.md).

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

Search pipeline and its graph: see [RAG.md](RAG.md#architecture).

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

## Models

Providers and models are set in the configuration and changed without changes in the pipeline code: see [DESIGN.md](DESIGN.md#stack). The model of each call is selected by its evaluation metrics: see [EVALUATION.md](EVALUATION.md#metrics).
