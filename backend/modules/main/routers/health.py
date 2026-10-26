"""`/api/health`: database connection check, docs/backend/API.md."""

from fastapi import APIRouter, HTTPException, status

from core.database import is_database_available

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health() -> dict[str, str]:
    if not await is_database_available():
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Database is unavailable")
    return {"status": "ok"}
