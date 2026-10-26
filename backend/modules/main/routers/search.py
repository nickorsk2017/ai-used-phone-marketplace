"""`POST /api/search`: docs/backend/API.md#search."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError

from modules.main.ai import AI_ERRORS
from modules.main.dependencies import DbSession
from modules.main.rate_limit import search_rate_limit
from modules.phones import services as phones_service
from modules.rag import services as rag_service
from modules.rag.schemas import PromptBlocked, SearchRequest
from schemas import SearchResponse

logger = logging.getLogger(__name__)

PROMPT_REJECTED = "The prompt was not accepted"
SEARCH_UNAVAILABLE = "The search is unavailable"

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", dependencies=[Depends(search_rate_limit)])
async def search(body: SearchRequest, session: DbSession) -> SearchResponse:
    """The ranked IDs from `modules/rag`, the listings from `modules/phones` in the same order, or the clarification."""
    try:
        result = await rag_service.search(session, body.prompt)
    except PromptBlocked as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, PROMPT_REJECTED) from error
    except (*AI_ERRORS, DBAPIError) as error:
        logger.exception("Search failed")
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, SEARCH_UNAVAILABLE) from error
    if result.clarification is not None:
        return SearchResponse(results=[], clarification=result.clarification)
    return SearchResponse(results=await phones_service.get_phones(session, result.phone_ids))
