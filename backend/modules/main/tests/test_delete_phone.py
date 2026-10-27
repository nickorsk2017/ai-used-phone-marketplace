"""`DELETE /api/phones/{id}`: docs/features/MY_LISTING.md#delete-phone-flow, docs/backend/AUTH.md#access."""

import uuid

import httpx
from fastapi import FastAPI

from conftest import AiStubs, StubChatModel, StubEmbeddings
from modules.main.tests.test_phones import ALLOWED, LISTING, count_rows, sign_in, use_stubs


async def publish(client: httpx.AsyncClient, ai_stubs: AiStubs) -> str:
    use_stubs(ai_stubs, StubChatModel(ALLOWED), StubEmbeddings())
    await sign_in(client)
    response = await client.post("/api/phones", json=LISTING)
    assert response.status_code == 201
    return response.json()["id"]


async def test_owner_deletes_the_listing_and_its_index_record(
    app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs
) -> None:
    phone_id = await publish(client, ai_stubs)
    response = await client.delete(f"/api/phones/{phone_id}")
    assert response.status_code == 204
    assert (await count_rows("phones"), await count_rows("search_index")) == (0, 0)
    assert (await client.get(f"/api/phones/{phone_id}")).status_code == 404
    assert (await client.get("/api/my-listings")).json() == {"listings": []}


async def test_foreign_listing_is_forbidden(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    phone_id = await publish(client, ai_stubs)
    client.cookies.clear()
    await sign_in(client)
    assert (await client.delete(f"/api/phones/{phone_id}")).status_code == 403
    assert (await count_rows("phones"), await count_rows("search_index")) == (1, 1)


async def test_delete_requires_a_session(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    phone_id = await publish(client, ai_stubs)
    client.cookies.clear()
    assert (await client.delete(f"/api/phones/{phone_id}")).status_code == 401
    assert await count_rows("phones") == 1


async def test_unknown_and_malformed_ids_return_404(app: FastAPI, client: httpx.AsyncClient) -> None:
    await sign_in(client)
    assert (await client.delete(f"/api/phones/{uuid.uuid4()}")).status_code == 404
    assert (await client.delete("/api/phones/not-an-id")).status_code == 404
