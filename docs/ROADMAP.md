# ROADMAP.md

v1.0 is a demo application (PoC) without production load. Some parts are simplified on purpose. This document lists what a production version could include.

The items below are hypothetical. In a real project, the architecture is built on actual needs: measured load, bottlenecks and business requirements. They are not known in advance, and this project does not include them.

Product features out of scope for v1.0: see [TASK.md](TASK.md#out-of-scope-for-v10).

## Production baseline

- CDN for the Frontend.
- Separate staging and production environments.
- Secrets in a secret manager instead of `.env` on the server.
- Paid tier of Supabase without project pausing and with higher limits.
- Full authorization and registration with signed sessions.
- CI quality gate: unit tests, integration tests and LLM evaluation (DeepEval) before deployment.
- Online search metrics from real users: position of the clicked result, share of searches with a Phone details view, share of searches with a Deal click. A larger evaluation dataset from real prompts.
- Monitoring, alerts and centralized logs.
- AI model router to compare several LLM models by quality, cost and latency.
- Sitemap of the Phone details pages (`app/sitemap.ts`) with a Backend endpoint that lists all active listings with their update dates.
- Cache of `POST /api/phones/description` results by model. The same model name (for example, `iPhone 16`) always returns the same description and model data, without a new LLM call.
- Model catalog instead of the model code from the LLM: see [RAG.md](ai/RAG.md#production-model-catalog).
- Design System for the Frontend on Atomic Design: atoms, molecules and organisms in `frontend/ui` on top of the HeroUI tokens from `themes/theme.css`. Storybook as the component catalog with stories for each state and visual regression tests.

## Architecture under growth

### High load

```
CDN -> Load balancer -> backend replicas (autoscaling)
                     -> Redis (cache, rate limit)
                     -> PostgreSQL (pooler, read replicas)
                     -> RabbitMQ -> indexing workers -> search engine (Pinecone or Elasticsearch)
```

- The same Docker images on a managed container platform (Cloud Run or Kubernetes). The backend is stateless and scales horizontally.
- Redis: cache of search results by prompt and filters, cache of LLM responses, shared rate limit storage for all instances.
- PostgreSQL: connection pooling, read replicas for search queries.
- Indexing through RabbitMQ: a separate `worker` process scaled independently from the API. Retries with backoff and a dead-letter queue.
- Search index moved from pgvector to a dedicated search engine when search load or volume requires it. Only `modules/rag` changes. Consistency between PostgreSQL and the search engine: indexing status per listing and a reindex job for failed or orphaned records.
- LLM: a smaller model for query parsing, a fallback model on provider errors or rate limits.
- On-demand revalidation of the Phone details page: a Next.js Route Handler `POST /api/revalidate` with a secret token, called by the Backend when a listing is updated or deleted. It calls `revalidatePath` for the listing URL, so the change is visible immediately instead of after the time-based revalidation.

### Business logic complexity

```
Frontend -> API Gateway (main) -> Auth service
                               -> Phones service
                               -> RAG service
           Services <-> Kafka (events: phone.created, phone.deleted)
```

- Modules moved to separate microservices along DDD boundaries, the `main` module becomes an API gateway: see [DESIGN.md](backend/DESIGN.md#modules).
- Event-driven communication between services through Kafka instead of direct calls. Outbox pattern for consistency between the database and the broker.
- Database per service.
- New domains as separate services: deals, moderation (antifraud and guardrails), notifications (WhatsApp integration).
