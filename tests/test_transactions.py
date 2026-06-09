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
