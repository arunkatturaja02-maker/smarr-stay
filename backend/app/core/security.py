"""Password hashing and JWT creation/validation."""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.models.user import UserRole

settings = get_settings()

# pwdlib's recommended configuration currently uses Argon2id.
password_hasher = PasswordHash.recommended()

# Used only to make failed logins for unknown identifiers take a similar
# amount of time as failed logins for existing accounts (timing-attack defence).
# This is not a real user's password.
_DUMMY_PASSWORD_HASH = password_hasher.hash("timing-only-not-a-real-password")


class TokenValidationError(Exception):
    """Raised when an access token is missing required properties or is invalid."""


def hash_password(password: str) -> str:
    """Hash a plain-text password. Only this hash is stored in PostgreSQL."""
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Safely compare a password with its stored hash."""
    try:
        return password_hasher.verify(password, password_hash)
    except Exception:
        # A malformed hash must never crash the login endpoint.
        return False


def verify_dummy_password(password: str) -> None:
    """Spend the same hashing work for unknown identifiers."""
    verify_password(password, _DUMMY_PASSWORD_HASH)


def create_access_token(user_id: UUID, role: UserRole) -> str:
    """Create a short-lived signed JWT containing the user id and role."""
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "role": role.value,
        "type": "access",
        "iss": settings.app_name,
        "iat": now,
        "exp": expires_at,
        "jti": str(uuid4()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    """Validate signature, expiry, issuer and claims, then return the user id.

    The role claim is informative only. Authorization always reloads the user
    from the database so a stale or tampered role claim cannot grant access.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            issuer=settings.app_name,
            options={
                "require": ["exp", "iat", "iss", "sub", "role", "type"],
            },
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenValidationError("Token expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenValidationError("Token is invalid.") from exc

    if payload.get("type") != "access":
        raise TokenValidationError("Unexpected token type.")

    try:
        return UUID(str(payload["sub"]))
    except (ValueError, TypeError, KeyError) as exc:
        raise TokenValidationError("Token subject is invalid.") from exc
