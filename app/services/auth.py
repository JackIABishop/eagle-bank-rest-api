from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

PBKDF2_ITERATIONS = 100_000
SALT_BYTES = 16


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        iterations_raw, salt_b64, digest_b64 = password_hash.split("$", maxsplit=2)
        iterations = int(iterations_raw)
    except ValueError:
        return False

    salt = base64.b64decode(salt_b64.encode("utf-8"))
    expected_digest = base64.b64decode(digest_b64.encode("utf-8"))
    candidate_digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(candidate_digest, expected_digest)


def hash_password(plain_password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return (
        f"{PBKDF2_ITERATIONS}$"
        f"{base64.b64encode(salt).decode('utf-8')}$"
        f"{base64.b64encode(digest).decode('utf-8')}"
    )


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_access_token(user_id: str) -> str:
    expiry = datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_expiry_seconds)
    payload = {"sub": user_id, "exp": expiry}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
