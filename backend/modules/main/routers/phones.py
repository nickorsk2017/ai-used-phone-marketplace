"""`/api/phones` endpoints: docs/backend/API.md, add phone flow: docs/features/MY_LISTING.md#add-phone-flow."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import run_in_transaction
from modules.main.ai import AI_ERRORS
from modules.main.dependencies import CurrentUserShortSession
from modules.main.rate_limit import phones_create_rate_limit, phones_description_rate_limit
from modules.phones import services as phones_service
from modules.phones.schemas import PhoneCreate, PhoneDescription, PhoneDescriptionRequest, PhoneRead
from modules.rag import services as rag_service
from modules.rag.schemas import IndexedPhone

logger = logging.getLogger(__name__)

MODEL_NOT_FOUND = "Model not found"
DESCRIPTION_UNAVAILABLE = "The description could not be generated"
LISTING_REJECTED = "The listing was not accepted"
LISTING_NOT_SAVED = "The listing was not saved"

router = APIRouter(prefix="/phones", tags=["phones"])


def _unavailable(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail)


@router.post("/description", dependencies=[Depends(phones_description_rate_limit)])
async def generate_description(body: PhoneDescriptionRequest, user: CurrentUserShortSession) -> PhoneDescription:
    try:
        description = await phones_service.generate_description(body.model_name)
    except AI_ERRORS as error:
        logger.exception("Description generation failed")
        raise _unavailable(DESCRIPTION_UNAVAILABLE) from error
    if description is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, MODEL_NOT_FOUND)
    return description


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(phones_create_rate_limit)])
async def create_phone(body: PhoneCreate, user: CurrentUserShortSession) -> PhoneRead:
    """Guardrail 1, embedding, then the listing and its index in one transaction with one retry.

    The slow calls run once, before the transaction: docs/backend/DESIGN.md#transaction-retry.
    """
    try:
        allowed = await phones_service.check_listing(body)
    except AI_ERRORS as error:
        logger.exception("Guardrail 1 failed, the listing is not saved")
        raise _unavailable(LISTING_NOT_SAVED) from error
    if not allowed:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, LISTING_REJECTED)

    try:
        embedding = await rag_service.embed_listing(body.model_name, body.description, body.condition_note)
    except AI_ERRORS as error:
        logger.exception("Listing embedding failed")
        raise _unavailable(LISTING_NOT_SAVED) from error

    async def save(session: AsyncSession) -> PhoneRead:
        phone = await phones_service.create_phone(session, user.id, body)
        indexed = IndexedPhone.model_validate({**phone.model_dump(), "phone_id": phone.id})
        await rag_service.index(session, indexed, embedding)
        return phone

    try:
        return await run_in_transaction(save)
    except DBAPIError as error:
        logger.exception("Listing transaction failed")
        raise _unavailable(LISTING_NOT_SAVED) from error
