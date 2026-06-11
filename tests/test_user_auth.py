from __future__ import annotations

import pytest

from tests.helpers import create_account_via_api, create_user_payload, login_and_get_headers

pytestmark = pytest.mark.anyio


async def test_create_user_returns_201_and_user_shape(client) -> None:
    response = await client.post("/v1/users", json=create_user_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("usr-")
    assert body["email"] == "user@example.com"
    assert body["address"]["town"] == "Knutsford"
    assert "password" not in body


async def test_login_returns_token_for_valid_credentials(client) -> None:
    await client.post("/v1/users", json=create_user_payload())

    response = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery"}, # Correct credentials
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tokenType"] == "Bearer"
    assert isinstance(body["accessToken"], str)
    assert body["expiresIn"] == 3600


async def test_login_returns_401_for_invalid_credentials(client) -> None:
    await client.post("/v1/users", json=create_user_payload())

    response = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "wrong-password"}, # Incorrect credentials
    )

    assert response.status_code == 401
    assert response.json() == {"message": "Email or password is incorrect"}


async def test_fetch_own_user_requires_bearer_auth_and_returns_user(client) -> None:
    create_response = await client.post("/v1/users", json=create_user_payload())
    user_id = create_response.json()["id"]
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery"},
    )
    token = login_response.json()["accessToken"]

    response = await client.get(
        f"/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user_id


async def test_fetch_user_returns_401_without_token(client) -> None:
    create_response = await client.post("/v1/users", json=create_user_payload())
    user_id = create_response.json()["id"]

    response = await client.get(f"/v1/users/{user_id}")

    assert response.status_code == 401
    assert response.json() == {"message": "Access token is missing or invalid"}


async def test_fetch_other_user_returns_403(client) -> None:
    first_create = await client.post("/v1/users", json=create_user_payload("first@example.com"))
    second_create = await client.post("/v1/users", json=create_user_payload("second@example.com"))
    first_user_id = first_create.json()["id"]
    second_user_id = second_create.json()["id"]

    # Login with the first user to get a token
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "first@example.com", "password": "correct-horse-battery"},
    )
    token = login_response.json()["accessToken"]

    # Try to fetch data of the second user
    response = await client.get(
        f"/v1/users/{second_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json() == {"message": "The user is not allowed to access the user details"}


async def test_fetch_user_returns_404_for_missing_user(client) -> None:
    await client.post("/v1/users", json=create_user_payload())
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery"},
    )
    token = login_response.json()["accessToken"]

    response = await client.get(
        "/v1/users/usr-missing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {"message": "User was not found"}


async def test_fetch_user_returns_400_for_invalid_user_id_format(client) -> None:
    await client.post("/v1/users", json=create_user_payload())
    login_response = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery"},
    )
    token = login_response.json()["accessToken"]

    response = await client.get(
        "/v1/users/not-a-user-id",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid details supplied"


async def test_update_own_user_updates_profile_and_login_credentials(client) -> None:
    create_response = await client.post("/v1/users", json=create_user_payload())
    user_id = create_response.json()["id"]
    headers = await login_and_get_headers(client, "user@example.com")

    response = await client.patch(
        f"/v1/users/{user_id}",
        json={
            "name": "Updated User",
            "email": "updated@example.com",
            "password": "new-secure-password",
            "phoneNumber": "+447700900999",
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated User"
    assert response.json()["email"] == "updated@example.com"

    old_login = await client.post(
        "/v1/auth/login",
        json={"email": "user@example.com", "password": "correct-horse-battery"},
    )
    new_login = await client.post(
        "/v1/auth/login",
        json={"email": "updated@example.com", "password": "new-secure-password"},
    )
    assert old_login.status_code == 401
    assert new_login.status_code == 200


async def test_update_user_rejects_an_email_owned_by_another_user(client) -> None:
    first = await client.post("/v1/users", json=create_user_payload("first@example.com"))
    await client.post("/v1/users", json=create_user_payload("second@example.com"))
    headers = await login_and_get_headers(client, "first@example.com")

    response = await client.patch(
        f"/v1/users/{first.json()['id']}",
        json={"email": "second@example.com"},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json() == {"message": "A user with that email already exists"}


async def test_update_user_returns_403_for_another_user(client) -> None:
    first = await client.post("/v1/users", json=create_user_payload("first@example.com"))
    second = await client.post("/v1/users", json=create_user_payload("second@example.com"))
    headers = await login_and_get_headers(client, "first@example.com")

    response = await client.patch(
        f"/v1/users/{second.json()['id']}",
        json={"name": "Not Allowed"},
        headers=headers,
    )

    assert first.json()["id"] != second.json()["id"]
    assert response.status_code == 403


async def test_delete_own_user_returns_204_and_invalidates_existing_token(client) -> None:
    created = await client.post("/v1/users", json=create_user_payload())
    user_id = created.json()["id"]
    headers = await login_and_get_headers(client, "user@example.com")

    response = await client.delete(f"/v1/users/{user_id}", headers=headers)
    fetch_response = await client.get(f"/v1/users/{user_id}", headers=headers)

    assert response.status_code == 204
    assert fetch_response.status_code == 401


async def test_delete_user_returns_409_while_bank_accounts_exist(client) -> None:
    created = await client.post("/v1/users", json=create_user_payload())
    user_id = created.json()["id"]
    headers = await login_and_get_headers(client, "user@example.com")
    await create_account_via_api(client, headers)

    response = await client.delete(f"/v1/users/{user_id}", headers=headers)

    assert response.status_code == 409
    assert response.json() == {"message": "User cannot be deleted while bank accounts exist"}
