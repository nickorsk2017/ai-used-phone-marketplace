import os
import sys

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import config_errors as database_config_errors
from core.tracing import config_errors as tracing_config_errors
from core.tracing import configure_tracing
from modules.main.config import config_errors, get_settings
from modules.main.routers import health, my_listings, phones, search, users
from modules.phones.config import config_errors as phones_config_errors
from modules.rag.config import config_errors as rag_config_errors


def check_config() -> None:
    """Stop the process when required environment variables are missing: docs/backend/DESIGN.md#configuration."""
    # `dict.fromkeys`: a variable shared by several modules (`OPENAI_API_KEY`) is listed once.
    errors = list(
        dict.fromkeys(
            [
                *database_config_errors(),
                *tracing_config_errors(),
                *config_errors(),
                *phones_config_errors(),
                *rag_config_errors(),
            ]
        )
    )
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
    # Before the first LLM client: LangChain reads the LangSmith settings from the environment only.
    configure_tracing()
    app = FastAPI(title="Second-Hand Mobile E-market API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(users.router)
    api.include_router(phones.router)
    api.include_router(my_listings.router)
    api.include_router(search.router)
    app.include_router(api)
    return app
