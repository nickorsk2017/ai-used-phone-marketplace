# Multi-stage build with uv: docs/INFRA.md#docker-compose.
FROM ghcr.io/astral-sh/uv:0.13.4 AS uv

FROM python:3.13-slim AS build
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY modules/users/pyproject.toml modules/users/
COPY modules/auth/pyproject.toml modules/auth/
COPY modules/phones/pyproject.toml modules/phones/
COPY modules/rag/pyproject.toml modules/rag/
COPY modules/main/pyproject.toml modules/main/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-packages --no-dev --no-install-workspace

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-packages --no-dev

FROM python:3.13-slim AS runtime
RUN useradd --system --create-home app
WORKDIR /app
COPY --from=build --chown=app:app /app /app
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
USER app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
