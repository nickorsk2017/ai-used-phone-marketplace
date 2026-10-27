# DOCUMENTATION.md

List of the project documents. `docs/` is the source of truth: the system is designed here first, the code is written after that.

## Principles

1. Every product decision, module, data model and API contract is described in `docs/` before implementation.
2. The Claude agent generates code from the documentation and follows the rules in [CLAUDE.md](../CLAUDE.md) and in the `CLAUDE.md` of each subsystem.
3. Each fact is described in one document only. Other documents link to it.
4. A change in behavior starts with a change in the documentation. Code follows the documentation.
5. If the documentation and the code disagree, the agent does not resolve the conflict silently. It lists the discrepancies for the Engineer to fix.

## System

| Document | Content |
| --- | --- |
| [TASK.md](../TASK.md) | Product, problem, business requirements, scope of v1.0 |
| [BRIEF.md](../BRIEF.md) | Design document: problem, harnesses, interface, architecture |
| [INFRA.md](INFRA.md) | Docker Compose, deployment, protection |
| [TODO.md](TODO.md) | Production version and architecture under growth |

## Backend

| Document | Content |
| --- | --- |
| [DESIGN.md](backend/DESIGN.md) | Stack, modules, indexing, protection |
| [STRUCTURE.md](backend/STRUCTURE.md) | Folders and files of the application and its modules |
| [SCHEMAS.md](backend/SCHEMAS.md) | Data models, search index, migrations |
| [API.md](backend/API.md) | Endpoints |
| [AUTH.md](backend/AUTH.md) | Browser session without registration, access rules |

## AI

| Document | Content |
| --- | --- |
| [DESIGN.md](ai/DESIGN.md) | AI stack, AI in the Backend modules |
| [HARNESS.md](ai/HARNESS.md) | LLM Harness (RAG Harness): LLM calls, contracts, validation, failure handling |
| [CLAUDE-HARNESS.md](ai/CLAUDE-HARNESS.md) | Claude Harness: development process with Planner, Executor, Validator |
| [RAG.md](ai/RAG.md) | Search: hybrid RAG, LLM output, model code |
| [RERANKING.md](ai/RERANKING.md) | Reranker: input, output validation, diversity limit, fallback |
| [GUARDRAILS.md](ai/GUARDRAILS.md) | Toxic content, fraud and Prompt Injection protection of listings, Prompt Injection protection of search |
| [EVALUATION.md](ai/EVALUATION.md) | Evaluation, Observability and cost of the LLM calls |

## Frontend

| Document | Content |
| --- | --- |
| [DESIGN.md](frontend/DESIGN.md) | Stack, pages, rendering, UI rules |
| [STRUCTURE.md](frontend/STRUCTURE.md) | Folders and files of the application |
| [SCHEMAS.md](frontend/SCHEMAS.md) | Types, form validation, browser storage |

## Features

| Document | Page |
| --- | --- |
| [SEARCH_PAGE.md](features/SEARCH_PAGE.md) | Search by prompt |
| [MY_LISTING.md](features/MY_LISTING.md) | My listings: create and delete a listing |
| [PHONE_DETAILS.md](features/PHONE_DETAILS.md) | Phone details: SEO, Deal flow |
