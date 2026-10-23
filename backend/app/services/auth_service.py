"""Service-layer authentication and registration logic."""

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_dummy_password, verify_password
from app.models.user import User, UserRole
from app.schemas.auth import RegistrationRequest


class InvalidCredentialsError(Exception):
    """Unknown identifier, wrong password, or either one."""


class AccountDisabledError(Exception):
    """The account exists but has been disabled by staff administration."""


class PendingApprovalError(Exception):
    """The account is valid but has not yet been approved."""


class DuplicateAccountError(Exception):
    def __init__(self, field: str) -> None:
        self.field = field
        super().__init__(field)


def _duplicate_field_from_integrity_error(error: IntegrityError) -> str | None:
    """Map a database uniqueness error to a safe public field name."""
    message = str(error.orig).lower()
    if "email" in message:
        return "email"
    if "employee_id" in message or "employee" in message:
        return "employee_id"
    return None


def create_staff_account(
    db: Session, data: RegistrationRequest, role: UserRole
) -> User:
    """Create an unapproved staff account.

    Public registration never creates an approved privileged account.
    """
    email = str(data.email).lower()
    employee_id = data.employee_id.upper()

    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise DuplicateAccountError("email")
    if db.scalar(select(User.id).where(User.employee_id == employee_id)) is not None:
        raise DuplicateAccountError("employee_id")

    user = User(
        full_name=data.full_name,
        employee_id=employee_id,
        email=email,
        phone_number=data.phone_number,
        password_hash=hash_password(data.password),
        role=role,
        is_active=True,
        is_approved=False,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        duplicate_field = _duplicate_field_from_integrity_error(exc)
        if duplicate_field is not None:
            raise DuplicateAccountError(duplicate_field) from exc
        raise
    db.refresh(user)
    return user


def authenticate_staff(db: Session, identifier: str, password: str) -> User:
    """Authenticate by email or employee ID.

    Error messages are deliberately generic so an attacker cannot use login
    responses to discover registered email addresses or employee IDs.
    """
    cleaned = identifier.strip()
    user = db.scalar(
        select(User).where(
            or_(
                User.email == cleaned.lower(),
                User.employee_id == cleaned.upper(),
            )
        )
    )

    if user is None:
        verify_dummy_password(password)
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    if not user.is_active:
        raise AccountDisabledError

    if not user.is_approved:
        raise PendingApprovalError

    return user
