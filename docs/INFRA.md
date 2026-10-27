# INFRA.md

## Decision

v1.0 runs on a single server with Docker Compose. The server and the reverse proxy (for example Nginx or Caddy) are not fixed by the project.

PostgreSQL with the pgvector extension runs in a Docker container on the same server: the `db` service. The vector index is stored in the same database, no separate vector database.

External providers are connected by API keys only:

- OpenAI: LLM and embeddings.
- LangSmith: traces and evaluation of the LLM calls, optional: see [EVALUATION.md](ai/EVALUATION.md#langsmith).

## Architecture

```
Internet -> reverse proxy (443, HTTPS) -> frontend (Next.js standalone)
                                        -> backend (FastAPI)

backend -> db (PostgreSQL + pgvector, Docker volume)
        -> OpenAI
        -> LangSmith (optional)
```

## Docker Compose

`docker-compose.yml` in the repository root, started with `make up` and stopped with `make down`. The same setup runs locally and on the server.

Services:

- `db`: PostgreSQL 17 with pgvector, image `pgvector/pgvector:pg17`. Data is stored in the `postgres-data` volume and is kept after `make down`. Port 5432 inside the Docker network, `127.0.0.1:5433` on the host for `psql`.
- `frontend`: Next.js with `output: "standalone"`, `frontend/Dockerfile`, port 3000. Starts after `backend` is healthy.
- `backend`: FastAPI (Uvicorn), `backend/Dockerfile`, port 8000. Starts after `db` is healthy. Health check: `GET /api/health`, see [API.md](backend/API.md).

Configuration:

- `make up` reads `backend/.env` and `frontend/.env`.
- `db` is created with `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` from `backend/.env`. The values are applied on the first start only, when the volume is empty.
- `backend` reads `backend/.env` and connects with `POSTGRES_*`, see [DESIGN.md](backend/DESIGN.md#configuration). `docker-compose.yml` sets `POSTGRES_HOST=db` and `POSTGRES_PORT=5432`, so the working database and the evaluation database of `EVAL_DATABASE_*` are in `db`. Without Docker (`make backend-dev`) the defaults `localhost` and `5432` are used.
- `NEXT_PUBLIC_API_BASE_URL` and `NEXT_PUBLIC_SITE_URL` are read from `frontend/.env` at build time: Next.js inlines them into the build. A change requires a new build (`make up`).
- `API_INTERNAL_URL` (`http://backend:8000`): the Backend URL for server-side requests of the Frontend (Phone details, ISR), set in `docker-compose.yml`. The browser uses `NEXT_PUBLIC_API_BASE_URL`. Without `API_INTERNAL_URL` server-side requests use `NEXT_PUBLIC_API_BASE_URL`.
- `FORWARDED_ALLOW_IPS` (default `127.0.0.1`): the proxy addresses trusted by Uvicorn `--proxy-headers`, see [Application](#application).

`make up`:

1. Checks that `backend/.env` and `frontend/.env` exist.
2. Builds the `frontend` and `backend` images.
3. Checks the Backend configuration in a one-off `backend` container (`check_config`, see [DESIGN.md](backend/DESIGN.md#configuration)).
4. Starts `db` and applies the Alembic migrations in a one-off `backend` container.
5. Starts the services in the background and waits until they are healthy.

All ports are published on `127.0.0.1` only: `frontend` 3000, `backend` 8000, `db` 5433. On the server the reverse proxy is the only entry point from the Internet. Docker writes its own iptables rules and bypasses the firewall, so a port published on all interfaces would be open to the Internet.

## Build and deployment

Deployment goes through GitHub pull requests. Branches:

- `dev`: development. Feature branches are merged into `dev` through pull requests.
- `production`: the deployed version. Changes reach `production` only through a pull request from `dev`.

A merge into `production` deploys the new version to the server: the `frontend` and `backend` images are built and the services are restarted with Docker Compose, see [Docker Compose](#docker-compose).

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
| `modules/phones` | `GET /api/phones/{id}/contact` | 5 requests per 60 seconds per client IP, own counter. Protection of WhatsApp numbers against scraping |
| `modules/rag` | `POST /api/search` | 3 requests per 10 seconds per client IP, own counter. Protection against cost attacks on OpenAI |

- The counters are stored in the memory of the process. With several Uvicorn workers every worker has its own counters. Shared storage: see [TODO.md](TODO.md#high-load).
- The client IP comes from `X-Forwarded-For`: the reverse proxy forwards the client IP, Uvicorn runs with `--proxy-headers` and `FORWARDED_ALLOW_IPS=<proxy address>`. Without these settings all requests have the proxy IP and share one limit.

A monthly spending limit is set in OpenAI.

## Makefile targets

- `make up`: build the images, apply the migrations and start the services, see [Docker Compose](#docker-compose).
- `make down`: stop and remove the containers.
- `make logs`: follow the service logs.
- `make reset-db`: stop and remove the containers and delete the `postgres-data` volume. All data is lost. Needed when `POSTGRES_USER`, `POSTGRES_PASSWORD` or `POSTGRES_DB` changed after the first start, see [Docker Compose](#docker-compose).
- `make kill-all-ports`: free the host ports 3000, 8000 and 5433: stop the Docker containers that publish them, kill the other processes that listen on them (SIGTERM, then SIGKILL after 1 second). Docker Desktop processes are skipped.
- `make docker-seed`: apply the migrations and load the [seed](backend/STRUCTURE.md#seed) into the database of `db`. Real OpenAI calls (embeddings).
- `make docker-eval`: run the [evaluation](ai/EVALUATION.md#run) in a one-off `backend` container on the evaluation database in `db`, with the parameters of `make eval` (`DATASET`, `LOCAL`). Real OpenAI calls.
- `make docker-seed-test`: prepare the [evaluation database](ai/EVALUATION.md#evaluation-database) `EVAL_DATABASE_DB` in `db` without running the evaluation: create it, apply the migrations, reload the seed when its fingerprint changed. Real OpenAI calls (embeddings) on a reload.
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

This is the PoC version. Possible improvements are described in [TODO.md](TODO.md).

## Tradeoffs

### Server vs Serverless

- Single deployment: the Frontend and the Backend run in one `docker-compose.yml` with one deployment flow.
- Fixed cost and the same Docker Compose setup locally and on the server.
- PostgreSQL in a container on the same server: no external database provider and no extra cost for the PoC. The data lives in the `postgres-data` volume of the server, backups are not set up in v1.0: see [TODO.md](TODO.md).
