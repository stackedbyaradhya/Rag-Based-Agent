from datetime import UTC, datetime, timedelta
import base64
import hashlib
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def _password_bytes(password: str) -> bytes:
    # Pre-hash to fixed length so very long passwords are always safe for bcrypt.
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_password_bytes(plain_password), hashed_password.encode("utf-8"))


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expires_delta = timedelta(minutes=settings.jwt_access_token_exp_minutes)
    expire = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {"exp": expire, "sub": subject}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        options={"verify_sub": False},
    )
