# DESIGN.md

System-level architecture. Each part is described in its own folder: [backend/DESIGN.md](backend/DESIGN.md), [frontend/DESIGN.md](frontend/DESIGN.md), [ai/DESIGN.md](ai/DESIGN.md).

## Approaches

1. Documentation first. `docs/` is the source of truth about the architecture and the product. Design comes first, code comes after it: a module is described in the documentation, then the code is generated from it. A change in behavior starts with a change in the documentation. Rules: [CLAUDE.md](../CLAUDE.md#1-documentation-is-the-source-of-truth). See [Rationale](#documentation-first).
2. Claude Harness. Tasks are executed by a pipeline with four roles: Engineer, Planner, Executor and Validator. The agent works by fixed rules and a fixed flow: each role follows its own instructions in `.claude/skills/<Role>/SKILL.md`, writes only its own artifacts and moves the task along a state machine. Entry point: [.claude/CLAUDE.md](../.claude/CLAUDE.md). See [Rationale](#claude-harness).
3. Additional rules in `CLAUDE.md`. Rules for the agent that are not described in `docs/` are placed in [CLAUDE.md](../CLAUDE.md) and in the `CLAUDE.md` of each subsystem. These rules do not contradict `docs/`. On a discrepancy the agent lists it for the Engineer and does not resolve it silently.

## End User and Interface

### Buyer

A person who wants to buy a phone cheaper. The device and its practicality matter more than novelty.

- Search page: one text field with a hint and an example prompt, no filter controls. The buyer describes the phone in own words: condition, budget, brand, camera, battery. See [SEARCH_PAGE.md](features/SEARCH_PAGE.md).
- Phone details page: specifications, price, condition, the seller's note and the "Deal" button with the seller's WhatsApp number. See [PHONE_DETAILS.md](features/PHONE_DETAILS.md).
- No registration: search and Deal work without a user. See [AUTH.md](backend/AUTH.md#session-flow).

Why a web page with one prompt instead of a chat: see [Rationale](#web-page-with-one-prompt-instead-of-a-chat).

### Seller

A person who sells a used phone.

- My listings page: the seller enters the model name, the AI generates the description and the specifications, the seller reviews and edits them, then sets the condition and the price. See [MY_LISTING.md](features/MY_LISTING.md).

## Architecture

Why each technology is chosen: see [Rationale](#rationale).

- Backend: a modular monolith on Python and FastAPI with the modules `auth`, `phones`, `rag` and `main`. Pydantic, SQLAlchemy, Alembic. See [backend/DESIGN.md](backend/DESIGN.md).
- Frontend: Next.js, React, TypeScript, HeroUI v3, Tailwind CSS, React Hook Form, Zod, Zustand. See [frontend/DESIGN.md](frontend/DESIGN.md).
- AI: OpenAI through LangChain, LangGraph for the search pipeline, pgvector for the vector index, DeepEval and LangSmith for evaluation. See [ai/DESIGN.md](ai/DESIGN.md).
- Database: PostgreSQL (Supabase) with the pgvector extension. See [backend/SCHEMAS.md](backend/SCHEMAS.md).
- Infra: a VPS with Docker Compose, Caddy and Cloudflare, images built in GitHub Actions. See [INFRA.md](INFRA.md).

## Rationale

### Web page with one prompt instead of a chat

- The result is a list of listings that the buyer compares by price and condition. A list on a page is easier to scan than chat messages.
- Each listing has its own page with a URL: it is indexed by search engines and can be shared by link. A chat has no page per listing.
- One prompt is enough to describe the request. To refine the search, the buyer edits the prompt and sends it again. A multi-turn dialog is not needed in v1.0.

### Documentation first

- One source of truth for the Engineer and the agent: the agent generates code from the documents, and the Validator checks the code against them.
- Decisions and their rationale are reviewed before the code is written. A change in a document is cheaper than a change in the code.
- Downside: every change of behavior needs a document change first. The documentation and the code can drift apart: the agent lists each discrepancy for the Engineer, see [CLAUDE.md](../CLAUDE.md#1-documentation-is-the-source-of-truth).

### Claude Harness

- Planning, implementation and validation are separate roles. The Validator does not check its own code.
- The rules are enforced by a hook and by CI, not only by the prompt: a role cannot write the artifacts of another role, and a task cannot be closed without a PASS validation.
- The state of a task is stored in files, not in the chat context. Work can be resumed after the context is cleared.
- Downside: overhead for small changes. Tasks of LOW complexity skip the Planner.

### Backend

- Modular monolith: fast MVP development, each module can be moved to a separate microservice later. See [ROADMAP.md](ROADMAP.md#business-logic-complexity).
- Python: the AI libraries of the project (LangChain, LangGraph, DeepEval, LangSmith) are Python-first. The Backend and the AI pipeline are one codebase in one language.
- FastAPI: asynchronous. LLM and embedding calls are network I/O, one process serves other requests while it waits for the provider. The OpenAPI schema is generated from the Pydantic models.
- Pydantic: one schema library for the API contracts and for the structured LLM output. An LLM response that fails validation is retried: see [RAG.md](ai/RAG.md#errors-and-retries).
- SQLAlchemy and Alembic: ORM and versioned migrations, one chain for the Backend: see [SCHEMAS.md](backend/SCHEMAS.md#migrations).

### Database

- Supabase: managed PostgreSQL with pgvector, one database for the listings and the search index. Free tier for the PoC, no database administration on the VPS, the server stays stateless. The free tier pauses an inactive project: the paid tier is in [ROADMAP.md](ROADMAP.md#production-baseline).

### AI

- OpenAI through LangChain: the provider is changed in the configuration without changes in the pipeline code. See [ai/DESIGN.md](ai/DESIGN.md#langchain-and-the-model-provider).
- LangGraph: the search pipeline has conditions and retries, not a linear chain. See [RAG.md](ai/RAG.md#langgraph).
- pgvector: hybrid search in one SQL query and one transaction for the listing and its index. See [RAG.md](ai/RAG.md#pgvector-vs-a-dedicated-search-engine).
- DeepEval and LangSmith: evaluation, observability and cost of the LLM calls. See [EVALUATION.md](ai/EVALUATION.md).

### Frontend

- Next.js: SEO is required for the Phone details page. The indexed page is rendered on the server with ISR, the session-dependent pages are Client Components. See [PHONE_DETAILS.md](features/PHONE_DETAILS.md#seo).
- TypeScript: typed contracts with the Backend API.
- HeroUI v3: [TASK.md](TASK.md#out-of-scope-for-v10) requires ready-made UI components, HeroUI is the chosen library. See [frontend/DESIGN.md](frontend/DESIGN.md#heroui).
- Tailwind CSS: HeroUI v3 is built on it, the theme tokens and the spacing scale come from one system. See [frontend/DESIGN.md](frontend/DESIGN.md#ui).
- React Hook Form and Zod: form state of the listing form, validation rules and TypeScript types in one schema. See [frontend/SCHEMAS.md](frontend/SCHEMAS.md).
- Zustand: client state of the Client Component pages without a provider tree and boilerplate. The state in v1.0 is small, Redux is not needed.

### Infra

- VPS with Docker Compose: one deployment flow, fixed cost, the same setup locally and on the server. See [INFRA.md](INFRA.md#vps-vs-serverless).
