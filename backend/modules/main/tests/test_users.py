import uuid

import httpx

VALID_USER = {"whatsapp": "+1 415 555 2671", "first_name": "Ann", "last_name": "Lee"}


async def create_user(client: httpx.AsyncClient) -> dict:
    response = await client.post("/api/users", json=VALID_USER)
    assert response.status_code == 201
    return response.json()


async def test_create_user_returns_generated_id(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    assert uuid.UUID(user["id"]).version == 4
    assert user["whatsapp"] == "+14155552671"
    assert set(user) == {"id", "whatsapp", "first_name", "last_name", "created_at"}


async def test_create_user_rejects_client_id(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json={**VALID_USER, "id": str(uuid.uuid4())})
    assert response.status_code == 422


async def test_create_user_rejects_invalid_body(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/users", json={"whatsapp": "123", "first_name": "", "last_name": "Lee"})
    assert response.status_code == 422


async def test_owner_gets_own_user(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.get(f"/api/users/{user['id']}", headers={"X-User-Id": user["id"]})
    assert response.status_code == 200
    assert response.json() == user


async def test_get_user_requires_header(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.get(f"/api/users/{user['id']}")
    assert response.status_code == 401


async def test_get_foreign_user_is_forbidden(client: httpx.AsyncClient) -> None:
    owner = await create_user(client)
    other = await create_user(client)
    response = await client.get(f"/api/users/{owner['id']}", headers={"X-User-Id": other["id"]})
    assert response.status_code == 403


async def test_get_unknown_user_returns_404(client: httpx.AsyncClient) -> None:
    unknown_id = str(uuid.uuid4())
    response = await client.get(f"/api/users/{unknown_id}", headers={"X-User-Id": unknown_id})
    assert response.status_code == 404


async def test_get_malformed_user_id_returns_404(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/users/u-1", headers={"X-User-Id": "u-1"})
    assert response.status_code == 404


async def test_owner_check_compares_uuids(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.get(f"/api/users/{user['id']}", headers={"X-User-Id": user["id"].upper()})
    assert response.status_code == 200


async def test_malformed_header_is_forbidden(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.get(f"/api/users/{user['id']}", headers={"X-User-Id": "u-1"})
    assert response.status_code == 403


UPDATED_USER = {"whatsapp": "+44 20 7946 0958", "first_name": "Bob", "last_name": "Stone"}


async def test_owner_updates_own_user(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.put(f"/api/users/{user['id']}", json=UPDATED_USER, headers={"X-User-Id": user["id"]})
    assert response.status_code == 200
    updated = response.json()
    assert updated == {**user, "whatsapp": "+442079460958", "first_name": "Bob", "last_name": "Stone"}
    loaded = await client.get(f"/api/users/{user['id']}", headers={"X-User-Id": user["id"]})
    assert loaded.json() == updated


async def test_update_requires_header(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.put(f"/api/users/{user['id']}", json=UPDATED_USER)
    assert response.status_code == 401


async def test_update_foreign_user_is_forbidden(client: httpx.AsyncClient) -> None:
    owner = await create_user(client)
    other = await create_user(client)
    response = await client.put(f"/api/users/{owner['id']}", json=UPDATED_USER, headers={"X-User-Id": other["id"]})
    assert response.status_code == 403


async def test_update_unknown_user_returns_404(client: httpx.AsyncClient) -> None:
    unknown_id = str(uuid.uuid4())
    response = await client.put(f"/api/users/{unknown_id}", json=UPDATED_USER, headers={"X-User-Id": unknown_id})
    assert response.status_code == 404


async def test_update_rejects_invalid_body(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    response = await client.put(
        f"/api/users/{user['id']}", json={**UPDATED_USER, "first_name": " "}, headers={"X-User-Id": user["id"]}
    )
    assert response.status_code == 422


async def test_update_rejects_id_and_created_at(client: httpx.AsyncClient) -> None:
    user = await create_user(client)
    for field, value in (("id", str(uuid.uuid4())), ("created_at", "2020-01-01T00:00:00Z")):
        response = await client.put(
            f"/api/users/{user['id']}", json={**UPDATED_USER, field: value}, headers={"X-User-Id": user["id"]}
        )
        assert response.status_code == 422


async def test_cors_allows_frontend_origin(client: httpx.AsyncClient) -> None:
    response = await client.options(
        "/api/users/any",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "x-user-id",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
