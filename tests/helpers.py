from __future__ import annotations


def create_user_payload(
    email: str = "user@example.com",
    *,
    name: str = "Test User",
    line1: str = "1 High Street",
    town: str = "Knutsford",
    county: str = "Cheshire",
    postcode: str = "WA16 6AA",
    phone_number: str = "+447700900123",
    password: str = "correct-horse-battery",
) -> dict:
    return {
        "name": name,
        "address": {
            "line1": line1,
            "town": town,
            "county": county,
            "postcode": postcode,
        },
        "phoneNumber": phone_number,
        "email": email,
        "password": password,
    }


async def login_and_get_headers(
    client,
    email: str,
    password: str = "correct-horse-battery",
) -> dict[str, str]:
    response = await client.post("/v1/auth/login", json={"email": email, "password": password})
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


async def create_account_via_api(
    client,
    headers: dict[str, str],
    *,
    name: str = "Daily Account",
    account_type: str = "personal",
) -> dict:
    response = await client.post(
        "/v1/accounts",
        json={"name": name, "accountType": account_type},
        headers=headers,
    )
    return response.json()


async def create_transaction_via_api(
    client,
    account_number: str,
    headers: dict[str, str],
    *,
    amount: float,
    transaction_type: str,
    currency: str = "GBP",
    reference: str | None = None,
) -> dict:
    payload = {
        "amount": amount,
        "currency": currency,
        "type": transaction_type,
    }
    if reference is not None:
        payload["reference"] = reference

    response = await client.post(
        f"/v1/accounts/{account_number}/transactions",
        json=payload,
        headers=headers,
    )
    return response.json()
