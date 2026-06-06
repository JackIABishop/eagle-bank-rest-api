from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


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
