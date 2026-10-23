"""Authentication and staff-registration API routes."""

from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegistrationRequest,
    RegistrationResponse,
    UserProfile,
)
from app.services.auth_service import (
    AccountDisabledError,
    DuplicateAccountError,
    InvalidCredentialsError,
    PendingApprovalError,
    authenticate_staff,
    create_staff_account,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
settings = get_settings()


def _raise_duplicate(error: DuplicateAccountError) -> NoReturn:
    if error.field == "email":
        message = "An account with this email already exists."
        code = "email_in_use"
    else:
        message = "An account with this employee ID already exists."
        code = "employee_id_in_use"

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={"code": code, "message": message, "field": error.field},
    )


def _register(
    db: Session, payload: RegistrationRequest, role: UserRole
) -> RegistrationResponse:
    try:
        user = create_staff_account(db, payload, role)
    except DuplicateAccountError as exc:
        _raise_duplicate(exc)

    return RegistrationResponse(
        message=(
            "Registration received. An administrator must approve your account "
            "before you can sign in."
        ),
        role=user.role,
        requires_approval=True,
        email=user.email,
    )


@router.post(
    "/register/receptionist",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_receptionist(
    payload: RegistrationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> RegistrationResponse:
    """Public registration for receptionists. The account starts unapproved."""
    return _register(db, payload, UserRole.RECEPTIONIST)


@router.post(
    "/register/manager",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_manager(
    payload: RegistrationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> RegistrationResponse:
    """Public registration for housekeeping managers. Starts unapproved."""
    return _register(db, payload, UserRole.HOUSEKEEPING_MANAGER)


@router.post(
    "/register/staff",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_staff(
    payload: RegistrationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> RegistrationResponse:
    """Public registration for housekeeping staff. Starts unapproved."""
    return _register(db, payload, UserRole.HOUSEKEEPING_STAFF)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> LoginResponse:
    """Authenticate an approved, active staff member and set an HttpOnly JWT cookie."""
    try:
        user = authenticate_staff(db, payload.identifier, payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "invalid_credentials",
                "message": "Invalid email/employee ID or password.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AccountDisabledError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_disabled",
                "message": "This account has been disabled. Contact an administrator.",
            },
        )
    except PendingApprovalError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_pending_approval",
                "message": "Your account is awaiting administrator approval.",
            },
        )

    token = create_access_token(user.id, user.role)
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        max_age=settings.access_token_seconds,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
        domain=settings.cookie_domain,
    )
    response.headers["Cache-Control"] = "no-store"

    return LoginResponse(
        message="Signed in successfully.",
        user=UserProfile.model_validate(user),
    )


@router.get("/me", response_model=UserProfile)
def get_me(current_user: CurrentUser, response: Response) -> UserProfile:
    """Return the authenticated user's safe profile."""
    response.headers["Cache-Control"] = "no-store"
    return UserProfile.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response) -> MessageResponse:
    """Clear the access-token cookie.

    JWTs are stateless, so a copied token remains technically valid until it
    expires. The short lifetime limits that risk. A token denylist can be added
    later if immediate revocation is required.
    """
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        domain=settings.cookie_domain,
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    response.headers["Cache-Control"] = "no-store"
    return MessageResponse(message="Signed out successfully.")
