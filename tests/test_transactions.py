from __future__ import annotations

import pytest

from tests.helpers import (
    create_account_via_api,
    create_transaction_via_api,
    create_user_payload,
    login_and_get_headers,
)

pytestmark = pytest.mark.anyio


async def test_create_deposit_transaction_returns_201_and_transaction_shape(client) -> None:
    await client.post("/v1/users", json=create_user_payload("deposit@example.com"))
    headers = await login_and_get_headers(client, "deposit@example.com")
    account = await create_account_via_api(client, headers)

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 125.50,
            "currency": "GBP",
            "type": "deposit",
            "reference": "Initial deposit",
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("tan-")
    assert body["amount"] == 125.50
    assert body["currency"] == "GBP"
    assert body["type"] == "deposit"
    assert body["reference"] == "Initial deposit"

    account_response = await client.get(
        f"/v1/accounts/{account['accountNumber']}",
        headers=headers,
    )
    assert account_response.status_code == 200
    assert account_response.json()["balance"] == 125.50


async def test_create_withdrawal_transaction_returns_201_and_transaction_shape(client) -> None:
    await client.post("/v1/users", json=create_user_payload("withdrawal@example.com"))
    headers = await login_and_get_headers(client, "withdrawal@example.com")
    account = await create_account_via_api(client, headers)
    await create_transaction_via_api(
        client,
        account["accountNumber"],
        headers,
        amount=300.00,
        transaction_type="deposit",
        reference="Funding",
    )

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 75.00,
            "currency": "GBP",
            "type": "withdrawal",
            "reference": "Cash withdrawal",
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["amount"] == 75.00
    assert body["type"] == "withdrawal"
    assert body["reference"] == "Cash withdrawal"

    account_response = await client.get(
        f"/v1/accounts/{account['accountNumber']}",
        headers=headers,
    )
    assert account_response.status_code == 200
    assert account_response.json()["balance"] == 225.00


async def test_create_withdrawal_returns_422_for_insufficient_funds(client) -> None:
    await client.post("/v1/users", json=create_user_payload("insufficient@example.com"))
    headers = await login_and_get_headers(client, "insufficient@example.com")
    account = await create_account_via_api(client, headers)

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 25.00,
            "currency": "GBP",
            "type": "withdrawal",
            "reference": "Attempted withdrawal",
        },
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json() == {"message": "Insufficient funds to process transaction"}


async def test_create_transaction_returns_403_for_another_users_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("transaction-owner@example.com"))
    await client.post("/v1/users", json=create_user_payload("other-user@example.com"))
    owner_headers = await login_and_get_headers(client, "transaction-owner@example.com")
    other_headers = await login_and_get_headers(client, "other-user@example.com")
    account = await create_account_via_api(client, owner_headers)

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 10.00,
            "currency": "GBP",
            "type": "deposit",
            "reference": "Wrong owner",
        },
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json() == {"message": "The user is not allowed to access the transaction"}


async def test_create_transaction_returns_404_for_missing_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-transaction-account@example.com"))
    headers = await login_and_get_headers(client, "missing-transaction-account@example.com")

    response = await client.post(
        "/v1/accounts/01000000/transactions",
        json={
            "amount": 10.00,
            "currency": "GBP",
            "type": "deposit",
            "reference": "Missing account",
        },
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Bank account was not found"}


async def test_create_transaction_returns_400_when_required_data_is_missing(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-transaction-data@example.com"))
    headers = await login_and_get_headers(client, "missing-transaction-data@example.com")
    account = await create_account_via_api(client, headers)

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "currency": "GBP",
            "type": "deposit",
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["message"] == "Invalid details supplied"


async def test_create_transaction_returns_401_without_token(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-token@example.com"))
    headers = await login_and_get_headers(client, "missing-token@example.com")
    account = await create_account_via_api(client, headers)

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 10.00,
            "currency": "GBP",
            "type": "deposit",
            "reference": "No token",
        },
    )

    assert response.status_code == 401
    assert response.json() == {"message": "Access token is missing or invalid"}


async def test_create_deposit_returns_422_when_balance_would_exceed_contract_maximum(client) -> None:
    await client.post("/v1/users", json=create_user_payload("balance-cap@example.com"))
    headers = await login_and_get_headers(client, "balance-cap@example.com")
    account = await create_account_via_api(client, headers)

    await create_transaction_via_api(
        client,
        account["accountNumber"],
        headers,
        amount=9999.00,
        transaction_type="deposit",
        reference="Nearly maxed",
    )

    response = await client.post(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        json={
            "amount": 2.00,
            "currency": "GBP",
            "type": "deposit",
            "reference": "Too much",
        },
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json() == {"message": "Account balance cannot exceed 10000.00"}


async def test_list_transactions_returns_200_for_owned_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("list-transactions@example.com"))
    headers = await login_and_get_headers(client, "list-transactions@example.com")
    account = await create_account_via_api(client, headers)
    await create_transaction_via_api(
        client,
        account["accountNumber"],
        headers,
        amount=100.00,
        transaction_type="deposit",
        reference="Pay-in",
    )
    await create_transaction_via_api(
        client,
        account["accountNumber"],
        headers,
        amount=20.00,
        transaction_type="withdrawal",
        reference="Cash",
    )

    response = await client.get(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["transactions"]) == 2
    assert {transaction["type"] for transaction in body["transactions"]} == {"deposit", "withdrawal"}


async def test_list_transactions_returns_403_for_another_users_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("list-owner@example.com"))
    await client.post("/v1/users", json=create_user_payload("list-other@example.com"))
    owner_headers = await login_and_get_headers(client, "list-owner@example.com")
    other_headers = await login_and_get_headers(client, "list-other@example.com")
    account = await create_account_via_api(client, owner_headers)

    response = await client.get(
        f"/v1/accounts/{account['accountNumber']}/transactions",
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json() == {"message": "The user is not allowed to access the transactions"}


async def test_list_transactions_returns_404_for_missing_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-list-account@example.com"))
    headers = await login_and_get_headers(client, "missing-list-account@example.com")

    response = await client.get(
        "/v1/accounts/01000000/transactions",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Bank account was not found"}


async def test_fetch_specific_transaction_returns_200_for_owned_transaction(client) -> None:
    await client.post("/v1/users", json=create_user_payload("fetch-transaction@example.com"))
    headers = await login_and_get_headers(client, "fetch-transaction@example.com")
    account = await create_account_via_api(client, headers)
    transaction = await create_transaction_via_api(
        client,
        account["accountNumber"],
        headers,
        amount=42.00,
        transaction_type="deposit",
        reference="Single fetch",
    )

    response = await client.get(
        f"/v1/accounts/{account['accountNumber']}/transactions/{transaction['id']}",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction["id"]


async def test_fetch_specific_transaction_returns_404_for_missing_transaction(client) -> None:
    await client.post("/v1/users", json=create_user_payload("missing-transaction@example.com"))
    headers = await login_and_get_headers(client, "missing-transaction@example.com")
    account = await create_account_via_api(client, headers)

    response = await client.get(
        f"/v1/accounts/{account['accountNumber']}/transactions/tan-missing1",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Transaction was not found"}


async def test_fetch_specific_transaction_returns_403_for_another_users_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("fetch-owner@example.com"))
    await client.post("/v1/users", json=create_user_payload("fetch-other@example.com"))
    owner_headers = await login_and_get_headers(client, "fetch-owner@example.com")
    other_headers = await login_and_get_headers(client, "fetch-other@example.com")
    account = await create_account_via_api(client, owner_headers)
    transaction = await create_transaction_via_api(
        client,
        account["accountNumber"],
        owner_headers,
        amount=25.00,
        transaction_type="deposit",
        reference="Private transaction",
    )

    response = await client.get(
        f"/v1/accounts/{account['accountNumber']}/transactions/{transaction['id']}",
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json() == {"message": "The user is not allowed to access the transaction"}


async def test_fetch_transaction_returns_404_when_transaction_belongs_to_another_account(client) -> None:
    await client.post("/v1/users", json=create_user_payload("wrong-account@example.com"))
    headers = await login_and_get_headers(client, "wrong-account@example.com")
    first_account = await create_account_via_api(client, headers, name="First Account")
    second_account = await create_account_via_api(client, headers, name="Second Account")
    transaction = await create_transaction_via_api(
        client,
        first_account["accountNumber"],
        headers,
        amount=25.00,
        transaction_type="deposit",
        reference="First account only",
    )

    response = await client.get(
        f"/v1/accounts/{second_account['accountNumber']}/transactions/{transaction['id']}",
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == {"message": "Transaction was not found"}


async def test_list_transactions_returns_401_without_token(client) -> None:
    response = await client.get("/v1/accounts/01000000/transactions")

    assert response.status_code == 401
    assert response.json() == {"message": "Access token is missing or invalid"}
