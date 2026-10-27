"""`/api/phones` endpoints: docs/backend/API.md.

Add phone flow: docs/features/MY_LISTING.md#add-phone-flow. Details and contact: docs/features/PHONE_DETAILS.md.
"""

import logging
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import run_in_transaction
from modules.main.ai import AI_ERRORS
from modules.main.dependencies import CurrentUserShortSession, DbSession, owner_access
from modules.main.rate_limit import (
    phones_contact_rate_limit,
    phones_create_rate_limit,
    phones_description_rate_limit,
)
from modules.phones import services as phones_service
from modules.phones.schemas import PhoneCreate, PhoneDescription, PhoneDescriptionRequest, PhoneRead
from modules.rag import services as rag_service
from modules.rag.schemas import IndexedPhone
from modules.users import services as users_service
from modules.users.schemas import UserContact

logger = logging.getLogger(__name__)

MODEL_NOT_FOUND = "Model not found"
DESCRIPTION_UNAVAILABLE = "The description could not be generated"
LISTING_REJECTED = "The listing was not accepted"
LISTING_NOT_SAVED = "The listing was not saved"
PHONE_NOT_FOUND = "Phone not found"

router = APIRouter(prefix="/phones", tags=["phones"])

# `Owner` access to the listing of `{phone_id}`: the owner ID, docs/backend/AUTH.md#access.
PhoneOwner = Annotated[
    uuid.UUID,
    Depends(
        owner_access(
            phones_service.get_phone_owner_id,
            lambda owner_id: owner_id,
            path_param="phone_id",
            not_found=PHONE_NOT_FOUND,
        )
    ),
]


def _unavailable(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail)


def _phone_id(value: str) -> uuid.UUID:
    """Malformed ids are unknown listings: 404, docs/backend/AUTH.md#access."""
    try:
        return uuid.UUID(value)
    except ValueError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PHONE_NOT_FOUND) from error


@router.get("/{phone_id}")
async def get_phone(phone_id: str, session: DbSession) -> PhoneRead:
    """Public listing details: `PhoneRead` has no `user_id`."""
    phone = await phones_service.get_phone(session, _phone_id(phone_id))
    if phone is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PHONE_NOT_FOUND)
    return phone


@router.get("/{phone_id}/contact", dependencies=[Depends(phones_contact_rate_limit)])
async def get_phone_contact(phone_id: str, session: DbSession) -> UserContact:
    """Contact of the listing owner by the listing ID: the owner ID stays on the Backend."""
    owner_id = await phones_service.get_phone_owner_id(session, _phone_id(phone_id))
    owner = await users_service.get_user(session, owner_id) if owner_id else None
    if owner is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, PHONE_NOT_FOUND)
    return UserContact.model_validate(owner)


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


@router.delete("/{phone_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phone(phone_id: str, owner: PhoneOwner, session: DbSession) -> None:
    """The listing and its search index record in one transaction: docs/features/MY_LISTING.md#delete-phone-flow.

    `PhoneOwner` has checked the session, the ID and the owner in the same transaction.
    """
    deleted_id = _phone_id(phone_id)
    await phones_service.delete_phone(session, deleted_id)
    await rag_service.delete(session, deleted_id)
