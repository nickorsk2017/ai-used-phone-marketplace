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
- Trust is the main barrier. 32% of second-hand buyers met a scam in two years ([Which?](https://news.stv.tv/world/third-of-buyers-experienced-scam-on-second-hand-marketplaces-in-last-two-years-which-survey-finds)).

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

Development pipeline, not product runtime ([.claude/CLAUDE.md](.claude/CLAUDE.md)). Roles: Engineer (human: `TASK.md`, approval, commit), Planner (`PLAN.md`), Executor (code, `EXEC.md`), Validator (`VALIDATION.md`, PASS or FAIL against tests and `docs/`).

- Routing: LOW skips the Planner, HIGH adds Engineer approval. FAIL returns to the Executor, a repeated FAIL goes to the Engineer.
- Enforcement: a `PreToolUse` hook blocks foreign artifacts and illegal transitions, `pre-commit` blocks a broken task.
- State in `STATE.yaml`, not in the chat. `.claude/tasks/DONE/` is the audit trail.
- Downside: overhead for small changes, reduced by the LOW route.

## End User and Interface

- Buyer: one text field with an example prompt. No filters, no registration. A vague prompt gets one clarification question. An advice question gets a text answer ([SEARCH_PAGE.md](docs/features/SEARCH_PAGE.md)).
- Phone details: specifications, price, condition, seller's note, "Deal" button with the WhatsApp number ([PHONE_DETAILS.md](docs/features/PHONE_DETAILS.md)).
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

## Tooling and Tradeoffs

- LangGraph: branches and per-node retries match the pipeline diagram. Considered: plain async Python with hand-written branches and tracing.
- LangSmith: per-node traces and run comparison after a prompt change, no extra code. Considered: logs.
- Ranking metrics as code: relevant listings are computed by rules over the known seed, so Recall is measured without an LLM judge. Considered: DeepEval, Ragas.
- OpenAI through LangChain: provider changed in configuration. pgvector: hybrid search in one SQL query.
- FastAPI: AI libraries are Python-first. Pydantic validates API contracts and LLM output.
- Next.js: server rendering and ISR for SEO of Phone details. HeroUI: ready-made components.
- Modular monolith: fast PoC, modules can become services later ([TODO.md](docs/TODO.md)).

