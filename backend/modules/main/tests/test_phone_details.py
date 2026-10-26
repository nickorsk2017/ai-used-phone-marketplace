"""`GET /api/phones/{id}` and `GET /api/phones/{id}/contact`: docs/features/PHONE_DETAILS.md."""

import uuid

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_engine, run_in_transaction
from modules.main.tests.test_phones import LISTING
from modules.phones import services as phones_service
from modules.phones.schemas import PhoneCreate
from modules.users import services as users_service
from modules.users.schemas import UserCreate

OWNER = UserCreate(whatsapp="+14155552671", first_name="Ann", last_name="Lee")


async def create_listing() -> str:
    async def save(session: AsyncSession) -> str:
        owner = await users_service.create_user(session, OWNER)
        phone = await phones_service.create_phone(session, owner.id, PhoneCreate(**LISTING))
        return str(phone.id)

    return await run_in_transaction(save)


async def test_details_are_public_without_owner(client: httpx.AsyncClient) -> None:
    phone_id = await create_listing()
    response = await client.get(f"/api/phones/{phone_id}")
    assert response.status_code == 200
    phone = response.json()
    assert {key: phone[key] for key in LISTING} == LISTING
    assert phone["id"] == phone_id
    assert "user_id" not in phone


async def test_contact_returns_owner_contact_only(client: httpx.AsyncClient) -> None:
    phone_id = await create_listing()
    response = await client.get(f"/api/phones/{phone_id}/contact")
    assert response.status_code == 200
    assert response.json() == {"whatsapp": "+14155552671", "first_name": "Ann", "last_name": "Lee"}


@pytest.mark.parametrize("suffix", ["", "/contact"])
@pytest.mark.parametrize("phone_id", ["not-a-uuid", str(uuid.uuid4())])
async def test_unknown_listing_is_404(client: httpx.AsyncClient, phone_id: str, suffix: str) -> None:
    response = await client.get(f"/api/phones/{phone_id}{suffix}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Phone not found"}


@pytest.mark.parametrize("suffix", ["", "/contact"])
async def test_deleted_listing_is_404(client: httpx.AsyncClient, suffix: str) -> None:
    phone_id = await create_listing()
    async with get_engine().begin() as connection:
        await connection.execute(text("DELETE FROM phones"))
    assert (await client.get(f"/api/phones/{phone_id}{suffix}")).status_code == 404


async def test_contact_of_missing_owner_is_404(client: httpx.AsyncClient) -> None:
    phone_id = await create_listing()
    async with get_engine().begin() as connection:
        await connection.execute(text("DELETE FROM users"))
    assert (await client.get(f"/api/phones/{phone_id}/contact")).status_code == 404
