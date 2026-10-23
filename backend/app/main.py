"""FastAPI application entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api.routes import auth, health
from app.core.config import get_settings

logger = logging.getLogger("staysmart")
settings = get_settings()

app = FastAPI(
    title="StaySmart API",
    description=(
        "Module 1: staff authentication, registration approval, JWT sessions "
        "and role-based authorization."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    return response


@app.exception_handler(RequestValidationError)
async def safe_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return field errors without echoing submitted values.

    FastAPI's default 422 response can include the rejected ``input`` value.
    That is undesirable for password fields, so only locations, messages, and
    error types are returned here.
    """
    errors = [
        {
            "loc": list(error.get("loc", [])),
            "msg": error.get("msg", "Invalid value."),
            "type": error.get("type", "value_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(OperationalError)
async def database_connection_error_handler(
    request: Request, exc: OperationalError
) -> JSONResponse:
    """Return a safe 503 instead of exposing database connection details."""
    logger.exception("Database connection failure while handling %s", request.url.path)
    return JSONResponse(
        status_code=503,
        content={
            "detail": {
                "code": "database_unavailable",
                "message": "The database is currently unavailable. Please try again later.",
            }
        },
    )


app.include_router(auth.router, prefix="/api")
app.include_router(health.router)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {"message": "StaySmart API is running. See /docs for the API reference."}
