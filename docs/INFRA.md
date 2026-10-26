# INFRA.md

## Decision

v1.0 runs on a single server with Docker Compose. The server and the reverse proxy (for example Nginx or Caddy) are not fixed by the project.

External providers are connected by API keys only:

- Supabase: PostgreSQL.
- OpenAI: LLM and embeddings.
- LangSmith: traces and evaluation of the LLM calls, optional: see [EVALUATION.md](ai/EVALUATION.md#langsmith).
- The vector index is stored in Supabase PostgreSQL with pgvector, no separate vector database.

## Architecture

```
Internet -> reverse proxy (443, HTTPS) -> frontend (Next.js standalone)
                                        -> backend (FastAPI)

backend -> Supabase (PostgreSQL)
        -> OpenAI
        -> LangSmith (optional)
```

Docker Compose services:

- `frontend`: Next.js with `output: "standalone"`.
- `backend`: FastAPI (Uvicorn).

## Build and deployment

1. Build the `frontend` and `backend` images.
2. `make deploy` runs `docker compose pull` and `docker compose up -d` on the server.

The image platform must match the server architecture (`linux/amd64` or `linux/arm64`).

## Server requirements

- Server with 1 to 2 GB RAM.
- Swap file 2 to 4 GB as a safety margin.
- Next.js `output: "standalone"` and multi-stage Dockerfiles with `uv` to reduce image size and memory usage.

## Security

- Open ports: 22, 80, 443 only.
- SSH key authentication, password login disabled.
- `unattended-upgrades` for security updates.
- Secrets are stored in `.env` on the server and are not committed to the repository.

## Protection

### Application

Rate limit in `modules/main`, a separate limit for every module or endpoint. A limit is a FastAPI dependency on the router or the endpoint. An exceeded limit returns 429 with `Retry-After`.

| Module | Endpoints | Limit |
| --- | --- | --- |
| `modules/users` | `/api/users/*` | 5 requests per 10 seconds per client IP, shared by all endpoints of the module |
| `modules/phones` | `POST /api/phones/description` | 1 request per 10 seconds per client IP, own counter. Protection against cost attacks on OpenAI |
| `modules/phones` | `POST /api/phones` | 1 request per 10 seconds per client IP, own counter. Protection against spam listings and cost attacks |
| `modules/phones` | `GET /api/my-listings` | 5 requests per 10 seconds per client IP, own counter. The page load and the reload after `POST /api/phones` ([MY_LISTING.md](features/MY_LISTING.md#add-phone-flow)) fit in the limit |
| `modules/rag` | `POST /api/search` | 3 requests per 10 seconds per client IP, own counter. Protection against cost attacks on OpenAI |

- The counters are stored in the memory of the process. With several Uvicorn workers every worker has its own counters. Shared storage: see [ROADMAP.md](ROADMAP.md#high-load).
- The client IP comes from `X-Forwarded-For`: the reverse proxy forwards the client IP, Uvicorn runs with `--proxy-headers --forwarded-allow-ips=<proxy address>`. Without these settings all requests have the proxy IP and share one limit.

Stricter limits are planned for the other modules:

- `GET /api/phones/{id}/contact`: protection of WhatsApp numbers against scraping.

A monthly spending limit is set in OpenAI.

## Makefile targets

- `make deploy`: pull the latest images and restart services on the server.
- `make logs`: show service logs.
- `make migrate`: apply Alembic migrations. Other migration commands: see [SCHEMAS.md](backend/SCHEMAS.md#migrations).
- `make up-all`
- `make frontend-install`
- `make frontend-build`
- `make frontend-start`
- `make frontend-dev`
- `make backend-install`
- `make backend-check`
- `make backend-dev`
- `make backend-test`
- `make eval`: LangSmith evaluation, see [EVALUATION.md](ai/EVALUATION.md#run).

## Improvement

This is the PoC version. Possible improvements are described in [ROADMAP.md](ROADMAP.md).

## Tradeoffs

### Server vs Serverless

- Single deployment: the Frontend and the Backend run in one `docker-compose.yml` with one deployment flow.
- Fixed cost and the same Docker Compose setup locally and on the server.
- Stateless server: data and the search index are stored in Supabase, the server can be recreated with one command.
