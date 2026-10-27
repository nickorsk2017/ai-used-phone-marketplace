# TODO.md

v1.0 is a demo application (PoC) without production load. Some parts are simplified on purpose. This document lists what a production version could include.

The items below are hypothetical. In a real project, the architecture is built on actual needs: measured load, bottlenecks and business requirements. They are not known in advance, and this project does not include them.

Product features out of scope for v1.0: see [TASK.md](../TASK.md#out-of-scope-for-v10).

## Production baseline

| Area | Item | Details |
|------|------|---------|
| Infrastructure | CDN | CDN for the Frontend. |
| Infrastructure | Environments | Separate staging and production environments. |
| Infrastructure | Secrets | Secrets in a secret manager instead of `.env` on the server. |
| Infrastructure | Managed PostgreSQL | Managed PostgreSQL with pgvector, automatic backups and point-in-time recovery instead of the `db` container. |
| Infrastructure | Observability | Monitoring, alerts and centralized logs. |
| Auth | Authorization and registration | Full authorization and registration: login, logout, expiration and revocation of a session. |
| CI | Quality gate | Unit tests, integration tests and LLM evaluation (`make eval LOCAL=1`) before deployment. |
| AI | Online search metrics | Metrics from real users: position of the clicked result, share of searches with a Phone details view, share of searches with a Deal click, sent as LangSmith feedback on the `rag.search` trace. A larger evaluation dataset from real prompts. |
| AI | AI model router | Comparison of several LLM models by quality, cost and latency. |
| AI | Description cache | Cache of `POST /api/phones/description` results by model. The same model name (for example, `iPhone 16`) always returns the same description and model data, without a new LLM call. |
| AI | Model catalog | Model catalog instead of the model code from the LLM: see [RAG.md](ai/RAG.md#production-model-catalog). |
| Backend | Update of a listing | `PATCH /api/phones/{id}`, access level `Owner`. Guardrail 1, the listing and its search index record in one transaction, as on create ([RAG.md](ai/RAG.md#indexing)). The embedding is regenerated only if the model name, description or condition note changed. Price, condition and specification changes update the copied fields only. |
| Backend | Idempotent create | `Idempotency-Key` on `POST /api/phones`: a retried request does not create a second listing, see [DESIGN.md](backend/DESIGN.md#transaction-retry-without-idempotency). |
| Frontend | Sitemap | Sitemap of the Phone details pages (`app/sitemap.ts`) with a Backend endpoint that lists all active listings with their update dates. |
| Frontend | Design System | Atomic Design: atoms, molecules and organisms in `frontend/ui` on top of the HeroUI tokens from `themes/theme.css`. Storybook as the component catalog with stories for each state and visual regression tests. |
| Frontend | Accessibility | WCAG 2.2 AA: keyboard navigation of search, listings and modals, screen reader announcements of loading, results, clarification and errors, color contrast of condition badges. Automated checks with axe in the Frontend tests and in CI. |

## Architecture under growth

### High load

```
CDN -> Load balancer -> backend replicas (autoscaling)
                     -> Redis (cache, rate limit)
                     -> PostgreSQL (pooler, read replicas)
                     -> RabbitMQ -> indexing workers -> search engine (Pinecone or Elasticsearch)
```

| Area | Item | Details |
|------|------|---------|
| Infrastructure | Container platform | The same Docker images on a managed container platform (Cloud Run or Kubernetes). The backend is stateless and scales horizontally. |
| Backend | Redis | Cache of search results by prompt and filters, cache of LLM responses, shared rate limit storage for all instances. |
| Database | PostgreSQL scaling | Connection pooling, read replicas for search queries. |
| Backend | Indexing queue | Indexing through RabbitMQ: a separate `worker` process scaled independently from the API. Retries with backoff and a dead-letter queue. |
| AI | Search engine | Search index moved from pgvector to a dedicated search engine when search load or volume requires it. Only `modules/rag` changes. Consistency between PostgreSQL and the search engine: indexing status per listing and a reindex job for failed or orphaned records. |
| AI | LLM models | A smaller model for query parsing, a fallback model on provider errors or rate limits. |
| Frontend | On-demand revalidation | A Next.js Route Handler `POST /api/revalidate` with a secret token, called by the Backend when a listing is updated or deleted. It calls `revalidatePath` for the listing URL, so the change is visible immediately instead of after the time-based revalidation. |

### Business logic complexity

```
Frontend -> API Gateway (main) -> Auth service
                               -> Phones service
                               -> RAG service
           Services <-> Kafka (events: phone.created, phone.deleted)
```

| Area | Item | Details |
|------|------|---------|
| Architecture | Microservices | Modules moved to separate microservices along DDD boundaries, the `main` module becomes an API gateway: see [DESIGN.md](backend/DESIGN.md#modules). |
| Architecture | Events | Event-driven communication between services through Kafka instead of direct calls. Outbox pattern for consistency between the database and the broker. |
| Database | Database per service | Each service owns its database. |
| Product | New domains | Separate services: deals, moderation (antifraud and guardrails), notifications (WhatsApp integration). |
