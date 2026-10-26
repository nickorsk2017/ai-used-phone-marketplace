FRONTEND_DIR := frontend
PNPM := pnpm --dir $(FRONTEND_DIR)

BACKEND_DIR := backend
UV := uv --directory $(BACKEND_DIR)
UV_RUN := $(UV) run --all-packages

.PHONY: help frontend-install frontend-build frontend-start frontend-dev backend-install backend-check backend-dev backend-test migrate migration up-all

help:
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
	@echo "  make backend-test      Run ruff and pytest (TEST_DATABASE_URL)"
	@echo "  make migrate           Apply the migrations up to head"
	@echo "  make migration MSG=\"add phone index\"  Autogenerate the next numbered migration"

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
	$(UV_RUN) ruff check .
	$(UV_RUN) pytest

migrate: backend-check
	$(UV_RUN) alembic upgrade head

migration: backend-check
	@test -n "$(MSG)" || { echo "Usage: make migration MSG=\"<description>\""; exit 1; }
	@next=$$(printf "%04d" $$(( $$(ls $(BACKEND_DIR)/migrations/versions/*.py 2>/dev/null | wc -l) + 1 ))); \
		$(UV_RUN) alembic revision --autogenerate --rev-id $$next -m "$(MSG)"

# ============================================================
# Infrastructure
# ============================================================
