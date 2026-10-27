# BRIEF.md

## Product

An AI marketplace of used phones. The buyer finds a phone in minutes instead of hours.

## The Problem

**User.** The buyer spends hours choosing a phone model.

**Business.** The business loses money when the user leaves the platform without quickly finding a product.

### Metrics

- 80% of shoppers buy elsewhere after a failed site search [1].
- Searchers convert at 4.63% vs 2.77% for non-searchers [1].
- Amazon Rufus users are 60% more likely to buy [2].
- Refurbished smartphone sales grew only 3% in H1 2025 [3].
- Buyers use reviews, friends, brand sites and videos before choosing [4].

Limits: vendor reports describe their own products; the 80% figure is a survey answer; no public source measures time to choose a used phone.

### Links

1. [Algolia: ecommerce search statistics](https://www.algolia.com/blog/ecommerce/ecommerce-search-statistics/)
2. [Fortune: Amazon Rufus](https://www.fortune.com/2025/11/02/amazon-rufus-ai-shopping-assistant-chatbot-10-billion-sales-monetization)
3. [Counterpoint via Communications Today: refurbished sales H1 2025](https://www.communicationstoday.co.in/global-refurbished-smartphone-sales-up-just-3-in-h1-2025/)
4. [YouGov: how consumers research before buying a phone](https://yougov.com/articles/46465-from-reviews-to-experts-how-global-consumers-research-before-buying-a-phone)
5. Details: [TASK.md](TASK.md#business-problem)


## Architecture

- Backend: modular monolith on FastAPI, modules `users`, `auth`, `phones`, `rag`, `main` ([DESIGN.md](docs/backend/DESIGN.md)).
- Frontend: Next.js, TypeScript, HeroUI v3, Tailwind CSS, React Hook Form, Zod, Zustand ([DESIGN.md](docs/frontend/DESIGN.md)).
- AI: OpenAI through LangChain, LangGraph, pgvector hybrid RAG with reranking ([DESIGN.md](docs/ai/DESIGN.md)).
- Database: PostgreSQL with pgvector in a Docker container. Seed of 90 listings ([INFRA.md](docs/INFRA.md)).

### Harness (RAG / LLM)

Principle: the LLM works only on free text. Price, condition, listing IDs, access and the WhatsApp number are deterministic code. Every LLM output is validated by Pydantic before it is used. Overview: [HARNESS.md](docs/ai/HARNESS.md).

#### Search pipeline

A LangGraph graph, `POST /api/search` ([RAG.md](docs/ai/RAG.md#architecture)):

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

Retries in one place each ([RAG.md](docs/ai/RAG.md#errors-and-retries)): network errors by the model client (`max_retries=2`, timeout 60 s), validation errors by the LangGraph node (2 attempts). Reranking details: [RERANKING.md](docs/ai/RERANKING.md).

#### Listing creation

1. The seller enters the model name. The LLM returns the model code, OS, specifications and description. An unknown model (`iPhone 25`) returns HTTP 422 and no description ([MY_LISTING.md](docs/features/MY_LISTING.md)).
2. The seller edits the text, sets condition and price.
3. Guardrail 1 before saving: Frontend Regex, Backend Regex (card numbers, phone numbers, links), LLM check for toxic content, fraud and Prompt Injection. Fail closed ([GUARDRAILS.md](docs/ai/GUARDRAILS.md)).
4. The listing and its search index record with the embedding are saved in one transaction: the index cannot get out of sync with the data.

Guardrail 1 protects the search too: listing text is later passed to the reranker, so Prompt Injection in a listing is blocked before it is stored.

#### Quality

- Untrusted text (prompt, listings) goes to the LLM inside delimiters as data.
- LangSmith traces each LLM call and each graph node: prompt, response, latency, tokens, cost.
- Plain tests: filters in the results, guardrails, reranker output validation.
- LangSmith datasets with code metrics, no LLM judge: parsing, clarification, model data generation, hallucinated models, ranking (Hit Rate, Precision, Recall, MRR, NDCG). Results: [Evaluation Results](#evaluation-results), method: [EVALUATION.md](docs/ai/EVALUATION.md).

### Claude Pipeline

The development process, not the product. Claude agents in the roles Planner, Executor and Validator generate the code from `docs/` and check it against them. A state machine in `STATE.yaml` routes the task by complexity, hooks enforce the write rules of each role, the Engineer approves high-risk plans and commits. Details: [CLAUDE-HARNESS.md](docs/ai/CLAUDE-HARNESS.md). Agent entry point: [.claude/CLAUDE.md](.claude/CLAUDE.md).

## End User and Interface

- Buyer: one text field with an example prompt. No filters, no registration. A vague prompt gets one clarification question. An advice question gets a text answer ([SEARCH_PAGE.md](docs/features/SEARCH_PAGE.md)).
- Phone details: specifications, price, condition, seller's note, "Deal" button with the WhatsApp number ([PHONE_DETAILS.md](docs/features/PHONE_DETAILS.md)).
- Waiting and errors: during the search the page shows a skeleton of the result cards. When the LLM gives no valid answer after the node retries, the buyer sees a message to repeat the request later.
- Search time: 5 to 13 s. Most of the time is the rerank call, an estimate from the token counts of the evaluation. Tradeoff: the rerank call improves the order of the results and adds latency. Plan: show the SQL results at once and load the reranked order after them, `reasoning_effort=low` for the LLM calls ([Next steps](#reflections)).
- Seller: enters the model name. AI fills the description and specifications. The seller edits them, sets condition and price.

Why a page with one prompt, not a chat:

- Listings are compared by price and condition. A list is easier to scan than messages.
- Each listing has a URL: indexed and shared by link.
- To refine, the buyer edits the prompt. Clarification covers the main dialog case.

## Right-Sizing

The simplest version is one LLM call: prompt in, listing IDs out. Each component closes one failure of it.

| Failure of one LLM call | Handling |
| --- | --- |
| Invented listings or prices | LLM returns filters and model codes, SQL selects listings |
| Broken hard limit ("under $400") | Price and condition are SQL filters |
| Rare or misspelled model | pgvector fallback below 20 results |
| Invalid JSON | Pydantic validation, node retry |

Guardrail and Parse fail closed (HTTP 503). Rerank fails open: it changes the order, not the content.

Rejected: an agent with tools (variable LLM calls, harder to evaluate, the request is one-shot). Vector search only (no exact model match, no price enforcement).

## What Is Real and What Is Stubbed

Real: search by one prompt, listing creation with AI-generated model data, guardrails, Phone details with the Deal flow, evaluation of the AI steps.

Stubbed or simplified on purpose:

| Part | v1.0 | Limitation |
| --- | --- | --- |
| Data | 90 synthetic seed listings, one per model ([EVALUATION.md](docs/ai/EVALUATION.md#data)) | No real traffic |
| Authorization | Browser session without registration ([AUTH.md](docs/backend/AUTH.md#tradeoffs)) | Session tied to one browser, no logout |
| Model identification | Model code from the LLM, no model catalog ([RAG.md](docs/ai/RAG.md#model-code-limitations)) | Rare models can get a wrong code, one model can get several codes |
| Phone details cache | Time-based revalidation, no sitemap ([PHONE_DETAILS.md](docs/features/PHONE_DETAILS.md#tradeoffs)) | An updated or deleted listing is shown for up to 60 seconds |
| WhatsApp | No integration: the seller enters the number, the buyer copies it ([PHONE_DETAILS.md](docs/features/PHONE_DETAILS.md#deal-flow)) | |
| Images, multi-turn chat | Not in v1.0 ([TASK.md](TASK.md#out-of-scope-for-v10)) | |

Each document in `docs/` has a Tradeoffs section with the rationale of its decisions.

## Evaluation AI

Run of `make docker-eval` on 2026-10-27: real OpenAI calls, experiments in LangSmith. Metrics, targets and datasets: [EVALUATION.md](docs/ai/EVALUATION.md#metrics).

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

Latency of the target, errors, tokens and cost per dataset. The target of `rag.search` is the whole search (guardrail, parse, retrieval, rerank), run one request at a time: its latency is the search latency of one request. The other datasets time one LLM step and run 4 requests in parallel.

| Dataset | p50 s | p95 s | Errors | Tokens | Cost $ |
| --- | --- | --- | --- | --- | --- |
| `rag.parse` | 3.27 | 5.00 | 0 | 17715 | 0.0034 |
| `rag.clarification` | 2.27 | 3.92 | 0 | 18068 | 0.0024 |
| `rag.search`: full search, prompt to results | 13.22 | 15.25 | 0 | 105679 | 0.0371 |
| `phones.description` | 3.25 | 4.47 | 0 | 9829 | 0.0054 |
| `phones.hallucinated_models` | 1.39 | 1.87 | 0 | 2037 | 0.0006 |
| Total | | | 0 | 153328 | 0.0489 |

Targets met: 100% valid JSON, all clarification cases, 100% hallucinated models rejected. Ranking has no target in v1.0. The reranker is an LLM, scores vary slightly between runs.

Changes after the previous run:

- `os` in `rag.parse` 0.69 to 1.00: the parse prompt sets the OS from a brand or a model ([RAG.md](docs/ai/RAG.md#llm-output-structure)).
- Precision@5 divides by `min(5, relevant listings)`: 6 of 15 cases have fewer than 5 relevant listings in the seed and could not score 1 before ([EVALUATION.md](docs/ai/EVALUATION.md#metrics)).

## Tooling and Tradeoffs

- LangGraph: branches and per-node retries match the pipeline diagram. Considered: plain async Python with hand-written branches and tracing.
- LangSmith: per-node traces and run comparison after a prompt change, no extra code. Considered: logs.
- Ranking metrics as code: relevant listings are computed by rules over the known seed, so Recall is measured without an LLM judge. Considered: DeepEval, Ragas.
- OpenAI through LangChain: provider changed in configuration. pgvector: hybrid search in one SQL query.
- FastAPI: AI libraries are Python-first. Pydantic validates API contracts and LLM output.
- Next.js: server rendering and ISR for SEO of Phone details. HeroUI: ready-made components.
- Modular monolith: fast PoC, modules can become services later ([TODO.md](docs/TODO.md)).

## Reflections

Time spent: 9 hours.

Next steps:

- Model experiments through an AI router (OpenRouter): a model per pipeline node, compared on the LangSmith evaluation datasets. Goals: lower search latency (p50 13.22 s, three sequential LLM calls), higher `model_code`, `os` and `precision@5`. Candidates: faster models with `reasoning_effort=low` for guardrail, parse and rerank; decision models such as Jev (TypeSafe AI) for the guardrail and the reranker. A switch is accepted only if the evaluation scores hold.
- Seed of 200 to 300 listings: more cases per dataset, more stable metrics.
- Model catalog with model ID variants: the LLM-generated model code covers one region now.

Least sure:

- `model_code` 0.80 in `phones.description`: one model can get several codes, so the SQL match by model code misses listings.
- Metrics on 90 synthetic listings and 15 cases per dataset: the numbers show a trend, not the quality on real traffic.


## ---------

This document is the design document of the submission (Deliverable 2). It is the only document required for the review.

`docs/` is not a part of the design document. It is the input of the development process: the architecture and the contracts are designed in `docs/` before the code, and the Claude agent generates the code from them. The approach reduces development time and rework. `docs/` is referenced for details only. List of the documents: [DOCUMENTATION.md](docs/DOCUMENTATION.md).