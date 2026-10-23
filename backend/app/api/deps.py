"""Reusable FastAPI authentication and role-authorization dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import TokenValidationError, decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole

settings = get_settings()

# auto_error=False allows us to supply our own consistent JSON error response.
bearer_scheme = HTTPBearer(auto_error=False)


def _authentication_error(message: str, code: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": code, "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def _extract_token(
    request: Request, credentials: HTTPAuthorizationCredentials | None
) -> str | None:
    """Prefer an explicit Bearer token, otherwise use the HttpOnly cookie."""
    if credentials is not None and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    return request.cookies.get(settings.cookie_name)


def get_current_user(
    request: Request,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Validate the JWT and load the current approved, active user from the DB."""
    token = _extract_token(request, credentials)
    if not token:
        raise _authentication_error("Authentication is required.", "not_authenticated")

    try:
        user_id = decode_access_token(token)
    except TokenValidationError as exc:
        raise _authentication_error(
            "Your session is invalid or has expired. Please sign in again.",
            "invalid_token",
        ) from exc

    user = db.get(User, user_id)
    if user is None:
        raise _authentication_error(
            "Your session is invalid or has expired. Please sign in again.",
            "invalid_token",
        )

    # These checks are repeated on every request, so disabling or unapproving
    # an account takes effect immediately even if its JWT is still unexpired.
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_disabled",
                "message": "This account has been disabled. Contact an administrator.",
            },
        )
    if not user.is_approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "account_pending_approval",
                "message": "Your account is awaiting administrator approval.",
            },
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: UserRole):
    """Dependency factory for role-protected endpoints.

    Permissions come from the freshly loaded database row, not from the JWT
    role claim or any frontend value.

    Example:
        @router.get("/manager-only")
        def manager_only(user: Annotated[User, Depends(
            require_roles(UserRole.HOUSEKEEPING_MANAGER)
        )]):
            ...
    """

    def role_checker(current_user: CurrentUser) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "forbidden",
                    "message": "You do not have permission to access this resource.",
                },
            )
        return current_user

    return role_checker


ReceptionistOnly = Annotated[
    User, Depends(require_roles(UserRole.RECEPTIONIST))
]
ManagerOnly = Annotated[
    User, Depends(require_roles(UserRole.HOUSEKEEPING_MANAGER))
]
HousekeepingStaffOnly = Annotated[
    User, Depends(require_roles(UserRole.HOUSEKEEPING_STAFF))
]
