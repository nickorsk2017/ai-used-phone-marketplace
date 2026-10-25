# INFRA.md

## Decision

v1.0 runs on a single VPS (about $5/month) with Docker Compose. Docker images are built in GitHub Actions, the VPS only pulls and runs them.

External providers are connected by API keys only:

- Supabase: PostgreSQL.
- OpenAI: LLM and embeddings.
- The vector index is stored in Supabase PostgreSQL with pgvector, no separate vector database.

## Architecture

```
Internet -> Cloudflare -> Caddy (443, HTTPS) -> frontend (Next.js standalone)
                                              -> backend (FastAPI)

backend -> Supabase (PostgreSQL)
        -> OpenAI
```

Docker Compose services:

- `caddy`: reverse proxy, TLS with a Cloudflare Origin Certificate. The certificate is configured in Caddy on the server, not in Docker.
- `frontend`: Next.js with `output: "standalone"`.
- `backend`: FastAPI (Uvicorn).

## Build and deployment

1. `git push` to the main branch.
2. GitHub Actions builds the `frontend` and `backend` images and pushes them to GitHub Container Registry (GHCR).
3. `make deploy` connects to the VPS over SSH and runs `docker compose pull` and `docker compose up -d`.

The server does not build images. If a build fails, the previous version keeps running.

The image platform must match the VPS architecture (`linux/amd64` or `linux/arm64`).

## Server requirements

- VPS with 1 to 2 GB RAM.
- Swap file 2 to 4 GB as a safety margin.
- Next.js `output: "standalone"` and multi-stage Dockerfiles with `uv` to reduce image size and memory usage.

## Security

- Open ports: 22, 80, 443 only.
- SSH key authentication, password login disabled.
- `unattended-upgrades` for security updates.
- Secrets are stored in `.env` on the server and are not committed to the repository.

## Protection

### Cloudflare

- All traffic goes through the Cloudflare proxy. The VPS IP address is not public.
- DDoS protection on the network and HTTP levels.
- SSL mode Full (strict): HTTPS from the user to Cloudflare and from Cloudflare to Caddy.
- Security rules (WAF): managed rules against common attacks (SQL injection, XSS), blocking of known bad bots.
- Rate limiting rules on `/api/*` per IP against DoS and scraping.

### Server

- Ports 80 and 443 accept traffic only from Cloudflare IP ranges. Direct requests to the VPS IP are blocked.

### Application

Rate limit in `modules/main` per IP and per user. Stricter limits apply to:

- LLM endpoints (`/api/search`, `/api/phones/description`): protection against cost attacks on OpenAI.
- `GET /api/phones/{id}/contact`: protection of WhatsApp numbers against scraping.
- `POST /api/phones`: protection against spam listings.

A monthly spending limit is set in OpenAI.

## Makefile targets

- `make deploy`: pull the latest images and restart services on the VPS.
- `make logs`: show service logs.
- `make migrate`: apply Alembic migrations to Supabase.

## Improvement

This is the PoC version. Possible improvements are described in [ROADMAP.md](ROADMAP.md).

## Tradeoffs

### VPS vs Serverless

- Single deployment: the Frontend, the Backend and the reverse proxy run in one `docker-compose.yml` with one deployment flow.
- Fixed cost and the same Docker Compose setup locally and on the server.
- Stateless server: data and the search index are stored in Supabase, the server can be recreated with one command.
