"""Shared test setup.

A fresh temporary SQLite database is used for every pytest run. The tests
never read DATABASE_URL from backend/.env and never touch PostgreSQL.
"""

import os
import secrets
import shutil
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import jwt
import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

TEST_DB_DIR = Path(tempfile.mkdtemp(prefix="staysmart-tests-"))
TEST_DB_PATH = TEST_DB_DIR / "staysmart_test.db"

# These environment variables override any local backend/.env file.
os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{TEST_DB_PATH.as_posix()}"
# Generated at test runtime so no reusable secret exists in the repository.
os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
os.environ["ENVIRONMENT"] = "test"
os.environ["COOKIE_SECURE"] = "false"
os.environ["COOKIE_SAMESITE"] = "lax"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "15"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.api.deps import require_roles  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

settings = get_settings()
VALID_PASSWORD = "StrongPass1"

ROLE_ENDPOINTS = {
    UserRole.RECEPTIONIST: "/api/auth/register/receptionist",
    UserRole.HOUSEKEEPING_MANAGER: "/api/auth/register/manager",
    UserRole.HOUSEKEEPING_STAFF: "/api/auth/register/staff",
}


# These probes exist only in the test process. They use the same production
# authorization dependency that future StaySmart endpoints will use.
probe_router = APIRouter(prefix="/api/test", tags=["test-only"])


@probe_router.get("/receptionist-only")
def receptionist_probe(
    user: Annotated[User, Depends(require_roles(UserRole.RECEPTIONIST))],
) -> dict[str, str]:
    return {"allowed": "true", "role": user.role.value}


@probe_router.get("/manager-only")
def manager_probe(
    user: Annotated[User, Depends(require_roles(UserRole.HOUSEKEEPING_MANAGER))],
) -> dict[str, str]:
    return {"allowed": "true", "role": user.role.value}


@probe_router.get("/staff-only")
def staff_probe(
    user: Annotated[User, Depends(require_roles(UserRole.HOUSEKEEPING_STAFF))],
) -> dict[str, str]:
    return {"allowed": "true", "role": user.role.value}


app.include_router(probe_router)


@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    """Run the real Alembic migration against the temporary SQLite file."""
    alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_config.set_main_option(
        "script_location", str(BACKEND_DIR / "alembic")
    )
    command.upgrade(alembic_config, "head")

    yield

    engine.dispose()
    shutil.rmtree(TEST_DB_DIR, ignore_errors=True)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def build_payload(role: UserRole, **overrides) -> dict[str, str]:
    suffix = uuid.uuid4().hex[:10]
    prefix = {
        UserRole.RECEPTIONIST: "REC",
        UserRole.HOUSEKEEPING_MANAGER: "MGR",
        UserRole.HOUSEKEEPING_STAFF: "STF",
    }[role]
    payload = {
        "full_name": f"Test {role.value.title()}",
        "employee_id": f"{prefix}-{suffix.upper()}",
        "email": f"{prefix.lower()}-{suffix}@example.com",
        "phone_number": "+91 98765 43210",
        "password": VALID_PASSWORD,
        "confirm_password": VALID_PASSWORD,
    }
    payload.update(overrides)
    return payload


def set_account_flags(user_id: str, **flags: bool) -> None:
    with SessionLocal() as db:
        user = db.get(User, uuid.UUID(user_id))
        assert user is not None
        for field, value in flags.items():
            setattr(user, field, value)
        db.commit()


def make_token(
    user_id: str,
    role: UserRole,
    *,
    expires_delta: timedelta = timedelta(minutes=10),
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role.value,
        "type": "access",
        "iss": settings.app_name,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


@pytest.fixture
def make_user(client):
    """Register a user and optionally approve/disable it directly in the test DB."""

    def _make_user(
        role: UserRole = UserRole.HOUSEKEEPING_STAFF,
        *,
        approved: bool = True,
        active: bool = True,
        **overrides,
    ) -> dict:
        payload = build_payload(role, **overrides)
        response = client.post(ROLE_ENDPOINTS[role], json=payload)
        assert response.status_code == 201, response.text

        with SessionLocal() as db:
            user = db.scalar(select(User).where(User.email == payload["email"]))
            assert user is not None
            user.is_approved = approved
            user.is_active = active
            db.commit()
            db.refresh(user)
            user_id = str(user.id)

        return {
            "payload": payload,
            "user_id": user_id,
            "email": payload["email"],
            "employee_id": payload["employee_id"],
        }

    return _make_user


@pytest.fixture
def login(client):
    def _login(
        identifier: str,
        password: str = VALID_PASSWORD,
        *,
        clear_cookies: bool = True,
    ):
        if clear_cookies:
            client.cookies.clear()
        return client.post(
            "/api/auth/login",
            json={"identifier": identifier, "password": password},
        )

    return _login
