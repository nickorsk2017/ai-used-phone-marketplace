"""`/api/users` and the session cookie: docs/backend/API.md, docs/backend/AUTH.md#cookie."""

import uuid
from http.cookies import SimpleCookie

import httpx
import pytest
from sqlalchemy import text

from core.database import get_engine
from modules.auth import services as auth_service
from modules.main.config import get_settings
from modules.main.dependencies import SESSION_COOKIE, SESSION_COOKIE_MAX_AGE

VALID_USER = {"whatsapp": "+1 415 555 2671", "first_name": "Ann", "last_name": "Lee"}
UPDATED_USER = {"whatsapp": "+44 20 7946 0958", "first_name": "Bob", "last_name": "Stone"}


async def create_user(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/users", json=VALID_USER)
    assert response.status_code == 201
    return response.json()


def session_cookie(response: httpx.Response) -> SimpleCookie:
    cookie = SimpleCookie()
    cookie.load(response.headers["set-cookie"])
    return cookie


async def test_create_user_returns_generated_id(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    assert uuid.UUID(user["id"]).version == 4
    assert user["whatsapp"] == "+14155552671"
    assert set(user) == {"id", "whatsapp", "first_name", "last_name", "created_at"}


async def test_create_user_sets_the_session_cookie(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json=VALID_USER)
    morsel = session_cookie(response)[SESSION_COOKIE]
    assert auth_service.verify_token(morsel.value, get_settings().session_secret) == uuid.UUID(response.json()["id"])
    assert morsel["httponly"] is True
    assert morsel["samesite"] == "lax"
    assert morsel["path"] == "/api"
    assert morsel["max-age"] == str(SESSION_COOKIE_MAX_AGE) == str(400 * 24 * 60 * 60)
    assert not morsel["secure"]


@pytest.mark.parametrize("secure", [True, False])
async def test_secure_attribute_follows_the_setting(
    client: httpx.AsyncClient, monkeypatch: pytest.MonkeyPatch, secure: bool
) -> None:
    monkeypatch.setattr(get_settings(), "cookie_secure", secure)
    response = await client.post("/api/users", json=VALID_USER)
    assert bool(session_cookie(response)[SESSION_COOKIE]["secure"]) is secure


async def test_create_user_rejects_client_id(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json={**VALID_USER, "id": str(uuid.uuid4())})
    assert response.status_code == 422
    assert "set-cookie" not in response.headers


async def test_create_user_rejects_invalid_body(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json={"whatsapp": "123", "first_name": "", "last_name": "Lee"})
    assert response.status_code == 422


async def test_current_user_is_loaded_by_the_cookie(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json() == user


async def test_valid_session_sets_the_cookie_again(client: httpx.AsyncClient) -> None:
    await create_user(client)
    response = await client.get("/api/users/me")
    assert session_cookie(response)[SESSION_COOKIE]["max-age"] == str(SESSION_COOKIE_MAX_AGE)


def assert_session_removed(response: httpx.Response) -> None:
    assert response.status_code == 401
    morsel = session_cookie(response)[SESSION_COOKIE]
    assert morsel.value == ""
    assert morsel["max-age"] == "0"
    assert morsel["path"] == "/api"


async def test_missing_cookie_returns_401(client: httpx.AsyncClient) -> None:
    assert_session_removed(await client.get("/api/users/me"))


async def test_tampered_cookie_returns_401(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    client.cookies.set(SESSION_COOKIE, f"{user['id']}.forged", path="/api")
    assert_session_removed(await client.get("/api/users/me"))


async def test_cookie_of_another_secret_returns_401(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    client.cookies.set(SESSION_COOKIE, auth_service.issue_token(uuid.UUID(user["id"]), "o" * 32), path="/api")
    assert_session_removed(await client.get("/api/users/me"))


async def test_deleted_user_returns_401_and_removes_the_cookie(client: httpx.AsyncClient) -> None:
    await create_user(client)
    async with get_engine().begin() as connection:
        await connection.execute(text("DELETE FROM users"))
    assert_session_removed(await client.get("/api/users/me"))
    assert SESSION_COOKIE not in client.cookies


async def test_user_id_header_is_not_a_credential(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    client.cookies.clear()
    response = await client.get("/api/users/me", headers={"X-User-Id": user["id"]})
    assert response.status_code == 401


async def test_removed_id_routes_are_not_found(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    assert (await client.get(f"/api/users/{user['id']}")).status_code == 404
    assert (await client.put(f"/api/users/{user['id']}", json=UPDATED_USER)).status_code == 404


async def test_current_user_updates_own_profile(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.put("/api/users/me", json=UPDATED_USER)
    assert response.status_code == 200
    updated = response.json()
    assert updated == {**user, "whatsapp": "+442079460958", "first_name": "Bob", "last_name": "Stone"}
    assert (await client.get("/api/users/me")).json() == updated


async def test_update_requires_a_session(client: httpx.AsyncClient) -> None:
    assert_session_removed(await client.put("/api/users/me", json=UPDATED_USER))


async def test_update_changes_only_the_current_user(client: httpx.AsyncClient) -> None:
    first = await create_user(client)
    client.cookies.clear()
    await create_user(client)
    await client.put("/api/users/me", json=UPDATED_USER)
    first_token = auth_service.issue_token(uuid.UUID(first["id"]), get_settings().session_secret)
    client.cookies.set(SESSION_COOKIE, first_token, path="/api")
    assert (await client.get("/api/users/me")).json() == first


async def test_update_rejects_invalid_body(client: httpx.AsyncClient) -> None:
    await create_user(client)
    response = await client.put("/api/users/me", json={**UPDATED_USER, "first_name": " "})
    assert response.status_code == 422


async def test_update_rejects_id_and_created_at(client: httpx.AsyncClient) -> None:
    await create_user(client)
    for field, value in (("id", str(uuid.uuid4())), ("created_at", "2020-01-01T00:00:00Z")):
        response = await client.put("/api/users/me", json={**UPDATED_USER, field: value})
        assert response.status_code == 422


async def test_cors_allows_credentials_for_the_frontend_origin(client: httpx.AsyncClient) -> None:
    response = await client.options(
        "/api/users/me",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "PUT"},
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert response.headers["access-control-allow-credentials"] == "true"


async def test_cors_rejects_another_origin(client: httpx.AsyncClient) -> None:
    response = await client.options(
        "/api/users/me",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "PUT"},
    )
    assert "access-control-allow-origin" not in response.headers
