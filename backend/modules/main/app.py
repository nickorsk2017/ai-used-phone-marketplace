import os
import sys

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config_errors as database_config_errors
from modules.main.config import config_errors, get_settings
from modules.main.routers import health, users


def check_config() -> None:
    """Stop the process when required environment variables are missing: docs/backend/DESIGN.md#configuration."""
    errors = [*database_config_errors(), *config_errors()]
    if errors:
        lines = "\n".join(f"  - {error}" for error in errors)
        message = (
            "Backend configuration error. Missing or invalid environment variables:\n"
            f"{lines}\n"
            "Set them in backend/.env (template: backend/.env.example) or in the environment."
        )
        raise SystemExit(_red(message))


def _red(text: str) -> str:
    """Red in a terminal, plain text in logs and with `NO_COLOR`."""
    if os.environ.get("NO_COLOR") or not sys.stderr.isatty():
        return text
    return f"\033[31m{text}\033[0m"


def create_app() -> FastAPI:
    check_config()
    app = FastAPI(title="Second-Hand Mobile E-market API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(users.router)
    app.include_router(api)
    return app
