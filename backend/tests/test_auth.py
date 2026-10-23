"""Module 1 authentication, registration and authorization tests."""

from datetime import timedelta

import pytest
from sqlalchemy import select

from app.core.security import verify_password
from app.db.session import SessionLocal
from app.models.user import User, UserRole

from .conftest import (
    ROLE_ENDPOINTS,
    VALID_PASSWORD,
    build_payload,
    make_token,
    set_account_flags,
)


def test_registration_creates_hashed_password(client):
    payload = build_payload(UserRole.RECEPTIONIST)

    response = client.post(ROLE_ENDPOINTS[UserRole.RECEPTIONIST], json=payload)

    assert response.status_code == 201
    assert response.json()["requires_approval"] is True
    assert "password" not in response.text
    assert "password_hash" not in response.text

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == payload["email"]))
        assert user is not None
        assert user.password_hash != VALID_PASSWORD
        assert user.password_hash.startswith("$argon2")
        assert verify_password(VALID_PASSWORD, user.password_hash)
        assert user.is_approved is False
        assert user.is_active is True


def test_plain_text_password_is_never_stored(client):
    payload = build_payload(UserRole.HOUSEKEEPING_STAFF)
    client.post(ROLE_ENDPOINTS[UserRole.HOUSEKEEPING_STAFF], json=payload)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == payload["email"]))
        assert user is not None
        assert user.password_hash != payload["password"]
        assert "StrongPass1" not in user.password_hash


def test_duplicate_email_is_rejected(client, make_user):
    existing = make_user(UserRole.RECEPTIONIST)
    duplicate = build_payload(
        UserRole.RECEPTIONIST,
        email=existing["email"].upper(),
    )

    response = client.post(ROLE_ENDPOINTS[UserRole.RECEPTIONIST], json=duplicate)

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "email_in_use"
    assert detail["field"] == "email"


def test_duplicate_employee_id_is_rejected(client, make_user):
    existing = make_user(UserRole.HOUSEKEEPING_MANAGER)
    duplicate = build_payload(
        UserRole.HOUSEKEEPING_MANAGER,
        employee_id=existing["employee_id"].lower(),
    )

    response = client.post(ROLE_ENDPOINTS[UserRole.HOUSEKEEPING_MANAGER], json=duplicate)

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "employee_id_in_use"
    assert detail["field"] == "employee_id"


def test_client_cannot_choose_role_in_registration(client):
    payload = build_payload(UserRole.RECEPTIONIST)
    payload["role"] = "HOUSEKEEPING_MANAGER"

    response = client.post(ROLE_ENDPOINTS[UserRole.RECEPTIONIST], json=payload)

    assert response.status_code == 422


def test_mismatched_passwords_are_rejected(client):
    payload = build_payload(
        UserRole.HOUSEKEEPING_STAFF,
        confirm_password="DifferentPass2",
    )

    response = client.post(ROLE_ENDPOINTS[UserRole.HOUSEKEEPING_STAFF], json=payload)

    assert response.status_code == 422
    assert "DifferentPass2" not in response.text
    assert "StrongPass1" not in response.text


def test_weak_password_is_rejected(client):
    payload = build_payload(
        UserRole.HOUSEKEEPING_STAFF,
        password="weakpass",
        confirm_password="weakpass",
    )

    response = client.post(ROLE_ENDPOINTS[UserRole.HOUSEKEEPING_STAFF], json=payload)

    assert response.status_code == 422
    assert "weakpass" not in response.text


@pytest.mark.parametrize("role", list(ROLE_ENDPOINTS))
def test_each_endpoint_assigns_its_fixed_role(client, role):
    payload = build_payload(role)

    response = client.post(ROLE_ENDPOINTS[role], json=payload)

    assert response.status_code == 201
    assert response.json()["role"] == role.value

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == payload["email"]))
        assert user is not None
        assert user.role == role
        assert user.is_approved is False


def test_approved_account_can_login_and_fetch_profile(client, make_user, login):
    user = make_user(UserRole.RECEPTIONIST)

    response = login(user["employee_id"])

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == user["email"]
    assert data["user"]["role"] == UserRole.RECEPTIONIST.value
    set_cookie = response.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["employee_id"] == user["employee_id"]


def test_login_with_email_is_supported(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_MANAGER)

    response = login(user["email"].upper())

    assert response.status_code == 200
    assert response.json()["user"]["email"] == user["email"]


def test_invalid_credentials_are_rejected_generically(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_STAFF)

    wrong_password = login(user["email"], "WrongPass1")
    unknown_identifier = login("does-not-exist@example.com", "WrongPass1")

    assert wrong_password.status_code == 401
    assert unknown_identifier.status_code == 401
    assert wrong_password.json()["detail"]["message"] == (
        unknown_identifier.json()["detail"]["message"]
    )
    assert wrong_password.json()["detail"]["code"] == "invalid_credentials"


def test_unapproved_account_cannot_login(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_MANAGER, approved=False)

    response = login(user["email"])

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "account_pending_approval"
    assert "set-cookie" not in response.headers


def test_unapproved_account_cannot_access_protected_endpoint(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_MANAGER)
    login(user["email"])

    set_account_flags(user["user_id"], is_approved=False)
    response = client.get("/api/auth/me")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "account_pending_approval"


def test_disabled_account_cannot_login(client, make_user, login):
    user = make_user(UserRole.RECEPTIONIST, active=False)

    response = login(user["email"])

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "account_disabled"


def test_disabled_account_cannot_access_protected_endpoint(client, make_user, login):
    user = make_user(UserRole.RECEPTIONIST)
    login(user["email"])

    set_account_flags(user["user_id"], is_active=False)
    response = client.get("/api/auth/me")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "account_disabled"


def test_unauthenticated_user_cannot_access_protected_endpoints(client):
    me = client.get("/api/auth/me")
    manager_probe = client.get("/api/test/manager-only")

    assert me.status_code == 401
    assert me.json()["detail"]["code"] == "not_authenticated"
    assert manager_probe.status_code == 401


def test_receptionist_cannot_access_manager_only_endpoint(client, make_user, login):
    user = make_user(UserRole.RECEPTIONIST)
    login(user["email"])

    allowed = client.get("/api/test/receptionist-only")
    forbidden = client.get("/api/test/manager-only")

    assert allowed.status_code == 200
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "forbidden"


def test_staff_cannot_access_receptionist_only_endpoint(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_STAFF)
    login(user["email"])

    allowed = client.get("/api/test/staff-only")
    forbidden = client.get("/api/test/receptionist-only")

    assert allowed.status_code == 200
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "forbidden"


def test_role_claim_is_not_trusted_for_authorization(client, make_user):
    user = make_user(UserRole.RECEPTIONIST)
    # A correctly signed token whose role claim lies about the user's role.
    forged_role_token = make_token(user["user_id"], UserRole.HOUSEKEEPING_MANAGER)

    response = client.get(
        "/api/test/manager-only",
        headers={"Authorization": f"Bearer {forged_role_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "forbidden"


def test_expired_token_is_rejected(client, make_user):
    user = make_user(UserRole.RECEPTIONIST)
    expired_token = make_token(
        user["user_id"],
        UserRole.RECEPTIONIST,
        expires_delta=timedelta(minutes=-1),
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_token"


def test_me_returns_only_safe_profile_fields(client, make_user, login):
    user = make_user(UserRole.HOUSEKEEPING_MANAGER)
    login(user["email"])

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert set(response.json()) == {
        "id",
        "full_name",
        "employee_id",
        "email",
        "phone_number",
        "role",
    }
    assert "password" not in response.text
    assert user["user_id"] == response.json()["id"]


def test_logout_clears_cookie_and_session(client, make_user, login):
    user = make_user(UserRole.RECEPTIONIST)
    login(user["email"])
    assert client.get("/api/auth/me").status_code == 200

    logout = client.post("/api/auth/logout")
    after_logout = client.get("/api/auth/me")

    assert logout.status_code == 200
    assert after_logout.status_code == 401
    assert after_logout.json()["detail"]["code"] == "not_authenticated"
