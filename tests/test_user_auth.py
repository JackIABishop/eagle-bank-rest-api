from __future__ import annotations

import pytest

pytestmark = pytest.mark.anyio

# Default test data 
def create_user_payload(email: str = "user@example.com") -> dict:
    return {
        "name": "Test User",
        "address": {
            "line1": "1 High Street",
            "town": "Knutsford",
            "county": "Cheshire",
            "postcode": "WA16 6AA",
        },
        "phoneNumber": "+447700900123",
        "email": email,
        "password": "correct-horse-battery",
    }


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
