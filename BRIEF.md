# BRIEF.md

System-level design. Details of each part: [backend/DESIGN.md](docs/backend/DESIGN.md), [frontend/DESIGN.md](docs/frontend/DESIGN.md), [ai/DESIGN.md](docs/ai/DESIGN.md).

## Problem Thesis

Who: buyers of used phones in the US who have not chosen a model yet, and the marketplace that sells to them.

### Buyer problem

- A used phone is a unique item: model, storage, battery health, grade and defects differ for each listing. The buyer describes needs ("good camera, long battery, under USD 400"), not a model code, and filters do not express such a request.
- The choice takes many sources: before buying a phone, people check written reviews (47%), friends and family (47%), the brand website (39%), video reviews (33%), sales staff (29%) and experts (28%) ([YouGov, 17 markets, 2023](https://yougov.com/articles/46465-from-reviews-to-experts-how-global-consumers-research-before-buying-a-phone)).
- Trust is the main barrier: 60% of UK and 56% of US consumers would consider a refurbished phone, condition and reliability are the main concern ([CCS Insight](https://www.ccsinsight.com/blog/refurbished-phones-gain-further-ground/)).
- Risk: 32% of buyers on second-hand marketplaces met a scam in the last two years: wrong item (15%), no item (15%), empty parcel (11%), counterfeit (10%) ([Which? via STV](https://news.stv.tv/world/third-of-buyers-experienced-scam-on-second-hand-marketplaces-in-last-two-years-which-survey-finds)). Purchase scams are 71% of Barclays scam claims in 2025, and the average claim grows as scammers target higher value items ([Barclays](https://home.barclays/news/press-releases/2025/03/barclays-scams-bulletin--online-marketplace-scams-on-the-rise--a)).

### Business problem

- Thin market: global refurbished smartphone sales grew 3% in H1 2025, mature markets about 1%, with intense competition and thin margins ([Counterpoint](https://www.communicationstoday.co.in/global-refurbished-smartphone-sales-up-just-3-in-h1-2025/)). Each lost buyer is a sale the marketplace paid traffic for.
- Bad search loses buyers: about 80% of shoppers say they are more likely to buy elsewhere after an unsuccessful site search, 82% of US shoppers avoid sites where search failed before, 21% of searchers exit from the results page ([Algolia summary of Google Cloud and Econsultancy](https://www.algolia.com/blog/ecommerce/ecommerce-search-statistics/)).
- Search is where revenue is: searchers convert at 4.63% against 2.77%, and 41% of ecommerce sites do not fully support key query types (Baymard 2024) ([Algolia](https://www.algolia.com/blog/ecommerce/ecommerce-search-statistics/)).
- Competitors already use AI: Amazon Rufus users are 60% more likely to complete a purchase, with over USD 10B of expected annual incremental sales ([Fortune](https://www.fortune.com/2025/11/02/amazon-rufus-ai-shopping-assistant-chatbot-10-billion-sales-monetization)). AI-referred traffic converts 42% better with 37% higher revenue per visit ([Adobe via Digital Commerce 360](https://www.digitalcommerce360.com/2026/04/23/ecommerce-trends-ai-key-conversion-metric/amp/)). AI agents influenced USD 67B of Cyber Week 2025 sales, and retailers with AI agents grew 32% faster ([Salesforce via CX Today](https://cxtoday.com/salesforce-reports-record-cyber-week-as-ai-agents-drive-67bn-in-sales)).
- Cost: a buyer who does not find a phone in minutes leaves for a competitor with AI search. The marketplace loses the sale, and sellers follow the demand.

### Limits of the data

- Amazon and Salesforce report on their own products.
- Adobe measures traffic from external AI assistants, not on-site search.
- The 80% figure is a survey answer, not measured behavior.
- The CCS Insight data is from 2020.
- No public source gives the time a buyer spends choosing a used phone.

Details: [TASK.md](docs/TASK.md#business-problem).

## Approaches

- Documentation First: a change of the product or the architecture starts in `docs/`. Claude generates the code from `docs/`, the Validator checks the code against `docs/`. See [CLAUDE.md](CLAUDE.md#1-documentation-is-the-source-of-truth).
- Harness pipeline: each task goes through the roles Engineer, Planner, Executor and Validator with fixed artifacts (`TASK.md`, `PLAN.md`, `EXEC.md`, `VALIDATION.md`) and a state machine in `STATE.yaml`.
- `CLAUDE.md` with rules: the root [CLAUDE.md](CLAUDE.md) for the repository, [.claude/CLAUDE.md](.claude/CLAUDE.md) for the harness, a `CLAUDE.md` in each Backend module and in the Frontend for its architecture and code.
- Engineer review before the task is set: the Engineer reviews `TASK.md` (scope, acceptance criteria, affected `docs/`) before the task enters the pipeline.
- Engineer review before the commit: after PASS the Engineer reviews the diff and `VALIDATION.md`, closes the task with `runner.py done` and commits.

## Two Harnesses

The project has two harnesses with different purposes:

| Harness | Purpose | User | Location |
| --- | --- | --- | --- |
| RAG Harness | Product: turns a free text prompt into ranked listings, generates listing data | Buyer and seller | `backend/modules/rag`, `backend/modules/phones` |
| Claude Harness | Development: generates and validates the code against `docs/` | Engineer | `.claude/` |

### RAG Harness

The orchestration around the LLM calls of the product. The LLM works only where the input is free text. Price, condition, access rules and the WhatsApp number are handled by deterministic code.

Search pipeline (LangGraph, one node per step: see [RAG.md](docs/ai/RAG.md#architecture)):

1. Guardrail 2: LLM check of the prompt for Prompt Injection, fail closed, HTTP 422 or 503. See [GUARDRAILS.md](docs/ai/GUARDRAILS.md#guardrail-2-search-prompt).
2. Parse: the LLM returns structured JSON with filters (condition, price), preferences (OS, camera, battery, display), up to 10 model codes and a query for the embedding. Pydantic validates the output, a validation error repeats the node.
3. Clarification: a prompt without phone criteria or an advice question returns a text answer, the pipeline ends without a database query.
4. Retrieval by model codes: SQL with exact price and condition filters.
5. Vector fallback: fewer than 20 listings start a pgvector search with the same filters.
6. Merge and deduplication by `phone_id`.
7. Rerank: one LLM call. The code removes unknown and repeated IDs and applies a relevance threshold and a diversity limit of 5 listings per model. On any error the candidates are returned without reranking. See [RERANKING.md](docs/ai/RERANKING.md).

Listing creation (see [MY_LISTING.md](docs/features/MY_LISTING.md)):

- The LLM generates the description and the specifications from the model name. A model that does not exist returns HTTP 422. The seller reviews and edits the data before publishing.
- Guardrail 1 in three layers: Frontend Regex, Backend Regex, LLM check for toxic content, fraud and Prompt Injection. Fail closed. See [GUARDRAILS.md](docs/ai/GUARDRAILS.md#guardrail-1-phone-saving).

Quality and observability:

- Untrusted text (prompt, listing) is passed to the LLM inside delimiters as data.
- LangSmith traces each LLM call and each graph node: prompt, response, latency, tokens, cost.
- Plain tests of filters, guardrails and reranker output validation. DeepEval metrics of ranking. See [EVALUATION.md](docs/ai/EVALUATION.md).

### Claude Harness

The development process: `docs/` is written first, Claude Code generates the code from it, and the Validator checks the code against it. Entry point: [.claude/CLAUDE.md](.claude/CLAUDE.md). It is not a part of the product runtime.

| Role | Who | Output |
| --- | --- | --- |
| Engineer | Human | `TASK.md` of a task, approval of HIGH plans |
| Planner | Claude, `skills/Planner` | `PLAN.md` |
| Executor | Claude, `skills/Executor` | Code and `EXEC.md` |
| Validator | Claude, `skills/Validator` | `VALIDATION.md`: PASS or FAIL after tests and the check against `docs/` |

- Routing by complexity: LOW skips the Planner, HIGH adds the Engineer approval. `STATE.yaml` holds the stage and the next actor, one actor per invocation.
- Loop: a FAIL returns the task to the Executor with the issues, a repeated FAIL escalates it to the Engineer.
- Enforcement: the `PreToolUse` hook `enforce_matrix.py` blocks writes to the artifacts of another role and illegal stage transitions, `pre-commit` blocks a commit of a broken task, `ci_check.py` checks all open tasks.
- State in files, not in the chat context: work resumes after the context is cleared. `.claude/tasks/DONE/` is the audit trail of each feature of v1.0.
- Downside: overhead for small changes, reduced by the LOW route.

## End User and Interface

- Buyer: one text field with a hint and an example prompt, no filter controls, no registration. A vague prompt (`What phone should I give my wife for her birthday?`) gets one clarification question instead of random listings. A question that asks for advice gets a text answer. See [SEARCH_PAGE.md](docs/features/SEARCH_PAGE.md).
- Phone details: specifications, price, condition, the seller's note and the "Deal" button with the WhatsApp number. See [PHONE_DETAILS.md](docs/features/PHONE_DETAILS.md).
- Seller: enters the model name, the AI generates the description and the specifications, the seller reviews and edits them, then sets the condition and the price. See [MY_LISTING.md](docs/features/MY_LISTING.md).

### Web page with one prompt instead of a chat

- The result is a list of listings compared by price and condition. A list is easier to scan than chat messages.
- Each listing has its own URL: indexed by search engines and shared by link.
- To refine the search, the buyer edits the prompt and sends it again. The clarification covers the main case of a dialog without a chat.

## Architecture

- Backend: modular monolith on FastAPI, modules `users`, `auth`, `phones`, `rag`, `main`. See [backend/DESIGN.md](docs/backend/DESIGN.md).
- Frontend: Next.js, TypeScript, HeroUI v3, Tailwind CSS, React Hook Form, Zod, Zustand. See [frontend/DESIGN.md](docs/frontend/DESIGN.md).
- AI: OpenAI through LangChain, LangGraph search pipeline, pgvector hybrid RAG with reranking, guardrails. See [RAG.md](docs/ai/RAG.md), [GUARDRAILS.md](docs/ai/GUARDRAILS.md).
- Quality: LangSmith traces and datasets, DeepEval ranking metrics, plain tests of filters and guardrails, seed of 90 listings. See [EVALUATION.md](docs/ai/EVALUATION.md).
- Database: PostgreSQL (Supabase) with pgvector. Infra: VPS, Docker Compose, Caddy, Cloudflare. See [INFRA.md](docs/INFRA.md).

## Right-Sizing

The simplest version is one LLM call: prompt in, listing IDs out. Each component closes one failure of that version.

| Failure of one LLM call | Handling |
| --- | --- |
| Invented listings or prices | The LLM returns filters and model codes, SQL selects the listings |
| Broken hard limit ("under $400") | Price and condition are SQL filters |
| Rare or misspelled model | pgvector fallback below 20 results |
| Invalid JSON | Pydantic validation, node retry |

Guardrail and Parse fail closed (HTTP 503). Rerank fails open: on error the candidates are returned in SQL order, since rerank changes the order, not the content.

Considered and rejected: an agent with tools (variable number of LLM calls, harder to evaluate, the request is one-shot), vector search only (no exact model match, no price enforcement).

## Tooling and Tradeoffs

### AI

- LangGraph: the pipeline has branches (clarification, vector search when fewer than 20 listings are found) and a retry policy per node. The graph matches the diagram in [RAG.md](docs/ai/RAG.md#architecture) one node per step. Considered: plain async Python, where branches, per node retries and step tracing are written by hand.
- LangSmith: each LLM call and each graph node is traced with prompt, response, latency, tokens and cost, without additional code. Datasets of the generation steps are compared between runs after a prompt or model change. Considered: logs, which give no per step view and no run comparison.
- DeepEval: LLM judge retrieval metrics as pytest tests, no labeled listings needed. Considered: Ragas, whose metrics target answer generation, while the project returns ranked listings.
- OpenAI through LangChain: the provider is changed in the configuration. pgvector: hybrid search in one SQL query and one transaction with the listing.
- Seed of 90 listings: the PoC can be tested by hand right after `make seed`, and the evaluation sets use the same known data.

### Backend

- Modular monolith: fast PoC development, each module can be moved to a separate service later. See [ROADMAP.md](docs/ROADMAP.md#business-logic-complexity).
- Python and FastAPI: the AI libraries are Python-first, LLM calls are network I/O served asynchronously. Pydantic validates both the API contracts and the structured LLM output.

### Frontend and Infra

- Next.js: SEO of the Phone details page with server rendering and ISR. HeroUI: ready-made components, as [TASK.md](docs/TASK.md#out-of-scope-for-v10) requires.
- VPS with Docker Compose: fixed cost, the same setup locally and on the server. Supabase free tier: no database administration on the VPS.

### Not done on purpose

Registration, WhatsApp integration, model catalog, images, multi-turn chat: see [README.md](README.md#what-is-real-and-what-is-stubbed).
