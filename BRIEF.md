# BRIEF.md

This document is the design document of the submission (Deliverable 2). It is the only document required for the review.

`docs/` is not a part of the design document. It is the input of the development process: the architecture and the contracts are designed in `docs/` before the code, and the Claude agent generates the code from them. The approach reduces development time and rework. `docs/` is referenced for details only.

## Product

An AI marketplace of used phones. The buyer finds a phone in minutes instead of hours.

## Problem Thesis

Problem owner: the marketplace manager, who loses paid traffic when search fails. End user: the buyer of a used phone, whose search behavior decides that conversion.

### Business problem: the marketplace manager

The manager pays for traffic. The search page decides if it converts. Filters do not match how buyers describe a used phone, so the buyer leaves.

- Bad search loses buyers. 80% of shoppers buy elsewhere after a failed site search. Searchers convert at 4.63% against 2.77% ([Algolia](https://www.algolia.com/blog/ecommerce/ecommerce-search-statistics/)).
- Competitors use AI. Amazon Rufus users are 60% more likely to buy ([Fortune](https://www.fortune.com/2025/11/02/amazon-rufus-ai-shopping-assistant-chatbot-10-billion-sales-monetization)).
- The market is thin: refurbished sales grew 3% in H1 2025 ([Counterpoint](https://www.communicationstoday.co.in/global-refurbished-smartphone-sales-up-just-3-in-h1-2025/)). Each lost buyer is paid traffic lost.

### Buyer problem: the end user

- Each used phone is unique: storage, battery health, grade, defects. The buyer describes needs ("good camera, under USD 400"), not a model code. Filters cannot express this.
- The choice takes many sources: reviews, friends, brand sites, videos ([YouGov](https://yougov.com/articles/46465-from-reviews-to-experts-how-global-consumers-research-before-buying-a-phone)).

Limits of the data: vendor reports describe their own products. The 80% figure is a survey answer. No public source measures the time to choose a used phone. Details: [TASK.md](TASK.md#business-problem).

## Two Harnesses

| Harness | Purpose | User | Location |
| --- | --- | --- | --- |
| RAG Harness | Product: prompt to ranked listings, listing data generation | Buyer, seller | `backend/modules/rag`, `backend/modules/phones` |
| Claude Harness | Development: code generated and validated against `docs/` | Engineer | `.claude/` |

### RAG Harness

The LLM works only on free text. Price, condition, access and the WhatsApp number are deterministic code.

Search, a LangGraph pipeline ([RAG.md](docs/ai/RAG.md#architecture)):

1. Guardrail: LLM check for Prompt Injection, fail closed.
2. Parse: LLM returns filters, preferences, up to 10 model codes and an embedding query. Pydantic validates, an error retries the node.
3. Clarification: no phone criteria, a text answer, no database query.
4. Retrieval: SQL by model codes with exact price and condition filters. Below 20 results, a pgvector fallback with the same filters. Dedup by `phone_id`.
5. Rerank: one LLM call. Code drops unknown IDs, applies a threshold and 5 listings per model. On error, SQL order ([RERANKING.md](docs/ai/RERANKING.md)).

Listing creation: the LLM generates the description and specs from the model name, an unknown model returns 422, the seller edits before publishing. Guardrail: Frontend Regex, Backend Regex, LLM check for toxic content, fraud and Prompt Injection, fail closed ([GUARDRAILS.md](docs/ai/GUARDRAILS.md)).

Quality: untrusted text goes to the LLM inside delimiters. LangSmith traces each call and node. Plain tests of filters, guardrails and reranker output. Ranking metrics on the seed: Hit Rate, Precision, Recall, MRR, NDCG ([EVALUATION.md](docs/ai/EVALUATION.md)).

### Claude Harness

The development process, not the product. Claude agents in the roles Planner, Executor and Validator generate and check the code against the specifications in `docs/`. The Engineer approves the task and commits. Details: [.claude/CLAUDE.md](.claude/CLAUDE.md).

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

## Architecture

- Backend: modular monolith on FastAPI, modules `users`, `auth`, `phones`, `rag`, `main` ([DESIGN.md](docs/backend/DESIGN.md)).
- Frontend: Next.js, TypeScript, HeroUI v3, Tailwind CSS, React Hook Form, Zod, Zustand ([DESIGN.md](docs/frontend/DESIGN.md)).
- AI: OpenAI through LangChain, LangGraph, pgvector hybrid RAG with reranking ([DESIGN.md](docs/ai/DESIGN.md)).
- Database: PostgreSQL with pgvector in a Docker container. Seed of 90 listings ([INFRA.md](docs/INFRA.md)).

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

## Evaluation Results

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

- Model selection through OpenRouter: experiments with different models per pipeline node, compared on the evaluation datasets in LangSmith. Goal: higher scores of `model_code`, `os` and `precision@5`.
- Latency: `reasoning_effort=low` for the guardrail, parse and rerank calls, and a faster model for the reranker and the parse node, selected by the same experiments. Search p50 is 13.22 s on the `rag.search` cases: the search makes up to three sequential LLM calls (guardrail, parse, rerank) and an embedding call.
- Seed of 200 to 300 listings: more cases and more relevant listings per case, more stable metrics.
- Catalog of models with the variants of the model IDs. The model code is generated by the LLM now and covers one region.

Least sure:

- `model_code` 0.80 in `phones.description`: one model can get several codes, so the SQL match by model code misses listings.
- Metrics on 90 synthetic listings and 15 cases per dataset: the numbers show a trend, not the quality on real traffic.
