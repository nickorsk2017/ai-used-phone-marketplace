FRONTEND_DIR := frontend
PNPM := pnpm --dir $(FRONTEND_DIR)

.PHONY: help frontend-install frontend-build frontend-start frontend-dev

help:
	@echo "Frontend:"
	@echo "  make frontend-install  Install frontend dependencies"
	@echo "  make frontend-build    Build the frontend for production"
	@echo "  make frontend-start    Start the production build"
	@echo "  make frontend-dev      Start the dev server"

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

# ============================================================
# Infrastructure
# ============================================================
