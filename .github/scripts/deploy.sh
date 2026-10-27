#!/usr/bin/env bash
# Runs on the server over SSH from .github/workflows/deploy.yml: docs/INFRA.md#build-and-deployment.
set -euo pipefail

cd "$DEPLOY_PATH"
test -f backend/.env || { echo "Missing $DEPLOY_PATH/backend/.env"; exit 1; }

export IMAGE_PREFIX IMAGE_TAG
compose() {
  docker compose --env-file backend/.env -f docker-compose.yml -f docker-compose.prod.yml "$@"
}

echo "$GHCR_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin
compose pull backend frontend
docker logout ghcr.io

compose run --rm --no-deps backend python -c "from modules.main.app import check_config; check_config()"
compose up -d --wait db
compose run --rm backend alembic upgrade head
compose up -d --wait --no-build --remove-orphans
docker image prune -f
