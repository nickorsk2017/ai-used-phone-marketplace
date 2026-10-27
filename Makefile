FRONTEND_DIR := frontend
PNPM := pnpm --dir $(FRONTEND_DIR)

BACKEND_DIR := backend
UV := uv --directory $(BACKEND_DIR)
UV_RUN := $(UV) run --all-packages

PORTS := 3000 8000 5433

COMPOSE = docker compose $(foreach env_file,$(wildcard $(BACKEND_DIR)/.env $(FRONTEND_DIR)/.env),--env-file $(env_file))

.PHONY: help up down logs reset-db kill-all-ports docker-seed docker-seed-test docker-eval docker-env frontend-install frontend-build frontend-start frontend-dev backend-install backend-check backend-dev backend-test migrate migration seed seed-reset eval up-all

help:
	@echo "Docker:"
	@echo "  make up                Build the images, start PostgreSQL, apply the migrations, start the frontend and backend containers"
	@echo "  make down              Stop and remove the containers, the database volume is kept"
	@echo "  make logs              Follow the logs of the containers"
	@echo "  make reset-db          Stop the containers and delete the database volume, all data is lost"
	@echo "  make kill-all-ports    Free the ports $(PORTS): stop the containers that publish them, kill the other processes that listen on them"
	@echo "  make docker-seed       Apply the migrations, then load the seed users and listings into the database of the db container"
	@echo "  make docker-seed-test  Prepare the evaluation database in the db container: create, migrate, reload the seed when it changed"
	@echo "  make docker-eval       Run the evaluation in the backend container (DATASET=rag.parse runs one, LOCAL=1 without LangSmith), real OpenAI calls"
	@echo "All:"
	@echo "  make up-all            Apply migrations, start the frontend and backend dev servers together (Ctrl+C stops both)"
	@echo "Frontend:"
	@echo "  make frontend-install  Install frontend dependencies"
	@echo "  make frontend-build    Build the frontend for production"
	@echo "  make frontend-start    Start the production build"
	@echo "  make frontend-dev      Start the dev server"
	@echo "Backend:"
	@echo "  make backend-install   Install backend dependencies of all modules"
	@echo "  make backend-check     Check the backend environment variables, fail with the list of missing ones"
	@echo "  make backend-dev       Start the API on http://localhost:8000 with reload"
	@echo "  make backend-test      Run ruff and pytest (TEST_DATABASE_*)"
	@echo "  make migrate           Apply the migrations up to head"
	@echo "  make migration MSG=\"add phone index\"  Autogenerate the next numbered migration"
	@echo "  make seed              Apply the migrations, then load the seed users and listings into the database"
	@echo "  make seed-reset        Delete the seed users and listings, then load them again"
	@echo "  make eval              Run the LangSmith evaluation of all datasets (DATASET=rag.parse runs one, LOCAL=1 without LangSmith), real OpenAI calls"

# ============================================================
# Docker
# ============================================================

up: docker-env
	$(COMPOSE) build
	$(COMPOSE) run --rm --no-deps backend python -c "from modules.main.app import check_config; check_config()"
	$(COMPOSE) run --rm backend alembic upgrade head
	$(COMPOSE) up -d --wait
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

reset-db: docker-env
	$(COMPOSE) down -v

kill-all-ports:
	@for port in $(PORTS); do \
		containers=$$(docker ps -q --filter publish=$$port 2>/dev/null); \
		if [ -n "$$containers" ]; then \
			echo "Port $$port: stopping containers $$containers"; \
			docker stop $$containers >/dev/null; \
		fi; \
		for pid in $$(lsof -nP -iTCP:$$port -sTCP:LISTEN -t 2>/dev/null); do \
			name=$$(ps -p $$pid -o comm= 2>/dev/null); \
			case "$$name" in *docker*|*vpnkit*) echo "Port $$port: skipping Docker process $$pid ($$name)"; continue;; esac; \
			echo "Port $$port: killing $$pid ($$name)"; \
			kill $$pid 2>/dev/null; \
			sleep 1; \
			kill -0 $$pid 2>/dev/null && kill -9 $$pid 2>/dev/null; \
		done; \
	done; \
	echo "Ports $(PORTS) are free"

docker-seed: docker-env
	$(COMPOSE) run --rm --build backend alembic upgrade head
	$(COMPOSE) run --rm backend python -m seed.run

docker-seed-test: docker-env
	$(COMPOSE) run --rm --build backend python -m eval.database

docker-eval: docker-env
	$(COMPOSE) run --rm --build backend python -m eval.run $(if $(DATASET),--dataset $(DATASET)) $(if $(LOCAL),--local)

docker-env:
	@test -f $(BACKEND_DIR)/.env || { echo "Missing $(BACKEND_DIR)/.env, template: $(BACKEND_DIR)/.env.example"; exit 1; }
	@test -f $(FRONTEND_DIR)/.env || { echo "Missing $(FRONTEND_DIR)/.env, template: $(FRONTEND_DIR)/.env.example"; exit 1; }

# ============================================================
# All
# ============================================================

up-all: migrate
	$(MAKE) -j2 backend-dev frontend-dev

# ============================================================
# Frontend
# ============================================================

frontend-install:
	$(PNPM) install

frontend-build:
	$(PNPM) build

frontend-start:
	$(PNPM) start

frontend-dev:
	$(PNPM) dev

# ============================================================
# Backend
# ============================================================

backend-install:
	$(UV) sync --all-packages

backend-check:
	@$(UV_RUN) python -c "from modules.main.app import check_config; check_config()"

backend-dev: backend-check
	$(UV_RUN) uvicorn main:app --reload --port 8000

backend-test:
	$(UV_RUN) ruff check --quiet .
	$(UV_RUN) pytest
	@printf '\033[1;32mAll checks passed!\033[0m\n'

migrate: backend-check
	$(UV_RUN) alembic upgrade head

migration: backend-check
	@test -n "$(MSG)" || { echo "Usage: make migration MSG=\"<description>\""; exit 1; }
	@next=$$(printf "%04d" $$(( $$(ls $(BACKEND_DIR)/migrations/versions/*.py 2>/dev/null | wc -l) + 1 ))); \
		$(UV_RUN) alembic revision --autogenerate --rev-id $$next -m "$(MSG)"

seed: migrate
	$(UV_RUN) python -m seed.run

seed-reset: migrate
	$(UV_RUN) python -m seed.run --reset

eval:
	$(UV_RUN) python -m eval.run $(if $(DATASET),--dataset $(DATASET)) $(if $(LOCAL),--local)

# ============================================================
# Infrastructure
# ============================================================
