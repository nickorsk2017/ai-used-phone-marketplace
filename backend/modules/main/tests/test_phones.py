"""`/api/phones` and `/api/my-listings`: docs/backend/API.md, docs/features/MY_LISTING.md#add-phone-flow."""

import httpx
import openai
import pytest
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from conftest import AiStubs, StubChatModel, StubEmbeddings
from core.database import get_engine
from modules.main.rate_limit import phones_create_rate_limit
from modules.phones.schemas import GeneratedDescription, GuardrailVerdict
from modules.rag import services as rag_service

USER = {"whatsapp": "+1 415 555 2671", "first_name": "Ann", "last_name": "Lee"}
LISTING = {
    "model_code": "A2483",
    "model_name": "iPhone 13 Pro",
    "os": "ios",
    "camera_megapixels": 12,
    "battery_capacity": 3095,
    "display_size": 6.1,
    "description": "iPhone 13 Pro with a 6.1-inch ProMotion display.",
    "condition": "average",
    "condition_note": "Small scratches on the frame",
    "price": 450,
}
ALLOWED = GuardrailVerdict(allowed=True)


def provider_error() -> openai.APITimeoutError:
    return openai.APITimeoutError(request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"))


async def sign_in(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/users", json=USER)
    assert response.status_code == 201
    return response.json()


def use_stubs(ai_stubs: AiStubs, guardrail: StubChatModel, embeddings: StubEmbeddings) -> None:
    ai_stubs.guardrail = guardrail
    ai_stubs.embeddings = embeddings


def without_create_limit(app: FastAPI) -> None:
    """Tests that publish several listings: the limit itself is tested in `test_rate_limit.py`."""
    app.dependency_overrides[phones_create_rate_limit] = lambda: None


async def count_rows(table: str) -> int:
    async with get_engine().connect() as connection:
        return await connection.scalar(text(f"SELECT count(*) FROM {table}"))


async def test_description_found(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    generated = GeneratedDescription(model_found=True, **{key: LISTING[key] for key in list(LISTING)[:7]})
    ai_stubs.description = StubChatModel(generated)
    await sign_in(client)
    response = await client.post("/api/phones/description", json={"model_name": "iphone 13 pro"})
    assert response.status_code == 200
    assert response.json() == {key: LISTING[key] for key in list(LISTING)[:7]}


async def test_description_not_found(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    ai_stubs.description = StubChatModel(GeneratedDescription(model_found=False))
    await sign_in(client)
    response = await client.post("/api/phones/description", json={"model_name": "iPhone 25"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Model not found"}


async def test_description_provider_error(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    ai_stubs.description = StubChatModel(provider_error())
    await sign_in(client)
    response = await client.post("/api/phones/description", json={"model_name": "iPhone 13 Pro"})
    assert response.status_code == 503


@pytest.mark.parametrize(("method", "path"), [("POST", "/api/phones"), ("POST", "/api/phones/description")])
async def test_session_is_required(client: httpx.AsyncClient, method: str, path: str) -> None:
    response = await client.request(method, path, json=LISTING)
    assert response.status_code == 401


async def test_create_saves_the_listing_and_the_index(
    app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs
) -> None:
    embeddings = StubEmbeddings()
    use_stubs(ai_stubs, StubChatModel(ALLOWED), embeddings)
    await sign_in(client)
    response = await client.post("/api/phones", json=LISTING)
    assert response.status_code == 201
    phone = response.json()
    assert {key: phone[key] for key in LISTING} == LISTING
    assert "user_id" not in phone
    async with get_engine().connect() as connection:
        row = (await connection.execute(text("SELECT * FROM search_index"))).mappings().one()
    assert str(row["phone_id"]) == phone["id"]
    assert (row["model_code"], row["condition"], row["price"]) == ("A2483", "average", 450)
    assert embeddings.texts == [
        "iPhone 13 Pro\niPhone 13 Pro with a 6.1-inch ProMotion display.\nSmall scratches on the frame"
    ]


@pytest.mark.parametrize(
    ("guardrail", "body"),
    [
        (StubChatModel(ALLOWED), {**LISTING, "condition_note": "Pay with 4111 1111 1111 1111"}),
        (StubChatModel(ALLOWED), {**LISTING, "description": "Details on phonedeals.shop"}),
        (StubChatModel(GuardrailVerdict(allowed=False, category="prompt_injection")), LISTING),
    ],
)
async def test_blocked_listing_is_not_saved(
    app: FastAPI, client: httpx.AsyncClient, guardrail: StubChatModel, body: dict, ai_stubs: AiStubs
) -> None:
    embeddings = StubEmbeddings()
    use_stubs(ai_stubs, guardrail, embeddings)
    await sign_in(client)
    response = await client.post("/api/phones", json=body)
    assert response.status_code == 422
    assert response.json() == {"detail": "The listing was not accepted"}
    assert embeddings.calls == 0
    assert await count_rows("phones") == 0


async def test_guardrail_error_fails_closed(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    use_stubs(ai_stubs, StubChatModel(provider_error()), StubEmbeddings())
    await sign_in(client)
    assert (await client.post("/api/phones", json=LISTING)).status_code == 503
    assert await count_rows("phones") == 0


async def test_embedding_error_saves_nothing(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    use_stubs(ai_stubs, StubChatModel(ALLOWED), StubEmbeddings(error=provider_error()))
    await sign_in(client)
    assert (await client.post("/api/phones", json=LISTING)).status_code == 503
    assert await count_rows("phones") == 0
    assert await count_rows("search_index") == 0


def fail_index(monkeypatch: pytest.MonkeyPatch, failures: int, sqlstate: str = "40001") -> list[int]:
    """The search index insert fails `failures` times, after the listing insert of the same transaction."""
    index = rag_service.index
    calls: list[int] = []

    async def flaky_index(session: AsyncSession, phone, embedding) -> None:
        calls.append(1)
        if len(calls) <= failures:
            await session.execute(
                text(f"DO $$ BEGIN RAISE EXCEPTION 'index failed' USING ERRCODE = '{sqlstate}'; END $$")
            )
        await index(session, phone, embedding)

    monkeypatch.setattr(rag_service, "index", flaky_index)
    return calls


async def test_transient_error_is_retried_without_a_new_embedding(
    app: FastAPI, client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch, ai_stubs: AiStubs
) -> None:
    guardrail, embeddings = StubChatModel(ALLOWED), StubEmbeddings()
    use_stubs(ai_stubs, guardrail, embeddings)
    calls = fail_index(monkeypatch, failures=1)
    await sign_in(client)
    response = await client.post("/api/phones", json=LISTING)
    assert response.status_code == 201
    assert len(calls) == 2
    assert (guardrail.calls, embeddings.calls) == (1, 1)
    assert (await count_rows("phones"), await count_rows("search_index")) == (1, 1)


@pytest.mark.parametrize(("failures", "sqlstate", "attempts"), [(2, "40001", 2), (1, "22000", 1)])
async def test_failed_transaction_saves_nothing(
    app: FastAPI,
    client: httpx.AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    failures: int,
    sqlstate: str,
    attempts: int,
    ai_stubs: AiStubs,
) -> None:
    use_stubs(ai_stubs, StubChatModel(ALLOWED), StubEmbeddings())
    calls = fail_index(monkeypatch, failures=failures, sqlstate=sqlstate)
    await sign_in(client)
    response = await client.post("/api/phones", json=LISTING)
    assert response.status_code == 503
    assert response.json() == {"detail": "The listing was not saved"}
    assert len(calls) == attempts
    assert (await count_rows("phones"), await count_rows("search_index")) == (0, 0)


async def test_my_listings_returns_own_listings_newest_first(
    app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs
) -> None:
    use_stubs(ai_stubs, StubChatModel(ALLOWED, ALLOWED, ALLOWED), StubEmbeddings())
    without_create_limit(app)
    await sign_in(client)
    first = (await client.post("/api/phones", json=LISTING)).json()
    second = (await client.post("/api/phones", json={**LISTING, "price": 400})).json()

    client.cookies.clear()
    await sign_in(client)
    await client.post("/api/phones", json={**LISTING, "price": 300})
    other_ids = [phone["id"] for phone in (await client.get("/api/my-listings")).json()["listings"]]
    assert first["id"] not in other_ids and second["id"] not in other_ids
    assert len(other_ids) == 1


async def test_my_listings_order(app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs) -> None:
    use_stubs(ai_stubs, StubChatModel(ALLOWED, ALLOWED), StubEmbeddings())
    without_create_limit(app)
    await sign_in(client)
    first = (await client.post("/api/phones", json=LISTING)).json()
    second = (await client.post("/api/phones", json={**LISTING, "price": 400})).json()
    response = await client.get("/api/my-listings")
    assert response.status_code == 200
    assert [phone["id"] for phone in response.json()["listings"]] == [second["id"], first["id"]]


async def test_my_listings_requires_a_session(client: httpx.AsyncClient) -> None:
    assert (await client.get("/api/my-listings")).status_code == 401


class PoolCheckingChatModel(StubChatModel):
    """Records the connections checked out of the pool while the LLM call waits."""

    def __init__(self, *answers) -> None:
        super().__init__(*answers)
        self.checked_out: list[int] = []

    async def ainvoke(self, messages: list):
        self.checked_out.append(get_engine().pool.checkedout())
        return await super().ainvoke(messages)


async def test_no_connection_is_held_during_the_llm_calls(
    app: FastAPI, client: httpx.AsyncClient, ai_stubs: AiStubs
) -> None:
    description = PoolCheckingChatModel(GeneratedDescription(model_found=False))
    guardrail = PoolCheckingChatModel(ALLOWED)
    ai_stubs.description = description
    use_stubs(ai_stubs, guardrail, StubEmbeddings())
    await sign_in(client)
    await client.post("/api/phones/description", json={"model_name": "iPhone 25"})
    assert (await client.post("/api/phones", json=LISTING)).status_code == 201
    assert description.checked_out == [0]
    assert guardrail.checked_out == [0]


@pytest.mark.parametrize("model_code", ["www.deals.shop", "A 2483", ""])
async def test_invalid_model_code_is_rejected(
    app: FastAPI, client: httpx.AsyncClient, model_code: str, ai_stubs: AiStubs
) -> None:
    guardrail = StubChatModel(ALLOWED)
    use_stubs(ai_stubs, guardrail, StubEmbeddings())
    await sign_in(client)
    assert (await client.post("/api/phones", json={**LISTING, "model_code": model_code})).status_code == 422
    assert guardrail.calls == 0
    assert await count_rows("phones") == 0
