from __future__ import annotations

import pytest

from tests.helpers import create_account_via_api, create_user_payload, login_and_get_headers

pytestmark = pytest.mark.anyio


async def test_create_account_returns_201_and_account_shape(client) -> None:
    await client.post("/v1/users", json=create_user_payload("account-owner@example.com"))
    headers = await login_and_get_headers(client, "account-owner@example.com")

    response = await client.post(
        "/v1/accounts",
        json={"name": "Daily Account", "accountType": "personal"},
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["accountNumber"].startswith("01")
    assert body["sortCode"] == "10-10-10" # Default sortCode for API 
    assert body["accountType"] == "personal" # Default accountType for API
    assert body["balance"] == 0.0
    assert body["currency"] == "GBP"


async def test_list_accounts_returns_only_the_authenticated_users_accounts(client) -> None:
    await client.post("/v1/users", json=create_user_payload("first-account@example.com"))
    await client.post("/v1/users", json=create_user_payload("second-account@example.com"))

    first_headers = await login_and_get_headers(client, "first-account@example.com")
    second_headers = await login_and_get_headers(client, "second-account@example.com")

    await create_account_via_api(client, first_headers, name="First Account")
    await create_account_via_api(client, first_headers, name="Second Account")
    await create_account_via_api(client, second_headers, name="Other Customer Account")

    response = await client.get("/v1/accounts", headers=first_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["accounts"]) == 2
    assert {account["name"] for account in body["accounts"]} == {"First Account", "Second Account"}


async def test_fetch_account_returns_own_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("fetch-account@example.com"))
    headers = await login_and_get_headers(client, "fetch-account@example.com")
    created_account = await create_account_via_api(client, headers)

    response = await client.get(
        f"/v1/accounts/{created_account['accountNumber']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["accountNumber"] == created_account["accountNumber"]


async def test_fetch_account_returns_403_for_another_users_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("owner-one@example.com"))
    await client.post("/v1/users", json=create_user_payload("owner-two@example.com"))
    first_headers = await login_and_get_headers(client, "owner-one@example.com")
    second_headers = await login_and_get_headers(client, "owner-two@example.com")
    created_account = await create_account_via_api(client, first_headers)

    response = await client.get(
        f"/v1/accounts/{created_account['accountNumber']}",
        headers=second_headers,
    )

    assert response.status_code == 403
    assert response.json() == {"message": "The user is not allowed to access the bank account details"}


async def test_update_account_returns_updated_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("update-account@example.com"))
    headers = await login_and_get_headers(client, "update-account@example.com")
    created_account = await create_account_via_api(client, headers)

    response = await client.patch(
        f"/v1/accounts/{created_account['accountNumber']}",
        json={"name": "Renamed Account"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed Account"


async def test_delete_account_returns_204_and_removes_the_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("delete-account@example.com"))
    headers = await login_and_get_headers(client, "delete-account@example.com")
    created_account = await create_account_via_api(client, headers)

    delete_response = await client.delete(
        f"/v1/accounts/{created_account['accountNumber']}",
        headers=headers,
    )
    fetch_response = await client.get(
        f"/v1/accounts/{created_account['accountNumber']}",
        headers=headers,
    )

    assert delete_response.status_code == 204
    assert fetch_response.status_code == 404


async def test_list_accounts_returns_401_without_token(client) -> None:
    response = await client.get("/v1/accounts")

    assert response.status_code == 401
    assert response.json() == {"message": "Access token is missing or invalid"}


async def test_update_account_returns_404_for_missing_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-account@example.com"))
    headers = await login_and_get_headers(client, "missing-account@example.com")

    response = await client.patch(
        "/v1/accounts/01000000",
        json={"name": "No Account Here"},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Bank account was not found"}
